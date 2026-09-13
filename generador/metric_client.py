"""Cliente HTTP para enviar eventos al servicio de métricas."""

import requests


def enviar_metrica(
    url: str,
    tipo: str,
    resultado
):
    """
    Envía el resultado de una consulta al servicio de métricas.

    Si el servicio no está disponible, no interrumpe
    la ejecución del experimento.
    """

    if not url:
        return

    evento = {
        "tipo": tipo,
        "cache": resultado.cache,
        "latencia_ms": resultado.latencia_ms,
        "latencia_cache_ms": resultado.latencia_cache_ms,
        "ok": resultado.ok,
        "status": resultado.status,
        "n_resultados": resultado.n_resultados,
        "error": resultado.error
    }

    try:
        requests.post(
            url,
            json=evento,
            timeout=2
        )

    except requests.RequestException:
        pass