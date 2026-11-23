"""Validación y normalización de textos."""

LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"


def esta_vacio(texto: str | None) -> bool:
    """Indica si el texto es ``None``, está vacío o solo contiene espacios.

    >>> esta_vacio("   ")
    True
    >>> esta_vacio(" a ")
    False
    """
    return texto is None or not texto.strip()


def normalizar_nombre(nombre: str) -> str:
    """Quita los espacios sobrantes y pone en mayúscula la inicial de cada palabra.

    >>> normalizar_nombre("  ada   LOVELACE ")
    'Ada Lovelace'
    """
    texto = nombre.strip()
    texto = " ".join(texto.split())
    return texto.title()


def es_email(texto: str) -> bool:
    """Comprueba de forma sencilla que el texto tiene forma de correo.

    Reglas: no contiene espacios, tiene exactamente una arroba, hay texto
    antes de la arroba, y el dominio contiene al menos un punto que no está
    ni al principio ni al final.

    >>> es_email("ada@ejemplo.com")
    True
    >>> es_email("ada@ejemplo")
    False
    """
    arrobas = texto.count("@")
    if arrobas != 1 or " " in texto:
        return False
    usuario, dominio = texto.split("@")
    if not usuario:
        return False
    return "." in dominio[1:-1]


def es_dni(texto: str) -> bool:
    """Comprueba que el texto es un DNI válido: ocho dígitos y la letra correcta.

    La letra se obtiene tomando el resto de dividir el número entre 23 y
    usándolo como posición en ``LETRAS_DNI``. Admite la letra en minúscula y
    espacios alrededor.

    >>> es_dni("12345678Z")
    True
    >>> es_dni("12345678A")
    False
    """
    texto = texto.strip().upper()
    if len(texto) != 9:
        return False
    letra = texto[8]
    numeros = texto[:8]
    if not (numeros.isascii() and numeros.isdigit()):
        return False
    division = int(numeros) % 23
    return LETRAS_DNI[division] == letra
