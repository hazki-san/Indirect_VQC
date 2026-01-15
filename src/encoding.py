import numpy as np

from typing import List

from qulacs import QuantumCircuit, Observable
from qulacs.gate import CZ, RX, RY, RZ, Identity, Y, merge

from src.time_evolusion_gate import create_time_evo_unitary

def encode(
    nqubit: int, 
    feature: list[float], 
    param: list[float], 
    depth: int, 
    ugateH: Observable, 
    encode_type: int, 
    feature_num: int,
    num_for_et2layer: int,
    fixed_random_params: list[float],
) -> QuantumCircuit:
    """
    VQC encoding circuit after encoding part
   
    Args:
        nqubit (int): number of qubits
        feature (ndarray): Initial params for rotation gates and time evolusion gate:[t1, t2, ..., td, theta1, ..., theta(d*4)]
        param (ndarray): 一番初めの時間が欲しい
        depth (int): paramsから指定の時間を引っ張ってくる用
        encode_type: エンコード回路どうしますかのやつ config参照
    Returns:
        QuantumCircuit

    今のところXYモデルしか対応してない

    """

    circuit = QuantumCircuit(nqubit)
    if encode_type == -1: #hardware efficient circuit
        for i in range (nqubit):
            for j in range (feature_num):
                circuit.add_gate(RX(i, feature[j]))

    elif encode_type == 1:
        for i in range (feature_num):
            if i == 0:
                t_before = 0
                t_after = param[i]
            else:
                t_before = param[i-1]
                t_after = param[i]
            t_evo_gate = create_time_evo_unitary(ugateH, t_before, t_after)

            circuit.add_gate(RX(0, feature[i]))
            circuit.add_gate(RX(1, fixed_random_params[3*i]))
            circuit.add_gate(RY(0, fixed_random_params[3*i+1]))
            circuit.add_gate(RY(1, fixed_random_params[3*i+2]))
            circuit.add_gate(CZ(0, 1))

            circuit.add_gate(t_evo_gate)
    elif encode_type == 2:
        circuit.add_gate(RX(0, feature[0]))
        circuit.add_gate(RX(1, feature[1]))
        circuit.add_gate(RY(0, feature[2]))
        circuit.add_gate(RY(1, feature[3]))
        circuit.add_gate(CZ(0, 1))
        t_before = 0
        t_after = param[0]
        time_evo_gate = create_time_evo_unitary(ugateH, t_before, t_after)
        circuit.add_gate(time_evo_gate)

        for i in range (num_for_et2layer):
            circuit.add_gate(RX(0, fixed_random_params[4*i]))
            circuit.add_gate(RX(1, fixed_random_params[4*i+1]))
            circuit.add_gate(RY(0, fixed_random_params[4*i+2]))
            circuit.add_gate(RY(1, fixed_random_params[4*i+3]))
            circuit.add_gate(CZ(0, 1))
            t_before = param[i]
            t_after = param[i+1]
            time_evo_gate = create_time_evo_unitary(ugateH, t_before, t_after)
            circuit.add_gate(time_evo_gate)

    else:
        
        circuit.add_gate(RX(0, feature[0]))
        circuit.add_gate(RX(1, feature[1]))
        circuit.add_gate(RY(0, feature[2]))
        circuit.add_gate(RY(1, feature[3]))
        circuit.add_gate(CZ(0, 1))

        #time evolusion
        t_before = 0
        t_after = param[0]
        time_evo_gate = create_time_evo_unitary(ugateH, t_before, t_after)
        circuit.add_gate(time_evo_gate)

    return circuit
