import numpy as np

def create_param(depth: int, gateset: int, t_init: float, t_final: float) -> np.ndarray:

    """
    create initla parameters for the circuit

    time: 0 - max time
    theta: 0 - 1

    Args:
        depth(int): number of depth
        gateset (int): number og rotation gate set. each gateset has 4 gate.1でいいよ
        t_init(float): initial time
        t_final(float): final time

    Returns:
        numpy.ndarray: an nd:array
            [t1, (for encoding)
             t2, ..., td, t(d+1), (for vqc ansatz)
             theta1, ..., theta(d*4*gateset)] (for vqc ansatz)

    """
    param = np.array([])
    #Time param
    time = np.random.uniform(t_init, t_final, depth+1)
    time = np.sort(time)
    param = np.append(param, time)
    #for i in time:
    #    param = np.append(param, i)
    #    #print(f"   t_{i}: {}")

    #Theta param
    theta = np.random.random(depth * gateset * 4) * 1e-1
    param = np.append(param, theta)

    #for i in theta:
    #    param = np.append(param, i)

    return param

    