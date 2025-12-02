import numpy as np
from qulacs import Observable
from qulacs.gate import DenseMatrix

"""
処理があんま分かってないので阿南さんのとarijitさんのを読み込むように
以下コードは阿南さんの形
"""
def create_time_evo_unitary(hamiltonian: Observable, t_before: float, t_after: float):

    """
    Args:
        hamiltonian: qulacs observable
        t_berfore: before time
        t_after: after time
    
    Returns:
        a density matrix gate U(t)=exp(-iHt)

    """

    diag, eigen_vecs = self._hamiltonian.eigh
    time_evol_op = np.dot(
        np.dot(eigen_vecs, np.diag(np.exp(-1j * (t_after - t_before) * diag))),
        eigen_vecs.T.conj(),
    )
    return DenseMatrix([i for i in range(self.n_qubits)], time_evol_op)
    