[WIP]
1. App request api to prometheus 

from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime
from datetime import datetime
from datetime import timedelta

from prometheus_client import start_http_server, Counter, Histogram

prom = PrometheusConnect(url="http://prometheus.istio-system.svc.cluster.local:9090", disable_ssl=True)

start_time = parse_datetime("10minutes")
end_time = parse_datetime("now")
chunk_size = timedelta(minutes=1)

metric_data_request_count = prom.get_metric_range_data("istio_requests_total{source_app="request-simulate", destination_app="appsimulate", response_code="200",connection_security_policy="unknown"}",start_time=start_time,end_time=end_time,chunk_size=chunk_size)

metric_data_request_count = prom.get_metric_range_data("istio_requests_total{source_app="request-simulate", destination_app="appsimulate",start_time=start_time,end_time=end_time, chunk_size=chunk_size)