import boto3
import datetime

cloudwatch = boto3.client('cloudwatch', region_name = 'ap-southeast-1')

metric_name = 'RequestPredict'
metric_value = 123
namespace = 'RequestPredict'
dimensions = [
    {
        'Name': 'Predict',
        'Value': 'RequestCount'
    },
]

metric_data = {
    'MetricName': metric_name,
    'Dimensions': dimensions,
    'Timestamp': datetime.datetime.utcnow(),
    'Value': metric_value,
    'Unit': 'Count'
}

metric_data_list = [metric_data]

response = cloudwatch.put_metric_data(
    Namespace=namespace,
    MetricData=metric_data_list
)

print(response)