from other_solvers.cplex_mip import main as cplex_main
from other_solvers.cpsat import main as cpsat_main
from main_pysat_encodings import main as sat_main

import multiprocessing as mp
import csv
import os

TIMEOUT = 180
OUTPUT_DIR = "experiment_results"

def child(func, N, q):
    q.put(func(N, TIMEOUT))

def run(func, N):
    q = mp.Queue()
    p = mp.Process(target=child, args=(func, N, q))
    p.start()
    p.join(TIMEOUT)

    if p.is_alive():
        p.terminate()
        p.join()
        return None                 # timeout

    return q.get()

# # SAT wrapped to match (result, solve_time) shape, tries every encoding and keeps the fastest solved one
# def sat_wrapper(N, timeout):
#     best = None

#     for encoding in ["pairwise", "sequential", "binary"]:  # commander not implemented yet
#         clauses, variables, build, solve, total, sat_result = sat_main(N, encoding, False)

#         if sat_result and (best is None or solve < best[1]):
#             best = (sat_result, solve)

#     return best if best is not None else (False, None)

METHODS = {
#    "sat": sat_wrapper,
    "cpsat": cpsat_main,
    "cplex": cplex_main,
}

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(os.path.join(OUTPUT_DIR, "method_results.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["N", "method", "solve_time", "result"])

        for N in [4, 8, 16, 32, 64, 128, 256, 512, 768, 1024]:
            for method, func in METHODS.items():
                result = run(func, N)

                if result is None:
                    print("N:", N, method, "timeout", flush=True)
                    writer.writerow([N, method, None, "timeout"])
                else:
                    sat_result, solve_time = result
                    print("N:", N, method, "solve:", solve_time, "result:", sat_result, flush=True)
                    writer.writerow([N, method, solve_time, sat_result])
