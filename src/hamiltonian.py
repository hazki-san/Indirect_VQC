from typing import List

from openfermion.ops.operators.qubit_operator import QubitOperator
from qulacs import Observable
from qulacs.observable import create_observable_from_openfermion_text

def create_xy_hamiltonian(n_qubit: int, cn: List[float], bn: list[float], r: float) -> Observable:

    """
        
    """