"""Módulo 7 - Práctica 7: análisis de las ventas del año.

Un pequeño proceso de análisis completo: cargar, limpiar, calcular indicadores,
generar gráficos y exportar los resultados.

Uso:

    python m7_practica_analisis.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATOS = Path(__file__).resolve().parent.parent / "datos"
SALIDA = Path(__file__).resolve().parent / "salida_practica_7"
COLUMNAS_TEXTO = ["vendedor", "region", "producto", "categoria"]


def cargar(ruta: str | Path) -> pd.DataFrame:
    """Lee el CSV de ventas con todas las columnas como texto."""
    return pd.read_csv(ruta, encoding="utf-8", dtype=str)


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve las ventas limpias y con las columnas calculadas.

    1. Texto sin espacios sobrantes y con la inicial en mayúscula.
    2. Sin filas duplicadas.
    3. ``fecha`` como fecha (formato "AAAA-MM-DD"), ``unidades`` y ``precio``
       como números. ``precio`` admite coma decimal.
    4. Las regiones ausentes pasan a ser "Sin región".
    5. Se descartan las filas sin fecha, vendedor, unidades o precio válidos, y
       las que tienen unidades o precio menores o iguales que cero.
    6. ``unidades`` queda como entero.
    7. Columnas nuevas: ``importe`` (unidades por precio) y ``mes`` ("AAAA-MM").
    8. Filas ordenadas por fecha, con el índice renumerado desde 0. A igual
       fecha se conserva el orden original.

    No modifica el DataFrame recibido.
    """
    datos = df.copy()
    for columna in COLUMNAS_TEXTO:
        datos[columna] = datos[columna].str.strip().str.capitalize()
    datos = datos.drop_duplicates()
    datos = datos.assign(
        fecha=pd.to_datetime(datos["fecha"], format="%Y-%m-%d", errors="coerce"),
        unidades=pd.to_numeric(datos["unidades"], errors="coerce"),
        precio=pd.to_numeric(datos["precio"].str.replace(",", ".", regex=False),
                             errors="coerce"),
        region=datos["region"].fillna("Sin región"),
    )
    datos = datos.dropna(subset=["fecha", "vendedor", "unidades", "precio"])
    datos = datos[(datos["unidades"] > 0) & (datos["precio"] > 0)]
    datos = datos.astype({"unidades": int})
    datos = datos.assign(
        importe=datos["unidades"] * datos["precio"],
        mes=datos["fecha"].dt.strftime("%Y-%m"),
    )
    return datos.sort_values("fecha", kind="stable").reset_index(drop=True)


def indicadores(df: pd.DataFrame) -> dict:
    """Devuelve los indicadores principales de unas ventas preparadas.

    Claves:

    - "ventas": número de ventas (int).
    - "importe_total": float con dos decimales.
    - "ticket_medio": importe medio por venta, float con dos decimales.
    - "mejor_vendedor": el de mayor importe total.
    - "mejor_mes": el mes "AAAA-MM" de mayor importe total.
    - "producto_mas_vendido": el de más unidades.
    """
    importe_total = df["importe"].sum()
    return {
        "ventas": len(df),
        "importe_total": round(float(importe_total), 2),
        "ticket_medio": round(float(importe_total / len(df)), 2),
        "mejor_vendedor": df.groupby("vendedor")["importe"].sum().idxmax(),
        "mejor_mes": df.groupby("mes")["importe"].sum().idxmax(),
        "producto_mas_vendido": df.groupby("producto")["unidades"].sum().idxmax(),
    }


def ranking_vendedores(df: pd.DataFrame, objetivos: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una fila por vendedor, de mayor a menor importe.

    Columnas, en este orden: vendedor, ventas, importe, objetivo, cumplimiento
    y cumplido. ``importe`` va redondeado a dos decimales, ``cumplimiento`` es
    el porcentaje del objetivo alcanzado con un decimal y ``cumplido`` indica
    si el importe llega al objetivo. El índice va de 0 en adelante.

    ``objetivos`` tiene las columnas vendedor y objetivo.
    """
    ranking = (
        df.groupby("vendedor")
        .agg(ventas=("importe", "size"), importe=("importe", "sum"))
        .reset_index()
        .merge(objetivos[["vendedor", "objetivo"]], on="vendedor", how="left")
        .sort_values("importe", ascending=False, ignore_index=True)
    )
    ranking["importe"] = ranking["importe"].round(2)
    ranking["cumplimiento"] = (ranking["importe"] / ranking["objetivo"] * 100).round(1)
    ranking["cumplido"] = ranking["importe"] >= ranking["objetivo"]
    return ranking[["vendedor", "ventas", "importe", "objetivo", "cumplimiento", "cumplido"]]


def evolucion_mensual(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una fila por mes, en orden, con las columnas mes, importe y variacion.

    ``importe`` va redondeado a dos decimales. ``variacion`` es el cambio en
    porcentaje respecto al mes anterior, con un decimal; en el primer mes es
    un valor ausente. El índice va de 0 en adelante.
    """
    mensual = df.groupby("mes")["importe"].sum()
    return pd.DataFrame({
        "mes": mensual.index,
        "importe": mensual.round(2).values,
        "variacion": (mensual.pct_change() * 100).round(1).values,
    })


def generar_graficos(df: pd.DataFrame, carpeta: str | Path) -> list[Path]:
    """Guarda dos gráficos en ``carpeta`` y devuelve sus rutas, en este orden.

    1. ``importe_por_vendedor.png``: barras, de mayor a menor importe.
    2. ``evolucion_mensual.png``: líneas con el importe de cada mes.

    Crea la carpeta si no existe. Cada gráfico lleva título y etiqueta en el
    eje Y. Las figuras se cierran después de guardarlas.
    """
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    por_vendedor = df.groupby("vendedor")["importe"].sum().sort_values(ascending=False)
    figura, ejes = plt.subplots(figsize=(8, 5))
    ejes.bar(por_vendedor.index, por_vendedor.values, color="#4C72B0")
    ejes.set_title("Importe total por vendedor")
    ejes.set_ylabel("Importe (€)")
    ejes.yaxis.set_major_formatter(lambda valor, _: f"{valor:,.0f}".replace(",", "."))
    ejes.grid(axis="y", alpha=0.3)
    figura.tight_layout()
    ruta_vendedores = carpeta / "importe_por_vendedor.png"
    figura.savefig(ruta_vendedores, dpi=150)
    plt.close(figura)

    mensual = df.groupby("mes")["importe"].sum()
    figura, ejes = plt.subplots(figsize=(9, 5))
    ejes.plot(mensual.index, mensual.values, marker="o", color="#4C72B0")
    ejes.set_title("Evolución mensual del importe")
    ejes.set_xlabel("Mes")
    ejes.set_ylabel("Importe (€)")
    ejes.yaxis.set_major_formatter(lambda valor, _: f"{valor:,.0f}".replace(",", "."))
    ejes.grid(alpha=0.3)
    ejes.tick_params(axis="x", rotation=45)
    figura.tight_layout()
    ruta_mensual = carpeta / "evolucion_mensual.png"
    figura.savefig(ruta_mensual, dpi=150)
    plt.close(figura)

    return [ruta_vendedores, ruta_mensual]


def exportar(tabla: pd.DataFrame, ruta: str | Path) -> None:
    """Escribe la tabla en un CSV en UTF-8, sin la columna del índice.

    Crea la carpeta de destino si no existe.
    """
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(ruta, index=False, encoding="utf-8")


def main() -> None:
    """Ejecuta el análisis completo con los datos del módulo."""
    ventas = preparar(cargar(DATOS / "ventas_2026.csv"))
    objetivos = pd.read_csv(DATOS / "objetivos.csv")

    print("INDICADORES")
    for nombre, valor in indicadores(ventas).items():
        print(f"  {nombre:<22}{valor}")
    print()
    print("RANKING DE VENDEDORES")
    ranking = ranking_vendedores(ventas, objetivos)
    print(ranking.to_string(index=False))
    print()
    print("EVOLUCIÓN MENSUAL")
    print(evolucion_mensual(ventas).to_string(index=False))

    exportar(ranking, SALIDA / "ranking_vendedores.csv")
    exportar(evolucion_mensual(ventas), SALIDA / "evolucion_mensual.csv")
    for ruta in generar_graficos(ventas, SALIDA):
        print(f"Gráfico guardado en {ruta}")


if __name__ == "__main__":
    main()