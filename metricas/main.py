from flask import Flask, request, jsonify
from collections import Counter

app = Flask(__name__)

eventos = []


@app.route("/evento", methods=["POST"])
def evento():

    datos = request.json

    eventos.append(datos)

    return jsonify({
        "ok": True,
        "total_eventos": len(eventos)
    })


@app.route("/resumen")
def resumen():

    total = len(eventos)

    hits = sum(
        1 for e in eventos
        if e.get("cache") == "hit"
    )

    misses = sum(
        1 for e in eventos
        if e.get("cache") == "miss"
    )

    return jsonify({
        "consultas": total,
        "hits": hits,
        "misses": misses,
        "hit_rate": hits / total if total else 0
    })


@app.route("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )