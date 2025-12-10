import os
from datetime import datetime
from typing import Dict, List, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
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


        """    
        self.nqubit = nqubit

        # Optimization variables
        self.optimization_status: bool = optimization["status"]
        self.optimizar: str = optimization["algorithm"]
        self.constraints: bool = optimization["constraints"]

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

        #about trainig data
    
    def create_circuit(self, param):

        """
            encodingとansatzのところの回路を合体させる
        """
        encoding_circuit = encode(
            n_qubit = self.nqubit,
            feature = self.feature,
            param = self.param,
            depth = self.depth,
        )
        ansatz_circuit = ansatz_list(
            n_qubit = self.nqubit,
            depth = self.depth,
            param = param,
            ugateH = self.ugateH,
            gateset = self.gateset,
        )
        circuit = encoding_circuit
        circuit.merge_circuit(ansatz_circuit)

        return self.circuit

    def loss_func(param): #theta param
        
        #theta更新を一行入れる

        y_pred = []
        for i in range(train_Data):
            state = QuantumState(n_qubit)
            state.set_zero_state()

            #入力状態計算、出力状態計算
            #create_circuitに引数でtheta渡さないといけない気がとてもする
            create_circuit(param).update_quantum_state(state)

            #モデルの出力(Z)
            obs = Observable(nqubit)
            obs.add_operator(2.,'Z 0')
            y_pred[i] = obs.get_expectation_value(state)
        
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
        #初期(ランダム)パラメータでのコスト関数の値
        initial_cost = self.loss_func(init_param)

        cost_history = []
        min_cost = None
        optimized_parms = None

        #constraintsの確認

        #最適化実行
        vqc_result = minimize(
            loss_func, 
            init_param,
            method = self.optimizar,
            constraints = self.constraints,
            callback=lambda x: cost_history.append(self.loss_func(x)),
        )

        min_cost = np.min(cost_history)
        optimized_parms = opt.x.tolist()

        return vqc_result