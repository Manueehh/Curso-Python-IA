"""Excepciones del gestor de candidaturas.

Jerarquía:

    ErrorDeCandidaturas (Exception)     base de todos los errores de la aplicación
    ├── DatoNoValido                    un dato de una candidatura no vale
    ├── CandidaturaNoEncontrada         no existe una candidatura con ese identificador
    ├── TransicionNoPermitida           el cambio de estado no está permitido
    ├── CandidaturaDuplicada            ya hay una activa a la misma empresa y puesto
    └── ErrorDeAlmacen                  el fichero de datos no se puede leer

``CandidaturaNoEncontrada(identificador)`` guarda el identificador en el
atributo ``identificador`` y su mensaje es "No existe la candidatura 7".

``TransicionNoPermitida(actual, nuevo)`` guarda los dos estados en los
atributos ``actual`` y ``nuevo`` y su mensaje es
"No se puede pasar de enviada a oferta".

``CandidaturaDuplicada(empresa, puesto)`` guarda los dos textos en los
atributos ``empresa`` y ``puesto`` y su mensaje es
"Ya hay una candidatura activa a Acme - Data Engineer".
"""


class ErrorDeCandidaturas(Exception):
    """Base de todos los errores de la aplicación."""


class DatoNoValido(ErrorDeCandidaturas):
    """Un dato de una candidatura no vale."""


class CandidaturaNoEncontrada(ErrorDeCandidaturas):
    """No existe una candidatura con ese identificador."""

    def __init__(self, identificador: int):
        super().__init__(f"No existe la candidatura {identificador}")
        self.identificador = identificador


class TransicionNoPermitida(ErrorDeCandidaturas):
    """El cambio de estado no está permitido."""

    def __init__(self, actual: str, nuevo: str):
        super().__init__(f"No se puede pasar de {actual} a {nuevo}")
        self.actual = actual
        self.nuevo = nuevo


class CandidaturaDuplicada(ErrorDeCandidaturas):
    """Ya hay una candidatura activa a la misma empresa y puesto."""

    def __init__(self, empresa: str, puesto: str):
        super().__init__(f"Ya hay una candidatura activa a {empresa} - {puesto}")
        self.empresa = empresa
        self.puesto = puesto


class ErrorDeAlmacen(ErrorDeCandidaturas):
    """El fichero de datos no se puede leer."""
