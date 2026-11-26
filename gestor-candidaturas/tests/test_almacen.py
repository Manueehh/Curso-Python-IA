"""Hito 3: guardar y cargar en CSV."""

import pytest

from candidaturas import ErrorDeAlmacen, almacen
from candidaturas.modelos import CAMPOS


def test_cargar_el_ejemplo(ejemplo):
    assert len(ejemplo) == 12
    assert ejemplo[1].empresa == "Banco Ibérico"


def test_cargar_un_fichero_que_no_existe(tmp_path):
    assert almacen.cargar(tmp_path / "no_existe.csv") == []


def test_guardar_y_cargar_conserva_los_datos(ejemplo, tmp_path):
    ruta = tmp_path / "candidaturas.csv"
    almacen.guardar(ejemplo, ruta)
    assert almacen.cargar(ruta) == ejemplo


def test_guardar_escribe_la_cabecera(tmp_path):
    ruta = tmp_path / "vacio.csv"
    almacen.guardar([], ruta)
    assert ruta.read_text(encoding="utf-8").strip() == ",".join(CAMPOS)


def test_cargar_fila_incorrecta_indica_la_linea(ejemplo, tmp_path):
    ruta = tmp_path / "roto.csv"
    almacen.guardar(ejemplo[:3], ruta)
    texto = ruta.read_text(encoding="utf-8").replace("2026-10-25", "25/10/2026")
    ruta.write_text(texto, encoding="utf-8")
    with pytest.raises(ErrorDeAlmacen, match="Línea 4") as info:
        almacen.cargar(ruta)
    assert info.value.__cause__ is not None


def test_cargar_un_csv_de_la_primera_version(tmp_path):
    ruta = tmp_path / "antiguo.csv"
    ruta.write_text(
        "id,empresa,puesto,fuente,interes,estado,fecha_envio,fecha_respuesta,fecha_cierre\n"
        "1,Acme,Analista,linkedin,alto,enviada,2026-11-01,,\n",
        encoding="utf-8")
    [candidatura] = almacen.cargar(ruta)
    assert (candidatura.empresa, candidatura.modalidad, candidatura.salario) == ("Acme", "", None)
    almacen.guardar([candidatura], ruta)  # al guardar se añaden las columnas nuevas
    assert ruta.read_text(encoding="utf-8").splitlines()[0] == ",".join(CAMPOS)
