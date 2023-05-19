import pandas as pd
import numpy as np
import time
import boto3
from datetime import datetime
from datetime import timedelta
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime
from prometheus_client import start_http_server, Gauge
from tensorflow.keras.models import load_model
from joblib import load
from sklearn.preprocessing import MinMaxScaler

region = 'ap-southeast-1'


# import model saved
model = load_model('./model/bi-lstm-model.h5')
scaler_eventcount = load('./model/scaler-eventcount-bi-lstm.joblib')
scaler = load('./model/scaler-bi-lstm.joblib')


# Create a new Gauge metric named "my_gauge" with a help message
predicted_prometheus = Gauge('predicted_prometheus', 'This is predicted_prometheus metric')
start_http_server(8000)


# config values
# convert the datetime strings to datetime objects
# calculate the time offset between the datetime objects
ssm = boto3.client('ssm', region_name=region)
response_past_trigger = ssm.get_parameter(
    Name='/khanh-thesis/past_trigger_time',
    WithDecryption=True
)
response_current_trigger = ssm.get_parameter(
    Name='/khanh-thesis/current_trigger_time',
    WithDecryption=True
)

past_trigger_time = response_past_trigger['Parameter']['Value']
current_trigger_time = response_current_trigger['Parameter']['Value']
print("past_trigger_time:", past_trigger_time)
print("current_trigger_time:", current_trigger_time)
past_datetime = datetime.strptime(past_trigger_time, '%Y-%m-%d %H:%M:%S')
current_datetime = datetime.strptime(current_trigger_time, '%Y-%m-%d %H:%M:%S')
time_offset = current_datetime - past_datetime


# Load the Excel file into a Pandas DataFrame
wc_dataset = pd.read_csv('wc_dataset_processed.csv', usecols=['event_time', 'num_match_event'])
wc_dataset['event_time'] = pd.to_datetime(wc_dataset['event_time'])
wc_dataset = wc_dataset.set_index('event_time')
# Connect to Prometheus server
prom = PrometheusConnect(url="http://prometheus.khanh-thesis.online", disable_ssl=True)


def get_metrics(start_time, end_time, step):
    print("start_time: ", type(start_time))
    metric_data_request_count = prom.custom_query_range(
        query='sum(rate(istio_requests_total{source_app="request-simulate", destination_app="app-simulate", response_code="200", connection_security_policy="unknown", job="envoy-stats"}[1m])) * 50',
        start_time=start_time,
        end_time=end_time,
        step=step,
    )
    metric_data_sum_bytes = prom.custom_query_range(
        query='sum(rate(istio_response_bytes_sum{source_app="request-simulate", destination_app="app-simulate", response_code="200", connection_security_policy="unknown", job="envoy-stats"}[1m]) * 50)',
        start_time=start_time,
        end_time=end_time,
        step=step,
    )
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


def predict_values(time_series, scaler_eventcount, scaler):
    time_series[['sum_bytes', 'num_match_event']] = scaler.transform(time_series[['sum_bytes', 'num_match_event']])
    time_series[['request_count']] = scaler_eventcount.transform(time_series[['request_count']])
    # Reshape the time series data into a 3D array
    num_samples = 1
    timesteps = 10
    num_features = 3
    np_time_series = time_series.values
    reshaped_data = np_time_series.reshape(num_samples, timesteps, num_features)
    # Use the LSTM model to predict the next value in the time series
    predicted_value = model.predict(reshaped_data)
    # Inverse transform the predicted value using the scaler
    predicted_value = scaler_eventcount.inverse_transform(predicted_value)
    return predicted_value

# calib time 
calib_current_time = datetime.now()
calib_next_minute = calib_current_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
calib_delta_time = (calib_next_minute - calib_current_time).total_seconds() + 1
print("delta_time :", int(calib_delta_time))
time.sleep(calib_delta_time)
while True:
    # predict
    now = datetime.now()
    start_time = (now - timedelta(minutes=9)).strftime("%Y-%m-%d %H:%M:00")
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = now.strftime("%Y-%m-%d %H:%M:00")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    step = "1m"
    rs = get_metrics(start_time, end_time, step)
    if not rs.empty:
        rs['timestamp'] = pd.to_datetime(rs['timestamp'], unit='s')
        # minus 1 minutes because prometheus read data the data is in the past
        rs['timestamp'] = rs['timestamp'] - time_offset - timedelta(minutes=1)
        merged_df = pd.merge(wc_dataset, rs, left_on='event_time', right_on='timestamp', how='right')
        merged_df['num_match_event'] = merged_df['num_match_event'].fillna(0) # fill missing values with 0
        merged_df = merged_df.reindex(columns=['timestamp', 'request_count', 'sum_bytes', 'num_match_event'])
        merged_df = merged_df.drop('timestamp', axis=1)
        predicted_value = predict_values(merged_df, scaler_eventcount, scaler)
        print(int(predicted_value[0][0]))
        predicted_prometheus.set(int(predicted_value[0][0]))
    predict_end_time = datetime.now()
    predict_next_minute = predict_end_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
    predict_delta_time= (predict_next_minute - predict_end_time).total_seconds() + 1
    print("delta_time :", int(predict_delta_time))
    time.sleep(predict_delta_time)
