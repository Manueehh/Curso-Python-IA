"""Módulo 2 - Ejercicio 4: bucles."""

VOCALES = "aeiouáéíóúü"


def factorial(n: int) -> int:
    """Devuelve el factorial de ``n`` (n >= 0) usando un bucle.

    >>> factorial(5), factorial(0)
    (120, 1)
    """
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado


def es_primo(n: int) -> bool:
    """Indica si ``n`` es un número primo.

    >>> es_primo(13), es_primo(15), es_primo(1)
    (True, False, False)
    """
    if n < 2:
        return False
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 1
    return True


def invertir(texto: str) -> str:
    """Devuelve ``texto`` del revés usando un bucle.

    >>> invertir("Python")
    'nohtyP'
    """
    resultado = ""
    for caracter in texto:
        resultado = caracter + resultado
    return resultado


def contar_vocales(texto: str) -> int:
    """Cuenta las vocales de ``texto``, sin distinguir mayúsculas ni tildes.

    >>> contar_vocales("Programación")
    5
    """
    contador = 0
    for caracter in texto.lower():
        if caracter in VOCALES:
            contador += 1
    return contador


def suma_digitos(numero: int) -> int:
    """Suma los dígitos de un entero, ignorando el signo. Usa un while.

    >>> suma_digitos(1234), suma_digitos(-905)
    (10, 14)
    """
    numero = abs(numero)
    suma = 0
    while numero > 0:
        suma += numero % 10
        numero //= 10
    return suma


def fizzbuzz(n: int) -> str:
    """Devuelve la secuencia FizzBuzz de 1 a ``n`` separada por espacios.

    Los múltiplos de 3 se sustituyen por "Fizz", los de 5 por "Buzz" y los de
    ambos por "FizzBuzz".

    >>> fizzbuzz(5)
    '1 2 Fizz 4 Buzz'
    """
    partes = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            partes.append("FizzBuzz")
        elif i % 3 == 0:
            partes.append("Fizz")
        elif i % 5 == 0:
            partes.append("Buzz")
        else:
            partes.append(str(i))
    return " ".join(partes)


def tabla_multiplicar(numero: int) -> str:
    """Devuelve la tabla de multiplicar del 1 al 10, una línea por producto.

    >>> print(tabla_multiplicar(7).splitlines()[2])
    7 x  3 =  21
    """
    lineas = []
    for i in range(1, 11):
        lineas.append(f"{numero} x {i:2d} = {numero * i:3d}")
    return "\n".join(lineas)


def primer_multiplo_comun(a: int, b: int) -> int:
    """Devuelve el mínimo común múltiplo de dos enteros positivos con un while.

    >>> primer_multiplo_comun(4, 6)
    12
    """
    mayor = a if a > b else b
    multiplo = mayor
    while multiplo % a != 0 or multiplo % b != 0:
        multiplo += mayor
    return multiplo