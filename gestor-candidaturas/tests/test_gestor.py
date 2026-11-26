"""Hito 2: GestorCandidaturas."""

from datetime import date

import pytest

from candidaturas import (
    CandidaturaDuplicada,
    CandidaturaNoEncontrada,
    DatoNoValido,
    GestorCandidaturas,
    TransicionNoPermitida,
)
from candidaturas.modelos import ESTADOS

from conftest import HOY


def test_gestor_vacio():
    gestor = GestorCandidaturas()
    assert len(gestor) == 0
    assert list(gestor) == []


def test_gestor_recorre_por_identificador(ejemplo):
    gestor = GestorCandidaturas(list(reversed(ejemplo)))
    assert [c.id for c in gestor] == list(range(1, 13))


def test_crear_asigna_identificadores_consecutivos():
    gestor = GestorCandidaturas()
    primera = gestor.crear("Acme", "Data Analyst", fuente="linkedin", hoy=HOY)
    segunda = gestor.crear("Beta", "ML Engineer", fuente="infojobs", interes="alto", hoy=HOY)
    assert (primera.id, segunda.id) == (1, 2)
    assert (segunda.interes, segunda.fecha_envio, segunda.estado) == ("alto", HOY, "enviada")
    assert len(gestor) == 2


def test_crear_continua_tras_el_mayor(gestor):
    assert gestor.crear("Nueva", "Analista", fuente="otra", hoy=HOY).id == 13


def test_crear_usa_la_fecha_actual_por_defecto():
    candidatura = GestorCandidaturas().crear("Acme", "Analista", fuente="otra")
    assert candidatura.fecha_envio == date.today()


def test_crear_solo_por_nombre():
    with pytest.raises(TypeError):
        GestorCandidaturas().crear("Acme", "Analista", "linkedin")


def test_crear_con_datos_no_validos_no_guarda_nada():
    gestor = GestorCandidaturas()
    with pytest.raises(DatoNoValido):
        gestor.crear("", "Analista", fuente="linkedin", hoy=HOY)
    assert len(gestor) == 0


def test_crear_duplicada_activa(gestor):
    with pytest.raises(CandidaturaDuplicada):
        gestor.crear("  acme analytics ", "DATA ANALYST", fuente="linkedin", hoy=HOY)
    assert len(gestor) == 12


def test_crear_misma_oferta_si_la_anterior_esta_cerrada(gestor):
    # La 4 (Retail Plus, Analista BI) está rechazada: se puede volver a intentar
    assert gestor.crear("Retail Plus", "Analista BI", fuente="infojobs", hoy=HOY).id == 13


def test_obtener(gestor):
    assert gestor.obtener(5).empresa == "Datanova"
    with pytest.raises(CandidaturaNoEncontrada) as info:
        gestor.obtener(99)
    assert info.value.identificador == 99


def test_cambiar_estado_delega_en_la_candidatura(gestor):
    candidatura = gestor.cambiar_estado(3, "entrevista", hoy=HOY)
    assert candidatura is gestor.obtener(3)
    assert (candidatura.estado, candidatura.fecha_respuesta) == ("entrevista", HOY)
    with pytest.raises(TransicionNoPermitida):
        gestor.cambiar_estado(4, "entrevista", hoy=HOY)
    with pytest.raises(CandidaturaNoEncontrada):
        gestor.cambiar_estado(99, "entrevista", hoy=HOY)


@pytest.mark.parametrize(
    "texto, ids",
    [("data", [1, 2, 5, 7, 9, 10]), ("ANALISTA de", [6, 8, 11]), ("  ibérico ", [2]),
     ("nada", [])],
)
def test_buscar(gestor, texto, ids):
    assert [c.id for c in gestor.buscar(texto)] == ids


def test_activas_por_interes_y_antiguedad(gestor):
    assert [c.id for c in gestor.activas()] == [1, 2, 5, 11, 3, 6, 8, 10, 12]


def test_activas_a_igual_fecha_por_identificador():
    gestor = GestorCandidaturas()
    for empresa in ("C", "A", "B"):
        gestor.crear(empresa, "Analista", fuente="otra", hoy=HOY)
    assert [c.id for c in gestor.activas()] == [1, 2, 3]


def test_sin_respuesta(gestor):
    assert [c.id for c in gestor.sin_respuesta(HOY)] == [3, 6, 8]
    assert [c.id for c in gestor.sin_respuesta(date(2026, 12, 31))] == [3, 6, 8, 11, 12]


def test_contar_por_estado(gestor):
    conteo = gestor.contar_por_estado()
    assert list(conteo) == list(ESTADOS)
    assert conteo == {"enviada": 5, "entrevista": 2, "prueba_tecnica": 1, "oferta": 1,
                      "aceptada": 0, "rechazada": 2, "descartada": 1}
    assert GestorCandidaturas().contar_por_estado() == dict.fromkeys(ESTADOS, 0)


@pytest.mark.parametrize(
    "criterios, ids",
    [
        ({}, list(range(1, 13))),
        ({"estados": ["entrevista"]}, [1, 10]),
        ({"fuentes": ["infojobs", "otra"]}, [4, 6, 9, 12]),
        ({"estados": ["enviada"], "fuentes": ["linkedin"]}, [3, 11]),
        ({"texto": "data", "estados": ["rechazada"]}, [7]),
        ({"estados": [], "fuentes": None, "texto": ""}, list(range(1, 13))),
    ],
)
def test_filtrar(gestor, criterios, ids):
    assert [c.id for c in gestor.filtrar(**criterios)] == ids


def test_filtrar_solo_por_nombre(gestor):
    with pytest.raises(TypeError):
        gestor.filtrar(["enviada"])


def test_crear_con_campos_opcionales():
    nueva = GestorCandidaturas().crear(
        "Acme", "Analista", fuente="linkedin", modalidad="remoto", salario=30000,
        ubicacion="Madrid", enlace="https://acme.es/empleo/7", notas="Pide inglés", hoy=HOY)
    assert (nueva.modalidad, nueva.salario, nueva.ubicacion, nueva.enlace, nueva.notas) == (
        "remoto", 30000, "Madrid", "https://acme.es/empleo/7", "Pide inglés")


def test_filtrar_por_modalidad(gestor):
    assert [c.id for c in gestor.filtrar(modalidades=["remoto"])] == [3, 7, 11]
    assert [c.id for c in gestor.filtrar(modalidades=["remoto"], estados=["enviada"])] == [3, 11]
