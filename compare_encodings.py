import multiprocessing as mp
from main_pysat_encodings import main
from main import main as main_self_defined_encodings
import csv
import os

BUILD_SAFETY_MARGIN = 100
SOLVE_TIMEOUT = 180
OUTPUT_DIR = "experiment_results"

def child(N, enc, meta_q, result_q):
    if enc == "commander":
        main_self_defined_encodings(N, enc, False, meta_q, result_q)
    else:
        main(N, enc, False, meta_q, result_q)

def run(N, enc):
    # queues for the OS process, and the child process to exchange information
    meta_q = mp.Queue()
    result_q = mp.Queue()

    p = mp.Process(target=child, args=(N, enc, meta_q, result_q))
    p.start()

    clauses, variables = None, None
    try:
        # wait for the clauses to build, within build-timeout and report metadata
        clauses, variables = meta_q.get(timeout=BUILD_SAFETY_MARGIN)
    except:
        # build itself hung or crashed
        pass

    if clauses is None:
        # build timed out, kill it
        p.terminate()   # tell process to terminate
        p.join()        # wait for the process to finish what its doing (terminating)
        return None, None, None

    # separate timer for solving, join(T) tells process to wait T seconds
    p.join(SOLVE_TIMEOUT)

    # at time limit, if p is still running, kill it
    if p.is_alive():
        p.terminate()  # tell process to terminate
        p.join()       # wait for the process to finish what its doing (terminating)
        return clauses, variables, None   # solve timed out, metadata still preserved

    result = result_q.get()
    return clauses, variables, result

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(os.path.join(OUTPUT_DIR, "results.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "N", "encoding", "clauses", "variables",
            "build_time", "solve_time", "total_time", "result"
        ])

        for N in [4, 8, 16, 32, 64, 128, 256, 512, 768, 1024]:
            for encoding in ["commander"]: # "pairwise", "sequential", "binary",
                clauses, variables, result = run(N, encoding)

                if result is None:
                    print("N:", N, encoding, "timeout", flush=True)
                    writer.writerow([
                        N, encoding, clauses, variables,
                        None, None, None, "timeout"
                    ])
                else:
                    _, _, build, solve, total, sat_result = result

                    print(
                        "N:", N,
                        encoding,
                        "clauses:", clauses,
                        "variables:", variables,
                        "build:", build,
                        "solve:", solve,
                        "total:", total,
                        "result:", sat_result,
                        flush=True
                    )

                    writer.writerow([
                        N, encoding, clauses, variables,
                        build, solve, total, sat_result
                    ])
