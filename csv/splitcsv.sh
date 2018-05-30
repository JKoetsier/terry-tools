#!/bin/bash

# Splits a file in parts defined by the number of lines provided as the second
# parameter.
# Works ONLY for filenames without dots (.) in the filename, other than the
# one separating the extension
# Assumes CSV has header

if [ -z ${2+x} ]; then
   echo "Missing parameters. Provide filename and number of lines to split to";
   exit
fi

FILENAME=$1
LINES_EACH=$2

split -l $LINES_EACH $FILENAME

NAME=`echo "$FILENAME" | cut -d'.' -f1`
EXT=`echo "$FILENAME" | cut -d'.' -f2`

HEADER=$(head -1 $FILENAME)

for file in x*; do
    if [ "$(head -1 $file)" != "$HEADER" ]; then
	cat <(echo $HEADER) $file > $file
    fi
    mv $file "$NAME.$file.$EXT"
done

mv $FILENAME "$FILENAME.full"
