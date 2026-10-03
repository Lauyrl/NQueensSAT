from sat_encodings import *
from pysat.solvers import Glucose3
from time import perf_counter as now

def main(N, encodingType, print_board, meta_q=None, result_q=None):
    encodings = {
        "sequential": (exactly_one_sequential, at_most_one_sequential),
        "binary": (exactly_one_binary, at_most_one_binary),
        "commander": (exactly_one_commander, at_most_one_commander),
    }
    exactly_one, at_most_one = encodings[encodingType]

    ########## Build clauses ##################################################################################################################################
    t0 = now()

    clauses = []
 
    board = range(1, N*N+1) # 1-valued
    s_base = N*N+1          # value of utility variables must not overlap with base values

    for i in range(N):
        ########## Row clauses
        row = board[i*N : (i+1)*N]

        eo_row, s_base = exactly_one(row, N, s_base) 
        
        clauses.extend(eo_row)

        ########## Column clauses
        col = [board[i+r*N] for r in range(N)] # i-th column

        eo_col, s_base = exactly_one(col, N, s_base) 
        
        clauses.extend(eo_col)

    ########## Diagonal clauses
    # Identify the diagonals first
    diag1 = {}
    diag2 = {}
    for r in range(N):
        for c in range(N):
            key = r-c
            diag1.setdefault(key, []).append(r*N+c+1)

            key = r+c
            diag2.setdefault(key, []).append(r*N+c+1)

    for diag in (list(diag1.values()) + list(diag2.values())):
        if (len(diag) <= 1): continue

        amo_diag, s_base = at_most_one(diag, len(diag), s_base)

        clauses.extend(amo_diag)

    #####################################################################################################################################################
    if meta_q is not None:
        meta_q.put((len(clauses), s_base))

    ########## Solve ####################################################################################################################################
    t1 = now()

    solver = Glucose3()
    solver.append_formula(clauses)

    result = solver.solve()      # the parent process enforces the timeout

    t2 = now()                   # stop the clock before printing the board

    model = solver.get_model() if result else None
    solver.delete()

    if print_board:
        for r in range(N):
            row = ""
            for c in range(N):
                if (model[r*N+c] < 0):
                    row += ". "
                else: row += "Q "
            print(row)

    if result_q:
        result_q.put((len(clauses), s_base, t1-t0, t2-t1, t2-t0, result))
    return len(clauses), s_base, t1-t0, t2-t1, t2-t0, result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("N", type=int)
    parser.add_argument("encoding")
    parser.add_argument("--print-board", action="store_true")

    args = parser.parse_args()

    main(args.N, args.encoding, args.print_board)
