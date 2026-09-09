import os
from dataclasses import dataclass
from distributions import seleccionar_uniforme

@dataclass
class Config:
    distribucion: str
    n_consultas: int
    tasa_arribo: float
    seed: int
    cache_url: str


def cargar_config() -> Config:
    
    distribucion = os.getenv("DISTRIBUCION", "uniforme").lower()
    n_consultas = int(os.getenv("N_CONSULTAS", "100"))
    tasa_arribo = float(os.getenv("TASA_ARRIBO", "5"))
    seed = int(os.getenv("SEED", "42"))
    cache_url = os.getenv("CACHE_URL", "http://cache:5000/consulta")

    if distribucion not in ("uniforme", "zipf"):
        raise ValueError(
            "DISTRIBUCION debe ser 'uniforme' o 'zipf'"
        )

    if n_consultas <= 0:
        raise ValueError(
            "N_CONSULTAS debe ser mayor que 0"
        )

    if tasa_arribo <= 0:
        raise ValueError(
            "TASA_ARRIBO debe ser mayor que 0"
        )

    return Config(
        distribucion=distribucion,
        n_consultas=n_consultas,
        tasa_arribo=tasa_arribo,
        seed=seed,
        cache_url=cache_url,
    )


def main():
    config = cargar_config()

    print("Configuración del generador")
    print(f"Distribución: {config.distribucion}")
    print(f"Número de consultas: {config.n_consultas}")
    print(f"Tasa de arribo: {config.tasa_arribo} consultas/s")
    print(f"Seed: {config.seed}")
    print(f"Cache URL: {config.cache_url}")
    print("\nConsultas generadas:")

    for _ in range(5):
        print(seleccionar_uniforme())

if __name__ == "__main__":
    main()