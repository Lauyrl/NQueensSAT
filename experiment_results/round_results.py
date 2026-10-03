# round_results.py — reads raw results CSVs, writes rounded versions independently
import csv
import os

OUTPUT_DIR = "experiment_results"
DECIMALS = 4

# maps each input file to the time columns it contains
FILES = {
    "results.csv": ["build_time", "solve_time", "total_time"],
    "method_results.csv": ["solve_time"],
}

def round_file(in_name, time_columns):
    in_path = os.path.join(OUTPUT_DIR, in_name)
    out_path = os.path.join(OUTPUT_DIR, in_name.replace(".csv", "_rounded.csv"))

    with open(in_path, newline="") as infile, open(out_path, "w", newline="") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            for col in time_columns:
                if row[col]:
                    try:
                        row[col] = f"{float(row[col]):.{DECIMALS}f}"
                    except ValueError:
                        pass
            writer.writerow(row)

if __name__ == "__main__":
    for filename, time_columns in FILES.items():
        in_path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(in_path):
            round_file(filename, time_columns)
            print(f"Rounded {filename}")
        else:
            print(f"Skipped {filename} (not found)")
