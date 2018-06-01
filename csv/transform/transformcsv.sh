#!/bin/bash

# Bash/sed version of transformcsv.py. Added to check if this is faster. Does not seem to be the case.

if [ -z ${1+x} ]; then
   echo "Missing parameter. Provide filename of file to transform";
   exit
fi

sed -E \
-e 's/"([[:digit:]]+)\/([[:digit:]]+)\/([[:digit:]]+) ([[:digit:]]+:[[:digit:]]+:[[:digit:]]+) (\+[[:digit:]]+:[[:digit:]]+)?"/"\3\-\2-\1 \4"/g' \
-e 's/"1899-([[:digit:]]+-[[:digit:]]+ [[:digit:]]+:[[:digit:]]+:[[:digit:]]+)"/"1970-\1"/g' \
-e 's/"9476-([[:digit:]]+-[[:digit:]]+ [[:digit:]]+:[[:digit:]]+:[[:digit:]]+)"/"2018-\1"/g' \
-e 's/,"",/,NULL,/g' \
-e 's/,"",/,NULL,/g' \
-e 's/,""[[:space:]]*$/,NULL/g' \
-e 's/"true"/"1"/g' \
-e 's/"false"/"0"/g' \
$1