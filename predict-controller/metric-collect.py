import pandas as pd
import numpy as np
import time
import boto3
from datetime import datetime
from datetime import timedelta
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime
from prometheus_client import start_http_server, Gauge

region = 'ap-southeast-1'

# Create a new Gauge metric named "my_gauge" with a help message
predicted_prometheus = Gauge('predicted_prometheus', 'This is predicted_prometheus metric')
start_http_server(8000)

# Connect to Prometheus server
prom = PrometheusConnect(url="http://prometheus.khanh-thesis.online", disable_ssl=True)


ssm = boto3.client('ssm', region_name=region)
response_current_trigger = ssm.get_parameter(
    Name='/khanh-thesis/current_trigger_time',
    WithDecryption=True
)
current_trigger_time = response_current_trigger['Parameter']['Value']
print("current_trigger_time:", current_trigger_time)
current_datetime = datetime.strptime(current_trigger_time, '%Y-%m-%d %H:%M:%S')


def get_metrics(start_time, end_time, step):
    metric_data_request_count = prom.custom_query_range(
        query='sum(rate(istio_requests_total{source_app="app-loadtest", destination_app="app-simulate", response_code="200", connection_security_policy="unknown", job="envoy-stats"}[1m])) * 50',
        start_time=start_time,
        end_time=end_time,
        step=step,
    )
    metric_data_sum_bytes = prom.custom_query_range(
        query='sum(rate(istio_response_bytes_sum{source_app="app-loadtest", destination_app="app-simulate", response_code="200", connection_security_policy="unknown", job="envoy-stats"}[1m]) * 50)',
        start_time=start_time,
        end_time=end_time,
        step=step,
    )
    print(metric_data_request_count)
    print(metric_data_sum_bytes)
    if len(metric_data_request_count) == 0:
        return pd.DataFrame()
    if len(metric_data_request_count[0].get("values")) != 10:
        return pd.DataFrame()

    df = pd.DataFrame(metric_data_request_count[0].get("values"), columns=['timestamp', 'request_count'])
    sum_bytes = [ i[1] for i in metric_data_sum_bytes[0].get("values") ]
    df["sum_bytes"] = sum_bytes
    df['request_count'] = df['request_count'].astype(float)
    df['sum_bytes'] = df['sum_bytes'].astype(float)
    df['request_count'] = df['request_count'].astype(int)
    df['sum_bytes'] = df['sum_bytes'].astype(int)
    return df

def get_current_metric(timestamp):
    rs = prom.custom_query(query='sum(rate(istio_requests_total{source_app="request-simulate", response_code="200", connection_security_policy="unknown", job="envoy-stats"}[1m])) * 50', params={"time":unix_timestamp})
    return rs

time = datetime.now()
time = time.replace(second=0, microsecond=0)
unix_timestamp = int(time.timestamp())
rs = get_current_metric(time)
print(rs)
delta_startup_time = datetime.now() - current_datetime
print("delta_startup_time:", delta_startup_time)
print(timedelta(minutes=10))
if delta_startup_time < timedelta(minutes=10): 
    print("ssds")
else:
    print("nok")

# format_str = "%Y-%m-%d %H:%M:%S"
# # start_time = parse_datetime("9minutes")
# start_time = strftime("%Y-%m-%d %H:%M:%S", timestamp(time()) - 9m)
# end_time = strftime("%Y-%m-%d %H:%M:%S", timestamp(time()) - mod(timestamp(time()), 60))
# # end_time = parse_datetime("now")
# print(end_time)
# step = "1m"
# rs = get_metrics(start_time, end_time, step)
# print(rs)

def get_app_current_replicas():
    label = {"job" : "kube-state-metrics", "namespace": "app-simulate"}
    rs = prom.get_current_metric_value(
        metric_name='kube_deployment_status_replicas',
        label_config=label
        )
    return rs[0].get("value")[1]
print(get_app_current_replicas())