from flask import Flask, request, jsonify

import source

app = Flask(__name__)

SNAP = source.cargar_snapshot()


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _team_keys(x: dict) -> set:
    """Nombres y slugs por los que se puede referir a los equipos de un partido."""
    return {_norm(x.get("home_team")), _norm(x.get("away_team")),
            _norm(x.get("home_slug")), _norm(x.get("away_slug"))}


@app.route("/health")
def health():
    return jsonify({"ok": True, "matches": len(SNAP["matches"]),
                    "equipos_tabla": len(SNAP["standings"])})


@app.route("/admin/refresh", methods=["POST", "GET"])
def refresh():
    global SNAP
    SNAP = source.cargar_snapshot()
    return jsonify({"ok": True, "matches": len(SNAP["matches"]),
                    "scraping_time_ms": SNAP["scraping_time_ms"]})


@app.route("/scrape")
def scrape():
    tipo = request.args.get("tipo")
    m = SNAP["matches"]

    if tipo == "Q1":  # próximos partidos de un equipo
        eq = _norm(request.args.get("equipo"))
        r = [x for x in m if x["status"] == "scheduled" and eq in _team_keys(x)]
        r = sorted(r, key=lambda x: x["timestamp"] or 0)
        return jsonify({"tipo": tipo, "partidos": r, "n": len(r)})

    if tipo == "Q2":  # últimos partidos de un equipo
        eq = _norm(request.args.get("equipo"))
        lim = int(request.args.get("limit", 5))
        r = [x for x in m if x["status"] == "finished" and eq in _team_keys(x)]
        r = sorted(r, key=lambda x: x["timestamp"] or 0, reverse=True)[:lim]
        return jsonify({"tipo": tipo, "partidos": r, "n": len(r)})

    if tipo == "Q3":  # historial de enfrentamientos
        a, b = _norm(request.args.get("e1")), _norm(request.args.get("e2"))
        r = [x for x in m if a in _team_keys(x) and b in _team_keys(x)]
        r = sorted(r, key=lambda x: x["timestamp"] or 0, reverse=True)
        return jsonify({"tipo": tipo, "partidos": r, "n": len(r)})

    if tipo == "Q4":  # partidos por fecha / período
        d1, d2 = request.args.get("desde"), request.args.get("hasta")
        r = [x for x in m if x["date"] and d1 <= x["date"] <= d2]
        r = sorted(r, key=lambda x: x["timestamp"] or 0)
        return jsonify({"tipo": tipo, "partidos": r, "n": len(r)})

    if tipo == "Q5":  # tabla de posiciones
        return jsonify({"tipo": tipo, "tabla": SNAP["standings"]})

    return jsonify({"error": f"tipo '{tipo}' desconocido"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
