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


format_str = "%Y-%m-%d %H:%M:%S"
# start_time = parse_datetime("9minutes")
start_time = strftime("%Y-%m-%d %H:%M:%S", timestamp(time()) - 9m)
end_time = strftime("%Y-%m-%d %H:%M:%S", timestamp(time()) - mod(timestamp(time()), 60))
# end_time = parse_datetime("now")
print(end_time)
step = "1m"
rs = get_metrics(start_time, end_time, step)
print(rs)
