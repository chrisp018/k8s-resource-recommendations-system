import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime

# Connect to Prometheus server
prom = PrometheusConnect(url="http://prometheus.khanh-thesis.online", disable_ssl=True)

start_time = parse_datetime("9minutes")
end_time = parse_datetime("now")
step = "1m"
def get_metrics(start_time, end_time, step):
    metric_data_request_count = prom.custom_query_range(
        query='sum(rate(istio_requests_total{source_app="request-simulate", destination_app="appsimulate", response_code="200", connection_security_policy="unknown", job="envoy-stats"}[1m])) * 50',
        start_time=start_time,
        end_time=end_time,
        step=step,
    )
    metric_data_sum_bytes = prom.custom_query_range(
        query='sum(rate(istio_response_bytes_sum{source_app="request-simulate", destination_app="appsimulate", response_code="200", connection_security_policy="unknown", job="envoy-stats"}[1m]) * 50)',
        start_time=start_time,
        end_time=end_time,
        step=step,
    )
    print(len(metric_data_request_count[0].get("values")))
    if len(metric_data_request_count[0].get("values")) != 10:
        return False

    df = pd.DataFrame(metric_data_request_count[0].get("values"), columns=['timestamp', 'request_count'])
    sum_bytes = [ i[1] for i in metric_data_sum_bytes[0].get("values") ]
    df["sum_bytes"] = sum_bytes
    df['request_count'] = df['request_count'].astype(float)
    df['sum_bytes'] = df['sum_bytes'].astype(float)
    df['request_count'] = df['request_count'].astype(int)
    df['sum_bytes'] = df['sum_bytes'].astype(int)
    return df

rs = get_metrics(start_time, end_time, step)
print(rs)
