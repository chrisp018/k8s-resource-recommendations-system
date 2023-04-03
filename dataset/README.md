gzip -dc input/FILE_NAME.gz | bin/recreate state/object_mappings.sort > output/FILE_NAME.out
gzip -dc input/wc_day5_1.gz | bin/recreate state/object_mappings.sort > output/wc_day5_1.out
gzip -dc input/wc_day6_1.gz | bin/recreate state/object_mappings.sort > output/wc_day6_1.out


for x in `ls $1`; do aws s3 cp $x s3://khanh-thesis-dataset/encode-out/$x ; done