from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

def gen():
    return 70


@app.route('/server/<int:server_id>')
def metrics(server_id):
    return jsonify({"cpu": random.randint(90, 100), "mem": f"{random.randint(0, 10)}%", "disk": f"{random.randint(0, 100)}%",
         "uptime": f"{random.randint(1, 30)}d {random.randint(0, 23)}h {random.randint(0, 59)}m",'cpu':95,'mem':'93%','disk':'85%'})

import requests

response = requests.get('http://localhost:5000/server/met/cpu/40')
if response.status_code == 200:
    try:
        print(response.json())
    except requests.exceptions.JSONDecodeError:
        print("Response content is not valid JSON")
else:
    print(f"Request failed with status code {response.status_code}")

if __name__ == '__main__':
    app.run(port=5000)