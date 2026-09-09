"""Selectores de popularidad.

La distribucion no se aplica solo al *tipo* de consulta sino al objeto
consultado (equipo, par de equipos, ventana de fechas). Es la popularidad de
las claves la que determina el comportamiento del cache: si el equipo se
eligiera siempre de forma uniforme, los modos "uniforme" y "zipf" producirian
practicamente el mismo hit rate y la comparacion no mediria nada.

- uniforme: todos los elementos equiprobables.
- zipf:     p(i) proporcional a 1/i^s sobre el ranking del elemento (i = 1..n).
            s es configurable; s=0 degenera en uniforme y s>1 concentra mas.
"""

import random


DISTRIBUCIONES = ("uniforme", "zipf")


def pesos_uniformes(n):
    return [1.0] * n


def pesos_zipf(n, s=1.0):
    return [1.0 / (i ** s) for i in range(1, n + 1)]


class Selector:
    """Elige elementos de una lista segun la distribucion configurada.

    El ranking es la posicion del elemento en la lista, de modo que el orden en
    que se declaran los equipos define cuales son los "populares".
    """

    def __init__(self, distribucion="uniforme", s=1.0, rng=None):
        if distribucion not in DISTRIBUCIONES:
            raise ValueError(
                f"distribucion debe ser una de {DISTRIBUCIONES}, no {distribucion!r}"
            )
        if s < 0:
            raise ValueError("el exponente s de Zipf no puede ser negativo")

        self.distribucion = distribucion
        self.s = s
        self.rng = rng or random
        self._cache_pesos = {}

    def pesos(self, n):
        if n not in self._cache_pesos:
            if self.distribucion == "zipf":
                self._cache_pesos[n] = pesos_zipf(n, self.s)
            else:
                self._cache_pesos[n] = pesos_uniformes(n)
        return self._cache_pesos[n]

    def elegir(self, items):
        """Un elemento de items segun la distribucion."""
        if not items:
            raise ValueError("no se puede elegir de una lista vacia")
        return self.rng.choices(items, weights=self.pesos(len(items)), k=1)[0]

    def elegir_par(self, items):
        """Dos elementos distintos de items, ambos segun la distribucion.

        El orden se normaliza para que (a, b) y (b, a) sean la misma consulta,
        igual que hace cache_key() en el servicio de cache.
        """
        if len(items) < 2:
            raise ValueError("se necesitan al menos dos elementos")
        a = self.elegir(items)
        b = self.elegir(items)
        while b == a:
            b = self.elegir(items)
        return tuple(sorted((a, b)))
