# Tarea 1 SD - All you can Cache

Sistema distribuido de caché aplicado a consultas deportivas sobre datos de fútbol chileno obtenidos desde Soccerway.

El objetivo del proyecto es implementar y evaluar una arquitectura distribuida utilizando un sistema de caché basado en Redis, analizando su impacto mediante diferentes patrones de generación de tráfico, tamaños de memoria y métricas de rendimiento.

---

# Grupo 2

## Integrantes

- Felipe Bustos López
- Jonathan Flores Torres

---

# Arquitectura del sistema

La arquitectura está compuesta por los siguientes servicios:

```
                    +-------------+
                    |    Redis    |
                    | Cache Store |
                    +-------------+
                          ^
                          |
                          |
Generador de tráfico ---> Cache ---> Scraper
          |
          |
          v
 Métricas experimentales
          |
          v
 Archivos de resultados
```

---

# Componentes

## Generador de tráfico

Servicio encargado de generar consultas hacia el sistema distribuido.

Características:

- Generación de consultas Q1-Q5.
- Distribuciones de popularidad:
  - Uniforme.
  - Zipf.
- Modelos de llegada:
  - Poisson.
  - Constante.
- Seed configurable para reproducibilidad.
- Registro de métricas por consulta.
- Generación de archivos CSV para análisis.
- Soporte para experimentos controlados de caché.

---

## Servicio Cache

Servicio desarrollado con Flask encargado de administrar las consultas.

Funciones principales:

- Recibir consultas desde el generador.
- Generar claves determinísticas para Redis.
- Revisar existencia de datos almacenados.
- Consultar al scraper cuando ocurre un cache miss.
- Almacenar respuestas utilizando TTL.
- Medir latencia de respuesta.
- Incorporar padding artificial para evaluar presión de memoria.

---

## Scraper

Servicio encargado de obtener información deportiva desde Soccerway.

Características:

- Extracción de datos de fútbol chileno.
- Soporte para scraping real.
- Uso de snapshot offline para experimentos reproducibles.

---

## Redis

Sistema utilizado como almacenamiento de caché.

Configuración:

- Redis 7 Alpine.
- TTL configurable.
- Política de reemplazo LRU (`allkeys-lru`).
- Tamaño de memoria configurable mediante `REDIS_MEMORY`.

---

# Consultas disponibles

El sistema implementa cinco tipos de consultas:

| Consulta | Descripción |
|----------|-------------|
| Q1 | Próximos partidos de un equipo |
| Q2 | Últimos partidos de un equipo |
| Q3 | Historial de enfrentamientos entre dos equipos |
| Q4 | Partidos dentro de un rango de fechas |
| Q5 | Tabla general del campeonato |

---

# Despliegue

## Requisitos

- Docker
- Docker Compose

---

## Levantar el sistema completo

```bash
docker compose up --build
```

Esto inicia los servicios:

- Redis
- Scraper
- Cache
- Métricas
- Generador

---

# Configuración del generador

El comportamiento del generador puede modificarse mediante variables de entorno.

| Variable | Descripción |
|----------|-------------|
| DISTRIBUCION | Distribución de consultas: uniforme o zipf |
| ZIPF_S | Parámetro de la distribución Zipf |
| LLEGADAS | Modelo de llegada: poisson o constante |
| N_CONSULTAS | Cantidad total de consultas |
| TASA_ARRIBO | Tasa de llegada de consultas |
| SEED | Semilla para reproducibilidad |
| CSV_SALIDA | Archivo donde se almacenan resultados |
| CACHE_PADDING_BYTES | Tamaño artificial agregado a respuestas |

Ejemplo:

```bash
docker compose run --rm \
-e DISTRIBUCION=zipf \
-e ZIPF_S=1.0 \
-e LLEGADAS=poisson \
-e N_CONSULTAS=1000 \
-e TASA_ARRIBO=20 \
-e SEED=42 \
-e CSV_SALIDA=/app/data/generador_zipf.csv \
generador
```

---

# Experimentos realizados

## Comparación de distribuciones

Se evaluó el comportamiento del sistema utilizando dos patrones de generación de tráfico:

- Distribución Zipf.
- Distribución Uniforme.

Condiciones:

- 1000 consultas.
- Llegadas Poisson.
- Tasa de llegada: 20 consultas/s.
- Seed: 42.
- Caché inicialmente vacía.

## Resultados principales

| Métrica | Zipf | Uniforme |
|---------|------|----------|
| Consultas | 1000 | 1000 |
| Hits | 886 | 834 |
| Misses | 114 | 166 |
| Errores | 0 | 0 |
| Hit Rate | 88.60% | 83.40% |

Los resultados muestran que Zipf obtiene un mayor hit rate debido a la concentración de consultas sobre claves populares, aumentando la reutilización de información almacenada en caché.

---

# Experimentos de tamaño de caché

Se evaluó el impacto de aumentar la memoria disponible en Redis utilizando:

- Redis con política `allkeys-lru`.
- Distribución uniforme.
- 10000 consultas.
- Seed fija.
- Padding artificial de respuestas.
- Tamaños de caché:
  - 2 MB.
  - 5 MB.
  - 10 MB.

## Resultados

| Memoria caché | Hit Rate | Evicciones |
|--------------|----------|------------|
| 2 MB | 20.14% | 7920 |
| 5 MB | 20.17% | 5244 |
| 10 MB | 20.18% | 0 |

## Análisis

El aumento del tamaño de caché reduce significativamente las expulsiones realizadas por Redis mediante la política LRU.

Sin embargo, el hit rate presenta variaciones mínimas debido al patrón uniforme de consultas y al amplio espacio de claves disponible. Bajo este escenario, aumentar la memoria permite almacenar más información, pero no garantiza una mayor reutilización de consultas.

---

# Métricas generadas

El sistema registra información de cada consulta:

- Tipo de consulta.
- Parámetros utilizados.
- Estado del caché:
  - Hit.
  - Miss.
  - Error.
- Latencia de respuesta.
- Cantidad de resultados obtenidos.
- Información de evicciones Redis.
- Uso de memoria Redis.

Resultados almacenados:

```
data/

├── generador_zipf.csv
├── generador_uniforme.csv
├── resumen_cache_2mb.json
├── resumen_cache_5mb.json
├── resumen_cache_10mb.json
├── evicted_cache_2mb.txt
├── evicted_cache_5mb.txt
└── evicted_cache_10mb.txt
```

---

# Generación de gráficos

Los gráficos experimentales se generan automáticamente mediante:

```bash
python3 graficos/generar_graficos.py
```

Se generan:

- Hit rate según distribución.
- Hit rate por tipo de consulta.
- Latencia hit/miss.
- Hit rate según tamaño de caché.
- Evicciones según tamaño de caché.
- Latencia según tamaño de caché.

Archivos generados:

```
graficos/

├── hit_rate_distribucion.png
├── hit_rate_por_tipo.png
├── latencia_hit_miss.png
├── hit_rate_cache.png
├── evictions_cache.png
└── latencia_cache.png
```

---

# Experimentos de caché

Los experimentos de memoria pueden ejecutarse mediante:

```bash
./experimentos/cache_2mb.sh

./experimentos/cache_5mb.sh

./experimentos/cache_10mb.sh
```

Cada script:

1. Configura el tamaño de memoria Redis.
2. Limpia la caché.
3. Ejecuta el generador.
4. Guarda métricas del experimento.
5. Genera gráficos cuando están disponibles todos los resultados.

---

# Estructura del proyecto

```
sd-tarea1/

├── cache/
├── scraper/
├── generador/
├── metricas/
├── experimentos/
├── graficos/
├── data/
├── docker-compose.yml
└── README.md
```

---

# Repositorio

GitLab Grupo 2:

https://giteit.udp.cl/CIT2011/2026-2/seccion-2/grupo-2