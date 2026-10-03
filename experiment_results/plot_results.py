import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

OUTPUT_DIR = "experiment_results"
PLOT_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "plots")
N_VALUES = [4, 8, 16, 32, 64, 128, 256, 512, 768, 1024]  # define explicitly, used for x-ticks

df = pd.read_csv(os.path.join(OUTPUT_DIR, "results_rounded.csv"))

df["clauses"] = pd.to_numeric(df["clauses"], errors="coerce")
df["variables"] = pd.to_numeric(df["variables"], errors="coerce")
df["solve_time"] = pd.to_numeric(df["solve_time"], errors="coerce")

def plot_metric(metric, ylabel, title, filename):
    plt.figure(figsize=(10, 5))

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    for color_idx, (encoding, group) in enumerate(df.groupby("encoding")):
        color = colors[color_idx % len(colors)]

        group = group.sort_values("N")
        valid = group.dropna(subset=[metric])

        for i in range(len(valid) - 1):
            n1 = valid.iloc[i]["N"]
            n2 = valid.iloc[i + 1]["N"]

            index1 = N_VALUES.index(n1)
            index2 = N_VALUES.index(n2)

            linestyle = "--" if index2 - index1 > 1 else "-"

            plt.plot(
                [n1, n2],
                [valid.iloc[i][metric], valid.iloc[i + 1][metric]],
                marker="o",
                linestyle=linestyle,
                color=color,
                label=encoding if i == 0 else None
            )

        if len(valid) == 1:
            n = valid.iloc[0]["N"]
            plt.plot(
                n,
                valid.iloc[0][metric],
                marker="o",
                color=color,
                label=encoding
            )

        if not valid.empty and valid["N"].max() < group["N"].max():
            last_n = valid["N"].max()
            last_val = valid.loc[valid["N"] == last_n, metric].values[0]

            plt.plot(
                last_n,
                last_val,
                marker="x",
                markersize=12,
                color=color,
                zorder=5
            )

    plt.xlabel("N")
    plt.ylabel(ylabel)
    plt.title(title)

    x_labels = ["4", "", "16", "", "64", "128", "256", "512", "768", "1024"]
    plt.xticks(N_VALUES, labels=x_labels, rotation=45)

    plt.xlim(0, 1050)

    formatter = ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0, 0))
    plt.gca().yaxis.set_major_formatter(formatter)

    plt.legend()
    plt.grid(True, which="both", axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_OUTPUT_DIR, filename), dpi=300)


plot_metric("clauses", "Number of Clauses", "Number of Clauses vs N", "clauses_vs_N.png")
plot_metric("variables", "Number of Variables", "Number of Variables vs N", "variables_vs_N.png")
plot_metric("solve_time", "Solve Time (s)", "Solve Time vs N", "solve_time_vs_N.png")
