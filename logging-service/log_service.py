from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
import logging
from datetime import datetime

app = Flask(__name__)
metrics = PrometheusMetrics(app)
logging.basicConfig(filename='crud-logs.log', level=logging.INFO)

@app.route('/logs', methods=['POST'])
def log_event():
    data = request.json
    logging.info(f"{datetime.utcnow()} - {data}")
    return {"status": "logged"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)