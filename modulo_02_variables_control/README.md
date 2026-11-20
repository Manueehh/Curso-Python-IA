# Módulo 2. Variables, operadores y estructuras de control (6 horas)

Al terminar este módulo resolverás problemas de programación estructurada en Python idiomático: sabrás cómo se comportan los tipos básicos, qué es realmente una variable y cómo se escriben condicionales y bucles sin arrastrar costumbres de otros lenguajes.

| Unidad | Contenido | Tiempo |
| --- | --- | --- |
| 2.1 | Tipos de datos | 0,75 h |
| 2.2 | Variables y constantes | 0,5 h |
| 2.3 | Operadores | 0,75 h |
| 2.4 | Entrada y salida | 0,5 h |
| 2.5 | Condicionales | 0,75 h |
| 2.6 | Bucles for y while | 1,25 h |
| 2.7 | Ejercicios prácticos y práctica 2 | 1,5 h |

---

## 2.1 Tipos de datos

Python tiene pocos tipos básicos y todos son objetos. No hay tipos primitivos.

| Tipo | Qué representa | Ejemplos | Mutable |
| --- | --- | --- | --- |
| `int` | Enteros de precisión arbitraria | `42`, `-7`, `1_000_000` | No |
| `float` | Coma flotante de 64 bits | `3.14`, `1e-3`, `2.0` | No |
| `bool` | Valores lógicos | `True`, `False` | No |
| `str` | Texto Unicode | `"hola"`, `'adiós'` | No |
| `NoneType` | Ausencia de valor | `None` | No |

Las colecciones (`list`, `tuple`, `dict`, `set`) tienen su propio módulo.

### Enteros

Los enteros no desbordan. No existen `short`, `long` ni `BigInteger`: hay un único tipo `int` que crece lo que haga falta.

```python
>>> 2 ** 200
1606938044258990275541962092341162602522202993782792835301376
>>> 1_000_000          # el guion bajo separa miles y se ignora
1000000
>>> 0b1010, 0o17, 0xFF  # binario, octal y hexadecimal
(10, 15, 255)
```

### Números en coma flotante

`float` es un doble de 64 bits según IEEE 754, igual que el `double` de Java o C#. Tiene los mismos problemas de representación:

```python
>>> 0.1 + 0.2
0.30000000000000004
>>> 0.1 + 0.2 == 0.3
False
```

Cómo convivir con ello:

```python
import math
from decimal import Decimal

math.isclose(0.1 + 0.2, 0.3)             # True: comparación con tolerancia
round(0.1 + 0.2, 2)                      # 0.3: redondeo para presentar
Decimal("0.1") + Decimal("0.2")          # Decimal('0.3'): aritmética exacta para dinero
```

Regla práctica: nunca compares dos `float` con `==` y nunca uses `float` para importes monetarios en un sistema real.

### Booleanos

`True` y `False` van con mayúscula inicial. `bool` es una subclase de `int`, de modo que `True` vale 1 y `False` vale 0. No es algo que debas explotar, pero explica resultados como este:

```python
>>> True + True
2
>>> sum([True, False, True])   # cuenta cuántos son verdaderos
2
```

### Cadenas

Una cadena es una secuencia inmutable de caracteres Unicode. Se escribe con comillas simples o dobles, sin diferencia entre ambas. No existe un tipo `char`: un carácter es una cadena de longitud 1.

```python
nombre = "Ada"
frase = 'Dijo "hola" y se fue'
varias_lineas = """Primera línea
Segunda línea"""

len(nombre)          # 3
nombre[0]            # 'A'
nombre[-1]           # 'a': los índices negativos cuentan desde el final
nombre + " Lovelace" # concatenación
nombre * 3           # 'AdaAdaAda'
"da" in nombre       # True
```

Inmutable significa que ninguna operación cambia la cadena original; todas devuelven una nueva:

```python
>>> nombre = "ada"
>>> nombre.upper()
'ADA'
>>> nombre
'ada'
>>> nombre[0] = "A"
TypeError: 'str' object does not support item assignment
```

La manipulación de cadenas a fondo se ve en el Módulo 4.

### None

`None` es el único valor del tipo `NoneType` y representa «no hay valor». Es el equivalente de `null`. Se comprueba con `is`, no con `==`:

```python
resultado = None

if resultado is None:
    print("Todavía no hay resultado")
```

Una función que no ejecuta ningún `return` devuelve `None`.

### Conversión entre tipos

Python no convierte tipos por su cuenta, salvo entre números. La conversión se pide llamando al tipo como si fuera una función:

```python
int("42")        # 42
int(3.99)        # 3: trunca, no redondea
float("3.5")     # 3.5
str(42)          # '42'
bool(0)          # False
int("hola")      # ValueError: no se puede convertir
```

```python
>>> 3 + 2.5          # int y float se mezclan sin problema
5.5
>>> "3" + 2
TypeError: can only concatenate str (not "int") to str
```

### Comprobar el tipo

```python
type(42)                  # <class 'int'>
isinstance(42, int)       # True
isinstance(42, (int, float))  # True: admite una tupla de tipos
```

Usa `isinstance()` y no `type(x) == int`, porque `isinstance` respeta la herencia.

---

## 2.2 Variables y constantes

### Una variable es un nombre, no una caja

Esta es la idea más importante del módulo. En C o Java una variable de tipo primitivo es un hueco de memoria que contiene el valor. En Python una variable es una **etiqueta** que apunta a un objeto. La asignación nunca copia datos: solo hace que un nombre apunte a un objeto.

```python
a = [1, 2, 3]
b = a            # b apunta al MISMO objeto que a
b.append(4)
print(a)         # [1, 2, 3, 4]
```

`a` y `b` son dos nombres para una única lista. Lo puedes comprobar con `id()`, que devuelve la identidad del objeto, y con el operador `is`:

```python
>>> a is b
True
>>> id(a) == id(b)
True
```

Si vienes de Java, es el mismo comportamiento que las referencias a objetos. La diferencia es que en Python ocurre con **todos** los valores, también con los números.

### Mutables e inmutables

¿Por qué con los números no se nota?

```python
x = 10
y = x
y = y + 1
print(x)   # 10
```

Porque `int` es inmutable. `y + 1` no modifica el objeto `10`: crea un objeto nuevo, `11`, y hace que `y` apunte a él. `x` sigue apuntando al `10`.

| Inmutables | Mutables |
| --- | --- |
| `int`, `float`, `bool`, `str`, `tuple`, `None` | `list`, `dict`, `set` y casi todos los objetos propios |

La consecuencia práctica: cuando pasas una lista a una función y la función la modifica, el cambio se ve fuera. Volveremos a ello en los Módulos 3 y 4.

### Tipado dinámico

El tipo pertenece al objeto, no al nombre. Un mismo nombre puede apuntar a objetos de distinto tipo a lo largo del programa:

```python
dato = 10
dato = "diez"     # válido, aunque desaconsejable
```

Que el lenguaje lo permita no quiere decir que sea buena idea. Reutilizar un nombre para tipos distintos hace el código difícil de seguir.

### Anotaciones de tipo

Python permite anotar los tipos. Las anotaciones no cambian la ejecución: el intérprete las ignora. Sirven de documentación y las usan el editor y herramientas de análisis como `mypy` o Pylance para avisarte de errores antes de ejecutar.

```python
edad: int = 30
nombre: str = "Lucía"
precio: float = 19.99


def aplicar_descuento(precio: float, porcentaje: float) -> float:
    return precio * (1 - porcentaje / 100)
```

En proyectos profesionales es habitual anotar al menos las firmas de las funciones. A partir de este módulo las verás en los ejercicios.

### Asignación múltiple e intercambio

```python
x, y = 10, 20            # asignación múltiple
x, y = y, x              # intercambio sin variable temporal
a = b = c = 0            # los tres nombres apuntan al mismo 0
contador += 1            # asignación aumentada: +=, -=, *=, /=, //=, %=, **=
```

No existen los operadores `++` ni `--`. Se escribe `contador += 1`.

### Constantes

Python no tiene constantes de verdad. La convención es escribir el nombre en mayúsculas y que nadie lo reasigne:

```python
IVA_GENERAL = 21
MAX_INTENTOS = 3
URL_BASE = "https://api.ejemplo.com"
```

Se declaran al principio del módulo, después de los `import`. El lenguaje no impide cambiarlas; lo impiden la convención y la revisión de código.

---

## 2.3 Operadores

### Aritméticos

| Operador | Operación | Ejemplo | Resultado |
| --- | --- | --- | --- |
| `+` `-` `*` | Suma, resta, producto | `7 * 2` | `14` |
| `/` | División real, siempre `float` | `7 / 2` | `3.5` |
| `//` | División entera, redondea hacia abajo | `7 // 2` | `3` |
| `%` | Resto | `7 % 2` | `1` |
| `**` | Potencia | `2 ** 10` | `1024` |

Tres diferencias con Java y C#:

```python
>>> 8 / 2        # la división real devuelve float aunque sea exacta
4.0
>>> -7 // 2      # redondea hacia menos infinito (en Java, -7 / 2 es -3)
-4
>>> -7 % 2       # el resto toma el signo del divisor (en Java es -1)
1
```

`divmod(a, b)` devuelve cociente y resto a la vez: `divmod(17, 5)` es `(3, 2)`.

### De comparación

`==`, `!=`, `<`, `<=`, `>`, `>=`. Devuelven `bool` y se pueden **encadenar**, como en matemáticas:

```python
edad = 25
18 <= edad < 65          # True. Equivale a: 18 <= edad and edad < 65
```

### Lógicos

Se escriben con palabras: `and`, `or`, `not`. No existen `&&`, `||` ni `!`.

```python
es_adulto = edad >= 18
tiene_permiso = True

if es_adulto and tiene_permiso:
    ...
if not es_adulto or edad > 80:
    ...
```

Evalúan en cortocircuito, de izquierda a derecha. Y un detalle propio de Python: `and` y `or` no devuelven `True` o `False`, sino **uno de sus operandos**.

```python
>>> "Ada" or "Anónimo"     # el primero que sea verdadero
'Ada'
>>> "" or "Anónimo"
'Anónimo'
>>> 0 and 10 / 0           # no llega a evaluar la división
0
```

De ahí sale un modismo muy común para valores por defecto: `nombre = entrada or "Anónimo"`.

### Valores verdaderos y falsos (truthy y falsy)

Cualquier objeto se puede usar como condición. Se consideran falsos:

- `False` y `None`
- El cero de cualquier tipo numérico: `0`, `0.0`
- Las colecciones y cadenas vacías: `""`, `[]`, `()`, `{}`, `set()`

Todo lo demás es verdadero. Por eso la forma idiomática de comprobar si algo está vacío es:

```python
if not nombre:          # en lugar de: if nombre == "" o if len(nombre) == 0
    print("Falta el nombre")

if elementos:           # en lugar de: if len(elementos) > 0
    procesar(elementos)
```

Cuidado con un caso: si `0` es un valor válido, `if not cantidad` lo tratará como ausente. Cuando quieras distinguir «no hay valor» de «el valor es cero», compara con `is None`.

### Identidad y pertenencia

| Operador | Pregunta |
| --- | --- |
| `==` | ¿Tienen el mismo **valor**? |
| `is` | ¿Son el mismo **objeto**? |
| `in` | ¿Está contenido en la colección o cadena? |

```python
>>> a = [1, 2]
>>> b = [1, 2]
>>> a == b
True
>>> a is b
False
>>> 2 in a
True
>>> "py" in "python"
True
```

Regla: usa `is` solo para comparar con `None`, `True` o `False`. Para todo lo demás, `==`.

Es el error inverso al de Java: allí `==` compara referencias y hay que usar `.equals()`; en Python `==` compara valores, que es casi siempre lo que quieres.

### Expresión condicional

El operador ternario se escribe en otro orden: primero el valor, luego la condición.

```python
estado = "adulto" if edad >= 18 else "menor"
# En Java: String estado = edad >= 18 ? "adulto" : "menor";
```

### Precedencia

De mayor a menor: `**`, signo unario, `*` `/` `//` `%`, `+` `-`, comparaciones, `not`, `and`, `or`. Ante la duda, paréntesis: `(a and b) or c` se lee mejor que `a and b or c`.

---

## 2.4 Entrada y salida

### print

```python
print("Total:", 42)                 # varios argumentos separados por un espacio
print("a", "b", "c", sep="-")       # a-b-c
print("Sin salto", end="")          # no añade salto de línea
print()                             # línea en blanco
```

### f-strings

Una f-string es una cadena con el prefijo `f` que evalúa las expresiones entre llaves. Es la forma recomendada de construir texto.

```python
nombre, edad = "Ada", 36
print(f"{nombre} tiene {edad} años")
print(f"El doble de su edad es {edad * 2}")
print(f"{nombre.upper()!r}")        # !r muestra la representación: 'ADA'
print(f"{edad = }")                 # útil para depurar: edad = 36
```

Después de dos puntos va la **especificación de formato**:

| Formato | Efecto | Ejemplo | Resultado |
| --- | --- | --- | --- |
| `.2f` | Dos decimales | `f"{3.14159:.2f}"` | `3.14` |
| `,` | Separador de miles | `f"{1234567:,}"` | `1,234,567` |
| `.1%` | Porcentaje | `f"{0.256:.1%}"` | `25.6%` |
| `>8` | Alinear a la derecha en 8 | `f"{42:>8}"` | `      42` |
| `<8` | Alinear a la izquierda | `f"{'ab':<8}\|"` | `ab      \|` |
| `^8` | Centrar | `f"{'ab':^8}"` | `   ab   ` |
| `05d` | Rellenar con ceros | `f"{42:05d}"` | `00042` |

Se combinan: `f"{precio:>10.2f}"` alinea a la derecha en 10 caracteres con dos decimales. Así se construyen tablas de texto:

```python
print(f"{'Concepto':<15}{'Importe':>10}")
print(f"{'Salario base':<15}{1850.5:>10.2f}")
print(f"{'Retención':<15}{-277.58:>10.2f}")
```

Verás en código antiguo otras dos formas, `"%s tiene %d" % (nombre, edad)` y `"{} tiene {}".format(nombre, edad)`. Funcionan, pero en código nuevo se usan f-strings.

### input

`input()` muestra un mensaje, espera a que el usuario pulse Enter y devuelve lo escrito **siempre como `str`**.

```python
nombre = input("Nombre: ")
edad = int(input("Edad: "))
precio = float(input("Precio: "))
```

Si el usuario escribe algo que no es un número, `int()` lanza `ValueError` y el programa termina. Las excepciones se tratan en el Módulo 6; mientras tanto, se puede validar antes de convertir:

```python
texto = input("Edad: ").strip()

if texto.isdigit():
    edad = int(texto)
else:
    print("Eso no es un número entero positivo")
```

`str.isdigit()` solo acepta dígitos: rechaza negativos y decimales.

### Separar la lógica de la entrada y salida

Una función que calcula no debería pedir datos ni imprimir. Compara:

```python
# Difícil de probar y de reutilizar
def calcular_iva():
    precio = float(input("Precio: "))
    print(precio * 0.21)


# Fácil de probar: recibe datos y devuelve un resultado
def calcular_iva(precio: float) -> float:
    return precio * 0.21
```

Todos los ejercicios del curso siguen esta separación: funciones puras que calculan y un `main()` que se encarga de hablar con el usuario.

---

## 2.5 Condicionales

### if, elif, else

```python
nota = 7.5

if nota >= 9:
    calificacion = "Sobresaliente"
elif nota >= 7:
    calificacion = "Notable"
elif nota >= 5:
    calificacion = "Aprobado"
else:
    calificacion = "Suspenso"
```

- No hay paréntesis alrededor de la condición ni llaves. Hay dos puntos y sangría.
- `elif` sustituye a `else if`.
- Solo se ejecuta la primera rama cuya condición se cumple.

### Condiciones idiomáticas

```python
# Rango: comparación encadenada
if 18 <= edad < 65:
    ...

# Pertenencia: in con una tupla, en lugar de encadenar or
if dia in ("sábado", "domingo"):
    ...

# Vacío o no vacío: valor de verdad
if not lista:
    ...

# Nulo: is None
if resultado is None:
    ...

# Booleanos: sin comparar con True
if activo:            # no: if activo == True
    ...
```

### Cláusulas de guarda

En lugar de anidar condiciones, resuelve primero los casos especiales y sal:

```python
# Anidado: difícil de leer
def precio_entrada(edad):
    if edad >= 0:
        if edad < 4:
            return 0
        else:
            if edad < 65:
                return 12
            else:
                return 8
    else:
        return None


# Con guardas: cada caso en su línea
def precio_entrada(edad):
    if edad < 0:
        return None
    if edad < 4:
        return 0
    if edad < 65:
        return 12
    return 8
```

### match

Desde Python 3.10 existe `match`, que compara un valor con varios patrones. En su forma más simple se parece a un `switch`, pero sin `break` y sin caída entre casos:

```python
def describir_codigo(codigo: int) -> str:
    match codigo:
        case 200:
            return "Correcto"
        case 301 | 302:
            return "Redirección"
        case 404:
            return "No encontrado"
        case _:
            return "Otro"
```

`|` combina alternativas y `_` es el caso por defecto. `match` es en realidad mucho más potente (desestructura tuplas, listas, diccionarios y objetos), pero para elegir entre valores sencillos un `if`/`elif` o un diccionario suelen bastar.

---

## 2.6 Bucles for y while

### for recorre elementos, no índices

El `for` de Python es un *for-each*: recorre directamente los elementos de cualquier objeto iterable.

```python
lenguajes = ["Python", "Java", "C#"]

for lenguaje in lenguajes:
    print(lenguaje)

for letra in "hola":
    print(letra)
```

No existe el `for (int i = 0; i < n; i++)`. Esta es la costumbre que más cuesta abandonar:

```python
# Estilo C: funciona, pero no es Python
for i in range(len(lenguajes)):
    print(lenguajes[i])

# Idiomático
for lenguaje in lenguajes:
    print(lenguaje)

# Si además necesitas la posición
for posicion, lenguaje in enumerate(lenguajes, start=1):
    print(posicion, lenguaje)
```

### range

Cuando lo que necesitas es repetir algo un número de veces o generar una secuencia de enteros, usa `range()`:

| Llamada | Genera |
| --- | --- |
| `range(5)` | 0, 1, 2, 3, 4 |
| `range(2, 6)` | 2, 3, 4, 5 |
| `range(0, 10, 2)` | 0, 2, 4, 6, 8 |
| `range(5, 0, -1)` | 5, 4, 3, 2, 1 |

El límite superior nunca se incluye. `range` no crea una lista en memoria: va produciendo los números según se piden, así que `range(10**9)` no ocupa nada.

```python
for _ in range(3):        # _ indica que el valor no se usa
    print("Hola")

total = 0
for numero in range(1, 101):
    total += numero       # 5050
```

### while

Se usa cuando no se sabe de antemano cuántas vueltas habrá:

```python
intentos = 0

while intentos < 3:
    clave = input("Clave: ")
    if clave == "python":
        print("Acceso concedido")
        break
    intentos += 1
```

No existe `do ... while`. El patrón equivalente es un bucle infinito con `break`:

```python
while True:
    texto = input("Número positivo: ")
    if texto.isdigit() and int(texto) > 0:
        break
    print("Valor no válido, prueba otra vez")

numero = int(texto)
```

### break, continue y pass

| Sentencia | Efecto |
| --- | --- |
| `break` | Sale del bucle inmediatamente |
| `continue` | Salta al comienzo de la siguiente vuelta |
| `pass` | No hace nada. Sirve de relleno donde la sintaxis exige un bloque |

```python
for numero in range(1, 11):
    if numero % 2 == 0:
        continue          # se salta los pares
    if numero > 7:
        break             # se detiene al pasar de 7
    print(numero)         # 1, 3, 5, 7
```

### La cláusula else de los bucles

Los bucles pueden llevar un `else`. Se ejecuta cuando el bucle termina **sin haber pasado por un `break`**. Léelo como «si no se interrumpió»:

```python
def es_primo(n: int) -> bool:
    if n < 2:
        return False
    for divisor in range(2, int(n ** 0.5) + 1):
        if n % divisor == 0:
            break
    else:
        return True       # no se encontró ningún divisor
    return False
```

Evita la típica variable bandera `encontrado = False`. Se usa poco, pero conviene reconocerla.

### Bucles anidados

```python
for fila in range(1, 4):
    for columna in range(1, 4):
        print(f"{fila * columna:>3}", end="")
    print()
```

`break` solo sale del bucle más interno. Si necesitas salir de dos niveles, lo más limpio es mover los bucles a una función y usar `return`.

### Acumuladores y contadores

Los patrones clásicos se escriben igual que en cualquier lenguaje:

```python
suma = 0
cuenta = 0
maximo = None

for valor in (4, 8, 15, 16, 23, 42):
    suma += valor
    cuenta += 1
    if maximo is None or valor > maximo:
        maximo = valor
```

Aunque para estos casos Python ya trae `sum()`, `len()`, `max()` y `min()`. Antes de escribir un bucle, pregúntate si hay una función integrada que ya lo hace.

---

## 2.7 Ejercicios prácticos

Los ejemplos de la carpeta [`ejemplos/`](ejemplos/) recorren el módulo:

| Fichero | Qué muestra |
| --- | --- |
| `01_tipos_de_datos.py` | Enteros, flotantes, booleanos, cadenas, `None` y conversiones |
| `02_variables_y_referencias.py` | Nombres, identidad, mutabilidad y anotaciones |
| `03_operadores.py` | División, comparaciones encadenadas, cortocircuito, `is` e `in` |
| `04_entrada_salida.py` | f-strings con formato y validación de entrada |
| `05_condicionales.py` | `if`, guardas, expresión condicional y `match` |
| `06_bucles.py` | `for`, `range`, `enumerate`, `while`, `break`, `continue` y `else` |
| `07_mirada_datos.py` | Valores ausentes, precisión de los flotantes y formato de cifras |

- Ejercicios del módulo: [`ejercicios/README.md`](ejercicios/README.md)
- Práctica 2, adivina el número y calculadora de nómina: [`ejercicios/PRACTICA_2.md`](ejercicios/PRACTICA_2.md)

---

## Mirada de datos

Lo que has visto en este módulo es también la base del trabajo con datos numéricos. Tres ideas que volverán en el Módulo 7:

**Los valores ausentes existen y hay que decidir qué hacer con ellos.** En Python puro el valor ausente es `None`. En los datos numéricos es `NaN`, un flotante especial que no es igual a nada, ni siquiera a sí mismo:

```python
>>> nan = float("nan")
>>> nan == nan
False
>>> import math
>>> math.isnan(nan)
True
```

**Los flotantes son aproximados.** Un total calculado con flotantes no se compara con `==`: se usa `math.isclose` o se redondea al presentar. Para dinero exacto existe `decimal.Decimal`.

**Un bucle con acumulador es una agregación.** Este recorrido calcula una media saltando los valores ausentes:

```python
lecturas = [21.5, 22.1, None, 19.8, None, 23.4]

total = 0.0
validas = 0
for lectura in lecturas:
    if lectura is None:
        continue
    total += lectura
    validas += 1

print(f"Media: {total / validas:.2f}")           # Media: 21.70
print(f"Válidas: {validas / len(lecturas):.1%}")  # Válidas: 66.7%
```

Con pandas, en el Módulo 7, las mismas ocho líneas serán `lecturas.mean()` y `lecturas.notna().mean()`. Conviene haberlo escrito a mano una vez para saber qué hace la librería por ti. El ejemplo completo está en `ejemplos/07_mirada_datos.py`.

---

## Errores típicos de quien viene de otro lenguaje

| Error | Qué pasa | Forma correcta |
| --- | --- | --- |
| `for i in range(len(lista))` | Funciona, pero es código de C | `for elemento in lista` o `enumerate(lista)` |
| `if x == None` | Funciona casi siempre, pero no es fiable | `if x is None` |
| `if activo == True` | Redundante | `if activo` |
| `a is b` para comparar valores | Resultados imprevisibles | `a == b` |
| `0.1 + 0.2 == 0.3` | `False` | `math.isclose()` o `Decimal` |
| `7 / 2` esperando `3` | Da `3.5` | `7 // 2` |
| `contador++` | `SyntaxError` | `contador += 1` |
| `&&`, `\|\|`, `!` | `SyntaxError` | `and`, `or`, `not` |
| `b = a` para copiar una lista | `b` y `a` son la misma lista | `b = a.copy()` |
| Operar con lo que devuelve `input()` | `TypeError` | Convertir con `int()` o `float()` |

## Para saber más

- Tipos integrados: [docs.python.org/es/3/library/stdtypes.html](https://docs.python.org/es/3/library/stdtypes.html)
- Minilenguaje de formato: [docs.python.org/es/3/library/string.html#formatspec](https://docs.python.org/es/3/library/string.html#formatspec)
- Control de flujo en el tutorial oficial: [docs.python.org/es/3/tutorial/controlflow.html](https://docs.python.org/es/3/tutorial/controlflow.html)



# USO DE IA:
 
He usado la IA para solucionar un par de errores que me han salido al obtener el nombre del tipo de la variable (estaba haciendo type(valor) y no type(valor).__name__). Tambien para buscar los tramos del IRPF 