from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/bytes', methods=['GET'])
def get_bytes():
    num_bytes = request.args.get('num_bytes', default=0, type=int)
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
