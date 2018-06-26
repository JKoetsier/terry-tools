#!/usr/local/bin/bash

# Bash4 script
#
# Imports directory with CSV dumps into MongoDB
#
# Expects two parameters
# First is directory that contains CSV's
# Second parameter is database to import to

if [ -z ${2+x} ]; then
   echo "Missing parameters. Provide directory and database";
   exit
fi

DBNAME=$2
DIRECTORY=$1

if [ "${1: -1}" == "/" ]; then
    DIRECTORY=${1::-1}
fi

for file in $DIRECTORY/*.csv; do
    echo $file
    FILENAME=$(echo "$file" | sed "s/.*\///")
    COLLECTION=${FILENAME::-4}
    COLLECTION=${COLLECTION,,}
    mongoimport -d $DBNAME -c $COLLECTION --type CSV --file $file --headerline
done
