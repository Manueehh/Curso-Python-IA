# Módulo 4. Ejercicios

Cada fichero contiene funciones con su firma y su docstring. Sustituye cada `raise NotImplementedError` por tu código y comprueba el resultado con:

```bash
pytest modulo_04_colecciones -v
```

Para ejecutar solo los tests de un ejercicio:

```bash
pytest modulo_04_colecciones -v -k ej3
```

Una norma para todo el módulo: **ninguna función modifica los datos que recibe**. Si necesitas transformarlos, devuelve una colección nueva. Hay tests que lo comprueban.

## Ejercicio 1. Listas

Fichero: `m4_ej1_listas.py`

| Función | Qué practica |
| --- | --- |
| `extremos(lista)` | Índices negativos y caso vacío |
| `rotar(lista, posiciones)` | Slicing y concatenación |
| `segundo_mayor(numeros)` | Ordenar y eliminar repetidos |
| `trocear(lista, tamano)` | Slicing con `range` de paso |
| `sin_duplicados(lista)` | Eliminar repetidos conservando el orden |
| `insertar_ordenado(ordenada, valor)` | Construir una lista nueva sin tocar la original |
| `crear_tablero(filas, columnas, valor)` | La trampa de `[[0] * n] * m` |

## Ejercicio 2. Tuplas y diccionarios

Fichero: `m4_ej2_diccionarios.py`

| Función | Qué practica |
| --- | --- |
| `punto_medio(a, b)` | Desempaquetado de tuplas |
| `contar_palabras(texto)` | El patrón de contar con `get()` |
| `invertir(diccionario)` | Recorrido con `items()` |
| `notas_medias(estudiantes)` | Diccionario de listas |
| `mejor_estudiante(estudiantes)` | `max()` con `key` sobre un diccionario |
| `total_carrito(carrito)` | Lista de tuplas y desempaquetado en el `for` |
| `fusionar_inventarios(a, b)` | Copiar y actualizar sin modificar los originales |
| `valor_anidado(datos, ruta, por_defecto)` | Diccionarios anidados |

`mejor_estudiante` debe reutilizar `notas_medias`.

## Ejercicio 3. Conjuntos

Fichero: `m4_ej3_conjuntos.py`

| Función | Operación |
| --- | --- |
| `elementos_comunes(a, b)` | Intersección |
| `solo_en_una(a, b)` | Diferencia simétrica |
| `tiene_duplicados(elementos)` | Comparar longitudes |
| `duplicados(elementos)` | Conjunto de vistos |
| `es_pangrama(frase)` | Subconjunto |
| `permisos_que_faltan(requeridos, concedidos)` | Diferencia |
| `habilidades_compartidas(equipo)` | Intersección de varios conjuntos |

Reto: todas menos `duplicados` y `habilidades_compartidas` se pueden escribir en una sola línea.

## Ejercicio 4. Comprensiones

Fichero: `m4_ej4_comprensiones.py`

Cada función se resuelve con **una sola línea `return`** que contiene una comprensión o una expresión generadora. Hay un test que comprueba que el cuerpo de cada función es una única sentencia.

| Función | Tipo |
| --- | --- |
| `cuadrados_de_pares(limite)` | Lista con filtro |
| `longitudes(palabras)` | Diccionario |
| `iniciales(nombres)` | Conjunto con filtro |
| `limpiar(textos)` | Lista con transformación y filtro |
| `filtrar_por_precio(precios, maximo)` | Diccionario con filtro |
| `aplanar(matriz)` | Dos `for` |
| `trasponer(matriz)` | Anidada o con `zip(*matriz)` |
| `suma_de_importes(lineas)` | Expresión generadora dentro de `sum()` |

Si te atascas, escribe primero la versión con bucle, comprueba que pasa el test de funcionamiento y después conviértela.

## Ejercicio 5. Cadenas

Fichero: `m4_ej5_cadenas.py`

| Función | Qué practica |
| --- | --- |
| `es_palindromo(texto)` | Filtrar caracteres y slicing inverso |
| `contar_vocales(texto)` | Recorrer una cadena y `in` |
| `invertir_palabras(frase)` | `split()` y `join()` |
| `a_snake_case(texto)` | `replace()`, `lower()`, `split()` y `join()` |
| `enmascarar(numero, visibles)` | Slicing y repetición |
| `son_anagramas(a, b)` | `sorted()` sobre cadenas |
| `parsear_configuracion(texto)` | `split()` con límite y `strip()` |
| `formatear_tabla(filas)` | f-strings con alineación y `join()` |

## Ejercicio 6. Buscar, filtrar, ordenar y agrupar

Fichero: `m4_ej6_datos.py`

Todas las funciones reciben una lista de diccionarios como la del comentario inicial del fichero.

| Función | Equivalente en SQL |
| --- | --- |
| `buscar_por_id(registros, identificador)` | `WHERE id = ?` |
| `nombres(registros)` | `SELECT nombre` |
| `filtrar(registros, campo, valor)` | `WHERE campo = ?` |
| `ordenar_por(registros, campo, descendente)` | `ORDER BY campo` |
| `mejor_pagados(registros, cantidad)` | `ORDER BY salario DESC, nombre LIMIT n` |
| `agrupar_por(registros, campo)` | `GROUP BY campo` |
| `salario_medio_por_departamento(registros)` | `SELECT AVG(salario) ... GROUP BY departamento` |
| `emparejar(claves, filas)` | Convertir filas en registros |

`salario_medio_por_departamento` debe reutilizar `agrupar_por`.

## Si terminas antes

1. Reescribe `contar_palabras` con `collections.Counter` y `agrupar_por` con `defaultdict`.
2. Escribe `ordenar_por_varios(registros, campos)`, que ordena por una lista de campos. Pista: `operator.itemgetter(*campos)`.
3. Vuelve a `calcular_irpf` de la Práctica 2 y reescríbela con una lista de tuplas `(limite, tipo)` y un bucle, de forma que añadir un tramo no obligue a tocar el código.


## USO DE IA EN ESTE BLOQUE
Especialmente para los ejercicios de comprensiones, era algo que no habia visto mucho quitando algunas cosas sueltas, y me ha ayudado a comprenderlas bien (habia desarrollado el codigo sin compresion pero los tests me fallaban, y ahi es cuando ha intervenido la IA)