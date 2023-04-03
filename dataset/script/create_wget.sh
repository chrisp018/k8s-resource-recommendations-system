#!/bin/bash

# Specify the file containing the list of filenames
filename="zip.txt"

# Specify the output file
output_file="wget.txt"

# Read each line from the file and download the corresponding file
while read -r line; do
    command="wget ftp://ita.ee.lbl.gov/traces/WorldCup/$line"
    echo "$command" >> "$output_file"
done < "$filename"
