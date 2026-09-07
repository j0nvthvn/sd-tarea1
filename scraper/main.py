from datetime import datetime

from flask import Flask, request, jsonify

import source

app = Flask(__name__)


def _cargar_inicial() -> dict:
    """Precarga al iniciar. Si el modo live falla, cae a offline para no quedar sin servicio."""
    try:
        return source.cargar_snapshot()
    except Exception as e:
        app.logger.warning("Carga inicial falló (%s); usando datos offline como respaldo", e)
        return {
            "matches": source.cargar_matches_offline(),
            "standings": source.cargar_standings(),
            "fuente": "offline (respaldo)",
            "scraping_time_ms": 0.0,
            "refreshed_at": None,
        }


SNAP = _cargar_inicial()


def _norm(s) -> str:
    return (s or "").strip().lower()


def _team_keys(x: dict) -> set:
    """Nombres y slugs por los que se puede referir a los equipos de un partido."""
    return {_norm(x.get("home_team")), _norm(x.get("away_team")),
            _norm(x.get("home_slug")), _norm(x.get("away_slug"))}


def _fecha_valida(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def _error(msg: str, code: int = 400):
    return jsonify({"error": msg}), code


@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "fuente": SNAP.get("fuente"),
        "matches": len(SNAP["matches"]),
        "equipos_tabla": len(SNAP["standings"]),
        "scraping_time_ms": SNAP.get("scraping_time_ms"),
        "refreshed_at": SNAP.get("refreshed_at"),
    })


@app.route("/admin/refresh", methods=["POST", "GET"])
def refresh():
    global SNAP
    try:
        SNAP = source.cargar_snapshot()
        return jsonify({"ok": True, "fuente": SNAP["fuente"],
                        "matches": len(SNAP["matches"]),
                        "scraping_time_ms": SNAP["scraping_time_ms"]})
    except Exception as e:
        # Soccerway falló: conservamos el último snapshot válido en memoria
        return jsonify({"ok": False, "error": f"refresh falló: {e}",
                        "snapshot_previo_conservado": True}), 502


@app.route("/scrape")
def scrape():
    tipo = request.args.get("tipo")
    m = SNAP["matches"]

    if tipo in ("Q1", "Q2"):
        eq = _norm(request.args.get("equipo"))
        if not eq:
            return _error(f"{tipo} requiere el parámetro 'equipo'")
        if tipo == "Q1":
            r = [x for x in m if x["status"] == "scheduled" and eq in _team_keys(x)]
            r = sorted(r, key=lambda x: x["timestamp"] or 0)
        else:
            try:
                lim = int(request.args.get("limit", 5))
            except ValueError:
                return _error("'limit' debe ser un número entero")
            if lim <= 0:
                return _error("'limit' debe ser mayor que 0")
            r = [x for x in m if x["status"] == "finished" and eq in _team_keys(x)]
            r = sorted(r, key=lambda x: x["timestamp"] or 0, reverse=True)[:lim]
        return jsonify({"tipo": tipo, "partidos": r, "n": len(r)})

    if tipo == "Q3":
        a, b = _norm(request.args.get("e1")), _norm(request.args.get("e2"))
        if not a or not b:
            return _error("Q3 requiere los parámetros 'e1' y 'e2'")
        r = [x for x in m if a in _team_keys(x) and b in _team_keys(x)]
        r = sorted(r, key=lambda x: x["timestamp"] or 0, reverse=True)
        return jsonify({"tipo": tipo, "partidos": r, "n": len(r)})

    if tipo == "Q4":
        d1, d2 = request.args.get("desde"), request.args.get("hasta")
        if not d1 or not d2:
            return _error("Q4 requiere 'desde' y 'hasta' (formato YYYY-MM-DD)")
        if not (_fecha_valida(d1) and _fecha_valida(d2)):
            return _error("fechas inválidas, usar formato YYYY-MM-DD")
        if d1 > d2:
            return _error("'desde' no puede ser posterior a 'hasta'")
        r = [x for x in m if x["date"] and d1 <= x["date"] <= d2]
        r = sorted(r, key=lambda x: x["timestamp"] or 0)
        return jsonify({"tipo": tipo, "partidos": r, "n": len(r)})

    if tipo == "Q5":
        return jsonify({"tipo": tipo, "tabla": SNAP["standings"]})

    return _error(f"tipo '{tipo}' desconocido")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
