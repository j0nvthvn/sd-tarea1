from flask import Flask, request, jsonify

app = Flask(__name__)

eventos = []


def calcular_percentil(valores, p):
    if not valores:
        return 0.0

    valores_ordenados = sorted(valores)

    if len(valores_ordenados) == 1:
        return float(valores_ordenados[0])

    posicion = (len(valores_ordenados) - 1) * p / 100
    inferior = int(posicion)
    superior = min(inferior + 1, len(valores_ordenados) - 1)
    peso = posicion - inferior

    return (
        valores_ordenados[inferior] * (1 - peso)
        + valores_ordenados[superior] * peso
    )


def resumen_latencias(lista_eventos):
    latencias = [
        e.get("latencia_ms")
        for e in lista_eventos
        if isinstance(e.get("latencia_ms"), (int, float))
    ]

    if not latencias:
        return {
            "cantidad": 0,
            "media_ms": 0.0,
            "p50_ms": 0.0,
            "p95_ms": 0.0,
            "p99_ms": 0.0,
        }

    return {
        "cantidad": len(latencias),
        "media_ms": sum(latencias) / len(latencias),
        "p50_ms": calcular_percentil(latencias, 50),
        "p95_ms": calcular_percentil(latencias, 95),
        "p99_ms": calcular_percentil(latencias, 99),
    }


@app.route("/evento", methods=["POST"])
def evento():
    datos = request.get_json(silent=True) or {}

    eventos.append(datos)

    return jsonify({
        "ok": True,
        "total_eventos": len(eventos)
    })


@app.route("/resumen")
def resumen():
    total = len(eventos)

    hits_eventos = [e for e in eventos if e.get("cache") == "hit"]
    misses_eventos = [e for e in eventos if e.get("cache") == "miss"]

    hits = len(hits_eventos)
    misses = len(misses_eventos)

    return jsonify({
        "consultas": total,
        "hits": hits,
        "misses": misses,
        "hit_rate": hits / total if total else 0,
        "latencia": resumen_latencias(eventos),
        "latencia_hit": resumen_latencias(hits_eventos),
        "latencia_miss": resumen_latencias(misses_eventos),
    })


@app.route("/resumen/tipos")
def resumen_tipos():
    tipos = sorted(set(e.get("tipo") for e in eventos if e.get("tipo")))

    salida = {}

    for tipo in tipos:
        eventos_tipo = [e for e in eventos if e.get("tipo") == tipo]
        hits = sum(1 for e in eventos_tipo if e.get("cache") == "hit")
        misses = sum(1 for e in eventos_tipo if e.get("cache") == "miss")
        total = len(eventos_tipo)

        salida[tipo] = {
            "consultas": total,
            "hits": hits,
            "misses": misses,
            "hit_rate": hits / total if total else 0
        }

    return jsonify(salida)


@app.route("/reset")
def reset():
    eventos.clear()

    return jsonify({
        "ok": True,
        "eventos": 0
    })


@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "eventos": len(eventos)
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )