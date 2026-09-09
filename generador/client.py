"""Cliente HTTP hacia el servicio de cache."""

import time
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class Resultado:
    """Resultado de una consulta, con lo necesario para medir el cache.

    ok           : la consulta se respondio correctamente (HTTP 200 y JSON valido).
    cache        : "hit", "miss" o "bypass" segun lo informa el servicio de cache.
    latencia_ms  : tiempo total medido por el cliente (incluye red).
    latencia_cache_ms: tiempo informado por el servicio de cache, si viene.
    n_resultados : cantidad de partidos devueltos, util para detectar respuestas
                   vacias que igualmente se cachean.
    """

    ok: bool
    status: Optional[int]
    cache: Optional[str]
    latencia_ms: float
    latencia_cache_ms: Optional[float]
    n_resultados: Optional[int]
    error: Optional[str]


def _contar_resultados(data) -> Optional[int]:
    if not isinstance(data, dict):
        return None
    if isinstance(data.get("n"), int):
        return data["n"]
    for campo in ("partidos", "tabla"):
        if isinstance(data.get(campo), list):
            return len(data[campo])
    return None


def enviar_consulta(url: str, consulta: dict, timeout: float = 30.0) -> Resultado:
    """Envia una consulta al servicio de cache y mide su latencia.

    Nunca levanta excepciones: los fallos se devuelven como Resultado(ok=False)
    para que queden contabilizados aparte en las metricas en vez de confundirse
    con respuestas validas.
    """
    inicio = time.perf_counter()
    status = None
    try:
        respuesta = requests.get(url, params=consulta, timeout=timeout)
        status = respuesta.status_code
        respuesta.raise_for_status()
        cuerpo = respuesta.json()
    except requests.RequestException as error:
        # Incluye timeouts, errores de conexion, HTTP 4xx/5xx y JSON invalido
        # (requests.exceptions.JSONDecodeError hereda de RequestException).
        return Resultado(
            ok=False,
            status=status,
            cache=None,
            latencia_ms=(time.perf_counter() - inicio) * 1000,
            latencia_cache_ms=None,
            n_resultados=None,
            error=f"{type(error).__name__}: {error}",
        )

    latencia_ms = (time.perf_counter() - inicio) * 1000

    if not isinstance(cuerpo, dict):
        return Resultado(
            ok=False,
            status=respuesta.status_code,
            cache=None,
            latencia_ms=latencia_ms,
            latencia_cache_ms=None,
            n_resultados=None,
            error="respuesta con formato inesperado",
        )

    return Resultado(
        ok=True,
        status=respuesta.status_code,
        cache=cuerpo.get("cache"),
        latencia_ms=latencia_ms,
        latencia_cache_ms=cuerpo.get("latencia_ms"),
        n_resultados=_contar_resultados(cuerpo.get("data")),
        error=None,
    )


def esperar_servicio(url: str, intentos: int = 60, espera: float = 2.0) -> bool:
    """Espera a que un servicio responda antes de empezar el experimento.

    docker compose depends_on solo garantiza el orden de arranque, no que el
    scraper haya terminado de cargar su snapshot. Sin esta espera las primeras
    consultas fallan y ensucian las metricas.
    """
    for intento in range(1, intentos + 1):
        try:
            respuesta = requests.get(url, timeout=5)
            if respuesta.status_code == 200:
                return True
        except requests.RequestException:
            pass
        if intento < intentos:
            time.sleep(espera)
    return False
