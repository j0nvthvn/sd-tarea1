import os
import json
import time

from flask import Flask, request, jsonify
import redis
import requests

app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)
TTL = int(os.getenv("TTL_SECONDS", "300"))
SCRAPER_URL = "http://scraper:5000/scrape"


def cache_key(params: dict) -> str:
    """Clave determinista sobre los parámetros de la consulta.

    En Q3 los equipos se ordenan para que A vs B y B vs A compartan clave.
    """
    p = dict(params)
    if "e1" in p and "e2" in p:
        p["e1"], p["e2"] = sorted([p["e1"], p["e2"]])
    return "football:" + json.dumps(p, sort_keys=True, separators=(",", ":"))


@app.route("/consulta")
def consulta():
    params = request.args.to_dict()
    key = cache_key(params)
    t0 = time.time()

    cached = r.get(key)
    if cached is not None:
        return jsonify({"cache": "hit", "data": json.loads(cached),
                        "latencia_ms": (time.time() - t0) * 1000})

    resp = requests.get(SCRAPER_URL, params=params, timeout=30).json()
    r.setex(key, TTL, json.dumps(resp))
    return jsonify({"cache": "miss", "data": resp,
                    "latencia_ms": (time.time() - t0) * 1000})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
