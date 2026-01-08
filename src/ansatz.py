from typing import List

from qulacs import Observable, QuantumCircuit
from qulacs.gate import CZ, RX, RY, RZ, Identity, Y, merge

from .time_evolusion_gate import create_time_evo_unitary

def ansatz_list(
    nqubit: int, 
    depth: int, 
    param: list[float], 
    ugateH: Observable, 
    gateset: int, 
    encode_type: int, 
    feature_num: int,
    num_for_et2layer: int,
) -> QuantumCircuit:
    """
    VQC ansatz circuit after encoding part
   
    Args:
        nqubit (int): number of qubits
        depth (int): depth of ansatz circuit
        param (ndarray): Initial params for rotation gates and time evolusion gate:[t1, t2, ..., td, theta1, ..., theta(d*4)]
        ugateH (Observable): `qulacs_core.Observable`, Hamiltonian used in time evolusion gate i.e. exp(-iHt)
        gateset (int): number of gateset  大体1でいいと思う -> 撤去
    
    Returns:
        QuantumCircuit

    今のところXYモデルしか対応してない

    """

    circuit = QuantumCircuit(nqubit)
    
    if encode_type == 1:
        en_t_num = feature_num
    elif encode_type == 2:
        en_t_num = 1 + num_for_et2layer
    else:
        en_t_num = 1 

    flag = depth + en_t_num # Tracking angles in params

    for d in range(depth):
        #gateset周りが多分createparamのところでつじつま合わせできていないのでとりあえず1固定このまま
        
        circuit.add_gate(RX(0, param[flag]))
        circuit.add_gate(RX(1, param[flag + 1]))
        circuit.add_gate(RY(0, param[flag + 2]))
        circuit.add_gate(RY(1, param[flag + 3]))
    
        # CZ gate
        circuit.add_gate(CZ(0, 1))

        t_before = param[en_t_num + d - 1]
        t_after = param[en_t_num + d]
        time_evo_gate = create_time_evo_unitary(ugateH, t_before, t_after)
        circuit.add_gate(time_evo_gate)

        flag += 4 

    return circuit

def he_ansatz(nqubit: int, depth: int, param: list[float]):
    
    circuit = QuantumCircuit(nqubit)
    for d in range (depth):
        for i in range (nqubit):
            circuit.add_gate(RY(i, param[2*nqubit*d + 2*i]))
            circuit.add_gate(RZ(i, param[2*nqubit*d + 2*i+1]))
        for i in range(nqubit // 2):
            circuit.add_gate(CZ(2*i, 2*i+1))
        for i in range (nqubit // 2 - 1):
            circuit.add_gate(CZ(2*i+1, 2*i+2))
    #追加の回転
    for i in range (nqubit):
        circuit.add_gate(RX, param[2*i + 2*nqubit*depth])
        circuit.add_gate(RX, param[2*i + 2*nqubit*depth + 1])
    
    return circuit