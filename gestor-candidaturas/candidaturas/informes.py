"""Textos para mostrar por pantalla.

Las funciones de este módulo devuelven cadenas: no usan ``print``.
"""

from datetime import date

from .gestor import GestorCandidaturas
from .modelos import DIAS_SIN_RESPUESTA, INTERESES, Candidatura

ANCHO = 78


def linea(candidatura: Candidatura) -> str:
    """Devuelve una candidatura en una línea de columnas alineadas.

    Columnas: id a la derecha en 4; dos espacios; interés a la izquierda en
    8; estado en 16; fecha de envío en 12; empresa en 20; y el puesto al
    final sin relleno.

    >>> from datetime import date
    >>> linea(Candidatura(3, "Acme", "Data Analyst", "linkedin", date(2026, 11, 2), "alto"))
    '   3  alto    enviada         2026-11-02  Acme                Data Analyst'
    """
    c = candidatura
    return (f"{c.id:>4}  {c.interes:<8}{c.estado:<16}{c.fecha_envio.isoformat():<12}"
            f"{c.empresa:<20}{c.puesto}")


def listado(candidaturas: list[Candidatura]) -> str:
    """Devuelve una tabla con cabecera, una línea de guiones y una línea por candidatura.

    La cabecera usa los mismos anchos que ``linea`` con los rótulos "ID",
    "INTERÉS", "ESTADO", "ENVÍO", "EMPRESA" y "PUESTO". La línea de guiones
    mide ``ANCHO``. Si no hay candidaturas devuelve "No hay candidaturas.".
    """
    if not candidaturas:
        return "No hay candidaturas."
    cabecera = f"{'ID':>4}  {'INTERÉS':<8}{'ESTADO':<16}{'ENVÍO':<12}{'EMPRESA':<20}PUESTO"
    return "\n".join([cabecera, "-" * ANCHO, *(linea(c) for c in candidaturas)])


def resumen(gestor: GestorCandidaturas, hoy: date) -> str:
    """Devuelve el informe de situación con el formato del enunciado."""
    por_estado = gestor.contar_por_estado()
    activas = gestor.activas()
    lineas = [
        "=" * ANCHO,
        f"{'INFORME DE CANDIDATURAS':^{ANCHO}}",
        "=" * ANCHO,
        f"Fecha del informe: {hoy.isoformat()}",
        f"Total de candidaturas: {len(gestor)}",
        "",
        "Por estado",
        *(f"  {estado:<16}{cantidad:>4}" for estado, cantidad in por_estado.items()),
        "",
        "Activas por interés",
        *(f"  {interes:<16}{sum(c.interes == interes for c in activas):>4}"
          for interes in reversed(INTERESES)),
        "",
        f"Sin respuesta en {DIAS_SIN_RESPUESTA} días o más: {len(gestor.sin_respuesta(hoy))}",
        "=" * ANCHO,
    ]
    return "\n".join(lineas)
