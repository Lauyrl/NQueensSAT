from pysat.solvers import Glucose3
from pysat.card import CardEnc, EncType
from time import perf_counter as now

def main(N, encodingType, print_board, meta_q=None, result_q=None):
    encodings = {
        "pairwise": EncType.pairwise,
        "sequential": EncType.seqcounter,
        "binary": EncType.bitwise,
        "commander": None,
    }
    encoding = encodings[encodingType]

    ########## Build clauses ##################################################################################################################################
    t0 = now()

    clauses = []
 
    board = range(1, N*N+1) # 1-valued
    s_base = N*N            # top id, utility variables are allocated with non-overlapping ids after this

    for i in range(N):
        ########## Row clauses
        row = board[i*N : (i+1)*N]

        eo_row = CardEnc.equals(row, top_id=s_base, encoding=encoding) 
        eo_clauses = eo_row.clauses
        s_base = eo_row.nv 
        
        clauses.extend(eo_clauses)

        ########## Column clauses
        col = [board[i+r*N] for r in range(N)] # i-th column
 
        eo_col = CardEnc.equals(col, top_id=s_base, encoding=encoding) 
        eo_clauses = eo_col.clauses
        s_base = eo_col.nv 
        
        clauses.extend(eo_clauses)

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

        amo_diag = CardEnc.atmost(diag, top_id=s_base, encoding=encoding)
        amo_clauses = amo_diag.clauses
        s_base = amo_diag.nv 

        clauses.extend(amo_clauses)

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

    if print_board and model:
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
