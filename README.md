# Tarea 1 SD - All you can Cache

Sistema distribuido de caché aplicado a consultas deportivas sobre datos de fútbol chileno obtenidos desde Soccerway.

El objetivo del proyecto es implementar y evaluar una arquitectura distribuida utilizando un sistema de caché basado en Redis, analizando su impacto mediante diferentes patrones de generación de tráfico y métricas de rendimiento.

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
       Archivos CSV
```

---

# Componentes

## Generador de tráfico

Servicio encargado de generar consultas hacia el sistema distribuido.

Características:

- Generación de consultas Q1-Q5.
- Distribución de popularidad:
  - Uniforme.
  - Zipf.
- Modelos de llegada:
  - Poisson.
  - Constante.
- Seed configurable para reproducibilidad.
- Registro de métricas por consulta.
- Generación de archivos CSV para análisis.

---

## Servicio Cache

Servicio desarrollado con Flask encargado de administrar las consultas.

Funciones principales:

- Recibir consultas desde el generador.
- Revisar existencia de datos en Redis.
- Consultar al scraper cuando ocurre un cache miss.
- Almacenar respuestas utilizando TTL.
- Medir latencia de respuesta.

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
- Política de reemplazo LRU.

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
| TASA_ARRIBO | Tasa de llegada de consultas por segundo |
| SEED | Semilla para reproducibilidad |
| CSV_SALIDA | Archivo donde se almacenan los resultados |

Ejemplo de ejecución:

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

Se realizaron experimentos comparando dos distribuciones de generación de tráfico:

- Distribución Zipf.
- Distribución Uniforme.

Condiciones utilizadas:

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
| Throughput | 16.98 consultas/s | 16.39 consultas/s |

Los resultados muestran que la distribución Zipf obtiene un mayor porcentaje de aciertos debido a una mayor concentración de consultas sobre claves populares.

---

# Métricas generadas

El generador registra información de cada consulta realizada:

- Tipo de consulta.
- Parámetros utilizados.
- Estado del caché:
  - Hit.
  - Miss.
  - Error.
- Latencia de respuesta.
- Latencia del caché.
- Cantidad de resultados obtenidos.
- Errores asociados.

Los resultados son almacenados en archivos CSV:

```
data/
├── generador_zipf.csv
└── generador_uniforme.csv
```

---

# Estructura del proyecto

```
sd-tarea1/

├── cache/
├── scraper/
├── generador/
├── metricas/
├── data/
├── docker-compose.yml
└── README.md
```

---

# Repositorio

GitLab Grupo 2:

<https://giteit.udp.cl/CIT2011/2026-2/seccion-2/grupo-2>