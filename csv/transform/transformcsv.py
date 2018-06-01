import sys
import os
import re
import threading
import time
import itertools

outputbuffersize_lines = 1000
inputchunck = 1000
maxthreads = 8
globaltotallines = 0
globalrunningtime = 0.0
lock = threading.Condition()

'''
Changes occurrences of the format "20/12/2016 20:08:51 +00:00" or "20/12/2016 20:08:51" to
"2016-12-20 20:08:51"
'''


def transformdates(line: str):
    return re.sub(r'"(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+) (?P<time>\d+:\d+:\d+)( \+\d+:\d+)?"',
                  "\"\g<year>-\g<month>-\g<day> \g<time>\"", line)

def transformbogusdates(line: str):
    return re.sub(r'"1899-(?P<rest>\d+-\d+ \d+:\d+:\d+)"', '"1970-\g<rest>"', line)


def transformemptystrings(line: str) -> str:
    return re.sub(r',(""(?=,)|""$)', ",NULL", line)


def transformbooleans(line: str) -> str:
    line = re.sub(r'"true"', "1", line, flags=re.I)
    return re.sub(r'"false"', "0", line, flags=re.I)

def transformline(line: str) -> str:
    result = line

    result = transformdates(result)
    result = transformbogusdates(result)
    result = transformemptystrings(result)
    result = transformbooleans(result)

    return result


def transformcsv(file: str, outputdir: str) -> int:
    global globaltotallines
    global globalrunningtime

    start = time.time()
    filename = file.split("/")[-1]
    dstfile = outputdir + "/" + filename

    if os.path.exists(dstfile):
        os.remove(dstfile)

    totallines = 0

    ## Per line
    with open(file, "r") as inputfile:
        with open(dstfile, "a") as outputfile:
            outputbuffer = []
            for inputline in inputfile:
                outputbuffer.append(transformline(inputline))

                if len(outputbuffer) > outputbuffersize_lines:
                    outputfile.writelines(outputbuffer)
                    totallines += len(outputbuffer)
                    outputbuffer = []

            outputfile.writelines(outputbuffer)
            totallines += len(outputbuffer)

    ## Test with islice. Not faster
    ##
    ## Islice, Chunks n = 1000
    ## We're done. Took 2864.780461 seconds in total for 32454885 lines. Avg 11328.925703 lines/sec.
    ## Total thread running time: 7140.146623134613 sec. Avg: 4545.408759 lines/sec
    ##
    ## With reading per line:
    ## We're done. Took 1595.845968 seconds in total for 32454885 lines. Avg 20337.103740 lines/sec.
    ## Total thread running time: 4849.047528266907 sec. Avg: 6693.043285 lines/sec


    # with open(file, "r") as inputfile:
    #     with open(dstfile, "a") as outputfile:
    #         outputbuffer = []
    #
    #         while True:
    #             inputlines = list(itertools.islice(inputfile, inputchunck))
    #             totallines += len(inputlines)
    #
    #             if not inputlines:
    #                 break
    #
    #
    #             for inputline in inputlines:
    #                 outputbuffer.append(transformline(inputline))
    #
    #                 if len(outputbuffer) > outputbuffersize_lines:
    #                     outputfile.writelines(outputbuffer)
    #                     outputbuffer = []
    #
    #         outputfile.writelines(outputbuffer)

    end = time.time()

    passed = end - start
    print("Done %s (%d lines) in %f seconds. %f lines/sec" % (file, totallines, passed, (float(totallines) / passed)))

    lock.acquire()
    globaltotallines += totallines
    globalrunningtime += passed
    lock.release()

    return totallines


def transformcsvfiles(directory: str):
    global globaltotallines
    global globalrunningtime

    start = time.time()
    if directory[-1] == "/":
        directory = directory[0:-1]

    outputdir = directory + "/output2"

    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    files = [ f for f in os.listdir(directory) if os.path.isfile(directory + "/" + f) and f.endswith(".csv") ]

    files_w_length = []

    for f in files:
        fpath = directory + "/" + f
        st_size = os.stat(fpath).st_size

        files_w_length.append({
            "filepath": fpath,
            "size": st_size
        })

    sorted_files = sorted(files_w_length, key=lambda k: k['size'])


    while True:

        while threading.active_count() < maxthreads and len(sorted_files) > 0:
            t = threading.Thread(target=transformcsv, args=[sorted_files.pop()['filepath'], outputdir])
            t.start()

        if threading.active_count() == 1 and len(sorted_files) == 0:
            break

    end = time.time()
    passed = end - start

    print("We're done. Took %f seconds in total for %d lines. Avg %f lines/sec. Total thread running time: "
          "%s sec. Avg: %f lines/sec" %
          (passed, globaltotallines, float(globaltotallines) / passed, globalrunningtime,
           float(globaltotallines) / globalrunningtime))




if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Call program with directory as parameter:")
        print("{} directory".format(sys.argv[0]))
        exit(1)

    transformcsvfiles(sys.argv[1])
