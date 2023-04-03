import boto3
import botocore
import pandas as pd
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

BUCKET_NAME = 'khanh-thesis-dataset' # replace with your bucket name

# enter authentication credentials
s3 = boto3.resource('s3', aws_access_key_id = 'AKIA4DUJ26DIPAUODTVZ', 
    aws_secret_access_key= 'Y0bbJWcYLZsGC/2zBGgTDkh+Hsux7lZKzKjuXezL')

files_name = [
    'wc_day5_20.csv',
    'wc_day21_30.csv',
    'wc_day31_40.csv',
    'wc_day41_46.csv',
    'wc_day47_50.csv',
    'wc_day51_52.csv',
    'wc_day53_55.csv',
    'wc_day56_58.csv',
    'wc_day59_60.csv',
    'wc_day61_61.csv',
    'wc_day62_62.csv',
    'wc_day63_63.csv',
    'wc_day64_64.csv',
    'wc_day65_65.csv',
    'wc_day66_66.csv',
    'wc_day67_70.csv',
    'wc_day71_74.csv',
    'wc_day75_80.csv',
    'wc_day81.csv',
    'wc_day82.csv',
    'wc_day83_92.csv'
]
def download_files():
    # input file path
    input_files = [f'{file}' for file in files_name]

    # KEY = 'sample/wc_day5_1.out' # replace with your object key
    # KEY = 'encode-out/wc_day5_1.out' # replace with your object key

    try:
        for input_file in input_files:
            KEY = f'processed_data/{input_file}'
            s3.Bucket(BUCKET_NAME).download_file(KEY, input_file)
    
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
    else:
        raise

def plot_data(data):
    # Plot the time series data
    plt.plot(df['event_time'], df['event_count'])
    # # Add x and y labels
    plt.xlabel('Time')
    plt.ylabel('Event Count')
    plt.xticks(rotation=90)


# Create an empty list to hold the data
data_list = []

# Loop through each file and read the data into a DataFrame
for file in files_name:
    df = pd.read_csv(file)
    data_list.append(df)
# Concatenate all the DataFrames in the list into a single DataFrame
combined_df = pd.concat(data_list, ignore_index=True)

plot_data(combined_df)