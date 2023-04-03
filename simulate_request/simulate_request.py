import csv
import requests
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

endpoint = 'http://khanh-thesis-lb-989822710.ap-southeast-1.elb.amazonaws.com'
df = pd.read_csv('/home/clphan/thesis/processed_dataset/wc_dataset_processed.csv', usecols=[1, 2, 3])

for index, row in df.iterrows():
    sum_bytes = row['sum_bytes']
    sum_requests = row['event_count']
    print(sum_requests)
    if sum_requests != 0:
        seconds = 60/sum_requests
        while index < sum_requests:
            index += 1
            rs = requests.get(endpoint, headers={'Accept': 'application/json'})
            print('status code:', rs.status_code)
            print(seconds)
            time.sleep(seconds)
    else:
        time.sleep(60)
