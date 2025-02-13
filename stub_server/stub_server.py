from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

def gen():
    return 70


@app.route('/stub/server/<int:server_id>')
def metrics(server_id):
    return jsonify({"cpu": random.randint(0, 100), "mem": f"{random.randint(0, 10)}%", "disk": f"{random.randint(0, 100)}%",
         "uptime": f"{random.randint(1, 30)}d {random.randint(0, 23)}h {random.randint(0, 59)}m"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)