import sys
import os
import re

linebatchsize = 500

'''
Changes occurrences of the format "20/12/2016 20:08:51 +00:00" or "20/12/2016 20:08:51" to
"2016-12-20 20:08:51"
'''


def transformdates(line: str):
    return re.sub(r'"(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+) (?P<time>\d+:\d+:\d+)( \+\d+:\d+)?"',
                  "\"\g<year>-\g<month>-\g<day> \g<time>\"", line)


def transformemptystrings(line: str) -> str:
    result = re.sub(r',"",', ",NULL,", line)
    result = re.sub(r',""$', ",NULL", result)
    return result


def transformbooleans(line: str) -> str:
    line = re.sub(r'"true"', "1", line, flags=re.I)
    return re.sub(r'"false"', "0", line, flags=re.I)


def transformline(line: str) -> str:
    result = line

    result = transformdates(result)
    result = transformemptystrings(result)
    result = transformbooleans(result)

    return result


def transformcsv(file: str, outputdir: str):
    print("Transforming CSV {}".format(file))

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

                if len(outputbuffer) > linebatchsize:
                    outputfile.writelines(outputbuffer)
                    outputbuffer = []

            outputfile.writelines(outputbuffer)
            print("Written to {}".format(dstfile))


def transformcsvfiles(directory: str):
    if directory[-1] == "/":
        directory = directory[0:-1]

    outputdir = directory + "/output"

    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    for filename in os.listdir(directory):
        if os.path.isfile(directory + "/" + filename) and filename.endswith(".csv"):
            transformcsv(directory + "/" + filename, outputdir)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Call program with directory as parameter:")
        print("{} directory".format(sys.argv[0]))
        exit(1)

    transformcsvfiles(sys.argv[1])
