import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime


# config values
# convert the datetime strings to datetime objects
# calculate the time offset between the datetime objects
past_trigger_time = "1998-04-30 21:30:00"
current_trigger_time = "2023-04-20 14:24:00"
past_datetime = datetime.strptime(past_trigger_time, '%Y-%m-%d %H:%M:%S')
current_datetime = datetime.strptime(current_trigger_time, '%Y-%m-%d %H:%M:%S')
time_offset = current_datetime - past_datetime


# Load the Excel file into a Pandas DataFrame
wc_dataset = pd.read_csv('wc_dataset_processed.csv', usecols=['event_time', 'num_match_event'])
wc_dataset['event_time'] = pd.to_datetime(wc_dataset['event_time'])
wc_dataset = wc_dataset.set_index('event_time')


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
rs['timestamp'] = pd.to_datetime(rs['timestamp'], unit='s').apply(lambda x: x + timedelta(minutes=1) - timedelta(seconds=x.second))


# subtract datetime offset from timestamp column
# merge the two dataframes on the datetime columns
# fill missing values with 0 for the num_match_event column
rs['timestamp'] = rs['timestamp'] - time_offset
merged_df = pd.merge(wc_dataset, rs, left_on='event_time', right_on='timestamp', how='right')
merged_df['num_match_event'] = merged_df['num_match_event'].fillna(0)
merged_df = merged_df.reindex(columns=['timestamp', 'request_count', 'sum_bytes', 'num_match_event'])

print(merged_df)
