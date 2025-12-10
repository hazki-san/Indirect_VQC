from typing import List

from openfermion.ops.operators.qubit_operator import QubitOperator
from qulacs import Observable
from qulacs.observable import create_observable_from_openfermion_text

def create_xy_hamiltonian(nqubit: int, cn: List[float], bn: list[float], r: float) -> Observable:

    """
        Mathematical form:

        .. math::
        H_\text{custom} = \sum_{k=1}^{N-1}c_{k}[(1+\gamma)X_{k}X_{k+1}+(1-\gamma)Y_{k}Y_{k+1}] + \sum_{k=1}^{N}b_{k}Z_{k}

        Note: For cn = 0.5, bn = 1, and r = 1 it reduces to transverse-field Ising Hamiltonian.
   
    """
    hami = QubitOperator()
    for i in range(nqubit - 1):
        hami += (cn[i] * (1 + r)) * QubitOperator(f"X{i} X{i+1}")
        hami += (cn[i] * (1 - r)) * QubitOperator(f"Y{i} Y{i+1}")

    for i in range(nqubit):
        hami += bn[i] * QubitOperator(f"Z{i}")

    return create_observable_from_openfermion_text(str(hami))
