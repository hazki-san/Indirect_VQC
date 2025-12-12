import numpy as np
from qulacs import Observable
from qulacs.gate import DenseMatrix


"""
    def create_time_evo_unitary(hamiltonian: Observable, t_before: float, t_after: float):

"""
"""
    Args:
        hamiltonian: qulacs observable
        t_berfore: before time
        t_after: after time
    
    Returns:
        a density matrix gate U(t)=exp(-iHt)
"""
"""

    diag, eigen_vecs = self._hamiltonian.eigh
    time_evol_op = np.dot(
        np.dot(eigen_vecs, np.diag(np.exp(-1j * (t_after - t_before) * diag))),
        eigen_vecs.T.conj(),
    )
    return DenseMatrix([i for i in range(self.n_qubits)], time_evol_op)
"""

diag = None
eigen_vecs = None

def create_time_evo_unitary(hamiltonian: Observable, t_before: float, t_after: float):
    """
    Args:
        hamiltonian: qulacs obsevable
        t_berfore: initial time
        t_after: final time

    Returns:
        a dense matrix gate U(t) = exp(-iHt)
    """
    # Get the qubit number
    n = hamiltonian.get_qubit_count()
    # Converting to a matrix
    H_mat = hamiltonian.get_matrix().toarray()

    # Compute eigenvalues and eigenvectors only once and reuse them
    global diag, eigen_vecs

    if diag is None or eigen_vecs is None:
        # print("gloabl diag not found")
        diag, eigen_vecs = np.linalg.eigh(H_mat)

    # Compute the exponent of diagonalized Hamiltonian
    exponent_diag = np.diag(np.exp(-1j * (t_after - t_before) * diag))

    # Construct the time evolution operator
    time_evol_op = np.dot(np.dot(eigen_vecs, exponent_diag), eigen_vecs.T.conj())

    return DenseMatrix([i for i in range(n)], time_evol_op)
