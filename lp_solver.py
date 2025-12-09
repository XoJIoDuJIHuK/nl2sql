import numpy as np

def solve_unconstrained_plan(product_ids, A_dict, Y_dict):
    h = len(product_ids)
    id_to_idx = {pid: idx for idx, pid in enumerate(product_ids)}
    A = np.zeros((h, h))
    Y = np.zeros(h)
    for i_pid, row in A_dict.items():
        i = id_to_idx[i_pid]
        for j_pid, a_ij in row.items():
            j = id_to_idx[j_pid]
            A[i, j] = a_ij
    for pid, y in Y_dict.items():
        if pid in id_to_idx:
            Y[id_to_idx[pid]] = y
    I = np.eye(h)
    try:
        X = np.linalg.solve(I - A, Y)
        return {product_ids[idx]: X[idx] for idx in range(h)}
    except np.linalg.LinAlgError:
        raise ValueError("Matrix (I - A) is singular; check det(A) != 1 or model axioms.")
