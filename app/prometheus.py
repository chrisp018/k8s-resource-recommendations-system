import requests
from datetime import datetime
from datetime import timedelta

from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime

# NOTE: Time clock of system

# Connect to Prometheus server
prom = PrometheusConnect(url="http://52.74.71.209:9090", disable_ssl=True)

start_time = parse_datetime("12minutes")
end_time = parse_datetime("now")
chunk_size = timedelta(minutes=1)
# Get the list of all the metrics that the Prometheus host scrapes
# print(prom.all_metrics())

metric_data_request_count = prom.get_metric_range_data(
    'aws_applicationelb_request_count_sum{exported_job="aws_applicationelb", instance="52.74.71.209:9106", job="prometheus", load_balancer="app/khanh-thesis-lb/f31974a644a1ddaa"}',
    start_time=start_time,
    end_time=end_time,
    chunk_size=chunk_size,
)

print(metric_data_request_count)
# metric_data_sum_bytes = prom.get_metric_range_data(
#     "aws_applicationelb_processed_bytes_sum{exported_job='aws_applicationelb', instance='52.74.71.209:9106', job='prometheus', load_balancer='app/khanh-thesis-lb/f31974a644a1ddaa'}",
#     start_time=start_time,
#     end_time=end_time,
#     chunk_size=chunk_size,
# )
# print(metric_data_sum_bytes)

# print('metric_data_request_count: ')
# for data in metric_data_request_count:
#     value = data.get('values')[0]
#     epoch_time = value[0]
#     date_time = datetime.fromtimestamp( epoch_time )
#     request_count = value[1]
#     print(date_time, request_count)

# print('metric_data_sum_bytes')
# for data in metric_data_sum_bytes:
#     value = data.get('values')[0]
#     epoch_time = value[0]
#     date_time = datetime.fromtimestamp( epoch_time )
#     request_count = value[1]
#     print(date_time, request_count)
