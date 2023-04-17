import requests
from datetime import datetime
from datetime import timedelta

from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime

# Connect to Prometheus server
prom = PrometheusConnect(url="http://52.74.71.209:9090", disable_ssl=True)

start_time = parse_datetime("12minutes")
end_time = parse_datetime("now")
chunk_size = timedelta(minutes=1)

def get_metrics(start_time, end_time, chunk_size):
    metrics_data = [[] for i in range(10)]
    metric_data_request_count = prom.get_metric_range_data(
        "aws_applicationelb_request_count_sum{exported_job='aws_applicationelb', instance='52.74.71.209:9106', job='prometheus', load_balancer='app/khanh-thesis-lb/f31974a644a1ddaa'}",
        start_time=start_time,
        end_time=end_time,
        chunk_size=chunk_size,
    )

    metric_data_sum_bytes = prom.get_metric_range_data(
        "aws_applicationelb_processed_bytes_sum{exported_job='aws_applicationelb', instance='52.74.71.209:9106', job='prometheus', load_balancer='app/khanh-thesis-lb/f31974a644a1ddaa'}",
        start_time=start_time,
        end_time=end_time,
        chunk_size=chunk_size,
    )
    index = 0
    if len(metric_data_request_count) != 10:
        return False
    for data_request in metric_data_request_count:
        value = data_request.get('values')[0]
        epoch_time = value[0]
        dt_request = datetime.fromtimestamp( epoch_time )
        request_count = value[1]
        metrics_data[index].append(request_count)
        for data_bytes in metric_data_sum_bytes:
            value = data_bytes.get('values')[0]
            epoch_time = value[0]
            dt_bytes = datetime.fromtimestamp( epoch_time )
            sum_bytes = value[1]
            if dt_bytes == dt_request:
                metrics_data[index].append(sum_bytes)
                break
        index += 1
    for i in range(10):
        for k in range(len(metrics_data[i])):
            metrics_data[i][k] = eval(metrics_data[i][k])
        if len(metrics_data[i]) < 3:
            for j in range(3 - len(metrics_data[i])):
                metrics_data[i].append(0)
    return metrics_data

print(get_metrics(start_time, end_time, chunk_size))