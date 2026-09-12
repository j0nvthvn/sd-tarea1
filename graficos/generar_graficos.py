import json
import os
import matplotlib.pyplot as plt

DATA_DIR = "data"
OUT_DIR = "graficos"


def cargar_json(nombre):
    ruta = os.path.join(DATA_DIR, nombre)
    if not os.path.exists(ruta):
        return None
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_grafico(nombre_archivo):
    os.makedirs(OUT_DIR, exist_ok=True)
    ruta = os.path.join(OUT_DIR, nombre_archivo)
    plt.tight_layout()
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Grafico generado: {ruta}")


def grafico_hit_rate_distribucion(zipf_resumen, uniforme_resumen):
    if not zipf_resumen or not uniforme_resumen:
        print("Faltan datos para hit_rate_distribucion.png")
        return

    etiquetas = ["Zipf", "Uniforme"]
    valores = [
        zipf_resumen["hit_rate"] * 100,
        uniforme_resumen["hit_rate"] * 100,
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(etiquetas, valores)
    plt.ylim(0, 100)
    plt.ylabel("Hit Rate (%)")
    plt.title("Comparacion del hit rate segun distribucion")

    for i, v in enumerate(valores):
        plt.text(i, v + 1, f"{v:.2f}%", ha="center")

    guardar_grafico("hit_rate_distribucion.png")


def grafico_latencia_hit_miss(zipf_resumen, uniforme_resumen):

    if not zipf_resumen or not uniforme_resumen:
        print("Faltan datos para latencia_hit_miss.png")
        return

    if (
        "latencia_hit" not in zipf_resumen
        or "latencia_miss" not in zipf_resumen
        or "latencia_hit" not in uniforme_resumen
        or "latencia_miss" not in uniforme_resumen
    ):
        print("Los JSON no tienen información de latencia hit/miss")
        return

    categorias = ["Hit", "Miss"]

    zipf_valores = [
        zipf_resumen["latencia_hit"]["media_ms"],
        zipf_resumen["latencia_miss"]["media_ms"]
    ]

    uniforme_valores = [
        uniforme_resumen["latencia_hit"]["media_ms"],
        uniforme_resumen["latencia_miss"]["media_ms"]
    ]

    x = range(len(categorias))
    ancho = 0.35

    plt.figure(figsize=(8, 5))

    plt.bar(
        [i - ancho/2 for i in x],
        zipf_valores,
        width=ancho,
        label="Zipf"
    )

    plt.bar(
        [i + ancho/2 for i in x],
        uniforme_valores,
        width=ancho,
        label="Uniforme"
    )

    plt.xticks(x, categorias)

    plt.ylabel("Latencia promedio (ms)")
    plt.title("Comparación de latencia entre Hit y Miss")
    plt.legend()

    for i, valor in enumerate(zipf_valores):
        plt.text(
            i - ancho/2,
            valor + 0.2,
            f"{valor:.2f}",
            ha="center"
        )

    for i, valor in enumerate(uniforme_valores):
        plt.text(
            i + ancho/2,
            valor + 0.2,
            f"{valor:.2f}",
            ha="center"
        )

    guardar_grafico("latencia_hit_miss.png")


def grafico_hit_rate_por_tipo(zipf_tipos, uniforme_tipos):
    if not zipf_tipos or not uniforme_tipos:
        print("Faltan datos para hit_rate_por_tipo.png")
        return

    tipos = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    zipf_valores = [zipf_tipos[t]["hit_rate"] * 100 for t in tipos]
    uniforme_valores = [uniforme_tipos[t]["hit_rate"] * 100 for t in tipos]

    x = list(range(len(tipos)))
    ancho = 0.35

    plt.figure(figsize=(10, 5))
    plt.bar([i - ancho / 2 for i in x], zipf_valores, width=ancho, label="Zipf")
    plt.bar([i + ancho / 2 for i in x], uniforme_valores, width=ancho, label="Uniforme")

    plt.xticks(x, tipos)
    plt.ylim(0, 100)
    plt.ylabel("Hit Rate (%)")
    plt.title("Hit rate por tipo de consulta")
    plt.legend()

    guardar_grafico("hit_rate_por_tipo.png")

def grafico_hit_rate_cache():

    memorias = ["2MB", "5MB", "10MB"]

    valores = []

    for memoria in ["2mb", "5mb", "10mb"]:
        datos = cargar_json(
            f"resumen_cache_{memoria}.json"
        )

        if datos:
            valores.append(
                datos["hit_rate"] * 100
            )
        else:
            print(
                f"Falta resumen_cache_{memoria}.json"
            )
            return


    plt.figure(figsize=(8,5))

    plt.bar(
        memorias,
        valores
    )

    plt.ylim(0,100)

    plt.ylabel("Hit Rate (%)")
    plt.xlabel("Memoria caché")

    plt.title(
        "Hit Rate según tamaño de caché"
    )


    for i,v in enumerate(valores):
        plt.text(
            i,
            v + 1,
            f"{v:.2f}%",
            ha="center"
        )


    guardar_grafico(
        "hit_rate_cache.png"
    )



def grafico_evictions_cache():

    memorias = ["2MB", "5MB", "10MB"]

    valores = []


    for memoria in ["2mb","5mb","10mb"]:

        ruta = os.path.join(
            DATA_DIR,
            f"evicted_cache_{memoria}.txt"
        )

        if not os.path.exists(ruta):
            print(
                f"Falta {ruta}"
            )
            return


        with open(ruta) as f:
            linea = f.readline()

        valores.append(
            int(linea.split(":")[1])
        )


    plt.figure(figsize=(8,5))


    plt.bar(
        memorias,
        valores
    )

    plt.ylabel(
        "Claves expulsadas"
    )

    plt.xlabel(
        "Memoria caché"
    )

    plt.title(
        "Evicciones Redis según tamaño de caché"
    )


    for i,v in enumerate(valores):
        plt.text(
            i,
            v + max(valores)*0.02,
            str(v),
            ha="center"
        )


    guardar_grafico(
        "evictions_cache.png"
    )



def grafico_latencia_cache():

    memorias = ["2MB", "5MB", "10MB"]

    valores = []

    for memoria in ["2mb", "5mb", "10mb"]:

        datos = cargar_json(
            f"resumen_cache_{memoria}.json"
        )

        if datos:
            valores.append(
                datos["latencia"]["media_ms"]
            )
        else:
            print(
                f"Falta resumen_cache_{memoria}.json"
            )
            return


    plt.figure(figsize=(8,5))

    plt.bar(
        memorias,
        valores
    )

    plt.ylabel(
        "Latencia media (ms)"
    )

    plt.xlabel(
        "Memoria caché"
    )

    plt.title(
        "Latencia promedio según tamaño de caché"
    )


    # Ajustar escala para visualizar diferencias pequeñas
    minimo = min(valores)

    plt.ylim(
        minimo - 0.2,
        max(valores) + 0.2
    )


    for i,v in enumerate(valores):

        plt.text(
            i,
            v + 0.03,
            f"{v:.3f} ms",
            ha="center"
        )


    plt.grid(
        axis="y"
    )


    guardar_grafico(
        "latencia_cache.png"
    )

def main():

    zipf_resumen = cargar_json("resumen_zipf.json")
    uniforme_resumen = cargar_json("resumen_uniforme.json")

    zipf_tipos = cargar_json("resumen_zipf_tipos.json")
    uniforme_tipos = cargar_json("resumen_uniforme_tipos.json")


    grafico_hit_rate_distribucion(
        zipf_resumen,
        uniforme_resumen
    )

    grafico_latencia_hit_miss(
        zipf_resumen,
        uniforme_resumen
    )

    grafico_hit_rate_por_tipo(
        zipf_tipos,
        uniforme_tipos
    )


    # Experimentos tamaño caché

    grafico_hit_rate_cache()

    grafico_evictions_cache()

    grafico_latencia_cache()


if __name__ == "__main__":
    main()