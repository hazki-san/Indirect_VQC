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
from src.ansatz import ansatz_list

class IndirectVQC:

    def __init__(
        self,
        nqubit: int,
        ansatz: Dict,
        init_param: Union[List[float], str],
        optimization: Dict,
        dataset: Dict,
    ) -> None:
        """
            Args:
                nqubit: number of qubits
                ansatz: ansatz関係のもの
                optimization: status, algorithm and constraints
                init_param[]:空の場合はcreateparamで適当に作る
                optimization:
                dataset:

        """    
        self.nqubit = nqubit

        # Optimization variables
        self.optimization_status: bool = optimization["status"]
        self.optimizar: str = optimization["algorithm"]
        self.constraints: bool = optimization["constraint"]

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

        #open data file
        self.train_feature = np.loadtxt(self.train_data_path, delimiter=',')
        self.test_feature = np.loadtxt(self.test_data_path, delimiter=',')
        #特徴を0~2πに正規化するように encodingの内側でも可


    def create_circuit(self, param, feature):

        """
            encodingとansatzのところの回路を合体させる
        """
        encoding_circuit = encode(
            nqubit = self.nqubit,
            feature = feature,##self.featureじゃなくてその中の要素を引数で入れた方がいいかも
            param = param,
            depth = self.depth,
            ugateH=self.ugate_hami,
        )
        ansatz_circuit = ansatz_list(
            nqubit = self.nqubit,
            depth = self.depth,
            param = param,
            ugateH = self.ugate_hami,
            gateset = self.ansatz_gateset,
        )
        circuit = encoding_circuit
        circuit.merge_circuit(ansatz_circuit)

        return circuit

    #def set_U_out(param):
        

    def loss_func(self, param): #theta param
        
        #theta更新を一行入れる?

        y_pred = []
        y_train = self.train_feature[:,self.feature_num]

        #for debug
        print(f"y_train is [{y_train}]" )

        for i in range(self.train_num):
            state = QuantumState(self.nqubit)
            state.set_zero_state()

            #入力状態計算、出力状態計算
            #create_circuitに引数でtheta渡さないといけない気がとてもする
            self.create_circuit(param, self.train_feature[i]).update_quantum_state(state)

            #モデルの出力(Z)
            obs = Observable(self.nqubit)
            obs.add_operator(2.,'Z 0')
            y_pred.append(obs.get_expectation_value(state))
            #debug
            print(f"  #y_{i}_pred: {obs.get_expectation_value(state)}")
                    
        loss = ((y_pred - y_train)**2).mean()

        return loss
 
    def run_vqc(self):

        #もしinit_paramが空かrandomにしろという感じだったら
        init_param = create_param(
            depth=self.depth, 
            gateset = self.ansatz_gateset, 
            t_init = self.ansatz_t_min, 
            t_final=self.ansatz_t_max,
        )
        #for debug
        print(init_param)


        #初期(ランダム)パラメータでのコスト関数の値
        initial_cost = self.loss_func(init_param)

        cost_history = []
        min_cost = None
        optimized_parms = None

        #constraintsの確認

        #最適化実行
        opt = minimize(
            fun=self.loss_func, 
            x0=init_param,
            method = self.optimizar,
            constraints = self.constraints,
            callback=lambda x: cost_history.append(self.loss_func(x)),
        )

        min_cost = np.min(cost_history)
        optimized_param = opt.x.tolist()

        vqc_result: Dict = {
            "initial_cost": initial_cost,
            "min_cost": min_cost,
            "optimized_param": optimized_param
        }

        return vqc_result