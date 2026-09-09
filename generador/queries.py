import random


EQUIPOS = [
    "Colo Colo",
    "Universidad de Chile",
    "Universidad Catolica",
    "Palestino",
    "Union Espanola",
    "Everton",
    "Huachipato",
    "Audax Italiano"
]


TIPOS_CONSULTA = [
    "Q1",
    "Q2",
    "Q3",
    "Q4",
    "Q5"
]


def generar_q1():
    return {
        "tipo": "Q1",
        "equipo": random.choice(EQUIPOS)
    }


def generar_q2():
    return {
        "tipo": "Q2",
        "equipo": random.choice(EQUIPOS)
    }


def generar_q3():
    equipos = random.sample(EQUIPOS, 2)

    return {
        "tipo": "Q3",
        "e1": equipos[0],
        "e2": equipos[1]
    }


def generar_q4():
    return {
        "tipo": "Q4",
        "desde": "2026-09-01",
        "hasta": "2026-09-10"
    }


def generar_q5():
    return {
        "tipo": "Q5"
    }


def generar_consulta(tipo=None):

    if tipo is None:
        tipo = random.choice(TIPOS_CONSULTA)

    consultas = {
        "Q1": generar_q1,
        "Q2": generar_q2,
        "Q3": generar_q3,
        "Q4": generar_q4,
        "Q5": generar_q5
    }

    return consultas[tipo]()