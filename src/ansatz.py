from typing import List

from qulacs import Observable, QuantumCircuit
from qulacs.gate import CZ, RX, RY, RZ, Identity, Y, merge

from .time_evolusion_gate import create_time_evo_unitary

def ansatz_list(n_qubit: int, depth: int, params: list[float], ugateH: Observable, gateset: int) -> QuantumCircuit:
    """
    VQC ansatz circuit after encoding part
   
    Args:
        n_qubit (int): number of qubits
        depth (int): depth of ansatz circuit
        params (ndarray): Initial params for rotation gates and time evolusion gate:[t1, t2, ..., td, theta1, ..., theta(d*4)]
        ugateH (Observable): `qulacs_core.Observable`, Hamiltonian used in time evolusion gate i.e. exp(-iHt)
        gateset (int): number of gateset  大体1でいいと思う
    
    Returns:
        QuantumCircuit

    今のところXYモデルしか対応してない

    """

    circuit = QuantumCircuit(n_qubit)
    
    flag = depth # Tracking angles in params

    for d in range(depth):

        for i in range(gateset):
            # Rotation gate
            circuit.add_gate(RX(0, params[flag + i]))
            circuit.add_gate(RX(1, params[flag + i + 1]))
            circuit.add_gate(RY(0, params[flag + i + 2]))
            circuit.add_gate(RY(1, params[flag + i + 3]))
        
        # CZ gate
        circuit.add_gate(CZ(0, 1))

        if depth == 0:
            t_before = 0
            t_after = params[depth]
            time_evo_gate = create_time_evo_unitary(ugateH, t_before, t_after)
            circuit.add_gate(time_evo_gate)
        else:
            t_before = param[depth]
            t_after = params[depth + 1]
            time_evo_gate = create_time_evo_unitary(ugateH, t_before, t_after)
            circuit.add_gate(time_evo_gate)

        flag += 4 * gateset

    return circuit
            