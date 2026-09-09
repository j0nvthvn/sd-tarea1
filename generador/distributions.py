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
    Selecciona consultas con igual probabilidad.
    """

    tipo = random.choice(TIPOS_CONSULTA)

    return generar_consulta(tipo)



def seleccionar_zipf():
    """
    Selecciona consultas siguiendo una distribución Zipf.

    Las primeras consultas tienen mayor probabilidad
    de aparecer.
    """

    pesos = {
        "Q1": 50,
        "Q2": 25,
        "Q3": 12,
        "Q4": 8,
        "Q5": 5
    }

    tipos = list(pesos.keys())
    probabilidades = list(pesos.values())

    tipo = random.choices(
        tipos,
        weights=probabilidades,
        k=1
    )[0]

    return generar_consulta(tipo)