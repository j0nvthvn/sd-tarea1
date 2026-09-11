from flask import Flask, request, jsonify
from collections import defaultdict
import csv
import os


app = Flask(__name__)

eventos = []


def percentil(valores, p):
    if not valores:
        return None

    valores = sorted(valores)

    posicion = (len(valores) - 1) * p / 100

    inferior = int(posicion)
    superior = min(inferior + 1, len(valores) - 1)

    peso = posicion - inferior

    return (
        valores[inferior] * (1 - peso)
        + valores[superior] * peso
    )


def estadisticas_latencia(valores):

    if not valores:
        return {
            "cantidad": 0,
            "media_ms": None,
            "p50_ms": None,
            "p95_ms": None,
            "p99_ms": None
        }

    return {
        "cantidad": len(valores),
        "media_ms": sum(valores) / len(valores),
        "p50_ms": percentil(valores, 50),
        "p95_ms": percentil(valores, 95),
        "p99_ms": percentil(valores, 99)
    }


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


    latencias = [
        e.get("latencia_ms")
        for e in eventos
        if isinstance(e.get("latencia_ms"), (int,float))
    ]


    return jsonify({

        "consultas": total,

        "hits": hits,

        "misses": misses,

        "hit_rate": hits / total if total else 0,

        "latencia": estadisticas_latencia(latencias)

    })


@app.route("/resumen/tipos")
def resumen_tipos():

    tipos = defaultdict(list)


    for evento in eventos:

        tipos[evento.get("tipo")].append(evento)


    resultado = {}


    for tipo, datos in tipos.items():

        hits = sum(
            1 for e in datos
            if e.get("cache") == "hit"
        )

        misses = sum(
            1 for e in datos
            if e.get("cache") == "miss"
        )


        resultado[tipo] = {

            "consultas": len(datos),

            "hits": hits,

            "misses": misses,

            "hit_rate": hits / (hits + misses)
            if hits + misses else 0

        }


    return jsonify(resultado)


@app.route("/exportar")
def exportar():

    ruta = "/app/data/metricas.csv"

    os.makedirs(
        "/app/data",
        exist_ok=True
    )


    with open(
        ruta,
        "w",
        newline="",
        encoding="utf-8"
    ) as archivo:


        escritor = csv.DictWriter(
            archivo,
            fieldnames=eventos[0].keys()
        )


        escritor.writeheader()

        escritor.writerows(eventos)


    return jsonify({
        "ok": True,
        "archivo": ruta,
        "eventos": len(eventos)
    })

@app.route("/reset")
def reset():

    eventos.clear()

    return jsonify({
        "ok": True,
        "eventos": len(eventos)
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