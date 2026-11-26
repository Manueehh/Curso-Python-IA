"""Interfaz web: cada página se ejecuta con el simulador de Streamlit (AppTest)."""

import shutil
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from candidaturas import almacen

from conftest import RUTA_EJEMPLO

RAIZ = Path(__file__).parent.parent


@pytest.fixture
def ruta(tmp_path, monkeypatch):
    destino = tmp_path / "candidaturas.csv"
    shutil.copy(RUTA_EJEMPLO, destino)
    monkeypatch.setenv("CANDIDATURAS_CSV", str(destino))
    return destino


def abrir(pagina: str) -> AppTest:
    """Ejecuta una página de web_app con los datos de la variable de entorno."""
    guion = (f"import sys\nsys.path.insert(0, {str(RAIZ)!r})\n"
             f"import web_app\nweb_app.renderizar(web_app.{pagina})\n")
    at = AppTest.from_string(guion, default_timeout=30).run()
    assert not at.exception, at.exception
    return at


def test_aplicacion_completa_arranca(ruta):
    at = AppTest.from_file(str(RAIZ / "web_app.py"), default_timeout=30).run()
    assert not at.exception
    assert at.title[0].value == "🎯 Panel"


def test_panel_muestra_indicadores(ruta):
    at = abrir("pagina_panel")
    metricas = {m.label: m.value for m in at.main.metric}
    assert metricas["📨 Total"] == "12"
    assert metricas["🟢 Activas"] == "9"
    assert metricas["💬 Tasa de respuesta"] == "50.0 %"


def test_barra_lateral(ruta):
    at = abrir("pagina_panel")
    assert {m.label: m.value for m in at.sidebar.metric} == {"Activas": "9", "Sin respuesta": "3"}


def test_tablero_agrupa_las_activas(ruta):
    at = abrir("pagina_tablero")
    texto = " ".join(m.value for m in at.markdown)
    assert "Enviada · 5" in texto
    assert "Entrevista · 2" in texto
    assert "Banco Ibérico" in texto
    assert "Retail Plus" not in texto  # rechazada: no aparece


def test_listado_filtra(ruta):
    at = abrir("pagina_listado")
    at.text_input[0].input("data").run()
    assert at.caption[1].value == "6 de 12 candidaturas"
    assert at.dataframe[0].value["Empresa"].tolist()[0] == "Acme Analytics"


def test_alta_guarda_en_el_csv(ruta):
    at = abrir("pagina_alta")
    at.text_input[0].input("Nueva SL")
    at.text_input[1].input("Data Engineer")
    at.button[0].click().run()
    assert not at.exception
    guardada = almacen.cargar(ruta)[-1]
    assert (guardada.id, guardada.empresa, guardada.fuente, guardada.interes) == (
        13, "Nueva SL", "linkedin", "medio")


def test_alta_con_error_no_guarda(ruta):
    at = abrir("pagina_alta")
    at.text_input[1].input("Analista")
    at.button[0].click().run()
    assert at.error[0].value == "La empresa es obligatoria"
    assert len(almacen.cargar(ruta)) == 12


def test_alta_duplicada(ruta):
    at = abrir("pagina_alta")
    at.text_input[0].input("Acme Analytics")
    at.text_input[1].input("Data Analyst")
    at.button[0].click().run()
    assert "Ya hay una candidatura activa" in at.error[0].value


def test_cambiar_estado_solo_ofrece_transiciones_validas(ruta):
    at = abrir("pagina_estado")
    # La primera activa en orden de revisión es la 1 (entrevista)
    assert [b.label for b in at.button] == ["Prueba técnica", "Oferta", "Rechazada", "Descartada"]
    at.button(key="pasar_oferta").click().run()
    assert not at.exception
    assert almacen.cargar(ruta)[0].estado == "oferta"


def test_seguimiento_acciones_rapidas(ruta):
    at = abrir("pagina_seguimiento")
    assert len(at.button) == 6  # 3 candidaturas sin respuesta x 2 acciones
    at.button(key="descartar_3").click().run()
    assert almacen.cargar(ruta)[2].estado == "descartada"


def test_informe(ruta):
    at = abrir("pagina_informe")
    assert "INFORME DE CANDIDATURAS" in at.code[0].value


def test_fichero_corrupto(ruta):
    ruta.write_text(ruta.read_text(encoding="utf-8").replace("linkedin", "twitter", 1),
                    encoding="utf-8")
    at = abrir("pagina_panel")
    assert "No se pueden cargar los datos" in at.error[0].value


def test_sin_fichero_empieza_vacio(tmp_path, monkeypatch):
    monkeypatch.setenv("CANDIDATURAS_CSV", str(tmp_path / "nuevo.csv"))
    at = abrir("pagina_panel")
    assert "Todavía no hay candidaturas" in at.info[0].value


def test_alta_con_condiciones(ruta):
    at = abrir("pagina_alta")
    at.text_input[0].input("Nueva SL")
    at.text_input[1].input("Data Engineer")
    at.text_input[2].input("https://nueva.es/empleo/1")
    at.text_input[3].input("Madrid")
    at.number_input[0].set_value(35000)
    at.text_area[0].input("Pide Airflow")
    at.button[0].click().run()
    assert not at.exception
    nueva = almacen.cargar(ruta)[-1]
    assert (nueva.salario, nueva.ubicacion, nueva.enlace, nueva.notas) == (
        35000, "Madrid", "https://nueva.es/empleo/1", "Pide Airflow")


def test_alta_enlace_no_valido(ruta):
    at = abrir("pagina_alta")
    at.text_input[0].input("Nueva SL")
    at.text_input[1].input("Data Engineer")
    at.text_input[2].input("nueva.es")
    at.button[0].click().run()
    assert "El enlace tiene que empezar" in at.error[0].value
    assert len(almacen.cargar(ruta)) == 12


def test_panel_salario_medio(ruta):
    at = abrir("pagina_panel")
    metricas = {m.label: m.value for m in at.main.metric}
    assert metricas["💶 Salario medio"] == "31.625 €"


def test_listado_muestra_las_condiciones(ruta):
    at = abrir("pagina_listado")
    fila = at.dataframe[0].value.iloc[0]
    assert (fila["Modalidad"], fila["Salario"], fila["Ubicación"]) == (
        "🔀 Híbrido", "32.000 €", "Madrid")
