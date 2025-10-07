"""
Flask example app using CallFlow Tracer.

Run:
    pip install "callflow-tracer[web]"
    python examples/flask_app/app.py
Then open the generated flask_trace.html after making a few requests.
"""

from __future__ import annotations

import random
import time
from flask import Flask, jsonify

from callflow_tracer import trace_scope
from callflow_tracer.integrations import setup_flask_tracing

app = Flask(__name__)
setup_flask_tracing(app)


def _work(n: int) -> int:
    total = 0
    for _ in range(n):
        total += random.randint(1, 10)
        time.sleep(0.005)
    return total


@app.get("/")
def index():
    return jsonify({"message": "Hello from Flask + CallFlow Tracer"})


@app.get("/compute/<int:n>")
def compute(n: int):
    result = _work(max(1, min(n, 50)))
    return jsonify({"n": n, "result": result})


if __name__ == "__main__":
    # Wrap the app run in trace_scope so we export a single HTML file
    with trace_scope("flask_trace.html"):
        app.run(host="127.0.0.1", port=5000, debug=True)
