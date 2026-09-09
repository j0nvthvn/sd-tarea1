"""Construccion de las consultas Q1..Q5 que se envian al servicio de cache.

Los equipos se identifican por su *slug*, no por su nombre visible: el scraper
normaliza los parametros con strip().lower() y no elimina tildes, de modo que
"Universidad Catolica" jamas calzaria con "U. Catolica" y "Audax Italiano"
tampoco con "Audax". Los slugs (u-catolica, a-italiano, ...) son estables,
carecen de tildes y son los que expone el dataset del scraper.
"""

from datetime import date, timedelta


# Slugs presentes en scraper/data/matches.json (Primera Division 2026).
EQUIPOS = [
    "colo-colo",
    "u-de-chile",
    "u-catolica",
    "palestino",
    "cobresal",
    "huachipato",
    "everton",
    "coquimbo",
    "nublense",
    "o-higgins",
    "a-italiano",
    "u-la-calera",
    "la-serena",
    "limache",
    "dep-concepcion",
    "u-de-concepcion",
]

TIPOS_CONSULTA = ["Q1", "Q2", "Q3", "Q4", "Q5"]

# Rango cubierto por el dataset. Las ventanas de Q4 se sortean dentro de el
# para que la consulta no degenere en una unica clave siempre cacheada.
TEMPORADA_INICIO = date(2026, 4, 14)
TEMPORADA_FIN = date(2026, 12, 6)
VENTANA_DIAS = 7


def _ventanas(inicio=TEMPORADA_INICIO, fin=TEMPORADA_FIN, dias=VENTANA_DIAS):
    """Ventanas de fechas consecutivas que cubren la temporada."""
    ventanas = []
    actual = inicio
    while actual <= fin:
        termino = min(actual + timedelta(days=dias - 1), fin)
        ventanas.append((actual.isoformat(), termino.isoformat()))
        actual = termino + timedelta(days=1)
    return ventanas


VENTANAS = _ventanas()


def generar_q1(selector):
    """Proximos partidos de un equipo."""
    return {"tipo": "Q1", "equipo": selector.elegir(EQUIPOS)}


def generar_q2(selector):
    """Ultimos partidos jugados por un equipo."""
    return {"tipo": "Q2", "equipo": selector.elegir(EQUIPOS)}


def generar_q3(selector):
    """Historial entre dos equipos distintos."""
    e1, e2 = selector.elegir_par(EQUIPOS)
    return {"tipo": "Q3", "e1": e1, "e2": e2}


def generar_q4(selector):
    """Partidos dentro de una ventana de fechas."""
    desde, hasta = selector.elegir(VENTANAS)
    return {"tipo": "Q4", "desde": desde, "hasta": hasta}


def generar_q5(_selector):
    """Tabla de posiciones (consulta sin parametros)."""
    return {"tipo": "Q5"}


GENERADORES = {
    "Q1": generar_q1,
    "Q2": generar_q2,
    "Q3": generar_q3,
    "Q4": generar_q4,
    "Q5": generar_q5,
}


def generar_consulta(tipo, selector):
    """Construye la consulta del tipo pedido usando el selector de popularidad."""
    try:
        return GENERADORES[tipo](selector)
    except KeyError:
        raise ValueError(f"tipo de consulta desconocido: {tipo!r}") from None


def espacio_de_claves():
    """Cantidad de claves distintas que el generador puede producir.

    Sirve para dimensionar el experimento: si el espacio de claves es mucho
    menor que la memoria del cache, el hit rate se satura y la comparacion
    entre distribuciones deja de ser informativa.
    """
    n = len(EQUIPOS)
    return {
        "Q1": n,
        "Q2": n,
        "Q3": n * (n - 1) // 2,
        "Q4": len(VENTANAS),
        "Q5": 1,
        "total": n + n + n * (n - 1) // 2 + len(VENTANAS) + 1,
    }
