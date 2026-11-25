# Módulo 5. Ejercicios

En los Ejercicios 1 a 5 cada fichero contiene las clases con sus métodos ya declarados: firma, docstring y un `raise NotImplementedError` que tienes que sustituir por tu código. En el Ejercicio 6 escribes las clases enteras.

```bash
pytest modulo_05_poo -v
pytest modulo_05_poo -v -k ej3        # solo un ejercicio
```

En este módulo aparece `raise ValueError("mensaje")` para rechazar datos incorrectos. Por ahora basta con saber que interrumpe el método y avisa del error a quien lo llamó. Las excepciones se ven a fondo en el Módulo 6.

## Ejercicio 1. Clases, objetos y constructores

Fichero: `m5_ej1_clases.py`

| Clase | Qué practica |
| --- | --- |
| `Rectangulo` | `__init__`, `self`, métodos que leen el estado y un método que devuelve un objeto nuevo |
| `Contador` | Estado que cambia entre llamadas y atributo interno con guion bajo |
| `Tarea` | Valores iniciales que no vienen de parámetros y el valor por defecto mutable |

`Contador` es la versión con clase del cierre `crear_contador` del Módulo 3. Compara las dos soluciones cuando termines.

En `Tarea`, dos tareas creadas sin etiquetas no pueden compartir la misma lista. Hay un test que lo comprueba.

## Ejercicio 2. Atributos de clase y métodos especiales

Fichero: `m5_ej2_metodos.py`

| Clase | Qué practica |
| --- | --- |
| `Dinero` | `@staticmethod`, `@classmethod` como constructor alternativo, `__repr__`, `__str__`, `__eq__`, `__lt__` y `__add__` |
| `Playlist` | Atributo de clase compartido, `__len__`, `__contains__`, `__iter__`, `__getitem__` y `__str__` |

Cuando termines `Dinero`, prueba en el intérprete `sorted([...])`, `max(...)` y `sum(lista, Dinero(0))` con tus objetos.

## Ejercicio 3. Herencia y clases abstractas

Fichero: `m5_ej3_herencia.py`

```
Empleado (abstracta)
├── Fijo
│   └── Comercial
└── PorHoras
```

| Elemento | Qué practica |
| --- | --- |
| `Empleado.descripcion()` | Método concreto de la clase base que usa uno abstracto |
| `Fijo`, `PorHoras` | `super().__init__()` e implementación del método abstracto |
| `Comercial` | Sobrescritura que reutiliza el cálculo de la base con `super()` |
| `coste_mensual(plantilla)` | Polimorfismo: el mismo código para todas las subclases |
| `mejor_pagado(plantilla)` | `max()` con `key` sobre objetos |

`Empleado.salario_mensual` ya está declarado como abstracto. No lo toques.

## Ejercicio 4. Polimorfismo y duck typing

Fichero: `m5_ej4_polimorfismo.py`

Tres exportadores, `ExportadorCsv`, `ExportadorTexto` y `ExportadorMarkdown`, que **no heredan de ninguna clase común**. Lo único que comparten es el método `exportar(registros)` y el atributo de clase `extension`.

| Función | Qué practica |
| --- | --- |
| `exportar_con(exportador, registros)` | Usar un objeto sin preguntar por su tipo |
| `nombre_de_fichero(exportador, nombre)` | Lo mismo con un atributo |
| `exportar_a_todos(exportadores, registros)` | Recorrer objetos de clases distintas |
| `puede_exportar(objeto)` | Comprobar una capacidad, no un tipo |

En las cuatro funciones está prohibido usar `isinstance` y `type`. Un test les pasa un exportador que no has visto nunca y tienen que funcionar.

## Ejercicio 5. Encapsulación y propiedades

Fichero: `m5_ej5_encapsulacion.py`

| Clase | Qué practica |
| --- | --- |
| `CuentaBancaria` | Propiedad de solo lectura, estado interno protegido y validación en los métodos |
| `Producto` | Propiedad con setter que valida y propiedad calculada |
| `Temperatura` | Dos propiedades con setter sobre un único dato interno |

Recuerda que dentro del setter se asigna al atributo con guion bajo, `self._precio`, y que en `__init__` se asigna a la propiedad, `self.precio`, para que la validación se aplique también al crear el objeto.

## Ejercicio 6. Dataclasses y composición

Fichero: `m5_ej6_dataclasses.py`

Aquí no hay plantilla. Escribe tres dataclasses que cumplan esta especificación:

### `Punto`

- Inmutable (`frozen=True`).
- Campos `x` e `y`, de tipo `float`, con valor por defecto `0.0`.
- Método `distancia(otro)`: distancia entre los dos puntos, redondeada a dos decimales.

### `LineaPedido`

- Campos `producto` (`str`), `unidades` (`int`) y `precio` (`float`).
- Si `unidades` no es positivo, lanza `ValueError` en `__post_init__`.
- Propiedad de solo lectura `importe`: unidades por precio, con dos decimales.

### `Pedido`

- Campos `numero` (`int`), `cliente` (`str`) y `lineas`, una lista de `LineaPedido` que empieza vacía y es propia de cada pedido.
- Método `anadir(producto, unidades, precio)`: crea una línea, la añade y la devuelve.
- Propiedad de solo lectura `total`: suma de los importes, con dos decimales.
- `len(pedido)` devuelve el número de líneas.
- Método `productos()`: nombres de los productos del pedido, sin repetir y en orden alfabético.

```python
>>> pedido = Pedido(1042, "Ada")
>>> pedido.anadir("Teclado", 2, 45.0)
LineaPedido(producto='Teclado', unidades=2, precio=45.0)
>>> pedido.anadir("Ratón", 1, 19.9)
LineaPedido(producto='Ratón', unidades=1, precio=19.9)
>>> pedido.total, len(pedido), pedido.productos()
(109.9, 2, ['Ratón', 'Teclado'])
```

## Si terminas antes

1. Añade a `Dinero` el método `__hash__` y comprueba que ya puedes usar sus objetos como clave de un diccionario. ¿Por qué solo tiene sentido si el objeto no cambia?
2. Escribe un `Protocol` llamado `Exportador` para el Ejercicio 4 y anota con él las funciones.
3. Convierte `Rectangulo` en una dataclass. ¿Qué código desaparece?
4. Añade a `CuentaBancaria` un método de clase `desde_movimientos(titular, movimientos)` que cree la cuenta y aplique la lista de importes.

## USO DE IA EN ESTE MODULO
Dado el corto tiempo para realizar el modulo, he usado más de la que me hubiese gustado en la parte de la biblioteca, y para entender mejor algunos conceptos en la parte de encapsulacion