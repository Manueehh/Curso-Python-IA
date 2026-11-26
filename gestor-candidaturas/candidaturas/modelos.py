"""Modelo de dominio: la candidatura y sus reglas."""

from dataclasses import dataclass
from datetime import date

from .excepciones import DatoNoValido, TransicionNoPermitida

ESTADOS = ("enviada", "entrevista", "prueba_tecnica", "oferta",
           "aceptada", "rechazada", "descartada")
ACTIVOS = ("enviada", "entrevista", "prueba_tecnica", "oferta")
FINALES = ("aceptada", "rechazada", "descartada")
INTERESES = ("bajo", "medio", "alto")
FUENTES = ("linkedin", "infojobs", "web_empresa", "referido", "otra")
MODALIDADES = ("remoto", "hibrido", "presencial")

# Desde cada estado, a cuáles se puede pasar
TRANSICIONES = {
    "enviada": ("entrevista", "prueba_tecnica", "rechazada", "descartada"),
    "entrevista": ("prueba_tecnica", "oferta", "rechazada", "descartada"),
    "prueba_tecnica": ("entrevista", "oferta", "rechazada", "descartada"),
    "oferta": ("aceptada", "descartada"),
    "aceptada": (),
    "rechazada": (),
    "descartada": (),
}

DIAS_SIN_RESPUESTA = 15

CAMPOS = ["id", "empresa", "puesto", "fuente", "interes", "estado",
          "fecha_envio", "fecha_respuesta", "fecha_cierre",
          "modalidad", "salario", "ubicacion", "enlace", "notas"]

# Campos añadidos después de la primera versión: un CSV antiguo puede no tenerlos
CAMPOS_OPCIONALES = ("modalidad", "salario", "ubicacion", "enlace", "notas")


@dataclass
class Candidatura:
    """Una candidatura a una oferta de empleo.

    Campos, en este orden:

    - ``id`` (int)
    - ``empresa`` (str)
    - ``puesto`` (str)
    - ``fuente`` (str)
    - ``fecha_envio`` (date)
    - ``interes`` (str), por defecto "medio"
    - ``estado`` (str), por defecto "enviada"
    - ``fecha_respuesta`` (date o None), por defecto None
    - ``fecha_cierre`` (date o None), por defecto None
    - ``modalidad`` (str), una de ``MODALIDADES`` o la cadena vacía si no se sabe
    - ``salario`` (int o None): bruto anual en euros, None si no se sabe
    - ``ubicacion`` (str), por defecto la cadena vacía
    - ``enlace`` (str): URL de la oferta, por defecto la cadena vacía
    - ``notas`` (str), por defecto la cadena vacía
    """

    id: int
    empresa: str
    puesto: str
    fuente: str
    fecha_envio: date
    interes: str = "medio"
    estado: str = "enviada"
    fecha_respuesta: date | None = None
    fecha_cierre: date | None = None
    modalidad: str = ""
    salario: int | None = None
    ubicacion: str = ""
    enlace: str = ""
    notas: str = ""

    def __post_init__(self):
        """Limpia y valida los datos.

        Quita los espacios de alrededor de los textos, y pasa ``fuente``,
        ``interes``, ``estado`` y ``modalidad`` a minúsculas. Lanza
        ``DatoNoValido`` con uno de estos mensajes:

        - "La empresa es obligatoria"
        - "El puesto es obligatorio"
        - "Fuente no válida: <valor>"
        - "Interés no válido: <valor>"
        - "Estado no válido: <valor>"
        - "Modalidad no válida: <valor>"
        - "El salario no puede ser negativo"
        - "El enlace tiene que empezar por http:// o https://"
        """
        self.empresa = self.empresa.strip()
        self.puesto = self.puesto.strip()
        self.fuente = self.fuente.strip().lower()
        self.interes = self.interes.strip().lower()
        self.estado = self.estado.strip().lower()
        self.modalidad = self.modalidad.strip().lower()
        self.ubicacion = self.ubicacion.strip()
        self.enlace = self.enlace.strip()
        self.notas = self.notas.strip()
        if not self.empresa:
            raise DatoNoValido("La empresa es obligatoria")
        if not self.puesto:
            raise DatoNoValido("El puesto es obligatorio")
        if self.fuente not in FUENTES:
            raise DatoNoValido(f"Fuente no válida: {self.fuente}")
        if self.interes not in INTERESES:
            raise DatoNoValido(f"Interés no válido: {self.interes}")
        if self.estado not in ESTADOS:
            raise DatoNoValido(f"Estado no válido: {self.estado}")
        if self.modalidad and self.modalidad not in MODALIDADES:
            raise DatoNoValido(f"Modalidad no válida: {self.modalidad}")
        if self.salario is not None and self.salario < 0:
            raise DatoNoValido("El salario no puede ser negativo")
        if self.enlace and not self.enlace.startswith(("http://", "https://")):
            raise DatoNoValido("El enlace tiene que empezar por http:// o https://")

    @property
    def activa(self) -> bool:
        """Indica si la candidatura sigue en marcha (estado de ``ACTIVOS``)."""
        return self.estado in ACTIVOS

    def dias_desde_envio(self, hoy: date) -> int:
        """Días transcurridos desde el envío hasta ``hoy``."""
        return (hoy - self.fecha_envio).days

    def sin_respuesta(self, hoy: date) -> bool:
        """Indica si sigue "enviada" tras ``DIAS_SIN_RESPUESTA`` días o más."""
        return self.estado == "enviada" and self.dias_desde_envio(hoy) >= DIAS_SIN_RESPUESTA

    def cambiar_estado(self, nuevo: str, hoy: date) -> None:
        """Pasa la candidatura al estado ``nuevo``.

        Lanza ``DatoNoValido`` ("Estado no válido: <valor>") si el estado no
        existe y ``TransicionNoPermitida`` si ``TRANSICIONES`` no permite el
        cambio desde el estado actual.

        - Al salir de "enviada" hacia cualquier estado salvo "descartada", se
          guarda ``hoy`` en ``fecha_respuesta``: la empresa ha contestado.
        - Al llegar a un estado de ``FINALES`` se guarda ``hoy`` en
          ``fecha_cierre``.
        """
        nuevo = nuevo.strip().lower()
        if nuevo not in ESTADOS:
            raise DatoNoValido(f"Estado no válido: {nuevo}")
        if nuevo not in TRANSICIONES[self.estado]:
            raise TransicionNoPermitida(self.estado, nuevo)
        if self.estado == "enviada" and nuevo != "descartada":
            self.fecha_respuesta = hoy
        if nuevo in FINALES:
            self.fecha_cierre = hoy
        self.estado = nuevo

    def a_fila(self) -> dict[str, str]:
        """Devuelve la candidatura como diccionario de cadenas, con las claves de ``CAMPOS``.

        Las fechas van en formato ISO y una fecha o un salario ausentes son la
        cadena vacía. Es lo que se escribe en el CSV.
        """
        return {
            "id": str(self.id),
            "empresa": self.empresa,
            "puesto": self.puesto,
            "fuente": self.fuente,
            "interes": self.interes,
            "estado": self.estado,
            "fecha_envio": self.fecha_envio.isoformat(),
            "fecha_respuesta": _fecha_a_texto(self.fecha_respuesta),
            "fecha_cierre": _fecha_a_texto(self.fecha_cierre),
            "modalidad": self.modalidad,
            "salario": "" if self.salario is None else str(self.salario),
            "ubicacion": self.ubicacion,
            "enlace": self.enlace,
            "notas": self.notas,
        }

    @classmethod
    def desde_fila(cls, fila: dict[str, str]) -> "Candidatura":
        """Crea una candidatura a partir de un diccionario de cadenas como el de ``a_fila``.

        Es lo que se lee del CSV. Los ``CAMPOS_OPCIONALES`` pueden faltar (un
        CSV de la primera versión no los tiene) y toman su valor por defecto.
        Lanza ``DatoNoValido`` si falta algún otro campo, si el identificador
        o el salario no son enteros o si alguna fecha no es una fecha ISO,
        encadenando la excepción original. La validación de
        ``__post_init__`` se aplica igualmente.
        """
        opcionales = {campo: fila.get(campo) or "" for campo in CAMPOS_OPCIONALES}
        try:
            return cls(
                id=int(fila["id"]),
                empresa=fila["empresa"],
                puesto=fila["puesto"],
                fuente=fila["fuente"],
                fecha_envio=date.fromisoformat(fila["fecha_envio"]),
                interes=fila["interes"],
                estado=fila["estado"],
                fecha_respuesta=_texto_a_fecha(fila["fecha_respuesta"]),
                fecha_cierre=_texto_a_fecha(fila["fecha_cierre"]),
                modalidad=opcionales["modalidad"],
                salario=int(opcionales["salario"]) if opcionales["salario"] else None,
                ubicacion=opcionales["ubicacion"],
                enlace=opcionales["enlace"],
                notas=opcionales["notas"],
            )
        except KeyError as error:
            raise DatoNoValido(f"Falta el campo {error}") from error
        except ValueError as error:
            raise DatoNoValido(f"Dato con formato incorrecto: {error}") from error


def salario_desde_texto(texto: str) -> int | None:
    """Convierte lo que escribe una persona en un salario anual en euros.

    Admite puntos de miles, el símbolo del euro, espacios y una "k" final
    para miles. Un texto vacío es ``None``. Lanza ``DatoNoValido`` con el
    mensaje "Salario no válido: <texto>" si no es un número entero.

    >>> salario_desde_texto("35.000 €"), salario_desde_texto("32k"), salario_desde_texto("")
    (35000, 32000, None)
    """
    limpio = texto.strip().lower().replace(".", "").replace("€", "").replace(" ", "")
    if not limpio:
        return None
    multiplicador = 1000 if limpio.endswith("k") else 1
    numero = limpio.removesuffix("k")
    if not (numero.isascii() and numero.isdigit()):
        raise DatoNoValido(f"Salario no válido: {texto.strip()}")
    return int(numero) * multiplicador


def _fecha_a_texto(fecha: date | None) -> str:
    return fecha.isoformat() if fecha else ""


def _texto_a_fecha(texto: str) -> date | None:
    return date.fromisoformat(texto) if texto else None
