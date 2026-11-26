"""Guardar y cargar las candidaturas en un fichero CSV."""

import csv
from pathlib import Path

from .excepciones import DatoNoValido, ErrorDeAlmacen
from .modelos import CAMPOS, Candidatura


def guardar(candidaturas: list[Candidatura], ruta: str | Path) -> None:
    """Escribe las candidaturas en ``ruta`` como CSV con la cabecera ``CAMPOS``.

    Usa ``csv.DictWriter`` y ``Candidatura.a_fila``. Sobrescribe el fichero.
    """
    with open(ruta, "w", encoding="utf-8", newline="") as fichero:
        escritor = csv.DictWriter(fichero, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(c.a_fila() for c in candidaturas)


def cargar(ruta: str | Path) -> list[Candidatura]:
    """Lee las candidaturas de ``ruta``.

    Si el fichero no existe devuelve una lista vacía: es la primera
    ejecución. Si una fila no vale, lanza ``ErrorDeAlmacen`` con el mensaje
    "Línea N: <motivo>", donde N es el número de línea del fichero (la
    cabecera es la línea 1), encadenando la excepción original.
    """
    if not Path(ruta).exists():
        return []
    with open(ruta, encoding="utf-8", newline="") as fichero:
        candidaturas = []
        for numero, fila in enumerate(csv.DictReader(fichero), start=2):
            try:
                candidaturas.append(Candidatura.desde_fila(fila))
            except DatoNoValido as error:
                raise ErrorDeAlmacen(f"Línea {numero}: {error}") from error
    return candidaturas
