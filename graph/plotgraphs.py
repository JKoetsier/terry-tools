# plotgraphs.py
#
# When a directory is provided as argument, this script plots the last runs of each database system
#
# When a file is provided, it is assumed to be a mapping file, see mappingfile_example.txt
# The output file location can be provided as a second argument when a graph is plotted from a mapping file


import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import sys
import os
from typing import Dict, List, Tuple
import csv
import pandas
import itertools

figsize=(15,5)

dbnames_to_label = {
    "mysql": "MySQL",
    "postgres": "PostgreSQL",
    "monetdb": "MonetDB",
    "mssql": "SQL Server"
}

def get_label_for_dbname(dbname: str) -> str:
    if dbname in dbnames_to_label:
        return dbnames_to_label[dbname]

    return dbname

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
def get_result_timings_to_plot(directory: str) -> Dict[str, str]:
    files = [f for f in os.listdir(directory) if f.endswith("resulttimes.csv")]
    files.sort(reverse=True)

    return get_files_to_plot(files)

def get_response_timings_to_plot(directory: str) -> Dict[str, str]:
    files = [f for f in os.listdir(directory) if f.endswith("responsetimes.csv")]
    files.sort(reverse=True)

    return get_files_to_plot(files)

def get_systemstats_to_plot(directory: str) -> Dict[str, str]:
    files = [f for f in os.listdir(directory) if f.endswith("systemstats.csv")]
    files.sort(reverse=True)

    return get_files_to_plot(files)

def plot_timings(directory, files: List[str]):
    for dbname, file in files.items():
        outputfile = directory + "/" + file + ".png"

        plot_single_file(directory + "/" + file, label=get_label_for_dbname(dbname), savefile=outputfile)

def plot_from_directory(directory: str):
    result_timings_to_plot = get_result_timings_to_plot(directory)

    for dbname, file in result_timings_to_plot.items():
        outputfile = directory + "/" + file + ".png"

        plot_single_file(directory + "/" + file, label=get_label_for_dbname(dbname), savefile=outputfile)

    ## Plot all in one graph
    all = []
    labels = []

    for dbname, file in result_timings_to_plot.items():
        all.append(directory + "/" + file)
        labels.append(get_label_for_dbname(dbname))

    outputfile = directory + "/all.png"
    plot_multiple_files(all, labels, outputfile)

    response_timings_to_plot = get_response_timings_to_plot(directory)

    for dbname, file in response_timings_to_plot.items():
        outputfile = directory + "/" + file + ".png"

        plot_single_file(directory + "/" + file, label=get_label_for_dbname(dbname), savefile=outputfile)

    ## Plot all in one graph
    all = []
    labels = []

    for dbname, file in response_timings_to_plot.items():
        all.append(directory + "/" + file)
        labels.append(dbname)

    outputfile = directory + "/all.png"
    plot_multiple_files(all, labels, outputfile)

    ## Plot all dbs against each other
    combinations = list(itertools.combinations(response_timings_to_plot, r=2))

    for combination in combinations:
        outputfile = directory + "/" + combination[0] + "_" + combination[1] + ".png"

        files = []
        files.append(directory + "/" + response_timings_to_plot[combination[0]])
        files.append(directory + "/" + response_timings_to_plot[combination[1]])

        labels = []
        labels.append(get_label_for_dbname(combination[0]))
        labels.append(get_label_for_dbname(combination[1]))

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

            mean = np.mean(vals)

            if mean > 0:
                values[query] = {
                    "average": mean,
                    "stderr": stats.sem(vals)
                }

        return values

def plot_multiple_files(filepaths: List[str], labels: List[str] = None, savefile=None):
    width = 1.0 / len(filepaths) - 0.1

    error_config = {'ecolor': '0.3'}
    xlabels = []
    ind = []
    colors = ['r', 'b', 'g']
    fig = plt.figure(figsize=figsize)


    filevalues = []

    for filepath in filepaths:
        values = get_values_for_file(filepath)
        filevalues.append(values)


    allvalues = [v for filevals in filevalues for k, v in filevals.items()]

    allavgs = [v["average"] for v in allvalues]
    maxbarlength = max([v["average"] + v["stderr"] for v in allvalues])
    break_point = find_break_point(allavgs)

    ax = fig.subplots(1, 1)

    maxbottombarlength = None

    if break_point is not None:
        maxbottombarlength = max([ v["average"] + v["stderr"] for v in allvalues if v["average"] < break_point])

        ax.set_ylim(0, maxbottombarlength * 1.05)
        ax.spines['top'].set_visible(False)
    else:
        ax = fig.subplots(1, 1)
        ax.set_ylim(ymin=0, ymax=maxbarlength * 1.05)

    for idx, values in enumerate(filevalues):
        avgs = [v["average"] for k, v in values.items()]
        stdds = [v["stderr"] for k, v in values.items()]

        if len(xlabels) == 0:
            xlabels = values.keys()
            ind = np.arange(len(avgs))

        if labels is not None:
            ax.bar(ind + idx * width, avgs, width, yerr=stdds, alpha=0.4, color=colors[idx], error_kw=error_config, label=labels[idx])

        else:
            ax.bar(ind + idx * width, avgs, width, yerr=stdds, alpha=0.4, color=colors[idx], error_kw=error_config)

        if break_point is not None:
            for idx2, xy in enumerate(zip(ind, avgs)):
                if xy[1] > break_point:
                    # yxtext modulo calculation places annotations at different offsets so they don't everlap
                    ax.annotate('%s' % int(xy[1]),
                                      xy=(xy[0], maxbottombarlength),
                                      textcoords='offset points',
                                      fontsize=6,
                                      color=colors[idx],
                                      xytext=(0, 20 + (idx % len(filevalues)) * 20 + (idx2 % 2) * 10)
                    )


    ax.xaxis.tick_bottom()
    ax.set_xticks(ind)
    ax.set_xticklabels(xlabels, rotation='vertical')
    ax.set_ylabel("Time (ms)")
    ax.tick_params(axis='x', labelsize=7)
    ax.grid(True, alpha=0.3, linestyle="dashed")

    if labels is not None:
        ax.legend()

    if savefile is not None:
        plt.savefig(savefile, format="png", pad_inches=0.2, bbox_inches='tight')
    else:
        plt.show()

def find_break_point(values: List[float]):
    factor = 3

    outliers = find_outliers(values, factor)

    if len(outliers) == 0:
        return None

    revlist = list(reversed(sorted(values)))

    idx = revlist.index(min(outliers))

    return (revlist[idx + 1] + revlist[idx]) / 2

def find_outliers(values: List[float], factor=1.5):
    vals = list(values)
    outliers = []

    avg = np.mean(vals)
    max = avg * factor

    this_outliers = []

    for val in vals:
        if val > max:
            this_outliers.append(val)

    for outlier in this_outliers:
        vals.remove(outlier)
        outliers.append(outlier)

    return outliers



def draw_break_marks(axtop, axbottom):
    d = .01  # how big to make the diagonal lines in axes coordinates
    kwargs = dict(transform=axtop.transAxes, color='k', clip_on=False)
    axtop.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    axtop.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs.update(transform=axbottom.transAxes)  # switch to the bottom axes
    axbottom.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    axbottom.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal


def plot_single_file(filepath: str, label=None, savefile=None):
    labels = [label] if label is not None else None

    plot_multiple_files([filepath], labels=labels, savefile=savefile)

def subplot(fig, rows, cols, index):
    ax = fig.add_subplot(rows, cols, index)
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
    # fig.suptitle(dbname)

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

def plot_from_mapping_file(mapping_file: str, output_file=None):
    files = []
    labels = []

    with open(mapping_file) as f:
        for line in f:
            splittedLine = line.split()

            if len(splittedLine) < 2:
                print("Missing label in mapping file")
                exit(1)

            if not os.path.isfile(splittedLine[0]):
                print("Invalid file in mapping file {}".format(splittedLine[0]))
                exit(1)

            files.append(splittedLine[0])
            labels.append(str.join(" ", splittedLine[1:]))

    plot_multiple_files(files, labels, output_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Call program with directory parameter or mapping file:")
        print("{} directory|mapping file".format(sys.argv[0]))
        exit(1)

    if os.path.isdir(sys.argv[1]):
        plot_from_directory(sys.argv[1])
    elif os.path.isfile(sys.argv[1]):

        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            output_file = None

        plot_from_mapping_file(sys.argv[1], output_file)
    else:
        print("Path does not exist")
        exit(1)
