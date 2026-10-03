import sys
from ortools.sat.python import cp_model

def main(N, timeout=100):
    model = cp_model.CpModel()

    # 1 named variable per board position [i, j], x_i_j = 1 if queen is placed
    x = [[model.NewBoolVar(f'x_{i}_{j}') for j in range(N)] for i in range(N)]
    
    for i in range(N):
        model.Add(sum(x[i][j] for j in range(N)) == 1)  # exactly one queen per row
        model.Add(sum(x[j][i] for j in range(N)) == 1)  # exactly one queen per column

    diag1, diag2 = {}, {}
    for i in range(N):
        for j in range(N):
            diag1.setdefault(i - j, []).append(x[i][j])  # group cells by diagonal (i - j = key)
            diag2.setdefault(i + j, []).append(x[i][j])  # group cells by anti-diagonal (i + j = key)

    for diag in list(diag1.values()) + list(diag2.values()):
        if len(diag) <= 1: continue # skip diagonals with only one cell, no constraint needed
        
        model.Add(sum(diag) <= 1)  # at most one queen per diagonal

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout
    status = solver.Solve(model)  # run the CP-SAT solver, respecting the time limit

    return status == cp_model.OPTIMAL, round(solver.WallTime(), 4)

if __name__ == "__main__":
    N = int(sys.argv[1])
    result, solve_time = main(N)
    print("Status:", "SOLVED" if result else "NOT SOLVED")
    print("Time to solve:", solve_time)
