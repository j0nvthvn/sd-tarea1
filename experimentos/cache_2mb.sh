#!/bin/bash

echo "================================="
echo "Experimento Cache 2MB"
echo "================================="

REDIS_MEMORY=2mb docker compose up -d --force-recreate redis

sleep 2

docker compose exec redis redis-cli FLUSHALL

curl http://localhost:9000/reset

REDIS_MEMORY=2mb docker compose run --rm \
-e EXPERIMENTO_CACHE=true \
-e CACHE_PADDING_BYTES=5000 \
-e DISTRIBUCION=uniforme \
-e N_CONSULTAS=10000 \
-e SEED=42 \
generador

echo "Guardando resultados..."

curl http://localhost:9000/resumen \
> data/resumen_cache_2mb.json

docker compose exec redis redis-cli INFO stats \
| grep evicted \
> data/evicted_cache_2mb.txt

docker compose exec redis redis-cli DBSIZE \
> data/dbsize_cache_2mb.txt

docker compose exec redis redis-cli CONFIG GET maxmemory \
> data/memory_cache_2mb.txt

echo "Verificando datos para gráficos..."

if [ -f data/resumen_cache_2mb.json ] && \
   [ -f data/resumen_cache_5mb.json ] && \
   [ -f data/resumen_cache_10mb.json ] && \
   [ -f data/evicted_cache_2mb.txt ] && \
   [ -f data/evicted_cache_5mb.txt ] && \
   [ -f data/evicted_cache_10mb.txt ]; then

    python3 graficos/generar_graficos.py

else

    echo "Faltan resultados de otros tamaños de caché."

fi

echo "Experimento Cache 2MB terminado"