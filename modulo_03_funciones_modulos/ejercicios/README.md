# Módulo 3. Ejercicios

Cada fichero contiene funciones con su firma y su docstring. El docstring dice exactamente qué debe hacer la función e incluye un ejemplo. Sustituye cada `raise NotImplementedError` por tu código y comprueba el resultado con:

```bash
pytest modulo_03_funciones_modulos -v
```

Para ejecutar solo los tests de un ejercicio:

```bash
pytest modulo_03_funciones_modulos -v -k ej1
```

Los ejemplos `>>>` de los docstrings también se pueden ejecutar como tests:

```bash
python -m doctest modulo_03_funciones_modulos/ejercicios/m3_ej1_funciones.py
```

Si no imprime nada, todos los ejemplos del fichero se cumplen.

## Ejercicio 1. Definición de funciones

Fichero: `m3_ej1_funciones.py`

| Función | Qué practica |
| --- | --- |
| `area_circulo(radio)` | Definir, documentar y devolver un valor |
| `area_rectangulo(base, altura)` | Varios parámetros |
| `area_triangulo(base, altura)` | División real |
| `calcular_area(figura, *, radio, base, altura)` | Una función que coordina a otras y parámetros solo por nombre |
| `minimo_y_maximo(*numeros)` | Retorno múltiple y `*args` |
| `describir(funcion)` | Las funciones son objetos: `__name__` y `__doc__` |

`calcular_area` no debe repetir ninguna fórmula: tiene que llamar a las tres funciones anteriores.

## Ejercicio 2. Parámetros y retorno

Fichero: `m3_ej2_parametros.py`

| Función | Qué practica |
| --- | --- |
| `potencia(base, exponente=2)` | Valores por defecto |
| `sumar_todos(*numeros)` | `*args` |
| `crear_usuario(nombre, *, activo=True, **extras)` | Solo por nombre y `**kwargs` |
| `anadir_elemento(elemento, lista=None)` | El error del valor por defecto mutable |
| `formatear_nombre(nombre, apellido, *, mayusculas, separador)` | Opciones solo por nombre |
| `estadisticas(*numeros)` | Retorno múltiple con caso vacío |

Antes de resolver `anadir_elemento`, escríbela mal a propósito con `lista=[]`, ejecuta los tests y lee el mensaje del que falla.

## Ejercicio 3. Ámbito, cierres y funciones como argumento

Fichero: `m3_ej3_ambito.py`

| Función | Qué practica |
| --- | --- |
| `crear_contador(inicio=0)` | Cierre con estado y `nonlocal` |
| `multiplicador(factor)` | Cierre que recuerda un parámetro |
| `aplicar(funcion, valores)` | Función de orden superior |
| `componer(f, g)` | Devolver una función construida a partir de otras |
| `ordenar_por_longitud(palabras)` | `sorted()` con `key` |
| `mas_caro(productos)` | `max()` con `key` y una `lambda` |

En este fichero no se puede usar `global`. Hay un test que lo comprueba.

## Ejercicio 4. Librería estándar

Fichero: `m3_ej4_libreria.py`

| Función | Módulo que necesitas |
| --- | --- |
| `hipotenusa(cateto_a, cateto_b)` | `math` |
| `dias_entre(fecha_inicio, fecha_fin)` | `datetime` |
| `es_fin_de_semana(fecha_iso)` | `datetime` |
| `extension(ruta)` | `pathlib` |
| `palabra_mas_frecuente(texto)` | `collections` |
| `tirar_dados(cantidad, caras=6, semilla=None)` | `random` |

Los `import` no están escritos: decide tú qué importar y cómo. Antes de escribir un bucle, busca en la documentación del módulo si ya hay una función que hace lo que necesitas.

## Si terminas antes

1. Añade un doctest más a tres funciones y ejecútalos con `python -m doctest`.
2. Escribe `memorizar(funcion)`: devuelve una versión de `funcion` que guarda en un diccionario los resultados ya calculados y no vuelve a calcularlos. Es un cierre con estado.
3. Reescribe `aplicar` usando la función integrada `map()` y compara las dos versiones.

## USO DE IA
Ninguno, las dudas fueron consultadas mediante foros como StackOverflow