from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "telemetry.json")
with open(DATA_PATH) as f:
    telemetry = json.load(f)

@app.post("/")
async def latency(request: Request):
    body = await request.json()
    regions = body["regions"]
    threshold = body["threshold_ms"]

    result = {}

    for region in regions:
        records = [r for r in telemetry if r["region"] == region]
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(l > threshold for l in latencies)
        }

    return result
