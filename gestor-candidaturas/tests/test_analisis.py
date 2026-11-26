"""Hito 6: análisis con pandas."""

import pandas as pd
import pytest

from candidaturas import analisis
from candidaturas.modelos import CAMPOS, ESTADOS

from conftest import HOY


@pytest.fixture
def tabla(ejemplo):
    return analisis.a_tabla(ejemplo)


@pytest.fixture
def vacia():
    return analisis.a_tabla([])


def test_a_tabla_columnas_y_tipos(tabla):
    assert list(tabla.columns) == CAMPOS
    assert len(tabla) == 12
    assert pd.api.types.is_integer_dtype(tabla["id"])
    for columna in ("fecha_envio", "fecha_respuesta", "fecha_cierre"):
        assert pd.api.types.is_datetime64_any_dtype(tabla[columna])
    assert tabla["fecha_respuesta"].isna().sum() == 6


def test_a_tabla_vacia(vacia):
    assert list(vacia.columns) == CAMPOS
    assert len(vacia) == 0
    assert pd.api.types.is_datetime64_any_dtype(vacia["fecha_envio"])


def test_a_tabla_no_modifica_las_candidaturas(ejemplo):
    antes = [c.a_fila() for c in ejemplo]
    analisis.a_tabla(ejemplo)
    assert [c.a_fila() for c in ejemplo] == antes


def test_embudo(tabla, vacia):
    assert analisis.embudo(tabla).to_dict() == {
        "enviada": 5, "entrevista": 2, "prueba_tecnica": 1, "oferta": 1,
        "aceptada": 0, "rechazada": 2, "descartada": 1}
    assert list(analisis.embudo(vacia).index) == list(ESTADOS)
    assert analisis.embudo(vacia).sum() == 0


def test_respuesta_por_fuente(tabla):
    resultado = analisis.respuesta_por_fuente(tabla)
    assert list(resultado.columns) == ["enviadas", "con_respuesta", "porcentaje"]
    assert list(resultado.index) == ["referido", "linkedin", "web_empresa", "infojobs", "otra"]
    assert resultado.loc["infojobs"].tolist() == [3, 1, 33.3]
    assert resultado.loc["otra", "porcentaje"] == 0.0


def test_dias_hasta_respuesta(tabla, vacia):
    dias = analisis.dias_hasta_respuesta(tabla)
    assert dias.to_dict() == {1: 7, 2: 8, 4: 8, 5: 5, 7: 7, 10: 4}
    assert pd.api.types.is_integer_dtype(dias)
    assert analisis.dias_hasta_respuesta(vacia).empty


def test_indicadores(tabla):
    resultado = analisis.indicadores(tabla, HOY)
    assert resultado == {"total": 12, "activas": 9, "tasa_respuesta": 50.0,
                         "dias_medios_respuesta": 6.5, "ofertas": 1, "sin_respuesta": 3,
                         "salario_medio": 31625}
    assert all(type(valor) in (int, float) for valor in resultado.values())
    assert type(resultado["salario_medio"]) is int


def test_indicadores_vacio(vacia):
    assert analisis.indicadores(vacia, HOY) == {
        "total": 0, "activas": 0, "tasa_respuesta": 0.0,
        "dias_medios_respuesta": None, "ofertas": 0, "sin_respuesta": 0,
        "salario_medio": None}


def test_grafico_embudo(tabla, tmp_path):
    ruta = analisis.grafico_embudo(tabla, tmp_path / "embudo.png")
    assert ruta.exists()
    assert ruta.read_bytes()[:4] == b"\x89PNG"


def test_envios_por_semana(tabla, vacia):
    semanas = analisis.envios_por_semana(tabla)
    assert semanas.index[0] == pd.Timestamp("2026-10-19")
    assert semanas.to_dict() == {
        pd.Timestamp("2026-10-19"): 3, pd.Timestamp("2026-10-26"): 2,
        pd.Timestamp("2026-11-02"): 4, pd.Timestamp("2026-11-09"): 1,
        pd.Timestamp("2026-11-16"): 2}
    assert semanas.sum() == len(tabla)
    assert analisis.envios_por_semana(vacia).empty


def test_a_tabla_salario_entero_con_ausentes(tabla):
    assert str(tabla["salario"].dtype) == "Int64"
    assert tabla["salario"].isna().sum() == 4


def test_por_modalidad(tabla, vacia):
    resultado = analisis.por_modalidad(tabla)
    assert list(resultado.index) == ["remoto", "hibrido", "presencial", "sin indicar"]
    assert list(resultado.columns) == ["candidaturas", "activas", "salario_medio"]
    assert resultado["candidaturas"].tolist() == [3, 4, 4, 1]
    assert resultado["activas"].tolist() == [2, 4, 2, 1]
    assert resultado.loc["hibrido", "salario_medio"] == 34333
    assert pd.isna(resultado.loc["sin indicar", "salario_medio"])
    assert analisis.por_modalidad(vacia)["candidaturas"].tolist() == [0, 0, 0, 0]
