"""Análisis del conjunto de candidaturas con pandas.

Ninguna función modifica las candidaturas ni recorre la tabla fila a fila.
"""

from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from .modelos import (  # noqa: E402
    ACTIVOS,
    CAMPOS,
    DIAS_SIN_RESPUESTA,
    ESTADOS,
    MODALIDADES,
    Candidatura,
)

FECHAS = ["fecha_envio", "fecha_respuesta", "fecha_cierre"]


def a_tabla(candidaturas: list[Candidatura]) -> pd.DataFrame:
    """Devuelve un ``DataFrame`` con una fila por candidatura y las columnas de ``CAMPOS``.

    ``id`` es entero, ``salario`` es entero con ausentes (``Int64``) y las
    tres fechas son fechas (``datetime64``); una fecha ausente es ``NaT``.
    Con la lista vacía devuelve una tabla vacía con esas mismas columnas y
    tipos.
    """
    tabla = pd.DataFrame([c.a_fila() for c in candidaturas], columns=CAMPOS)
    tabla = tabla.astype({"id": int})
    tabla["salario"] = pd.to_numeric(tabla["salario"].replace("", pd.NA)).astype("Int64")
    for columna in FECHAS:
        tabla[columna] = pd.to_datetime(tabla[columna], format="%Y-%m-%d")
    return tabla


def embudo(tabla: pd.DataFrame) -> pd.Series:
    """Cuántas candidaturas hay en cada estado, en el orden de ``ESTADOS``.

    Los estados sin candidaturas valen 0.
    """
    return tabla["estado"].value_counts().reindex(ESTADOS, fill_value=0)


def respuesta_por_fuente(tabla: pd.DataFrame) -> pd.DataFrame:
    """Enviadas, con respuesta y porcentaje de respuesta de cada fuente.

    Índice: la fuente. Columnas: ``enviadas``, ``con_respuesta`` y
    ``porcentaje`` (con un decimal). Ordenado de mayor a menor porcentaje y,
    a igual porcentaje, por nombre de la fuente.
    """
    resumen = tabla.groupby("fuente").agg(
        enviadas=("id", "count"),
        con_respuesta=("fecha_respuesta", "count"),
    )
    resumen["porcentaje"] = (resumen["con_respuesta"] / resumen["enviadas"] * 100).round(1)
    return (resumen.reset_index()
            .sort_values(["porcentaje", "fuente"], ascending=[False, True])
            .set_index("fuente"))


def dias_hasta_respuesta(tabla: pd.DataFrame) -> pd.Series:
    """Días entre el envío y la respuesta de cada candidatura con respuesta.

    Índice: el ``id``. Valores enteros. Las candidaturas sin respuesta no
    aparecen.
    """
    con_respuesta = tabla.dropna(subset=["fecha_respuesta"]).set_index("id")
    return (con_respuesta["fecha_respuesta"] - con_respuesta["fecha_envio"]).dt.days


def envios_por_semana(tabla: pd.DataFrame) -> pd.Series:
    """Cuántas candidaturas se enviaron cada semana.

    Índice: el lunes de cada semana (``datetime64``), sin huecos entre la
    primera y la última. Las semanas sin envíos valen 0.
    """
    return (tabla.set_index("fecha_envio")["id"]
            .resample("W-MON", label="left", closed="left")
            .count())


def por_modalidad(tabla: pd.DataFrame) -> pd.DataFrame:
    """Candidaturas, activas y salario medio de cada modalidad.

    Índice: las ``MODALIDADES`` en su orden y, al final, "sin indicar" para
    las que no la tienen. Columnas: ``candidaturas`` y ``activas`` (enteros,
    0 si no hay) y ``salario_medio`` (entero redondeado, ausente si ninguna
    de esa modalidad tiene salario).
    """
    orden = [*MODALIDADES, "sin indicar"]
    grupos = tabla.assign(
        modalidad=tabla["modalidad"].replace("", "sin indicar"),
        activa=tabla["estado"].isin(ACTIVOS),
    ).groupby("modalidad")
    resumen = pd.DataFrame({
        "candidaturas": grupos.size(),
        "activas": grupos["activa"].sum(),
        "salario_medio": grupos["salario"].mean().round(),
    }).reindex(orden)
    conteos = ["candidaturas", "activas"]
    resumen[conteos] = resumen[conteos].fillna(0).astype(int)
    resumen["salario_medio"] = resumen["salario_medio"].astype("Int64")
    return resumen


def indicadores(tabla: pd.DataFrame, hoy: date) -> dict:
    """Devuelve las cifras principales de la búsqueda.

    Claves:

    - ``total``: número de candidaturas (int)
    - ``activas``: en un estado de ``ACTIVOS`` (int)
    - ``tasa_respuesta``: porcentaje con respuesta, con un decimal (float); 0.0 sin datos
    - ``dias_medios_respuesta``: media de ``dias_hasta_respuesta``, con un decimal
      (float), o None si ninguna tiene respuesta
    - ``ofertas``: en estado "oferta" o "aceptada" (int)
    - ``sin_respuesta``: en "enviada" desde hace ``DIAS_SIN_RESPUESTA`` días o más (int)
    - ``salario_medio``: media de los salarios conocidos, redondeada (int), o None

    Los valores son tipos de Python, no de NumPy.
    """
    total = len(tabla)
    dias = dias_hasta_respuesta(tabla)
    antiguedad = (pd.Timestamp(hoy) - tabla["fecha_envio"]).dt.days
    sin_respuesta = (tabla["estado"] == "enviada") & (antiguedad >= DIAS_SIN_RESPUESTA)
    salarios = tabla["salario"].dropna()
    return {
        "total": total,
        "activas": int(tabla["estado"].isin(ACTIVOS).sum()),
        "tasa_respuesta": round(len(dias) / total * 100, 1) if total else 0.0,
        "dias_medios_respuesta": round(float(dias.mean()), 1) if len(dias) else None,
        "ofertas": int(tabla["estado"].isin(["oferta", "aceptada"]).sum()),
        "sin_respuesta": int(sin_respuesta.sum()),
        "salario_medio": int(round(salarios.mean())) if len(salarios) else None,
    }


def figura_embudo(tabla: pd.DataFrame) -> plt.Figure:
    """Devuelve una figura de barras horizontales del ``embudo``, en el orden de ``ESTADOS``.

    Quien la reciba decide qué hacer con ella: guardarla o mostrarla.
    """
    datos = embudo(tabla)
    figura, ejes = plt.subplots(figsize=(8, 4))
    ejes.barh(datos.index[::-1], datos.values[::-1])
    ejes.set_xlabel("Candidaturas")
    ejes.set_title("Candidaturas por estado")
    figura.tight_layout()
    return figura


def grafico_embudo(tabla: pd.DataFrame, ruta: str | Path) -> Path:
    """Guarda en ``ruta`` la ``figura_embudo`` como imagen y devuelve la ruta."""
    figura = figura_embudo(tabla)
    figura.savefig(ruta)
    plt.close(figura)
    return Path(ruta)
