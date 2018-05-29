import sys
import os
import re

linebatch = 500

'''
Changes occurrences of the format "20/12/2016 20:08:51 +00:00" or "20/12/2016 20:08:51" to
"2016-12-20 20:08:51"
'''
def transformdates(line: str):
    return re.sub(r'"(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+) (?P<time>\d+:\d+:\d+)( \+\d+:\d+)?"',
                     "\"\g<year>-\g<month>-\g<day> \g<time>\"", line)


def transformemptystrings(line: str):
    return re.sub(r'""', "NULL", line)

def transformline(line: str) -> str:
    result = line

    result = transformdates(result)
    result = transformemptystrings(result)
    return result


def transformcsv(file: str, outputdir: str):
    filename = file.split("/")[-1]
    dstfile = outputdir + "/" + filename

    if os.path.exists(dstfile):
        os.remove(dstfile)

    with open(file, "r") as inputfile:
        with open(dstfile, "a") as outputfile:
            inputlines = inputfile.readlines()

            outputbuffer = []
            for inputline in inputlines:
                outputbuffer.append(transformline(inputline))

                if len(outputbuffer) > linebatch:
                    outputfile.writelines(outputbuffer)
                    outputbuffer = []

            outputfile.writelines(outputbuffer)


def transformcsvfiles(directory):
    outputdir = directory + "/output"

    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    for filename in os.listdir(directory):

        if os.path.isfile(directory + "/" + filename):
            transformcsv(directory + "/" + filename, outputdir)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Call program with directory as parameter:")
        print("%s directory".format(sys.argv[0]))
        exit(1)

    transformcsvfiles(sys.argv[1])
