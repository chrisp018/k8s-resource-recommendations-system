import pandas as pd
from datetime import datetime
from datetime import timedelta
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime

time_offset = 1000

# Process CSV again for timeoffset
#
#
#
#

# Read match data 
match_data = '/content/drive/MyDrive/thesis/worldcup-match/worldcup-match-fmt-120minus.csv'
df_match = pd.read_csv(match_data)
df_match.head()
# Convert date columns to datetime objects
df_match['Date'] = pd.to_datetime(df_match['Date']).dt.tz_localize(None)
df_match['Date_minus_15_minutes'] = pd.to_datetime(df_match['Date_minus_15_minutes']).dt.tz_localize(None)
df_match['Date_plus_105_minutes'] = pd.to_datetime(df_match['Date_plus_105_minutes']).dt.tz_localize(None)
df_resampled['event_time'] = pd.to_datetime(df_resampled['event_time']).dt.tz_localize(None)


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
            # print(dt_request, dt_bytes)
            if dt_bytes == dt_request:
                metrics_data[index].append(sum_bytes)
                # metrics_data[index].append(0) # for testing match count
                break
            elif dt_bytes > dt_request:
                metrics_data[index].append(0)
                # metrics_data[index].append(0) # for testing match count
                break    
            
        index += 1
    return metrics_data

print(get_metrics(start_time, end_time, chunk_size))