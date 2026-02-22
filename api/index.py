from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import json
import numpy as np
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "q-vercel-latency.json")

with open(FILE_PATH) as f:
    data = json.load(f)


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    }


@app.options("/api")
async def options_handler():
    return Response(status_code=200, headers=cors_headers())


@app.post("/api")
async def analyze(request: Request):
    payload = await request.json()

    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 0)

    results = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]

        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        results[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return JSONResponse(content=results, headers=cors_headers())
