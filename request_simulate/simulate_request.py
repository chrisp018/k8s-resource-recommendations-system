import os
import csv
import requests
import time
import pandas as pd
import numpy as np
from prometheus_client import start_http_server, Counter, Histogram


REQUEST_COUNT = Counter('simulate_requests_total', 'Total number of simulate requests made by the app')
RESPONSE_SIZE = Histogram('simulate_response_size_bytes', 'Size of HTTP simulate responses', buckets=[0, 100, 1000, 10000, 100000, float("inf")])


endpoint = 'http://appsimulate.appsimulate.svc.cluster.local:5000/bytes'
df = pd.read_csv('wc_dataset_processed.csv', usecols=[1, 2, 3])


# Start an HTTP server to expose the metrics on port 8000
start_http_server(8000)


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
