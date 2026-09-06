import re
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from source import obtener_html

app = Flask(__name__)

def parse_tabla(html):
    soup = BeautifulSoup(html, "html.parser")
    cont = soup.select_one(".ui-table")
    if not cont:
        return {"tipo": "Q5", "tabla": [], "error": "no se encontró .ui-table"}
    def num(x):
        return int(x) if x and x.lstrip("-").isdigit() else None
    filas = []
    for row in cont.select(".ui-table__row"):
        name_el = row.select_one(".tableCellParticipant__name")
        if not name_el:
            continue
        rank_el  = row.select_one(".table__cell--rank")
        pts_el   = row.select_one(".table__cell--points")
        score_el = row.select_one(".table__cell--score")
        diff_el  = row.select_one(".table__cell--goalsForAgainstDiff")
        simples = [c.get_text(strip=True) for c in row.select(".table__cell--value")
                   if not any(x in c.get("class", []) for x in
                       ["table__cell--score", "table__cell--goalsForAgainstDiff", "table__cell--points"])]
        gf = ga = None
        if score_el and ":" in score_el.get_text():
            gf, ga = [s.strip() for s in score_el.get_text(strip=True).split(":")[:2]]
        m = re.search(r"/([A-Za-z0-9]{6,})/?$", name_el.get("href", "").rstrip("/"))
        filas.append({
            "pos": num(re.sub(r"\D", "", rank_el.get_text())) if rank_el else None,
            "equipo": name_el.get_text(strip=True),
            "equipo_id": m.group(1) if m else None,
            "pj": num(simples[0]) if len(simples) > 0 else None,
            "pg": num(simples[1]) if len(simples) > 1 else None,
            "pe": num(simples[2]) if len(simples) > 2 else None,
            "pp": num(simples[3]) if len(simples) > 3 else None,
            "gf": num(gf), "gc": num(ga),
            "dif": num(diff_el.get_text(strip=True)) if diff_el else None,
            "pts": num(pts_el.get_text(strip=True)) if pts_el else None,
        })
    return {"tipo": "Q5", "tabla": filas}

PARSERS = {"Q5": parse_tabla}

@app.route("/scrape")
def scrape():
    tipo = request.args.get("tipo")
    parser = PARSERS.get(tipo)
    if not parser:
        return jsonify({"error": f"tipo {tipo} no implementado"}), 400
    return jsonify(parser(obtener_html()))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)