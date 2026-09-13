#!/bin/bash

echo "================================="
echo "Experimento TTL 30 segundos"
echo "================================="

docker compose down

REDIS_MEMORY=2mb TTL_SECONDS=30 docker compose up -d redis cache metricas scraper

sleep 3

docker compose exec redis redis-cli FLUSHALL

curl http://localhost:9000/reset


TTL_SECONDS=30 docker compose run --rm \
-e EXPERIMENTO_CACHE=true \
-e CACHE_PADDING_BYTES=5000 \
-e DISTRIBUCION=uniforme \
-e N_CONSULTAS=10000 \
-e SEED=42 \
generador


curl http://localhost:9000/resumen \
> data/resumen_ttl_30s.json


docker compose exec redis redis-cli INFO stats | grep expired \
> data/expired_ttl_30s.txt


docker compose exec redis redis-cli INFO stats | grep evicted \
> data/evicted_ttl_30s.txt


docker compose exec redis redis-cli DBSIZE \
> data/dbsize_ttl_30s.txt


docker compose exec redis redis-cli INFO memory | grep used_memory_human \
> data/memory_ttl_30s.txt


echo "Generando gráficos..."

python3 graficos/generar_graficos.py || echo "No se pudieron generar todos los gráficos, faltan datos"


echo "================================="
echo "Experimento TTL 30s terminado"
echo "================================="