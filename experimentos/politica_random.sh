#!/bin/bash

echo "================================="
echo "Experimento Politica Random"
echo "================================="


REDIS_MEMORY=2mb REDIS_POLICY=allkeys-random docker compose up -d --force-recreate redis

sleep 2


docker compose exec redis redis-cli FLUSHALL

curl http://localhost:9000/reset


REDIS_MEMORY=2mb REDIS_POLICY=allkeys-random docker compose run --rm \
-e EXPERIMENTO_CACHE=true \
-e CACHE_PADDING_BYTES=5000 \
-e DISTRIBUCION=uniforme \
-e N_CONSULTAS=10000 \
-e SEED=42 \
generador


curl http://localhost:9000/resumen \
> data/resumen_politica_random.json


docker compose exec redis redis-cli INFO stats \
| grep evicted \
> data/evicted_politica_random.txt


docker compose exec redis redis-cli DBSIZE \
> data/dbsize_politica_random.txt


docker compose exec redis redis-cli INFO memory \
| grep used_memory_human \
> data/memory_politica_random.txt


echo "Experimento Random terminado"


if [ -f data/resumen_politica_lru.json ] && \
   [ -f data/resumen_politica_random.json ]; then

    echo "Resultados completos. Generando gráficos..."

    python3 graficos/generar_graficos.py

else

    echo "Falta ejecutar la otra política."

fi