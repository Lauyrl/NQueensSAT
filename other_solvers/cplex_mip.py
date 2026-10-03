import sys, time
from docplex.mp.model import Model

def main(N, timeout=100):
    model = Model()
    model.set_time_limit(timeout)

    # creates N x N binary variables, each with 2 keys, corresponding to their rows and columns, x[i, j]=1 if queen is placed
    x = model.binary_var_matrix(N, N, name='x')

    for i in range(N):
        model.add_constraint(model.sum(x[i, j] for j in range(N)) == 1)  # exactly one queen per row
        model.add_constraint(model.sum(x[j, i] for j in range(N)) == 1)  # exactly one queen per column

    diag1, diag2 = {}, {}
    for i in range(N):
        for j in range(N):
            diag1.setdefault(i - j, []).append(x[i, j])  # group cells by diagonal (i - j = key)
            diag2.setdefault(i + j, []).append(x[i, j])  # group cells by anti-diagonal (i + j = key)

    for diag in list(diag1.values()) + list(diag2.values()):
        if len(diag) <= 1: continue # skip diagonals with only one cell, no constraint needed

        model.add_constraint(model.sum(diag) <= 1)  # at most one queen per diagonal

    t0 = time.perf_counter()
    sol = model.solve()
    t1 = time.perf_counter()

    return bool(sol), round(t1 - t0, 4)

if __name__ == "__main__":
    N = int(sys.argv[1])
    result, solve_time = main(N)
    print("Status:", "SOLVED" if result else "NOT SOLVED")
    print("Time to solve:", solve_time)
