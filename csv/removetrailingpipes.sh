#!/bin/bash

# Removes trailing | symbols in file

mkdir output
for i in `ls *.tbl`; do sed 's/|$//' $i > output/$i; echo $i; done;
