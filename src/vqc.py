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
        nqubits: int,
        optimization: Dict,
        init_param: Union[List[float], str],
    ) -> None:
        """
        Args:
            nqubits: number of qubits
            optimization: 
            init_param[]:

            必要に応じてansatz入れたり
        """    
        self.nqubits = nqubits

        # Optimization variables
        self.optimization_status: bool = optimization["status"]
        self.optimizar: str = optimization["algorithm"]
        self.constraints: bool = optimization["constraints"]

        self.init_param = init_param
        
        self.circuit = None
    
    def create_circuit(self):

        """
        encodingとansatzのところの回路を合体させる
        """
        encoding_circuit = encode(
            n_qubit = self.nqubits,
            feature = self.feature,
            params = self.params,
            depth = self.depth,
        )
        ansatz_circuit = ansatz_list(
            n_qubit = self.nqubits,
            depth = self.depth,
            params = self.params,
            ugateH = self.ugateH,
            gateset = self.gateset,
        )
        circuit = encoding_circuit + ansatz_circuit
        return self.circuit

    def cost_function(num: int, label_train: List[int], label_result: List[int]) -> float:

        """
        loss_functionのほうがいいかも

        Args:
            num (int) : データ数
            label_train: 正解ラベル列
            label_result: 測定結果列
        Returns:
            cost: 平均二乗誤差をcostとして返す 0,1なので二乗しても変わらなさそうだからしてない

        """
        cost : float = 0

        for i in range(num):
            cost += (label_train[i]-label_result[i])
        
        cost = cost / num

        return cost


    def run_optimization():
        
        cost_history = []
        min_cost = None
        optimized_parms = None

        opt = minimize(
            self.cost_function,#検討
            parameters,
            method = self.optimizar,
            constraints = self.constraints,
            callback=lambda x: cost_history.append(self.cost_function(x)),
        )

        min_cost = np.min(cost_history)
        optimized_parms = opt.x.tolist()

        return min_cost, optimized_parms
    
    def run_vqc():

        return None