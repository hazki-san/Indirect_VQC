import os
from datetime import datetime
from typing import Dict, List, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from qulacs import DensityMatrix, Observable, QuantumCircuit, QuantumState
from qulacsvis import circuit_drawer
from scipy.optimize import minimize

from src.createparam import create_param
from src.hamiltonian import create_xy_hamiltonian
from src.encoding import encode
from src.ansatz import ansatz_list, he_ansatz
from src.constraint import create_time_constraints

from src.database.schema import Job, JobFactory
from src.database.sqlite import DBClient, create_job_table, insert_job

import time
import datetime

#count iteration
count_itr = 0
param_history = []
cost_history = []
iter_history = []
y_pred = []
y_pred_history = []

class IndirectVQC:

    def __init__(
        self,
        nqubit: int,
        ansatz: Dict,
        init_param: Union[List[float], str],
        optimization: Dict,
        dataset: Dict,
        output: Dict,
        config: Dict,
    ) -> None:
        """
            Args:
                nqubit: number of qubits
                ansatz: ansatz関係のもの
                optimization: status, algorithm and constraint
                init_param[]:空の場合はcreateparamで適当に作る
                optimization:
                dataset:
                output: DBまわり
                condig: DBに記録する用

        """    
        self.nqubit = nqubit

        # Optimization variables
        self.optimization_status: bool = optimization["status"]
        self.optimizar: str = optimization["algorithm"]
        self.constraint: bool = optimization["constraint"]

        # Ansatz variables
        self.ansatz_type: int = ansatz["type"]
        self.depth: int = ansatz["depth"]
        self.ansatz_t_min: float = ansatz["ugate"]["time"]["min"]
        self.ansatz_t_max: float = ansatz["ugate"]["time"]["max"]
        self.ansatz_gateset: int = ansatz["gateset"]
        self.ansatz_cn: List = ansatz["ugate"]["coefficient"]["cn"]
        self.ansatz_bn: List = ansatz["ugate"]["coefficient"]["bn"]
        self.ansatz_r: float = ansatz["ugate"]["coefficient"]["r"]
        
        self.init_param = init_param
        
        self.circuit = None

        self.ugate_hami = create_xy_hamiltonian(self.nqubit, self.ansatz_cn, self.ansatz_bn, self.ansatz_r)
        
        #about trainig data
        self.train_data_path :str = dataset["train"]["path"]
        self.train_num :int = dataset["train"]["num"]
        self.test_data_path :str = dataset["test1"]["path"]
        self.test_num :int = dataset["test1"]["num"]
        self.feature_num :int = dataset["feature_num"]
        self.encode_type :int = dataset["encode_type"]

        #about outputs
        self.dbout_id :str = output["project"]["id"]
        self.dbout_import :bool = output["bigquery"]["import"]
        self.dbout_dataset :str = output["bigquery"]["dataset"]
        self.dbout_table :str = output["bigquery"]["table"]
        self.config = config

        df = pd.read_csv(self.train_data_path, header=None)
        features = df.iloc[:, 0:self.feature_num].to_numpy(dtype = float)
        ys = df.iloc[:, self.feature_num].to_numpy(dtype=float)
        min_values = features.min(axis=0)
        max_values = features.max(axis=0)
        #正規化
        normalized_features = ((features - min_values) / (max_values - min_values)) * (2 * np.pi)
        self.train_features = normalized_features
        self.y_train = ys

        self.fixed_random_params = []
        self.et2_layers = 3
        #ecnodetypeごとの固定ランダムパラメータ
        if self.encode_type == 1:
            self.fixed_random_params = np.random.uniform(0, np.pi*2, self.feature_num*3)
        elif self.encode_type == 2:
            self.fixed_random_params = np.random.uniform(0, np.pi*2, self.et2_layers*4)
        
        
        """
        #open data file
        self.train_feature = pd.read_csv(self.train_data_path, header=None)
        features = self.train_feature.iloc[:, 0:self.feature_num].tolist() #irisは1~4列目が特徴量、5列目がラベル
        min_values = features.min()
        max_values = features.max()
        #正規化
        normalized_features = ((features - min_values) / (max_values - min_values)) * (2 * np.pi)
        self.train_feature.iloc[:, 0:self.feature_num] = normalized_features
        """
        #debug
        print(self.train_features)

    def record(self, param):
        global param_history
        global cost_history
        global iter_history
        global count_itr
        global y_pred
        global y_pred_history
        param_history.append(param)
        #cost_history.append(self.loss_func(param))
        #y_pred_history.append(list(y_pred))
        iter_history.append(count_itr)

    def record_database(
        self, job: Job, is_bq_import: bool, gcp_project_id: str, dataset: str, table: str
    ) -> None:
        client = DBClient("data/job_results.sqlite3")
        insert_job(client, job)

    def create_circuit(self, param, feature):

        """
            encodingとansatzのところの回路を合体させる
        """
        encoding_circuit = encode(
            nqubit = self.nqubit,
            feature = feature,
            param = param,
            depth = self.depth,
            ugateH=self.ugate_hami,
            encode_type=self.encode_type,
            feature_num=self.feature_num,
            num_for_et2layer=self.et2_layers,
            fixed_random_params=self.fixed_random_params,
        )
        #ランダムなansatzを入れる 何層か
        if(self.encode_type == -1): # direct
            ansatz_circuit = he_ansatz(
                nqubit=self.nqubit,
                depth=self.depth,
                param=param
            )
        else: # indirect
            ansatz_circuit = ansatz_list(
                nqubit = self.nqubit,
                depth = self.depth,
                param = param,
                ugateH = self.ugate_hami,
                gateset = self.ansatz_gateset,
                encode_type=self.encode_type,
                feature_num=self.feature_num,
                num_for_et2layer=self.et2_layers,
            )
        circuit = encoding_circuit
        circuit.merge_circuit(ansatz_circuit)

        return circuit

    def loss_func(self, param): #theta param
        
        #theta更新を一行入れる?
        global y_pred
        y_pred = []

        for i in range(self.train_num):
            state = QuantumState(self.nqubit)
            state.set_zero_state()

            #入力状態計算、出力状態計算
            self.create_circuit(param, self.train_features[i]).update_quantum_state(state)

            #モデルの出力(Z)
            obs = Observable(self.nqubit)
            obs.add_operator(1.,'Z 0')
            y_pred.append(obs.get_expectation_value(state))

        #debug
        global count_itr
        if(count_itr % 100 == 0): 
            #print(f"#{count_itr}  y_pred: {y_pred}")
            print(f"#{count_itr}   param: {param}")
            print(f"--------------------------------------------")
        count_itr += 1

        loss = ((y_pred - self.y_train)**2).mean()
        
        #record
        global cost_history
        global y_pred_history
        cost_history.append(loss)
        y_pred_history.append(np.array(y_pred).tolist())
        
        return loss
 
    def run_vqc(self):

        start_time = time.perf_counter()
        now = datetime.datetime.now()

        global param_history
        global cost_history
        global iter_history
        global y_pred
        global y_pred_history

        cost_history = []
        min_cost = None
        optimized_parms = None
        vqc_constraint = None
        initial_cost: float = None

        #for debug
        print(f"y_train  {self.y_train}" )

        if self.ansatz_type == "direct":
            self.encode_type = -1 #encodeそのまま使いたかったのでこの処理

        #もしinit_paramが空かrandomにしろという感じだったらの分岐を後で作る
        init_param = create_param(
            depth=self.depth, 
            gateset = self.ansatz_gateset, 
            t_init = self.ansatz_t_min, 
            t_final=self.ansatz_t_max,
            encode_type=self.encode_type,
            feature_num=self.feature_num,
            num_for_et2layer=self.et2_layers
        )
        #for debug
        print(f"init_param {init_param}")

        #初期(ランダム)パラメータでのコスト関数の値
        initial_cost = self.loss_func(init_param)
        cost_history.append(initial_cost)

        #encodeで使うtのnum
        if self.encode_type == 1:
            t_num_en = self.feature_num
        else:
            t_num_en = 1

        #constraintの確認
        if self.constraint and self.optimizar == "SLSQP":
            vqc_constraint = create_time_constraints(self.depth+t_num_en, self.depth*5+t_num_en)
        
        #bounds = [(0, 2*np.pi)] * len(init_param)
        
        option = {"maxiter": 2000}
        
        #最適化実行
        opt = minimize(
            fun=self.loss_func, 
            x0=init_param,
            method = self.optimizar,
            #bounds = bounds,
            constraints = vqc_constraint,
            #callback=lambda x: cost_history.append(self.loss_func(x)),
            callback=self.record,
            options=option,
        )
        end_time = time.perf_counter()
        #debug
        print(f"cost_history  {cost_history}")

        #record to database
        job = JobFactory(self.config).create(
            now, start_time, end_time, cost_history, param_history, iter_history, self.y_train, y_pred_history, self.fixed_random_params,
        )
        self.record_database(
            job,
            self.dbout_import,
            self.dbout_id,
            self.dbout_dataset,
            self.dbout_table,
        )

        #蛇足なのでそのうちmainと合わせて消したいかも？
        min_cost = cost_history[-1]
        optimized_param = param_history[-1]

        vqc_result: Dict = {
            "initial_cost": initial_cost,
            "min_cost": min_cost,
            "optimized_param": optimized_param
        }
        
        
        return vqc_result

    def debug(self):

        cost_history = []
        min_cost = None
        optimized_parms = None
        vqc_constraint = None
        initial_cost: float = None

        #for debug
        print(f"y_train  {self.y_train}" )

        #もしinit_paramが空かrandomにしろという感じだったら
        init_param = create_param(
            depth=self.depth, 
            gateset = self.ansatz_gateset, 
            t_init = self.ansatz_t_min, 
            t_final=self.ansatz_t_max,
        )
        #for debug
        
        print(f"init_param  {init_param}" )


        #初期(ランダム)パラメータでのコスト関数の値
        initial_cost = self.loss_func(init_param)

        min_cost = None

        #constraintsの確認

        #最適化実行


        vqc_result: Dict = {
            "initial_cost": initial_cost,
            "min_cost": min_cost,
            "optimized_param": None
        }

        return vqc_result