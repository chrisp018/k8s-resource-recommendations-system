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

((abs(df['event_count'] - df['event_count'].shift(1)) <= abs((df['event_count'].shift(1) - df['event_count'].shift(2)))) & (df['event_count'].shift(1) - df['event_count'].shift(2) < 0)).astype(int)

abs(df['event_count'] - df['event_count'].shift(1))

abs(df['event_count'] - df['event_count'].shift(1))/(abs(df['event_count'].shift(1) - df['event_count'].shift(2)) + abs(df['event_count'] - df['event_count'].shift(1))) >=90

(df['noise'] = abs(df['event_count'] - df['event_count'].shift(1))/(abs(df['event_count'].shift(1) - df['event_count'].shift(2)) + abs(df['event_count'] - df['event_count'].shift(1))) >=90 & (df['event_count'].shift(1) - df['event_count'].shift(2) < 0)).astype(int)



kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/namespaces/appsimulate/pods/appsimulate/predicted_prometheus" | jq .
kubectl get --raw "/apis/external.metrics.k8s.io/v1beta1/namespaces/appsimulate/predicted_prometheus" | jq .

istio_response_bytes_sum{destination_app='appsimulate', source_app='request-simulate'}

rate(istio_requests_total{source_app="request-simulate", destination_app="appsimulate", response_code="200", connection_security_policy="unknown"}[1m])*60

rate(istio_response_bytes_sum{source_app="request-simulate", destination_app="appsimulate", response_code="200", connection_security_policy="unknown"}[1m]) * 50 - rate(istio_requests_total{source_app="request-simulate", destination_app="appsimulate", response_code="200", connection_security_policy="unknown"}[1m]) * 50*150
curl http://localhost:15000/stats?filter=istio.*

curl http://appsimulate.appsimulate.svc.cluster.local:5000/bytes?num_bytes=7000

curl https://appsimulate.appsimulate.svc.cluster.local:15000/stats

curl http://172.21.52.95:1500/stats

kubectl get endpoints istiod -n istio-system -o json

kubectl get endpoints request-simulate -n request-simulate -o json