import os
import json
import time
from pathlib import Path

import httpx

URL = "https://cl.soccerway.com/chile/liga-de-primera/"
DATA = Path(__file__).parent / "data"
OFFLINE = os.getenv("SOCCERWAY_OFFLINE", "true").lower() == "true"

# Separadores de los feeds embebidos de Soccerway (registro, campo, clave-valor)
SEP_REG, SEP_CAMPO, SEP_KV = "~", "¬", "÷"


def _extraer_feed(html: str, key: str) -> str:
    """Extrae el string dentro de initialFeeds['key'] = { data: `...` }."""
    i = html.find(f"initialFeeds['{key}']")
    if i < 0:
        return ""
    j = html.find("`", i)
    k = html.find("`", j + 1)
    return html[j + 1:k] if 0 <= j < k else ""


def _parse_matches(feed: str, status: str) -> list:
    """Decodifica un feed y normaliza cada partido a un modelo propio."""
    out = []
    for rec in feed.split(SEP_REG):
        d = {}
        for c in rec.split(SEP_CAMPO):
            if SEP_KV in c:
                a, b = c.split(SEP_KV, 1)
                d[a] = b
        if "AA" in d and "AE" in d and "AF" in d:
            ts = int(d["AD"]) if d.get("AD", "").isdigit() else None
            out.append({
                "match_id": d["AA"],
                "date": time.strftime("%Y-%m-%d", time.gmtime(ts)) if ts else None,
                "timestamp": ts,
                "home_team": d.get("AE"),
                "away_team": d.get("AF"),
                "home_slug": d.get("WU"),
                "away_slug": d.get("WV"),
                "home_score": int(d["AG"]) if d.get("AG", "").isdigit() else None,
                "away_score": int(d["AT"]) if d.get("AT", "").isdigit() else None,
                "round": d.get("ER"),
                "status": status,
                "source": "soccerway",
            })
    return out


def descargar_html() -> str:
    with httpx.Client(timeout=20, follow_redirects=True,
                      headers={"User-Agent": "distributed-systems-course/1.0"}) as c:
        r = c.get(URL)
        r.raise_for_status()
        return r.text


def _cargar_matches_live() -> list:
    html = descargar_html()
    matches = (_parse_matches(_extraer_feed(html, "results"), "finished")
               + _parse_matches(_extraer_feed(html, "fixtures"), "scheduled"))
    return list({m["match_id"]: m for m in matches}.values())


def cargar_snapshot() -> dict:
    """Precarga en memoria: partidos (live u offline) + tabla oficial (snapshot)."""
    t0 = time.perf_counter()
    if OFFLINE:
        matches = json.loads((DATA / "matches.json").read_text(encoding="utf-8"))
    else:
        matches = _cargar_matches_live()
    standings = json.loads((DATA / "standings.json").read_text(encoding="utf-8"))
    return {
        "matches": matches,
        "standings": standings,
        "scraping_time_ms": (time.perf_counter() - t0) * 1000,
        "refreshed_at": time.time(),
    }
