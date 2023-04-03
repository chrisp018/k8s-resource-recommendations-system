# This script reads each line of the file specified by input_file and replaces FILE_NAME with the line content.
# The resulting command is then stored in the file specified by output_file using echo and >>.
#!/bin/bash
input_file=zip.txt
output_file=unzip_command.txt

while read line; do
    filename="${line%.*}"
    echo "gzip -dc input/${filename}.gz | bin/recreate state/object_mappings.sort > output/${filename}.out" >> "${output_file}"
done < "${input_file}"
