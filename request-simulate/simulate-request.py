import os
import csv
import requests
import time
import boto3
import pandas as pd
import numpy as np
from datetime import datetime
from prometheus_client import start_http_server, Counter, Histogram

region = 'ap-southeast-1'


REQUEST_COUNT = Counter('simulate_requests_total', 'Total number of simulate requests made by the app')
RESPONSE_SIZE = Histogram('simulate_response_size_bytes', 'Size of HTTP simulate responses', buckets=[0, 100, 1000, 10000, 100000, float("inf")])
start_http_server(8000)


ssm = boto3.client('ssm', region_name=region)
response = ssm.get_parameter(
    Name='/khanh-thesis/past_trigger_time',
    WithDecryption=True
)
past_trigger_time = response['Parameter']['Value'] #"1998-04-30 21:30:00"
now = datetime.now()
now_str = now.strftime('%Y-%m-%d %H:%M:00')
# Put the parameter value "2023-04-20 14:24:00"
response = ssm.put_parameter(
    Name='/khanh-thesis/current_trigger_time',
    Value=now_str,
    Type='String',
    Overwrite=True
)
print("Uploaded current time to SSM: /khanh-thesis/current_trigger_time")


endpoint = 'http://app-simulate.app-simulate.svc.cluster.local:5000/bytes'
df = pd.read_csv('wc_dataset_processed.csv')
df['event_time'] = pd.to_datetime(df['event_time'])
df.set_index('event_time', inplace=True)
trigger_time = pd.to_datetime(past_trigger_time)
df = df.loc[trigger_time:]
df.reset_index(inplace=True)
print(df.head())
df = df.loc[:, ['event_count', 'sum_bytes', 'num_match_event']]


time.sleep(30)
while True:
    for index, row in df.iterrows():
        sum_bytes = row['sum_bytes']
        sum_requests = row['event_count']
        print(sum_requests)
        if sum_requests != 0:
            seconds = 60/sum_requests
            bytes_send = int(sum_bytes/sum_requests)
            count=0
            while count < sum_requests:
                count += 1
                params = {'num_bytes': bytes_send}
                rs = requests.get(endpoint, params=params, headers={'Accept': 'application/octet-stream'})
                REQUEST_COUNT.inc()
                RESPONSE_SIZE.observe(len(rs.content))
                time.sleep(seconds)
            print(f"Request sent: {count}")
        else:
            time.sleep(60)
