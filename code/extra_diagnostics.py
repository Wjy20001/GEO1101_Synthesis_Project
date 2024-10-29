import os
import glob
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

def get_accuracy_and_time_from_df(df_path):
    """Extracts accuracy and average computation time from a CSV file."""
    df = pd.read_csv(df_path)
    accuracy = (df['true_room'] == df['found_room']).mean() * 100
    avg_time = df['calculation_time'].mean()
    return accuracy, avg_time

def collect_data(diagnostics_folder):
    """Collects accuracy and computation time for each file and groups by 'cs'."""
    grouped_data = defaultdict(lambda: {"N_values": [], "accuracies": [], "comp_times": []})
    all_N_values = set()

    for csv_file in glob.glob(os.path.join(diagnostics_folder, '*.csv')):
        accuracy, avg_time = get_accuracy_and_time_from_df(csv_file)
        match = re.search(r'N=(\d+)_cs=(\d+)', os.path.basename(csv_file))
        
        if match:
            N, cs = int(match.group(1)), match.group(2)
            all_N_values.add(N)
            grouped_data[cs]["N_values"].append(N)
            grouped_data[cs]["accuracies"].append(accuracy)
            grouped_data[cs]["comp_times"].append(avg_time)

    # Align each 'cs' group with the full set of N values
    all_N_values = sorted(all_N_values)
    for cs, data in grouped_data.items():
        accuracies_aligned, comp_times_aligned = [], []
        for N in all_N_values:
            if N in data["N_values"]:
                index = data["N_values"].index(N)
                accuracies_aligned.append(data["accuracies"][index])
                comp_times_aligned.append(data["comp_times"][index])
            else:
                accuracies_aligned.append(np.nan)
                comp_times_aligned.append(np.nan)
        data.update({"N_values": all_N_values, "accuracies": accuracies_aligned, "comp_times": comp_times_aligned})

    return grouped_data, all_N_values

def plot_grouped_data(grouped_data, all_N_values, diagnostics_folder, ylabel, title, metric_key, filename, accu=False):
    """Plots grouped data with different 'cs' values in a single plot."""
    fig, ax = plt.subplots()
    width = 0.15
    x = np.arange(len(all_N_values))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    for i, (cs, data) in enumerate(sorted(grouped_data.items())):
        ax.bar(x + i * width, data[metric_key], width, label=f'{cs}', color=colors[i % len(colors)])

    ax.set_xlabel('N best matches')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if accu:
        ax.set_yticks(range(50, 101, 5))
        ax.set_ylim(50, 100)
    else:
        ax.set_yticks(np.linspace(0,5,11))
        ax.set_ylim(0, 5)

    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(all_N_values, rotation=0, ha='right')
    ax.grid()
    ax.legend(title = 'cluster size', loc='lower right')

    plt.savefig(os.path.join(diagnostics_folder, filename))
    plt.show()

if __name__ == "__main__":
    diagnostics_folder = os.path.join('data', 'diagnostics')

    grouped_data, all_N_values = collect_data(diagnostics_folder)

    # Plot Accuracy
    plot_grouped_data(
        grouped_data, all_N_values, diagnostics_folder,
        ylabel="Accuracy (%)", title="Accuracy",
        metric_key="accuracies", filename="accuracy_plot.png", accu=True
    )

    # Plot Computation Time
    plot_grouped_data(
        grouped_data, all_N_values, diagnostics_folder,
        ylabel="Average Computation Time (s)", title="Computation Time",
        metric_key="comp_times", filename="comp_time_plot.png"
    )
