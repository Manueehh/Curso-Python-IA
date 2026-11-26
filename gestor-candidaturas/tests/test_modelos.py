"""Hito 1: excepciones y modelo."""

from datetime import date

import pytest

from candidaturas import (
    Candidatura,
    CandidaturaDuplicada,
    CandidaturaNoEncontrada,
    DatoNoValido,
    ErrorDeAlmacen,
    ErrorDeCandidaturas,
    TransicionNoPermitida,
)
from candidaturas.modelos import CAMPOS, CAMPOS_OPCIONALES, TRANSICIONES, salario_desde_texto

ENVIO = date(2026, 11, 1)


def nueva(**cambios) -> Candidatura:
    datos = {"id": 1, "empresa": "Acme", "puesto": "Data Analyst",
             "fuente": "linkedin", "fecha_envio": ENVIO}
    return Candidatura(**(datos | cambios))


# --------------------------------------------------------------- excepciones
@pytest.mark.parametrize(
    "clase", [DatoNoValido, CandidaturaNoEncontrada, TransicionNoPermitida,
              CandidaturaDuplicada, ErrorDeAlmacen],
)
def test_excepciones_heredan_de_la_base(clase):
    assert issubclass(clase, ErrorDeCandidaturas)
    assert issubclass(ErrorDeCandidaturas, Exception)


def test_excepciones_con_atributos():
    no_encontrada = CandidaturaNoEncontrada(7)
    assert no_encontrada.identificador == 7
    assert str(no_encontrada) == "No existe la candidatura 7"

    transicion = TransicionNoPermitida("enviada", "oferta")
    assert (transicion.actual, transicion.nuevo) == ("enviada", "oferta")
    assert str(transicion) == "No se puede pasar de enviada a oferta"

    duplicada = CandidaturaDuplicada("Acme", "Data Engineer")
    assert (duplicada.empresa, duplicada.puesto) == ("Acme", "Data Engineer")
    assert str(duplicada) == "Ya hay una candidatura activa a Acme - Data Engineer"


# ------------------------------------------------------------ validación
def test_candidatura_valores_por_defecto():
    c = nueva()
    assert (c.interes, c.estado, c.fecha_respuesta, c.fecha_cierre) == (
        "medio", "enviada", None, None)


def test_candidatura_limpia_los_textos():
    c = nueva(empresa="  Acme ", puesto=" Data Analyst  ", fuente=" LinkedIn ",
              interes="ALTO ")
    assert (c.empresa, c.puesto, c.fuente, c.interes) == (
        "Acme", "Data Analyst", "linkedin", "alto")


@pytest.mark.parametrize(
    "cambios, mensaje",
    [
        ({"empresa": "   "}, "La empresa es obligatoria"),
        ({"puesto": ""}, "El puesto es obligatorio"),
        ({"fuente": "twitter"}, "Fuente no válida: twitter"),
        ({"interes": "muy alto"}, "Interés no válido: muy alto"),
        ({"estado": "pausada"}, "Estado no válido: pausada"),
    ],
)
def test_candidatura_datos_no_validos(cambios, mensaje):
    with pytest.raises(DatoNoValido, match=mensaje):
        nueva(**cambios)


# ------------------------------------------------------------ estado
@pytest.mark.parametrize(
    "estado, activa",
    [("enviada", True), ("entrevista", True), ("prueba_tecnica", True),
     ("oferta", True), ("aceptada", False), ("rechazada", False), ("descartada", False)],
)
def test_candidatura_activa(estado, activa):
    assert nueva(estado=estado).activa is activa


def test_dias_desde_envio_y_sin_respuesta():
    c = nueva()
    assert c.dias_desde_envio(date(2026, 11, 15)) == 14
    assert c.sin_respuesta(date(2026, 11, 15)) is False
    assert c.sin_respuesta(date(2026, 11, 16)) is True
    assert nueva(estado="entrevista").sin_respuesta(date(2026, 12, 31)) is False


def test_cambiar_estado_respeta_las_transiciones():
    c = nueva()
    with pytest.raises(TransicionNoPermitida):
        c.cambiar_estado("oferta", date(2026, 11, 5))
    assert c.estado == "enviada"


def test_cambiar_estado_no_existente():
    with pytest.raises(DatoNoValido, match="Estado no válido: pausada"):
        nueva().cambiar_estado("pausada", date(2026, 11, 5))


def test_cambiar_estado_admite_mayusculas_y_espacios():
    c = nueva()
    c.cambiar_estado(" Entrevista ", date(2026, 11, 5))
    assert c.estado == "entrevista"


def test_cambiar_estado_anota_la_fecha_de_respuesta_una_vez():
    c = nueva()
    c.cambiar_estado("entrevista", date(2026, 11, 5))
    c.cambiar_estado("prueba_tecnica", date(2026, 11, 9))
    c.cambiar_estado("entrevista", date(2026, 11, 12))
    assert c.fecha_respuesta == date(2026, 11, 5)
    assert c.fecha_cierre is None


def test_descartar_sin_respuesta_no_es_una_respuesta():
    c = nueva()
    c.cambiar_estado("descartada", date(2026, 11, 5))
    assert c.fecha_respuesta is None
    assert c.fecha_cierre == date(2026, 11, 5)


def test_rechazo_directo_anota_respuesta_y_cierre():
    c = nueva()
    c.cambiar_estado("rechazada", date(2026, 11, 8))
    assert (c.fecha_respuesta, c.fecha_cierre) == (date(2026, 11, 8), date(2026, 11, 8))


def test_estados_finales_no_admiten_cambios():
    for final in ("aceptada", "rechazada", "descartada"):
        assert TRANSICIONES[final] == ()
        with pytest.raises(TransicionNoPermitida):
            nueva(estado=final).cambiar_estado("enviada", date(2026, 11, 8))


def test_flujo_completo_hasta_aceptar():
    c = nueva()
    for estado, dia in [("entrevista", 3), ("prueba_tecnica", 6), ("oferta", 10),
                        ("aceptada", 12)]:
        c.cambiar_estado(estado, date(2026, 11, dia))
    assert c.estado == "aceptada"
    assert (c.fecha_respuesta, c.fecha_cierre) == (date(2026, 11, 3), date(2026, 11, 12))


# ------------------------------------------------------------ filas CSV
def test_a_fila():
    c = nueva(estado="rechazada", fecha_respuesta=date(2026, 11, 4),
              fecha_cierre=date(2026, 11, 4))
    assert c.a_fila() == {
        "id": "1", "empresa": "Acme", "puesto": "Data Analyst", "fuente": "linkedin",
        "interes": "medio", "estado": "rechazada", "fecha_envio": "2026-11-01",
        "fecha_respuesta": "2026-11-04", "fecha_cierre": "2026-11-04",
        "modalidad": "", "salario": "", "ubicacion": "", "enlace": "", "notas": "",
    }
    assert list(nueva().a_fila()) == CAMPOS
    assert nueva().a_fila()["fecha_respuesta"] == ""


def test_desde_fila_es_la_inversa_de_a_fila():
    c = nueva(estado="entrevista", fecha_respuesta=date(2026, 11, 4))
    assert Candidatura.desde_fila(c.a_fila()) == c


@pytest.mark.parametrize(
    "cambio",
    [{"id": "uno"}, {"fecha_envio": "01/11/2026"}, {"fecha_respuesta": "ayer"},
     {"empresa": ""}],
)
def test_desde_fila_datos_no_validos(cambio):
    fila = nueva().a_fila() | cambio
    with pytest.raises(DatoNoValido):
        Candidatura.desde_fila(fila)


def test_desde_fila_falta_un_campo_y_encadena():
    fila = nueva().a_fila()
    del fila["fuente"]
    with pytest.raises(DatoNoValido) as info:
        Candidatura.desde_fila(fila)
    assert isinstance(info.value.__cause__, KeyError)


# ------------------------------------------------------------ campos opcionales
def test_campos_opcionales_por_defecto():
    c = nueva()
    assert (c.modalidad, c.salario, c.ubicacion, c.enlace, c.notas) == ("", None, "", "", "")


def test_campos_opcionales_se_limpian():
    c = nueva(modalidad=" Remoto ", ubicacion="  Madrid ", enlace=" https://a.es/1 ",
              notas="  hablar con RRHH ", salario=35000)
    assert (c.modalidad, c.ubicacion, c.enlace, c.notas, c.salario) == (
        "remoto", "Madrid", "https://a.es/1", "hablar con RRHH", 35000)


@pytest.mark.parametrize(
    "cambios, mensaje",
    [
        ({"modalidad": "a veces"}, "Modalidad no válida: a veces"),
        ({"salario": -1}, "El salario no puede ser negativo"),
        ({"enlace": "www.acme.com"}, "El enlace tiene que empezar por http:// o https://"),
    ],
)
def test_campos_opcionales_no_validos(cambios, mensaje):
    with pytest.raises(DatoNoValido, match=mensaje):
        nueva(**cambios)


def test_a_fila_y_desde_fila_con_todos_los_campos():
    c = nueva(modalidad="hibrido", salario=32000, ubicacion="Madrid",
              enlace="https://a.es/1", notas="Ver Glassdoor")
    fila = c.a_fila()
    assert (fila["modalidad"], fila["salario"]) == ("hibrido", "32000")
    assert Candidatura.desde_fila(fila) == c


def test_desde_fila_de_un_csv_antiguo_sin_campos_opcionales():
    fila = nueva().a_fila()
    for campo in CAMPOS_OPCIONALES:
        del fila[campo]
    assert Candidatura.desde_fila(fila) == nueva()


def test_desde_fila_salario_no_entero():
    with pytest.raises(DatoNoValido):
        Candidatura.desde_fila(nueva().a_fila() | {"salario": "mucho"})


@pytest.mark.parametrize(
    "texto, esperado",
    [("35000", 35000), ("35.000", 35000), (" 35.000 € ", 35000), ("32k", 32000),
     ("32 K", 32000), ("", None), ("   ", None)],
)
def test_salario_desde_texto(texto, esperado):
    assert salario_desde_texto(texto) == esperado


@pytest.mark.parametrize("texto", ["mucho", "35,5", "-3000", "k"])
def test_salario_desde_texto_no_valido(texto):
    with pytest.raises(DatoNoValido, match="Salario no válido"):
        salario_desde_texto(texto)
