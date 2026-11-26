"""Hito 4: informes."""

from datetime import date

from candidaturas import Candidatura, GestorCandidaturas
from candidaturas.informes import ANCHO, linea, listado, resumen

from conftest import HOY


def sin_espacios_finales(texto: str) -> list[str]:
    return [fila.rstrip() for fila in texto.split("\n")]


def test_linea():
    c = Candidatura(3, "Acme", "Data Analyst", "linkedin", date(2026, 11, 2), "alto")
    assert linea(c) == "   3  alto    enviada         2026-11-02  Acme                Data Analyst"


def test_listado(gestor):
    filas = listado(gestor.activas()).split("\n")
    assert filas[0].rstrip() == "  ID  INTERÉS ESTADO          ENVÍO       EMPRESA             PUESTO"
    assert filas[1] == "-" * ANCHO
    assert filas[2] == "   1  alto    entrevista      2026-10-20  Acme Analytics      Data Analyst"
    assert len(filas) == 2 + 9


def test_listado_vacio():
    assert listado([]) == "No hay candidaturas."


def test_resumen(gestor):
    esperado = """\
==============================================================================
                           INFORME DE CANDIDATURAS
==============================================================================
Fecha del informe: 2026-11-27
Total de candidaturas: 12

Por estado
  enviada            5
  entrevista         2
  prueba_tecnica     1
  oferta             1
  aceptada           0
  rechazada          2
  descartada         1

Activas por interés
  alto               4
  medio              4
  bajo               1

Sin respuesta en 15 días o más: 3
=============================================================================="""
    assert sin_espacios_finales(resumen(gestor, HOY)) == esperado.split("\n")


def test_resumen_vacio():
    texto = resumen(GestorCandidaturas(), HOY)
    assert "Total de candidaturas: 0" in texto
    assert "  enviada            0" in texto
    assert "Sin respuesta en 15 días o más: 0" in texto
    assert not texto.endswith("\n")
