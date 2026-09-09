import random

from queries import generar_consulta


TIPOS_CONSULTA = [
    "Q1",
    "Q2",
    "Q3",
    "Q4",
    "Q5"
]


def seleccionar_uniforme():
    """
    Selecciona una consulta donde todos los tipos
    tienen la misma probabilidad.
    """

    tipo = random.choice(TIPOS_CONSULTA)

    return generar_consulta(tipo)