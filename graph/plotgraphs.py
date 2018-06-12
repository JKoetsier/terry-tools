import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from typing import Dict, List
import csv
import pandas
import itertools

figsize=(15,5)


## Expects a list with files ordered in priority, of the form yyyymmdd_dbname_type.csv
## Returns one file per db
def get_files_to_plot(files: List[str]) -> Dict[str, str]:
    files_to_plot = {}

    for f in files:
        dbname = f.split('.')[0].split('_')[1]  # Tricky business

        if dbname not in files_to_plot:
            files_to_plot[dbname] = f

    return files_to_plot


# Finds all files of the form xxxxxxxx_dbname_timings.csv in directory and plots
# the last file per database type by default
def get_timings_to_plot(directory: str) -> Dict[str, str]:
    files = [f for f in os.listdir(directory) if f.endswith("timings.csv")]
    files.sort(reverse=True)

    return get_files_to_plot(files)


def get_systemstats_to_plot(directory: str) -> Dict[str, str]:
    files = [f for f in os.listdir(directory) if f.endswith("systemstats.csv")]
    files.sort(reverse=True)

    return get_files_to_plot(files)


def plot_from_directory(directory: str):
    timings_to_plot = get_timings_to_plot(directory)

    for dbname, file in timings_to_plot.items():
        outputfile = directory + "/" + file + ".png"

        plot_single_file(directory + "/" + file, dbname, outputfile)


    ## Plot all in one graph
    all = []
    labels = []

    for dbname, file in timings_to_plot.items():
        all.append(directory + "/" + file)
        labels.append(dbname)

    outputfile = directory + "/all.png"
    plot_multiple_files(all, labels, outputfile)

    ## Plot all dbs against each other
    combinations = list(itertools.combinations(timings_to_plot, r=2))

    for combination in combinations:
        outputfile = directory + "/" + combination[0] + "_" + combination[1] + ".png"

        files = []
        files.append(directory + "/" + timings_to_plot[combination[0]])
        files.append(directory + "/" + timings_to_plot[combination[1]])

        labels = []
        labels.append(combination[0])
        labels.append(combination[1])

        plot_multiple_files(files, labels, outputfile)

    ## Plot systemstats
    systemstats_to_plot = get_systemstats_to_plot(directory)

    for dbname, file in systemstats_to_plot.items():
        outputfile = directory + "/" + file + ".png"
        plot_systemstats(directory + "/" + file, dbname, outputfile)


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
            vals = [int(i) if i != "" else 0 for i in row[1:]]

            values[query] = {
                "average": np.mean(vals),
                "stddev": np.std(vals)
            }

        return values

def plot_multiple_files(filepaths: List[str], labels: List[str], savefile=None):
    width = 1.0 / len(filepaths) - 0.1

    error_config = {'ecolor': '0.3'}
    xlabels = []
    ind = []
    colors = ['r', 'b', 'g']
    plt.figure(figsize=figsize)

    for idx, f in enumerate(filepaths):
        values = get_values_for_file(f)
        avgs = [v["average"] for k, v in values.items()]
        stdds = [v["stddev"] for k, v in values.items()]

        # Get rid of weird Postgres vals for now TODO
        avgs = [a if a < 30000 else 0 for a in avgs]
        stdds = [s if s < 30000 else 0 for s in avgs]

        if len(xlabels) == 0:
            xlabels = ["q" + k for k, v in values.items()]
            ind = np.arange(len(avgs))

        plt.bar(ind + idx * width, avgs, width, yerr=stdds, alpha=0.4, color=colors[idx], error_kw=error_config, label=labels[idx])

    plt.ylabel("Time (microseconds)")
    plt.title("All db times")
    plt.ylim(ymin=0)
    plt.xticks(ind, xlabels)
    plt.legend()

    if savefile is not None:
        plt.savefig(savefile, format="png")
    else:
        plt.show()

def plot_single_file(filepath: str, dbname: str, savefile=None):
    values = get_values_for_file(filepath)

    avgs = [v["average"] for k, v in values.items()]
    stdds = [v["stddev"] for k, v in values.items()]
    xlabels = ["q" + k for k, v in values.items()]

    ind = np.arange(len(avgs))
    width = 0.35

    error_config = {'ecolor': '0.3'}

    plt.figure(figsize=figsize)
    plt.bar(ind, avgs, width, yerr=stdds, alpha=0.4, color='b', error_kw=error_config)
    plt.ylabel("Time (microseconds)")
    plt.title(dbname)
    plt.ylim(ymin=0)
    plt.xticks(ind, xlabels)

    if savefile is not None:
        plt.savefig(savefile, format="png")
    else:
        plt.show()

# time,userTicks,niceTicks,sysTicks,idleTicks,ioWaitTicks,irqTicks,softIrqTicks,stealTicks,totalTicks,cpuLoad,cpuLoad0,cpuLoad1,cpuLoad2,cpuLoad3,cpuLoad4,cpuLoad5,cpuLoad6,cpuLoad7,loadAvg1,loadAvg5,loadAvg15,usedMemory,totalMemory,usedSwap,totalSwap,totalReads,totalWrites
def plot_systemstats(filepath: str, dbname: str, savefile=None):
    firstrow = pandas.read_csv(filepath, nrows=1).columns
    headers = [h for h in firstrow if h.startswith("cpuLoad") and len(h) > len("cpuLoad")]

    csv = pandas.read_csv(filepath)
    times = csv.time
    times = [t - times[0] for t in times]  # Reset to 0

    plt.figure(figsize=figsize)
    plt.ylabel("CPU Usage 0-1")
    plt.title(dbname)
    plt.ylim(ymin=0)

    for h in headers:
        plt.plot(times, csv[h])

    if savefile is not None:
        plt.savefig(savefile, format="png")
    else:
        plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Call program with directory parameter:")
        print("{} directory".format(sys.argv[0]))
        exit(1)

    plot_from_directory(sys.argv[1])
