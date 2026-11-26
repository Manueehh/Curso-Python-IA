# Gestor de candidaturas

Aplicación de consola para llevar el seguimiento de una búsqueda de empleo: a qué ofertas te has apuntado, en qué punto está cada una, cuáles llevan semanas sin respuesta y qué portales funcionan mejor. Incluye un módulo de análisis con pandas sobre los propios datos de la aplicación.

## Puesta en marcha

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows (PowerShell)
pip install -r requirements.txt
pytest                              # todos los tests
python app.py                       # versión de consola
streamlit run web_app.py            # versión web, en http://localhost:8501
```

## Versión web

`web_app.py` es una segunda capa de presentación sobre el mismo paquete `candidaturas`: no hay ninguna regla de negocio en ella, igual que en `app.py`. El menú lateral (`st.navigation`) agrupa las páginas:

| Grupo | Página | Qué muestra |
| --- | --- | --- |
| Seguimiento | Panel | Indicadores, embudo por estado, respuesta por fuente, ritmo de envío semanal y a quién toca escribir |
| | Tablero | Las activas en columnas por fase, como tarjetas con interés, fuente y días desde el envío |
| | Sin respuesta | Las que llevan 15 días o más en «enviada», con acciones rápidas |
| Gestión | Candidaturas | Tabla con búsqueda y filtros por estado y fuente (`GestorCandidaturas.filtrar`) |
| | Nueva candidatura | Formulario con selectores visuales para la fuente y el interés |
| | Cambiar estado | El punto del proceso en el que está y un botón por cada estado permitido (`TRANSICIONES`) |
| Informes | Informe | El informe de texto de la consola y el embudo en PNG, descargables |

El tema está en `.streamlit/config.toml` y la paleta de los gráficos y las etiquetas en el diccionario `PALETA` y los estilos `ESTADO`, `INTERES`, `MODALIDAD` y `FUENTE` de `web_app.py`: para cambiar de colores basta con tocar esos dos sitios. Los gráficos del panel son de Altair; el embudo descargable es la figura de Matplotlib de `analisis.figura_embudo`.

**Persistencia.** Streamlit vuelve a ejecutar el script entero en cada interacción. Por eso la aplicación carga el CSV al principio de cada ejecución y, después de cada operación que modifica datos, lo guarda y repinta la página (`st.rerun`). El fichero es siempre la fuente de verdad: no hay estado que se pierda al recargar ni que se desincronice con la consola, y se pueden usar las dos versiones sobre el mismo `candidaturas.csv`.

La ruta del fichero se cambia con la variable de entorno `CANDIDATURAS_CSV`. Un CSV vale para un único usuario a la vez; para varios usuarios simultáneos el siguiente paso sería SQLite.

Para probarla con datos:

```bash
copy datos\candidaturas_ejemplo.csv candidaturas.csv      # en macOS/Linux: cp
python app.py
```

## Reglas del dominio

**Interés**, de menor a mayor: `bajo`, `medio`, `alto`.

**Fuentes**: `linkedin`, `infojobs`, `web_empresa`, `referido`, `otra`.

**Modalidades**: `remoto`, `hibrido`, `presencial`, o vacía si la oferta no lo dice.

**Datos opcionales** de cada candidatura: modalidad, salario bruto anual en euros (entero, no negativo), ubicación, enlace a la oferta (tiene que empezar por `http://` o `https://`) y notas libres. Un CSV de la primera versión, sin estas columnas, se sigue cargando: los campos que faltan toman su valor por defecto y se añaden al guardar.

**Estados** y cambios permitidos:

| Desde | Se puede pasar a |
| --- | --- |
| `enviada` | `entrevista`, `prueba_tecnica`, `rechazada`, `descartada` |
| `entrevista` | `prueba_tecnica`, `oferta`, `rechazada`, `descartada` |
| `prueba_tecnica` | `entrevista`, `oferta`, `rechazada`, `descartada` |
| `oferta` | `aceptada`, `descartada` |
| `aceptada`, `rechazada`, `descartada` | A ninguno |

- `rechazada`: te descarta la empresa. `descartada`: la descartas tú.
- Una candidatura está **activa** si está en `enviada`, `entrevista`, `prueba_tecnica` u `oferta`.
- Al salir de `enviada` hacia cualquier estado salvo `descartada` se anota la **fecha de respuesta**.
- Al llegar a `aceptada`, `rechazada` o `descartada` se anota la **fecha de cierre**.
- Está **sin respuesta** si sigue en `enviada` desde hace `DIAS_SIN_RESPUESTA` (15) días o más.
- Empresa y puesto son obligatorios.
- No puede haber dos candidaturas **activas** a la misma empresa y puesto, sin distinguir mayúsculas.
- Los identificadores son enteros consecutivos que empiezan en 1.

## Arquitectura

```
gestor-candidaturas/
├── app.py                  Menú. ÚNICO sitio con input, print y captura de errores
├── candidaturas/           Paquete con la lógica
│   ├── __init__.py
│   ├── excepciones.py      Errores propios
│   ├── modelos.py          Candidatura: los datos y sus reglas
│   ├── gestor.py           GestorCandidaturas: operaciones sobre el conjunto
│   ├── almacen.py          Guardar y cargar en CSV
│   ├── informes.py         Textos para mostrar
│   └── analisis.py         Análisis con pandas
├── datos/candidaturas_ejemplo.csv
└── tests/
```

| Capa | Responsabilidad | Qué no hace |
| --- | --- | --- |
| `modelos.py` | Una candidatura es siempre válida y solo cambia de estado según las reglas | No sabe que existen ficheros ni pantalla |
| `gestor.py` | Crear, buscar, ordenar y contar | No lee ni escribe ficheros; no usa `print` ni `input` |
| `almacen.py` | Convertir entre candidaturas y CSV | No decide cuándo se guarda |
| `informes.py` | Construir textos y devolverlos | No usa `print` |
| `analisis.py` | Ver las candidaturas como una tabla y calcular indicadores | No modifica nada; no recorre filas con `for` |
| `app.py` | Hablar con el usuario y capturar los errores | No contiene reglas de negocio |

Los docstrings de cada fichero son la especificación: léelos enteros antes de programar.

## Plan de trabajo

Haz **un commit al terminar cada hito**.

| Hito | Fichero | Qué construyes | Tiempo | Tests |
| --- | --- | --- | --- | --- |
| 1 | `excepciones.py`, `modelos.py`, `__init__.py` | Las excepciones y la clase `Candidatura` | 1,5 h | `pytest tests/test_modelos.py` |
| 2 | `gestor.py` | `GestorCandidaturas` | 1,5 h | `pytest tests/test_gestor.py` |
| 3 | `almacen.py` | `guardar` y `cargar` | 45 min | `pytest tests/test_almacen.py` |
| 4 | `informes.py` | `linea`, `listado` y `resumen` | 45 min | `pytest tests/test_informes.py` |
| 5 | `app.py` | El menú | 1 h | `pytest tests/test_app.py` |
| 6 | `analisis.py` | El análisis con pandas y el gráfico | 1 h | `pytest tests/test_analisis.py` |
| 7 | Todo | Revisión, limpieza y este README | 30 min | `pytest` |

Hasta que no definas las excepciones y el `__init__.py`, `pytest` no puede importar el paquete y muestra un error de importación. Es lo esperado: empieza por ahí.

### Pistas

- **Hito 1.** `cambiar_estado` consulta `TRANSICIONES`, sin cadenas de `if`. `a_fila` y `desde_fila` son inversas: `Candidatura.desde_fila(c.a_fila()) == c`.
- **Hito 2.** El gestor guarda las candidaturas en un diccionario por identificador y **delega** en la candidatura para cambiar el estado. `activas()` es una ordenación por varios criterios: la posición del interés en `INTERESES` te da su peso.
- **Hito 3.** `csv.DictWriter` / `csv.DictReader` con `with`, `encoding="utf-8"` y `newline=""`. Un fichero que no existe es la primera ejecución; una fila incorrecta detiene la carga con `ErrorDeAlmacen` y `raise ... from`.
- **Hito 5.** Una función pequeña por opción, un diccionario opción → función y un único `try/except ErrorDeCandidaturas`.
- **Hito 6.** `a_tabla` parte de `a_fila()`. Ninguna función necesita un bucle: `value_counts` + `reindex`, `groupby` + `agg`, restas de fechas con `.dt.days` y máscaras booleanas.

## Formato del informe

`resumen(gestor, hoy)` con `datos/candidaturas_ejemplo.csv` y la fecha 27/11/2026:

```
==============================================================================
                           INFORME DE CANDIDATURAS
==============================================================================
Fecha del informe: 2026-11-27
Total de candidaturas: 12

Por estado
  enviada            5
  entrevista         2
  prueba_tecnica     1
  oferta             1
  aceptada           0
  rechazada          2
  descartada         1

Activas por interés
  alto               4
  medio              4
  bajo               1

Sin respuesta en 15 días o más: 3
==============================================================================
```

- Ancho de 78 caracteres, en la constante `ANCHO`. El título va centrado.
- «Por estado» muestra **los siete** estados en el orden de `ESTADOS`, aunque valgan cero.
- «Activas por interés» cuenta solo las activas, de mayor a menor interés.
- En las dos listas: dos espacios, el nombre en 16 caracteres a la izquierda y la cantidad en 4 a la derecha.
- Sin salto de línea al final.

Y `analisis.indicadores(tabla, hoy)` con los mismos datos:

```python
{'total': 12, 'activas': 9, 'tasa_respuesta': 50.0, 'dias_medios_respuesta': 6.5,
 'ofertas': 1, 'sin_respuesta': 3, 'salario_medio': 31625}
```

## Ampliaciones (solo si lo anterior está completo)

1. Registro de operaciones con `logging` en `candidaturas.log`.
2. Opción de menú que exporta las activas a un CSV aparte.
3. Opción de menú que guarda el gráfico del embudo en PNG.
4. Campo de notas libres por candidatura (contacto, salario ofrecido…).
