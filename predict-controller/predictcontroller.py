import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime

# Load the Excel file into a Pandas DataFrame
df = pd.read_excel('wc_dataset_processed.csv')
df['event_time'] = pd.to_datetime(df['event_time'])
df = df.set_index('event_time')


# Connect to Prometheus server
prom = PrometheusConnect(url="http://prometheus.khanh-thesis.online", disable_ssl=True)

start_time = parse_datetime("9minutes")
end_time = parse_datetime("now")
step = "1m"
def find_events(timestamp):
    num_match_event = df.loc[timestamp, 'num_match_event']
    print(num_match_event)

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

# past_trigger_time = "1998-04-30 21:45:00"
# current_trigger_time = "2034-04-30 21:45:00"
# time_offset = past_trigger_time - current_trigger_time

# past_read_timedata = current_read_timedata - time_offset

# # get match value in excel match the time
# past_read_timedata = "1998-04-30 21:45:00"