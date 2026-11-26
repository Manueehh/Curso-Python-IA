"""Gestor de candidaturas: aplicación de consola.

Este fichero es la única parte del proyecto que habla con el usuario: usa
``input`` y ``print``, captura los errores de la aplicación y decide cuándo
se guarda. Toda la lógica está en el paquete ``candidaturas``.

Uso: python app.py [fichero.csv]
"""

import sys
from datetime import date
from pathlib import Path

from candidaturas import DatoNoValido, ErrorDeAlmacen, ErrorDeCandidaturas, GestorCandidaturas
from candidaturas import almacen, analisis, informes
from candidaturas.modelos import ESTADOS, FUENTES, INTERESES, MODALIDADES, salario_desde_texto

RUTA_POR_DEFECTO = Path("candidaturas.csv")

MENU = """
GESTOR DE CANDIDATURAS
1. Alta de candidatura
2. Listar todas
3. Listar activas
4. Buscar por empresa o puesto
5. Cambiar estado
6. Seguimiento: sin respuesta
7. Informe
8. Análisis
0. Guardar y salir
"""


def pedir_numero() -> int:
    texto = input("Número de candidatura: ")
    try:
        return int(texto)
    except ValueError as error:
        raise DatoNoValido(f"El número de candidatura tiene que ser un entero: {texto}") from error


def alta(gestor: GestorCandidaturas) -> None:
    empresa = input("Empresa: ")
    puesto = input("Puesto: ")
    fuente = input(f"Fuente ({', '.join(FUENTES)}): ")
    interes = input(f"Interés ({', '.join(INTERESES)}) [medio]: ") or "medio"
    modalidad = input(f"Modalidad ({', '.join(MODALIDADES)}) [sin indicar]: ")
    salario = salario_desde_texto(input("Salario bruto anual en euros [sin indicar]: "))
    ubicacion = input("Ubicación [sin indicar]: ")
    candidatura = gestor.crear(empresa, puesto, fuente=fuente, interes=interes,
                               modalidad=modalidad, salario=salario, ubicacion=ubicacion)
    print(f"Creada la candidatura {candidatura.id}.")


def listar_todas(gestor: GestorCandidaturas) -> None:
    print(informes.listado(list(gestor)))


def listar_activas(gestor: GestorCandidaturas) -> None:
    print(informes.listado(gestor.activas()))


def buscar(gestor: GestorCandidaturas) -> None:
    print(informes.listado(gestor.buscar(input("Texto a buscar: "))))


def cambiar_estado(gestor: GestorCandidaturas) -> None:
    identificador = pedir_numero()
    nuevo = input(f"Nuevo estado ({', '.join(ESTADOS)}): ")
    candidatura = gestor.cambiar_estado(identificador, nuevo)
    print(f"La candidatura {candidatura.id} pasa a {candidatura.estado}.")


def seguimiento(gestor: GestorCandidaturas) -> None:
    print(informes.listado(gestor.sin_respuesta()))


def informe(gestor: GestorCandidaturas) -> None:
    print(informes.resumen(gestor, date.today()))


def ver_analisis(gestor: GestorCandidaturas) -> None:
    tabla = analisis.a_tabla(list(gestor))
    for clave, valor in analisis.indicadores(tabla, date.today()).items():
        print(f"{clave}: {valor}")
    print()
    print(analisis.respuesta_por_fuente(tabla).to_string())


OPCIONES = {
    "1": alta,
    "2": listar_todas,
    "3": listar_activas,
    "4": buscar,
    "5": cambiar_estado,
    "6": seguimiento,
    "7": informe,
    "8": ver_analisis,
}


def main(ruta=RUTA_POR_DEFECTO) -> int:
    """Ejecuta la aplicación. Devuelve 0 si termina bien y 1 si no puede arrancar.

    Contrato que comprueban los tests:

    1. Carga las candidaturas de ``ruta``. Si lanza ``ErrorDeAlmacen``,
       imprime un mensaje que empieza por "Error:" y devuelve 1 sin pedir nada.
    2. Repite: imprime ``MENU`` y pide una opción con ``input``.
    3. Una opción que no existe imprime "Opción no válida." y vuelve al menú.
    4. Si una operación lanza ``ErrorDeCandidaturas``, imprime "Error: " y el
       mensaje de la excepción, y vuelve al menú. El programa no termina.
    5. La opción 0 guarda las candidaturas en ``ruta``, imprime
       "Datos guardados. Hasta luego." y devuelve 0.

    Datos que pide cada opción, en este orden y con un ``input`` por dato:

    - 1: empresa, puesto, fuente, interés, modalidad, salario y ubicación.
         Un interés vacío es "medio"; modalidad, salario y ubicación pueden
         quedar vacíos. Imprime "Creada la candidatura N."
    - 4: el texto que buscar.
    - 5: el número de candidatura y el nuevo estado.
         Imprime "La candidatura N pasa a <estado>."
    - 2, 3, 6, 7 y 8 no piden nada.

    Un número de candidatura que no es un entero se trata como un error de la
    aplicación: mensaje "Error: ..." y vuelta al menú, sin pedir el dato
    siguiente.
    """
    try:
        gestor = GestorCandidaturas(almacen.cargar(ruta))
    except ErrorDeAlmacen as error:
        print(f"Error: {error}")
        return 1

    while True:
        print(MENU)
        opcion = input("Opción: ").strip()
        if opcion == "0":
            almacen.guardar(list(gestor), ruta)
            print("Datos guardados. Hasta luego.")
            return 0
        accion = OPCIONES.get(opcion)
        if accion is None:
            print("Opción no válida.")
            continue
        try:
            accion(gestor)
        except ErrorDeCandidaturas as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else RUTA_POR_DEFECTO))
