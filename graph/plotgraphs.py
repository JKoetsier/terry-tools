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


# Finds all files of the form xxxxxxxx_dbname_resulttimes.csv in directory and plots
# the last file per database type by default
def get_timings_to_plot(directory: str) -> Dict[str, str]:
    files = [f for f in os.listdir(directory) if f.endswith("resulttimes.csv")]
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
            # from ns to ms
            vals = [int(i) / (1000 * 1000) if i != "" else 0 for i in row[1:]]

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

        if len(xlabels) == 0:
            xlabels = values.keys()
            ind = np.arange(len(avgs))

        plt.bar(ind + idx * width, avgs, width, yerr=stdds, alpha=0.4, color=colors[idx], error_kw=error_config, label=labels[idx])

    plt.ylabel("Time (ms)")
    plt.title("All db times")
    plt.ylim(ymin=0)
    plt.xticks(ind, xlabels, rotation='vertical')
    plt.tick_params(axis='x', labelsize=7)
    plt.legend()

    if savefile is not None:
        plt.savefig(savefile, format="png", pad_inches=0.2, bbox_inches='tight')
    else:
        plt.show()

def plot_single_file(filepath: str, dbname: str, savefile=None):
    values = get_values_for_file(filepath)

    avgs = [v["average"] for k, v in values.items()]
    stdds = [v["stddev"] for k, v in values.items()]
    xlabels = values.keys()

    ind = np.arange(len(avgs))
    width = 0.35

    error_config = {'ecolor': '0.3'}

    plt.figure(figsize=figsize)
    plt.bar(ind, avgs, width, yerr=stdds, alpha=0.4, color='b', error_kw=error_config)
    plt.ylabel("Time (ms)")
    plt.title(dbname)
    plt.ylim(ymin=0)
    plt.xticks(ind, xlabels, rotation='vertical')
    plt.tick_params(axis='x', labelsize=7)

    if savefile is not None:
        plt.savefig(savefile, format="png", pad_inches=0.2, bbox_inches='tight')
    else:
        plt.show()



def subplot(fig, rows, cols, index):
    ax = fig.add_subplot(rows, 1, index)
    ax.grid(True, alpha=0.3, linestyle="dashed")
    ax.set_ylim(ymin=0)
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines['left'].set_smart_bounds(True)
    ax.spines['bottom'].set_smart_bounds(True)
    ax.autoscale(tight=True)

    return ax

# time,userTicks,niceTicks,sysTicks,idleTicks,ioWaitTicks,irqTicks,softIrqTicks,stealTicks,totalTicks,cpuLoad,cpuLoad0,cpuLoad1,cpuLoad2,cpuLoad3,cpuLoad4,cpuLoad5,cpuLoad6,cpuLoad7,loadAvg1,loadAvg5,loadAvg15,usedMemory,totalMemory,usedSwap,totalSwap,totalReads,totalWrites
def plot_systemstats(filepath: str, dbname: str, savefile=None):
    firstrow = pandas.read_csv(filepath, nrows=1).columns


    csv = pandas.read_csv(filepath)
    times = csv.time
    times = [t - times[0] for t in times]  # Reset to 0

    have_swap = csv["totalSwap"][0] > 0
    total_plots = 3
    current_plot = 1

    if have_swap:
        total_plots += 1


    # Plot CPU loads per core
    headers = [h for h in firstrow if h.startswith("cpuLoad") and len(h) > len("cpuLoad")]

    thisfigsize = (figsize[0], figsize[1] * 3) # Triple height

    fig = plt.figure(figsize=thisfigsize)
    fig.subplots_adjust(hspace=0.4)
    fig.suptitle(dbname)

    ax = subplot(fig, total_plots, 1, current_plot)
    ax.set_ylabel("CPU Usage (0..1)")
    ax.set_xlabel("Time (ms)")
    ax.set_title("CPU Usage")

    for h in headers:
        ax.plot(times, csv[h], linewidth=1)

    # Plot avg CPU Load
    cpu_load = [v / 100.0 for v in csv["cpuLoad"]]
    ax.plot(times, cpu_load, linewidth=3)

    ax.legend(ncol=4, fontsize=9)

    # Memory usage plot
    current_plot += 1
    ax = subplot(fig, total_plots, 1, current_plot)


    totalMemory = [v / (1024 * 1024) for v in csv["totalMemory"]]
    usedMemory = [v / (1024*1024) for v in csv["usedMemory"]]

    ax.plot(times, usedMemory, linewidth=1)
    ax.fill_between(times, 0, usedMemory, facecolor="lightblue")
    ax.fill_between(times, usedMemory, totalMemory, facecolors="white")
    ax.set_ylabel("Memory Usage (MB)")
    ax.set_xlabel("Time (ms)")
    ax.set_title("Memory Usage")

    # Swap Plot
    if have_swap:
        current_plot += 1
        ax = subplot(fig, total_plots, 1, current_plot)

        totalSwap = [v / (1024 * 1024) for v in csv["totalSwap"]]
        usedSwap = [v / (1024*1024) for v in csv["usedSwap"]]

        ax.plot(times, usedSwap, linewidth=1)
        ax.fill_between(times, 0, usedSwap, facecolor="green")
        ax.fill_between(times, usedSwap, totalSwap, facecolor="white")

        ax.set_ylabel("Swap Usage (MB)")
        ax.set_xlabel("Time (ms)")
        ax.set_title("Swap Usage")


    # IO usage plot
    current_plot += 1
    ax = subplot(fig, total_plots, 1, current_plot)

    totalReads = csv["totalReads"]
    totalWrites = csv["totalWrites"]

    # Normalise
    reads =  [0] + [totalReads[i + 1] - r for i, r in enumerate(totalReads[:-1])]
    writes = [0] + [totalWrites[i + 1] - w for i, w in enumerate(totalWrites[:-1])]

    ax.plot(times, reads, linewidth=1, label="Reads")
    ax.plot(times, writes, linewidth=1, label="Writes")

    ax.set_ylabel("Bytes")
    ax.set_xlabel("Time (ms)")
    ax.set_title("I/O Usage")
    ax.legend(fontsize=9)

    if savefile is not None:
        plt.savefig(savefile, format="png", pad_inches=0.2, bbox_inches='tight')
    else:
        plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Call program with directory parameter:")
        print("{} directory".format(sys.argv[0]))
        exit(1)

    plot_from_directory(sys.argv[1])
