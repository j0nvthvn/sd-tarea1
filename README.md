# Tarea 1 SD - All you can Cache

Sistema distribuido de caché aplicado a consultas deportivas sobre datos de fútbol chileno obtenidos desde Soccerway.

El objetivo del proyecto es implementar y evaluar una arquitectura distribuida utilizando un sistema de caché basado en Redis, analizando su impacto mediante diferentes patrones de generación de tráfico, tamaños de memoria y políticas de reemplazo.

---

# Grupo 2

## Integrantes

- Felipe Bustos López
- Jonathan Flores Torres

---

# Arquitectura del sistema

La arquitectura está compuesta por los siguientes servicios:

```text
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
- Política de reemplazo configurable:
  - `allkeys-lru`.
  - `allkeys-random`.
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

## Levantar sistema completo

```bash
docker compose up --build
```

Esto inicia los servicios:

- Redis.
- Scraper.
- Cache.
- Métricas.
- Generador.

---

# Configuración del generador

El comportamiento del generador puede modificarse mediante variables de entorno.

| Variable | Descripción |
|----------|-------------|
| DISTRIBUCION | Distribución de consultas: uniforme o zipf |
| ZIPF_S | Parámetro distribución Zipf |
| LLEGADAS | Modelo de llegada: poisson o constante |
| N_CONSULTAS | Cantidad total de consultas |
| TASA_ARRIBO | Tasa de llegada de consultas |
| SEED | Semilla para reproducibilidad |
| CSV_SALIDA | Archivo de salida |
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

---

# Comparación de distribuciones

Se evaluó el comportamiento del sistema utilizando dos patrones de generación de tráfico:

- Distribución Zipf.
- Distribución Uniforme.

## Configuración

- 1000 consultas.
- Llegadas Poisson.
- Tasa de llegada: 20 consultas/s.
- Seed: 42.
- Caché inicialmente vacía.

## Resultados

| Métrica | Zipf | Uniforme |
|---------|------|----------|
| Consultas | 1000 | 1000 |
| Hits | 886 | 834 |
| Misses | 114 | 166 |
| Errores | 0 | 0 |
| Hit Rate | 88.60% | 83.40% |

## Análisis

La distribución Zipf obtiene un mayor hit rate debido a que concentra las consultas en un conjunto reducido de claves populares.

Esto permite una mayor reutilización de información almacenada en caché, mientras que la distribución uniforme presenta accesos más dispersos.

---

# Experimentos de tamaño de caché

Se evaluó el impacto de aumentar la memoria disponible en Redis.

## Configuración

- Política Redis: `allkeys-lru`.
- Distribución: Uniforme.
- Consultas: 10000.
- Seed: 42.
- Padding artificial: 5000 bytes.

Tamaños evaluados:

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

Al aumentar la memoria disponible disminuyen las expulsiones realizadas por Redis.

Sin embargo, el hit rate presenta cambios mínimos debido al patrón uniforme y al amplio espacio de claves generado.

El aumento de memoria permite almacenar más información, pero no necesariamente aumenta la reutilización cuando las consultas están distribuidas uniformemente.

---

# Evaluación de políticas de reemplazo

Se compararon dos políticas de reemplazo de Redis:

- `allkeys-lru`.
- `allkeys-random`.

## Configuración

- Caché: 2 MB.
- Consultas: 10000.
- Distribución: Uniforme.
- Modelo de llegada: Poisson.
- Seed: 42.
- Padding artificial: 5000 bytes.
- Caché inicialmente vacía.

## Resultados

| Métrica | LRU | Random |
|---------|-----|--------|
| Consultas | 10000 | 10000 |
| Hits | 2014 | 2010 |
| Misses | 7986 | 7990 |
| Hit Rate | 20.14% | 20.10% |
| Latencia promedio | 6.476 ms | 6.474 ms |
| Evicciones | 7429 | 7396 |

## Análisis

Ambas políticas presentan resultados similares debido a la ausencia de una fuerte localidad temporal en las consultas.

Aunque LRU intenta conservar las claves utilizadas recientemente, bajo un patrón uniforme no logra una ventaja significativa frente a Random.

La diferencia de hit rate fue menor al 0.05%, mostrando que bajo este escenario la política de reemplazo tiene un impacto reducido.

---

# Scripts de experimentación

Todos los experimentos fueron automatizados mediante scripts Bash ubicados en:

```text
experimentos/
```

---

# Experimentos de distribución

Comparan el comportamiento del sistema utilizando diferentes patrones de popularidad.

## Scripts

```bash
./experimentos/zipf.sh

./experimentos/uniforme.sh
```

## Configuración

- Consultas: 1000.
- Llegadas: Poisson.
- Tasa de llegada: 20 consultas/s.
- Seed: 42.
- Caché inicialmente vacía.

Resultados:

```text
data/

├── resumen_zipf.json
├── resumen_uniforme.json
├── resumen_zipf_tipos.json
├── resumen_uniforme_tipos.json
├── generador_zipf.csv
└── generador_uniforme.csv
```

---

# Experimentos de tamaño de caché

## Scripts

```bash
./experimentos/cache_2mb.sh

./experimentos/cache_5mb.sh

./experimentos/cache_10mb.sh
```

Resultados:

```text
data/

├── resumen_cache_2mb.json
├── resumen_cache_5mb.json
├── resumen_cache_10mb.json
├── evicted_cache_2mb.txt
├── evicted_cache_5mb.txt
└── evicted_cache_10mb.txt
```

---

# Experimentos de políticas de reemplazo

## Scripts

```bash
./experimentos/politica_lru.sh

./experimentos/politica_random.sh
```

Resultados:

```text
data/

├── resumen_politica_lru.json
├── resumen_politica_random.json
├── evicted_politica_lru.txt
├── evicted_politica_random.txt
├── dbsize_politica_lru.txt
└── dbsize_politica_random.txt
```

---

# Métricas generadas

El sistema registra:

- Tipo de consulta.
- Parámetros utilizados.
- Estado del caché:
  - Hit.
  - Miss.
  - Error.
- Latencia.
- Cantidad de resultados.
- Evicciones Redis.
- Uso de memoria Redis.

---

# Generación de gráficos

Los gráficos se generan mediante:

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
- Hit rate según política de reemplazo.
- Evicciones según política de reemplazo.
- Latencia según política de reemplazo.

Archivos:

```text
graficos/

├── hit_rate_distribucion.png
├── hit_rate_por_tipo.png
├── latencia_hit_miss.png
├── hit_rate_cache.png
├── evictions_cache.png
├── latencia_cache.png
├── hit_rate_politicas.png
├── evictions_politicas.png
└── latencia_politicas.png
```

---

# Estructura del proyecto

```text
sd-tarea1/

├── cache/
├── scraper/
├── generador/
├── metricas/
├── experimentos/
│   ├── zipf.sh
│   ├── uniforme.sh
│   ├── cache_2mb.sh
│   ├── cache_5mb.sh
│   ├── cache_10mb.sh
│   ├── politica_lru.sh
│   └── politica_random.sh
├── graficos/
├── data/
├── docker-compose.yml
└── README.md
```

---

# Repositorio

GitLab Grupo 2:

https://giteit.udp.cl/CIT2011/2026-2/seccion-2/grupo-2