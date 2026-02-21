from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

# allow CORS from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

# load telemetry data
with open("telemetry.json") as f:
    data = json.load(f)

@app.post("/api/latency")
async def analyze(payload: dict):
    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = {}

    for region in regions:
        rows = [r for r in data if r["region"] == region]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(l > threshold for l in latencies)
        }

    return result