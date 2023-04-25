from flask import Flask, request, jsonify
import numpy as np
import os

app = Flask(__name__)

target_rpm = 10

def consume_cpu_memory(n):
    result = []
    for i in range(n):
        # Consume CPU by computing the sum of a large random array
        arr = np.random.rand(10000)
        sum = np.sum(arr)
        # Consume memory by appending the array to the result list
        result.append(arr)
    return result


@app.route('/bytes', methods=['GET'])
def get_bytes():
    num_bytes = request.args.get('num_bytes', default=0, type=int)
    consume_cpu_memory(target_rpm)
    if num_bytes <= 0:
        return jsonify({'error': 'num_bytes must be greater than 0'}), 400
    return os.urandom(num_bytes), 200, {'Content-Type': 'application/octet-stream', 'Content-Length': num_bytes}


@app.route('/')
def get_root():
    return 'ok'


@app.route('/healthz/ready')
def get_readness():
    return 'ok'


@app.route('/healthz/live')
def get_liveness():
    return 'ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
