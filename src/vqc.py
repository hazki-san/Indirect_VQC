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

class IndirectVQC:

    def __init__(
        self,
        nqubits: int,
        feature_map: Dict,
        ansatz: Dict,
        loss_fn: str,
        optimization: Dict,
        init_param: Union[List[float], str],
    ) -> None:

        self.nqubits = nqubits
        self.state = state

        # Optimization variables
        self.optimization_status: bool = optimization["status"]

    