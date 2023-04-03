from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import random

# Create a Gauge object to represent the metric
g = Gauge('predicted_next_request_count', 'Predicted next request count', ['label1', 'label2'])

g.labels(label1='value1', label2='value2').set_to_current_time()
# Set the value of the metric
# g.labels(label1='value1', label2='value2').set(random.randint(1, 100))

# Create a CollectorRegistry object
registry = CollectorRegistry()

# Push the metric to the Pushgateway
push_to_gateway('http://52.74.71.209:9090', job='predict_request', registry=registry)
