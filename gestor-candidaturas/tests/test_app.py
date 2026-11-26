"""Hito 5: el menú de consola."""

import shutil

import pytest

import app
from candidaturas import almacen

from conftest import RUTA_EJEMPLO


@pytest.fixture
def ruta(tmp_path):
    destino = tmp_path / "candidaturas.csv"
    shutil.copy(RUTA_EJEMPLO, destino)
    return destino


def ejecutar(monkeypatch, capsys, ruta, respuestas):
    entradas = iter(respuestas)
    monkeypatch.setattr("builtins.input", lambda _="": next(entradas))
    codigo = app.main(ruta)
    return codigo, capsys.readouterr().out


def test_app_alta_y_guardar(monkeypatch, capsys, ruta):
    codigo, salida = ejecutar(monkeypatch, capsys, ruta,
                              ["1", "Nueva SL", "Data Engineer", "linkedin", "", "remoto",
                               "35.000 €", "Madrid", "0"])
    assert codigo == 0
    assert "Creada la candidatura 13." in salida
    assert "Datos guardados. Hasta luego." in salida
    nueva = almacen.cargar(ruta)[-1]
    assert (nueva.empresa, nueva.interes, nueva.modalidad, nueva.salario, nueva.ubicacion) == (
        "Nueva SL", "medio", "remoto", 35000, "Madrid")


def test_app_alta_sin_datos_opcionales(monkeypatch, capsys, ruta):
    _, salida = ejecutar(monkeypatch, capsys, ruta,
                         ["1", "Nueva SL", "Analista", "otra", "", "", "", "", "0"])
    assert "Creada la candidatura 13." in salida
    nueva = almacen.cargar(ruta)[-1]
    assert (nueva.modalidad, nueva.salario, nueva.ubicacion) == ("", None, "")


def test_app_primera_ejecucion_sin_fichero(monkeypatch, capsys, tmp_path):
    ruta = tmp_path / "nuevo.csv"
    codigo, salida = ejecutar(monkeypatch, capsys, ruta, ["2", "0"])
    assert codigo == 0
    assert "No hay candidaturas." in salida
    assert ruta.exists()


def test_app_errores_no_terminan_el_programa(monkeypatch, capsys, ruta):
    codigo, salida = ejecutar(monkeypatch, capsys, ruta, [
        "9",                                  # opción no válida
        "1", "", "Analista", "linkedin", "", "", "", "",  # empresa vacía
        "1", "Acme", "Analista", "linkedin", "", "remoto", "mucho",  # salario no válido
        "5", "uno",                           # número no entero
        "5", "4", "entrevista",               # transición no permitida
        "5", "99", "entrevista",              # no existe
        "0",
    ])
    assert codigo == 0
    assert "Opción no válida." in salida
    assert "Error: La empresa es obligatoria" in salida
    assert "Error: No se puede pasar de rechazada a entrevista" in salida
    assert "Error: No existe la candidatura 99" in salida
    assert "Error: Salario no válido: mucho" in salida
    assert salida.count("Error:") == 5


def test_app_cambiar_estado(monkeypatch, capsys, ruta):
    _, salida = ejecutar(monkeypatch, capsys, ruta, ["5", "3", "entrevista", "0"])
    assert "La candidatura 3 pasa a entrevista." in salida
    assert almacen.cargar(ruta)[2].estado == "entrevista"


@pytest.mark.parametrize(
    "respuestas, texto",
    [
        (["2", "0"], "Startup Lumen"),
        (["3", "0"], "Datanova"),
        (["4", "banco", "0"], "Banco Ibérico"),
        (["6", "0"], "Nimbus Cloud"),
        (["7", "0"], "INFORME DE CANDIDATURAS"),
        (["8", "0"], "tasa_respuesta"),
    ],
)
def test_app_opciones_de_consulta(monkeypatch, capsys, ruta, respuestas, texto):
    codigo, salida = ejecutar(monkeypatch, capsys, ruta, respuestas)
    assert codigo == 0
    assert texto in salida


def test_app_fichero_corrupto(monkeypatch, capsys, ruta):
    ruta.write_text(ruta.read_text(encoding="utf-8").replace("linkedin", "twitter", 1),
                    encoding="utf-8")
    codigo, salida = ejecutar(monkeypatch, capsys, ruta, [])
    assert codigo == 1
    assert salida.startswith("Error:")
