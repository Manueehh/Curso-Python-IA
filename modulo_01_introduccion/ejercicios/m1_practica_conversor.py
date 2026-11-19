"""Módulo 1 - Práctica 1: conversor de unidades.

Lee el enunciado en PRACTICA_1.md.
"""

# 1. Define aquí las constantes KM_POR_MILLA y KG_POR_LIBRA
KM_POR_MILLA = 1.609344
KG_POR_LIBRA = 0.45359237
PIES_POR_METRO = 0.3048


def celsius_a_fahrenheit(grados):
    grados_farenheit = float(grados * 9 / 5 + 32)
    return grados_farenheit


def fahrenheit_a_celsius(grados):
    grados_celsius = float((grados - 32) * 5 / 9)
    return grados_celsius


def km_a_millas(km):
    millas = float(km / KM_POR_MILLA)
    return millas


def millas_a_km(millas):
    km = float(millas * KM_POR_MILLA)
    return km


def kg_a_libras(kg):
    libras = float(kg / KG_POR_LIBRA)
    return libras


def libras_a_kg(libras):
    kg = float(libras * KG_POR_LIBRA)
    return kg

def metros_a_pies(metros):
    pies = metros / PIES_POR_METRO
    return pies

def pies_a_metros(pies):
    metros = pies * PIES_POR_METRO
    return metros


def formatear(valor, unidad_origen, resultado, unidad_destino):
    """Devuelve el texto de la conversión con dos decimales.

    >>> formatear(100, "°C", 212.0, "°F")
    '100.00 °C = 212.00 °F'
    """
    return f"{valor:.2f} {unidad_origen} = {resultado:.2f} {unidad_destino}"


def main():
    """Muestra el menú, pide los datos e imprime el resultado."""
    while True:
        print("0. SALIR")
        print("1. °C -> °F")
        print("2. °F -> °C")
        print("3. km -> mi")
        print("4. mi -> km")
        print("5. kg -> lb")
        print("6. lb -> kg")
        print("7. m -> ft")
        print("8. ft -> m")

        opcion = input("Elige una opción: ")
        if opcion == "0":
            break
        valor = float(input("Introduce el valor: "))
        if opcion == "1":
            print(formatear(valor, "°C", celsius_a_fahrenheit(valor), "°F"))
        elif opcion == "2":
            print(formatear(valor, "°F", fahrenheit_a_celsius(valor), "°C"))
        elif opcion == "3":
            print(formatear(valor, "km", km_a_millas(valor), "mi"))
        elif opcion == "4":
            print(formatear(valor, "mi", millas_a_km(valor), "km"))
        elif opcion == "5":
            print(formatear(valor, "kg", kg_a_libras(valor), "lb"))
        elif opcion == "6":
            print(formatear(valor, "lb", libras_a_kg(valor), "kg"))
        elif opcion == "7":
            print(formatear(valor, "m", metros_a_pies(valor), "ft"))
        elif opcion == "8":
            print(formatear(valor, "ft", pies_a_metros(valor), "m"))
        else:
            print("Opción no válida.")



if __name__ == "__main__":
    main()
