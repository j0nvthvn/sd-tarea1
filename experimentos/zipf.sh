#!/bin/bash

echo "================================="
echo "Experimento Zipf"
echo "================================="

curl http://localhost:9000/reset

docker compose exec redis redis-cli FLUSHALL

docker compose run --rm \
-e DISTRIBUCION=zipf \
-e ZIPF_S=1.0 \
-e N_CONSULTAS=1000 \
-e TASA_ARRIBO=20 \
-e SEED=42 \
-e CSV_SALIDA=/app/data/zipf_consultas.csv \
generador

echo "Guardando resumen..."

curl http://localhost:9000/resumen > data/resumen_zipf.json
curl http://localhost:9000/resumen/tipos > data/resumen_zipf_tipos.json

echo "Generando gráficos..."
python3 graficos/generar_graficos.py

echo "Experimento Zipf terminado"