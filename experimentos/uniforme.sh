#!/bin/bash

echo "================================="
echo "Experimento Uniforme"
echo "================================="

curl http://localhost:9000/reset

docker compose exec redis redis-cli FLUSHALL

docker compose run --rm \
-e DISTRIBUCION=uniforme \
-e N_CONSULTAS=1000 \
-e TASA_ARRIBO=20 \
-e SEED=42 \
-e CSV_SALIDA=/app/data/uniforme_consultas.csv \
generador

echo "Guardando resumen..."

curl http://localhost:9000/resumen > data/resumen_uniforme.json
curl http://localhost:9000/resumen/tipos > data/resumen_uniforme_tipos.json

echo "Generando gráficos..."
python3 graficos/generar_graficos.py

echo "Experimento Uniforme terminado"