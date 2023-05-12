import os
import csv
import requests
import time
import boto3
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from prometheus_client import start_http_server, Counter, Histogram, Gauge


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app_loadtest')


region = 'ap-southeast-1'


REQUEST_COUNT = Counter('app_loadtest_requests_total', 'Total number of app load test requests made by the app')
SUCCESSFUL_REQUEST_COUNT = Counter('app_loadtest_requests_successful_total', 'Total number of app load test requests successful made by the app')
FAILED_REQUEST_COUNT = Counter('app_loadtest_requests_failed_total', 'Total number of app load test requests failed made by the app')
RESPONSE_SIZE = Histogram('app_loadtest_response_size_bytes', 'Size of HTTP app load test responses', buckets=[0, 100, 1000, 10000, 100000, float("inf")])
RESPONSE_DURATION_EACH_REQUEST = Gauge('app_loadtest_response_duration_each_request', 'Duration of HTTP app load test response each request')
RESPONSE_DURATION_TOTAL_REQUEST = Gauge('app_loadtest_response_duration_all', 'Duration of HTTP app load test response all requests received')
start_http_server(8000)


endpoint = 'http://app-simulate.app-simulate.svc.cluster.local:5000/bytes'
ssm = boto3.client('ssm', region_name="ap-southeast-1")
time.sleep(5)
rs_app_loadtest_request = ssm.get_parameter(
    Name='/khanh-thesis/app_loadtest_request',
    WithDecryption=True
)
rs_app_loadtest_bytes = ssm.get_parameter(
    Name='/khanh-thesis/app_loadtest_bytes',
    WithDecryption=True
)
sum_requests = int(rs_app_loadtest_request['Parameter']['Value'])
sum_bytes = int(rs_app_loadtest_bytes['Parameter']['Value'])


while True:
    logger.info(f"sum_requests {sum_requests}")
    if sum_requests != 0:
        delta_time = 60/sum_requests
        bytes_send = int(sum_bytes/sum_requests)
        count=0
        start_time = datetime.now()
        for i in range(sum_requests):
            params = {'num_bytes': bytes_send}
            start_time_each_request = datetime.now()
            try:
                rs = requests.get(endpoint, params=params, headers={'Accept': 'application/octet-stream'})
                REQUEST_COUNT.inc()
                RESPONSE_SIZE.observe(len(rs.content))
                SUCCESSFUL_REQUEST_COUNT.inc()
            except Exception as e:
                logger.info(f"Request failed: {e}")
                FAILED_REQUEST_COUNT.inc()
            count += 1
            logger.info(f"Request sent: {count}")
            end_time_each_request = datetime.now()
            duration_each_request = (end_time_each_request - start_time_each_request).total_seconds()
            RESPONSE_DURATION_EACH_REQUEST.set(duration_each_request)
            logger.info(f"duration_each_request: {duration_each_request}")
            time.sleep(max(0, delta_time - duration_each_request*1.005))
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        RESPONSE_DURATION_TOTAL_REQUEST.set(duration)
        time.sleep(max(0, 60 - duration))
        logger.info(f"Request duration: {duration}")
    else:
        time.sleep(60)
