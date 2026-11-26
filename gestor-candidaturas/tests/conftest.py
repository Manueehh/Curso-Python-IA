"""Datos compartidos por los tests."""

from datetime import date
from pathlib import Path

import pytest

from candidaturas import GestorCandidaturas, almacen

HOY = date(2026, 11, 27)
RUTA_EJEMPLO = Path(__file__).parent.parent / "datos" / "candidaturas_ejemplo.csv"


@pytest.fixture
def ejemplo():
    """Las 12 candidaturas de ``datos/candidaturas_ejemplo.csv``."""
    return almacen.cargar(RUTA_EJEMPLO)


@pytest.fixture
def gestor(ejemplo):
    return GestorCandidaturas(ejemplo)
