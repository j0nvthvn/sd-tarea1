import os, json, time
from flask import Flask, request, jsonify
import redis, requests

app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)
TTL = int(os.getenv("TTL_SECONDS", "300"))
SCRAPER_URL = "http://scraper:5000/scrape"

def cache_key(params: dict) -> str:
    tipo = params.get("tipo", "")
    # para Q3 (enfrentamientos) ordenar los equipos para que A-B == B-A
    equipos = sorted([params.get("e1",""), params.get("e2","")])
    return f"{tipo}:{':'.join(filter(None, equipos))}"

@app.route("/consulta")
def consulta():
    params = request.args.to_dict()
    key = cache_key(params)
    t0 = time.time()
    
    cached = r.get(key)
    if cached is not None:
        # TODO: emitir métrica hit + latencia
        return jsonify({"cache": "hit", "data": json.loads(cached), "latencia_ms": (time.time()-t0)*1000})
    
    resp = requests.get(SCRAPER_URL, params=params, timeout=15).json()
    r.setex(key, TTL, json.dumps(resp))
    # TODO: emitir métrica miss + tiempo de scraping + latencia
    return jsonify({"cache": "miss", "data": resp,
                    "latencia_ms": (time.time()-t0)*1000})
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)