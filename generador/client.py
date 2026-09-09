import requests


def enviar_consulta(url: str, consulta: dict):
    """
    Envía una consulta al servicio cache.
    """

    try:
        respuesta = requests.get(
            url,
            params=consulta,
            timeout=30
        )

        return respuesta.json()

    except requests.RequestException as error:
        return {
            "error": str(error)
        }