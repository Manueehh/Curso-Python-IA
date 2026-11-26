"""Gestor de candidaturas de empleo.

Paquete con la lógica de la aplicación:

    excepciones.py   errores propios
    modelos.py       la clase Candidatura y sus reglas
    gestor.py        GestorCandidaturas: las operaciones sobre el conjunto
    almacen.py       guardar y cargar en CSV
    informes.py      textos para mostrar por pantalla
    analisis.py      análisis del conjunto con pandas
"""

from .excepciones import (
    CandidaturaDuplicada,
    CandidaturaNoEncontrada,
    DatoNoValido,
    ErrorDeAlmacen,
    ErrorDeCandidaturas,
    TransicionNoPermitida,
)
from .gestor import GestorCandidaturas
from .modelos import Candidatura

__all__ = [
    "Candidatura",
    "CandidaturaDuplicada",
    "CandidaturaNoEncontrada",
    "DatoNoValido",
    "ErrorDeAlmacen",
    "ErrorDeCandidaturas",
    "GestorCandidaturas",
    "TransicionNoPermitida",
]
