import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from typing import Dict, List
import csv


# Finds all files of the form xxxxxxxx_dbname.csv in directory and plots
# the last file per database type by default
def get_files_to_plot(directory: str) -> Dict[str, str]:
    files = [f for f in os.listdir(directory) if f.endswith(".csv")]
    files.sort(reverse=True)

    files_to_plot = {}

    for f in files:
        dbname = f.split('.')[0].split('_')[1]  # Tricky business

        if dbname not in files_to_plot:
            files_to_plot[dbname] = f

    return files_to_plot


def plot_from_directory(directory: str):
    files_to_plot = get_files_to_plot(directory)

    # for dbname, file in files_to_plot.items():
    #     plot_single_file(directory + "/" + file, dbname)

    all = []
    labels = []
    for dbname, file in files_to_plot.items():
        all.append(directory + "/" + file)
        labels.append(dbname)

    plot_multiple_files(all, labels)



def get_values_for_file(filepath: str) -> Dict[str, Dict[float, float]]:
    with open(filepath) as csvfile:
        reader = csv.reader(csvfile)
        values = {}
        didheader = False

        for row in reader:
            if didheader is False:
                didheader = True
                continue

            query = row[0]
            vals = [int(i) for i in row[1:] if i != ""]

            values[query] = {
                "average": np.mean(vals),
                "stddev": np.std(vals)
            }

        return values

def plot_multiple_files(filepaths: List[str], labels: List[str]):
    width = 1.0 / len(filepaths) - 0.1

    error_config = {'ecolor': '0.3'}
    xlabels = []
    ind = []
    colors = ['r', 'b']

    for idx, f in enumerate(filepaths):
        values = get_values_for_file(f)
        avgs = [v["average"] for k, v in values.items()]
        stdds = [v["stddev"] for k, v in values.items()]

        # Get rid of weird Postgres vals for now TODO
        avgs = [a if a < 50000 else 500 for a in avgs]
        stdds = [s if s < 5000 else 500 for s in avgs]

        if len(xlabels) == 0:
            xlabels = ["q" + k for k, v in values.items()]
            ind = np.arange(len(avgs))

        plt.bar(ind + idx * width, avgs, width, yerr=stdds, alpha=0.4, color=colors[idx], error_kw=error_config, label=labels[idx])

    plt.ylabel("Time (microseconds)")
    plt.title("All db times")
    plt.ylim(ymin=0)
    plt.xticks(ind, xlabels)
    plt.legend()
    plt.show()

def plot_single_file(filepath: str, dbname: str):
    values = get_values_for_file(filepath)

    avgs = [v["average"] for k, v in values.items()]
    stdds = [v["stddev"] for k, v in values.items()]
    xlabels = ["q" + k for k, v in values.items()]

    ind = np.arange(len(avgs))
    width = 0.35

    error_config = {'ecolor': '0.3'}

    plt.bar(ind, avgs, width, yerr=stdds, alpha=0.4, color='b', error_kw=error_config)
    plt.ylabel("Time (microseconds)")
    plt.title(dbname)
    plt.ylim(ymin=0)
    plt.xticks(ind, xlabels)
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Call program with directory parameter:")
        print("{} directory".format(sys.argv[0]))
        exit(1)

    plot_from_directory(sys.argv[1])
