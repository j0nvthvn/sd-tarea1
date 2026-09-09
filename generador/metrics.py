"""Acumulacion de metricas del experimento.

El servicio de cache informa en cada respuesta si fue hit o miss y cuanto
tardo. El generador es quien tiene que registrarlo: sin esto no queda ningun
dato con el que construir las curvas del informe.
"""

import csv
import os
from collections import Counter, defaultdict


def _percentil(valores_ordenados, p):
    if not valores_ordenados:
        return None
    if len(valores_ordenados) == 1:
        return valores_ordenados[0]
    posicion = (len(valores_ordenados) - 1) * p / 100
    inferior = int(posicion)
    superior = min(inferior + 1, len(valores_ordenados) - 1)
    peso = posicion - inferior
    return (
        valores_ordenados[inferior] * (1 - peso) + valores_ordenados[superior] * peso
    )


class Acumulador:
    def __init__(self):
        self.filas = []
        self.por_tipo = defaultdict(Counter)
        self.latencias_por_cache = defaultdict(list)
        self.total = 0
        self.errores = 0
        self.vacias = 0

    def registrar(self, indice, tipo, consulta, resultado):
        self.total += 1
        estado = resultado.cache if resultado.ok else "error"

        self.por_tipo[tipo][estado] += 1
        if not resultado.ok:
            self.errores += 1
        else:
            self.latencias_por_cache[estado].append(resultado.latencia_ms)
            if resultado.n_resultados == 0:
                self.vacias += 1

        self.filas.append(
            {
                "i": indice,
                "tipo": tipo,
                "consulta": ";".join(
                    f"{k}={v}" for k, v in sorted(consulta.items()) if k != "tipo"
                ),
                "estado": estado,
                "status_http": resultado.status,
                "latencia_ms": round(resultado.latencia_ms, 3),
                "latencia_cache_ms": (
                    round(resultado.latencia_cache_ms, 3)
                    if resultado.latencia_cache_ms is not None
                    else ""
                ),
                "n_resultados": (
                    resultado.n_resultados if resultado.n_resultados is not None else ""
                ),
                "error": resultado.error or "",
            }
        )

    @property
    def hits(self):
        return sum(c["hit"] for c in self.por_tipo.values())

    @property
    def misses(self):
        return sum(c["miss"] for c in self.por_tipo.values())

    def hit_rate(self):
        utiles = self.hits + self.misses
        return (self.hits / utiles) if utiles else 0.0

    def latencias(self, estado):
        return sorted(self.latencias_por_cache.get(estado, []))

    def resumen(self):
        resumen = {
            "total": self.total,
            "hits": self.hits,
            "misses": self.misses,
            "errores": self.errores,
            "respuestas_vacias": self.vacias,
            "hit_rate": self.hit_rate(),
        }
        for estado in ("hit", "miss"):
            valores = self.latencias(estado)
            resumen[f"latencia_{estado}"] = {
                "n": len(valores),
                "media_ms": (sum(valores) / len(valores)) if valores else None,
                "p50_ms": _percentil(valores, 50),
                "p95_ms": _percentil(valores, 95),
                "p99_ms": _percentil(valores, 99),
            }
        return resumen

    def escribir_csv(self, ruta):
        if not ruta:
            return None
        carpeta = os.path.dirname(ruta)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        with open(ruta, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(self.filas[0].keys()))
            escritor.writeheader()
            escritor.writerows(self.filas)
        return ruta

    def imprimir(self):
        r = self.resumen()
        print("\n" + "=" * 52)
        print("RESUMEN DEL EXPERIMENTO")
        print("=" * 52)
        print(f"Consultas enviadas : {r['total']}")
        print(f"Hits               : {r['hits']}")
        print(f"Misses             : {r['misses']}")
        print(f"Errores            : {r['errores']}")
        print(f"Respuestas vacias  : {r['respuestas_vacias']}")
        print(f"Hit rate           : {r['hit_rate']:.2%}")

        for estado in ("hit", "miss"):
            datos = r[f"latencia_{estado}"]
            if datos["n"]:
                print(
                    f"Latencia {estado:<5} (n={datos['n']:>4}): "
                    f"media {datos['media_ms']:.2f} ms | "
                    f"p50 {datos['p50_ms']:.2f} | "
                    f"p95 {datos['p95_ms']:.2f} | "
                    f"p99 {datos['p99_ms']:.2f}"
                )

        print("-" * 52)
        print(f"{'Tipo':<6}{'hit':>8}{'miss':>8}{'error':>8}{'hit rate':>12}")
        for tipo in sorted(self.por_tipo):
            c = self.por_tipo[tipo]
            utiles = c["hit"] + c["miss"]
            tasa = (c["hit"] / utiles) if utiles else 0.0
            print(
                f"{tipo:<6}{c['hit']:>8}{c['miss']:>8}{c['error']:>8}{tasa:>11.2%}"
            )
        print("=" * 52)
