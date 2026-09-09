"""Generador de trafico del experimento de cache distribuido.

Emite N consultas hacia el servicio de cache siguiendo:
  - una distribucion de popularidad sobre las claves (uniforme o Zipf), y
  - un proceso de llegadas (Poisson o determinista) con tasa configurable,
registrando hit/miss y latencia de cada respuesta.
"""

import json
import os
import random
import time
from dataclasses import dataclass, asdict

from client import enviar_consulta, esperar_servicio
from distributions import DISTRIBUCIONES, Selector
from metrics import Acumulador
from queries import TIPOS_CONSULTA, espacio_de_claves, generar_consulta


LLEGADAS = ("poisson", "constante")


@dataclass
class Config:
    distribucion: str
    zipf_s: float
    llegadas: str
    n_consultas: int
    tasa_arribo: float
    seed: int
    cache_url: str
    health_url: str
    timeout: float
    csv_salida: str


def _entero(nombre, defecto):
    try:
        return int(os.getenv(nombre, defecto))
    except ValueError:
        raise ValueError(f"{nombre} debe ser un numero entero") from None


def _decimal(nombre, defecto):
    try:
        return float(os.getenv(nombre, defecto))
    except ValueError:
        raise ValueError(f"{nombre} debe ser un numero") from None


def cargar_config() -> Config:
    config = Config(
        distribucion=os.getenv("DISTRIBUCION", "uniforme").strip().lower(),
        zipf_s=_decimal("ZIPF_S", "1.0"),
        llegadas=os.getenv("LLEGADAS", "poisson").strip().lower(),
        n_consultas=_entero("N_CONSULTAS", "100"),
        tasa_arribo=_decimal("TASA_ARRIBO", "5"),
        seed=_entero("SEED", "42"),
        cache_url=os.getenv("CACHE_URL", "http://cache:5000/consulta"),
        health_url=os.getenv("HEALTH_URL", "http://scraper:5000/health"),
        timeout=_decimal("TIMEOUT", "30"),
        csv_salida=os.getenv("CSV_SALIDA", "/app/data/generador.csv"),
    )

    if config.distribucion not in DISTRIBUCIONES:
        raise ValueError(f"DISTRIBUCION debe ser una de {DISTRIBUCIONES}")
    if config.llegadas not in LLEGADAS:
        raise ValueError(f"LLEGADAS debe ser una de {LLEGADAS}")
    if config.zipf_s < 0:
        raise ValueError("ZIPF_S no puede ser negativo")
    if config.n_consultas <= 0:
        raise ValueError("N_CONSULTAS debe ser mayor que 0")
    if config.tasa_arribo <= 0:
        raise ValueError("TASA_ARRIBO debe ser mayor que 0")
    if config.timeout <= 0:
        raise ValueError("TIMEOUT debe ser mayor que 0")

    return config


def imprimir_config(config: Config):
    print("Configuracion del generador")
    for clave, valor in asdict(config).items():
        print(f"  {clave:<14}: {valor}")
    print(f"  espacio_claves: {json.dumps(espacio_de_claves())}")


def main():
    config = cargar_config()
    imprimir_config(config)

    # Mismo seed => misma secuencia de consultas y mismos tiempos entre arribos,
    # de modo que dos corridas con distinta distribucion sean comparables.
    rng = random.Random(config.seed)
    selector = Selector(config.distribucion, s=config.zipf_s, rng=rng)
    metricas = Acumulador()

    if config.health_url:
        print(f"\nEsperando a que el backend responda en {config.health_url} ...")
        if esperar_servicio(config.health_url):
            print("Backend listo.")
        else:
            print("Aviso: el backend no respondio a tiempo; se continua igual.")

    print(f"\nEnviando {config.n_consultas} consultas...")
    inicio = time.perf_counter()

    for i in range(1, config.n_consultas + 1):
        tipo = selector.elegir(TIPOS_CONSULTA)
        consulta = generar_consulta(tipo, selector)
        resultado = enviar_consulta(config.cache_url, consulta, timeout=config.timeout)
        metricas.registrar(i, tipo, consulta, resultado)

        if i <= 5 or i % 100 == 0:
            estado = resultado.cache if resultado.ok else f"ERROR {resultado.error}"
            print(
                f"  [{i:>5}/{config.n_consultas}] {tipo} {consulta} "
                f"-> {estado} ({resultado.latencia_ms:.1f} ms, "
                f"n={resultado.n_resultados})"
            )

        if i < config.n_consultas:
            if config.llegadas == "poisson":
                time.sleep(rng.expovariate(config.tasa_arribo))
            else:
                time.sleep(1 / config.tasa_arribo)

    duracion = time.perf_counter() - inicio
    metricas.imprimir()
    print(
        f"Duracion total: {duracion:.1f} s "
        f"({config.n_consultas / duracion:.2f} consultas/s efectivas)"
    )

    try:
        ruta = metricas.escribir_csv(config.csv_salida)
        if ruta:
            print(f"Detalle por consulta escrito en {ruta}")
    except OSError as error:
        print(f"Aviso: no se pudo escribir el CSV ({error})")


if __name__ == "__main__":
    main()
