import numpy as np

from typing import List

from qulacs import QuantumCircuit, Observable
from qulacs.gate import CZ, RX, RY, RZ, Identity, Y, merge

from src.time_evolusion_gate import create_time_evo_unitary

def encode(nqubit: int, feature: list[float], param: list[float], depth: int, ugateH: Observable) -> QuantumCircuit:
    """
    VQC encoding circuit after encoding part
   
    Args:
        nqubit (int): number of qubits
        feature (ndarray): Initial params for rotation gates and time evolusion gate:[t1, t2, ..., td, theta1, ..., theta(d*4)]
        param (ndarray): 一番初めの時間が欲しい
        depth (int): paramsから指定の時間を引っ張ってくる用
    Returns:
        QuantumCircuit

    今のところXYモデルしか対応してない

    """

    circuit = QuantumCircuit(nqubit)

    #angle_1 = np.arcsin(feature[0])
    #angle_2 = np.arcsin(feature[1])
    #angle_3 = np.arcsin(feature[2])
    #angle_4 = np.arcsin(feature[3])
    
    circuit.add_gate(RX(0, angle_1))
    circuit.add_gate(RX(1, angle_2))
    circuit.add_gate(RY(0, angle_3))
    circuit.add_gate(RY(1, angle_4))
    circuit.add_gate(CZ(0, 1))

    #time evolusion
    t_before = 0
    t_after = param[0]
    #t_after = param[depth]
    time_evo_gate = create_time_evo_unitary(ugateH, t_before, t_after)
    circuit.add_gate(time_evo_gate)

    return circuit
