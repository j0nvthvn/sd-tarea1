import os
import random
from datetime import date, timedelta

MODO_CACHE = os.getenv(
    "EXPERIMENTO_CACHE",
    "false"
).lower() == "true"

VARIANTES_CACHE = 50000

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


EQUIPOS_CACHE = [
    f"equipo-{i}"
    for i in range(200)
]


TIPOS_CONSULTA = [
    "Q1",
    "Q2",
    "Q3",
    "Q4",
    "Q5"
]


TEMPORADA_INICIO = date(2026, 4, 14)
TEMPORADA_FIN = date(2026, 12, 6)
VENTANA_DIAS = 7


def _ventanas(
    inicio=TEMPORADA_INICIO,
    fin=TEMPORADA_FIN,
    dias=VENTANA_DIAS
):
    ventanas = []

    actual = inicio

    while actual <= fin:
        termino = min(
            actual + timedelta(days=dias - 1),
            fin
        )

        ventanas.append(
            (
                actual.isoformat(),
                termino.isoformat()
            )
        )

        actual = termino + timedelta(days=1)

    return ventanas


VENTANAS = _ventanas()

VENTANAS_CACHE = []

for i in range(1000):

    inicio = TEMPORADA_INICIO + timedelta(days=i)

    VENTANAS_CACHE.append(
        (
            inicio.isoformat(),
            (inicio + timedelta(days=6)).isoformat()
        )
    )


def generar_q1(selector):

    consulta = {
        "tipo": "Q1",
        "equipo": selector.elegir(EQUIPOS)
    }

    if MODO_CACHE:
        consulta["variante"] = selector.elegir(
            list(range(VARIANTES_CACHE))
        )

    return consulta


def generar_q2(selector):

    consulta = {
        "tipo": "Q2",
        "equipo": selector.elegir(EQUIPOS)
    }

    if MODO_CACHE:
        consulta["variante"] = selector.elegir(
            list(range(VARIANTES_CACHE))
        )

    return consulta


def generar_q3(selector):

    e1, e2 = selector.elegir_par(EQUIPOS)

    consulta = {
        "tipo": "Q3",
        "e1": e1,
        "e2": e2
    }

    if MODO_CACHE:
        consulta["variante"] = selector.elegir(
            list(range(VARIANTES_CACHE))
        )

    return consulta


def generar_q4(selector):

    desde, hasta = selector.elegir(VENTANAS)

    consulta = {
        "tipo": "Q4",
        "desde": desde,
        "hasta": hasta
    }

    if MODO_CACHE:
        consulta["variante"] = selector.elegir(
            list(range(VARIANTES_CACHE))
        )

    return consulta


def generar_q5(_selector):

    return {
        "tipo": "Q5"
    }


GENERADORES = {

    "Q1": generar_q1,

    "Q2": generar_q2,

    "Q3": generar_q3,

    "Q4": generar_q4,

    "Q5": generar_q5,

}


def generar_consulta(tipo, selector):
    try:

        return GENERADORES[tipo](selector)

    except KeyError:

        raise ValueError(
            f"tipo de consulta desconocido: {tipo!r}"
        ) from None



def espacio_de_claves():

    n = len(EQUIPOS)

    base = {
        "Q1": n,
        "Q2": n,
        "Q3": n * (n - 1) // 2,
        "Q4": len(VENTANAS),
        "Q5": 1,
    }

    if MODO_CACHE:

        for tipo in ["Q1", "Q2", "Q3", "Q4"]:
            base[tipo] *= VARIANTES_CACHE

    base["total"] = sum(base.values())

    return base