import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch', region_name = 'ap-southeast-1')

alb_name = "app/khanh-thesis/cca92d757a7006ec"

# Set the start and end times for the metric data
end_time = datetime.utcnow()
start_time = end_time - timedelta(minutes=10)

def get_metrics(start_time, end_time):
    metrics_data = [[] for i in range(10)]
    # Retrieve the request count and sum bytes for the instance over the past 24 hours
    rs_request_count = cloudwatch.get_metric_statistics(
        Namespace='AWS/ApplicationELB',
        MetricName='RequestCount',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': alb_name
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=60, # 1-minute interval
        Statistics=['Sum'],
    )

    rs_sum_bytes = cloudwatch.get_metric_statistics(
        Namespace='AWS/ApplicationELB',
        MetricName='ProcessedBytes',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': alb_name
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=60, # 1-minute interval
        Statistics=['Sum'],
    )

    index = 0
    print(len(rs_request_count.get('Datapoints')))
    if len(rs_request_count.get('Datapoints')) != 10:
        return False
    
    print('sumrequest')
    for request_count in rs_request_count['Datapoints']:
        timestamp_sr = request_count['Timestamp']
        sumrequest = request_count['Sum']
        print(f"{timestamp_sr}: {sumrequest}")
        metrics_data[index].append(sumrequest)
        # print('sumbytes')
        for sum_bytes in rs_sum_bytes['Datapoints']:
            timestamp_sb = sum_bytes['Timestamp']
            sumbytes = sum_bytes['Sum']
            print(f"{timestamp_sb}: {sumbytes}")
            if timestamp_sr == timestamp_sb:
                metrics_data[index].append(sumbytes)
                break
        index += 1
    for i in range(10):
        # for k in range(len(metrics_data[i])):
        #     metrics_data[i][k] = eval(metrics_data[i][k])
        if len(metrics_data[i]) < 3:
            for j in range(3 - len(metrics_data[i])):
                metrics_data[i].append(0)
    return metrics_data

print(get_metrics(start_time, end_time))