"""Gestor de candidaturas: interfaz web con Streamlit.

Es la alternativa a ``app.py``: la misma lógica del paquete ``candidaturas``
con otra capa de presentación. Este fichero es el único que usa Streamlit;
no contiene reglas de negocio.

Persistencia: en cada ejecución del script se cargan las candidaturas del
CSV, y después de cada operación que cambia algo se guardan y se vuelve a
pintar la página. Así el fichero es siempre la fuente de verdad.

Uso: streamlit run web_app.py
La ruta del CSV se puede cambiar con la variable de entorno CANDIDATURAS_CSV.
"""

import io
import os
from datetime import date
from pathlib import Path
from typing import NamedTuple

import altair as alt
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from candidaturas import ErrorDeAlmacen, ErrorDeCandidaturas, GestorCandidaturas
from candidaturas import almacen, analisis, informes
from candidaturas.modelos import (
    ACTIVOS,
    DIAS_SIN_RESPUESTA,
    ESTADOS,
    FUENTES,
    INTERESES,
    MODALIDADES,
    TRANSICIONES,
    Candidatura,
)


# ------------------------------------------------------------------ apariencia
# Paleta "verde azulado y coral". Los colores de la interfaz de Streamlit
# (botones, enlaces, fondos) están en .streamlit/config.toml y coinciden con estos.
PALETA = {
    "primario": "#0F766E",        # verde azulado
    "primario_suave": "#CCFBF1",
    "primario_medio": "#5EEAD4",
    "acento": "#F97316",          # coral
    "texto": "#1C1917",
    "texto_suave": "#78716C",
    "borde": "#E7E5E4",
}


class Estilo(NamedTuple):
    texto: str
    emoji: str
    icono: str = ""      # icono de Material para botones y badges
    color: str = "gray"  # color de st.badge
    hex: str = "#78716C"  # color en los gráficos


ESTADO = {
    "enviada": Estilo("Enviada", "📤", ":material/send:", "gray", "#78716C"),
    "entrevista": Estilo("Entrevista", "🗣️", ":material/forum:", "blue", "#0EA5E9"),
    "prueba_tecnica": Estilo("Prueba técnica", "🧪", ":material/code:", "violet", "#8B5CF6"),
    "oferta": Estilo("Oferta", "🎁", ":material/redeem:", "orange", "#F59E0B"),
    "aceptada": Estilo("Aceptada", "🎉", ":material/celebration:", "green", "#10B981"),
    "rechazada": Estilo("Rechazada", "❌", ":material/block:", "red", "#F43F5E"),
    "descartada": Estilo("Descartada", "🚫", ":material/do_not_disturb_on:", "gray", "#A8A29E"),
}
INTERES = {
    "alto": Estilo("Alto", "🔥", color="red"),
    "medio": Estilo("Medio", "⭐", color="orange"),
    "bajo": Estilo("Bajo", "💤", color="gray"),
}
MODALIDAD = {
    "remoto": Estilo("Remoto", "🏠", color="green", hex="#10B981"),
    "hibrido": Estilo("Híbrido", "🔀", color="blue", hex="#0EA5E9"),
    "presencial": Estilo("Presencial", "🏢", color="orange", hex="#F97316"),
    "sin indicar": Estilo("Sin indicar", "❔", color="gray", hex="#D6D3D1"),
}
FUENTE = {
    "linkedin": Estilo("LinkedIn", "💼"),
    "infojobs": Estilo("InfoJobs", "📋"),
    "web_empresa": Estilo("Web de la empresa", "🌐"),
    "referido": Estilo("Referido", "🤝"),
    "otra": Estilo("Otra", "✳️"),
}

# Camino "feliz" de una candidatura, para dibujar en qué punto está
CAMINO = ("enviada", "entrevista", "prueba_tecnica", "oferta", "aceptada")

CSS = """
<style>
.tarjeta-titulo {font-weight: 700; font-size: 1.05rem; margin: 0;}
.tarjeta-sub {color: #78716C; font-size: .9rem; margin: 0 0 .4rem 0;}
.columna {color: white; font-weight: 700; padding: .45rem .8rem;
          border-radius: .6rem; margin-bottom: .6rem;}
.camino {display: flex; flex-wrap: wrap; gap: .35rem; margin: .6rem 0 .2rem 0;}
.paso {padding: .3rem .75rem; border-radius: 999px; font-size: .82rem;
       background: #F5F5F4; color: #78716C;}
.paso.hecho {background: #CCFBF1; color: #115E59;}
.paso.actual {background: #0F766E; color: white; font-weight: 700;}
.paso.fin {background: #FFE4E6; color: #BE123C; font-weight: 700;}
</style>
"""


def con_emoji(estilos: dict[str, Estilo]):
    """Devuelve una función que muestra un valor como "emoji texto"."""
    return lambda valor: f"{estilos[valor].emoji} {estilos[valor].texto}"


def badge(estilos: dict[str, Estilo], valor: str) -> str:
    """Badge en sintaxis Markdown de Streamlit, para usar dentro de st.markdown."""
    estilo = estilos[valor]
    return f":{estilo.color}-badge[{estilo.emoji} {estilo.texto}]"


def euros(cantidad) -> str:
    """32000 -> "32.000 €"; un valor ausente es un guion."""
    if cantidad is None or pd.isna(cantidad):
        return "—"
    return f"{int(cantidad):,} €".replace(",", ".")


def cabecera(titulo: str, subtitulo: str) -> None:
    st.title(titulo)
    st.caption(subtitulo)


# ------------------------------------------------------------------ utilidades
def ruta_datos() -> Path:
    return Path(os.environ.get("CANDIDATURAS_CSV", Path(__file__).parent / "candidaturas.csv"))


def guardar_y_recargar(gestor: GestorCandidaturas, mensaje: str, *, globos: bool = False) -> None:
    """Guarda en el CSV, deja el aviso para la siguiente ejecución y repinta."""
    almacen.guardar(list(gestor), ruta_datos())
    st.session_state["aviso"] = mensaje
    st.session_state["globos"] = globos
    st.rerun()


def cambiar(gestor: GestorCandidaturas, candidatura: Candidatura, nuevo: str) -> None:
    """Cambia el estado desde un botón y guarda, o muestra el error."""
    try:
        gestor.cambiar_estado(candidatura.id, nuevo)
    except ErrorDeCandidaturas as error:
        st.error(str(error))
    else:
        guardar_y_recargar(
            gestor, f"{candidatura.empresa}: {ESTADO[nuevo].texto.lower()}",
            globos=nuevo == "aceptada",
        )


def tarjeta(candidatura: Candidatura, hoy: date) -> None:
    """Pinta una candidatura como tarjeta dentro del contenedor actual."""
    c = candidatura
    st.markdown(f'<p class="tarjeta-titulo">{c.empresa}</p>'
                f'<p class="tarjeta-sub">{c.puesto}</p>', unsafe_allow_html=True)
    badges = [badge(INTERES, c.interes), badge(FUENTE, c.fuente)]
    if c.modalidad:
        badges.append(badge(MODALIDAD, c.modalidad))
    st.markdown(" ".join(badges))
    detalles = " · ".join(texto for condicion, texto in [
        (c.ubicacion, f"📍 {c.ubicacion}"),
        (c.salario is not None, f"💶 {euros(c.salario)}"),
        (c.enlace, f"[Ver oferta ↗]({c.enlace})"),
    ] if condicion)
    dias = c.dias_desde_envio(hoy)
    aviso = f":red[hace {dias} días]" if c.sin_respuesta(hoy) else f"hace {dias} días"
    envio = f"Enviada el {c.fecha_envio:%d/%m/%Y} · {aviso}"
    st.caption(f"{detalles}  \n{envio}" if detalles else envio)


def camino(candidatura: Candidatura) -> str:
    """HTML con los pasos del proceso y el punto en el que está la candidatura."""
    estado = candidatura.estado
    if estado in CAMINO:
        actual = CAMINO.index(estado)
        pasos = [("actual" if i == actual else "hecho" if i < actual else "", paso)
                 for i, paso in enumerate(CAMINO)]
    else:
        pasos = [("hecho", "enviada"), ("fin", estado)]
    html = "".join(f'<span class="paso {clase}">{ESTADO[paso].emoji} {ESTADO[paso].texto}</span>'
                   for clase, paso in pasos)
    return f'<div class="camino">{html}</div>'


def tabla_vista(candidaturas: list[Candidatura], hoy: date) -> pd.DataFrame:
    """Tabla preparada para mostrar: textos con emoji y días desde el envío."""
    tabla = analisis.a_tabla(candidaturas)
    return pd.DataFrame({
        "ID": tabla["id"],
        "Empresa": tabla["empresa"],
        "Puesto": tabla["puesto"],
        "Estado": tabla["estado"].map(con_emoji(ESTADO)),
        "Interés": tabla["interes"].map(con_emoji(INTERES)),
        "Fuente": tabla["fuente"].map(con_emoji(FUENTE)),
        "Modalidad": tabla["modalidad"].replace("", "sin indicar").map(con_emoji(MODALIDAD)),
        "Salario": tabla["salario"].map(euros),
        "Ubicación": tabla["ubicacion"],
        "Envío": tabla["fecha_envio"],
        "Días": (pd.Timestamp(hoy) - tabla["fecha_envio"]).dt.days,
        "Respuesta": tabla["fecha_respuesta"].dt.strftime("%d/%m/%Y").fillna("—"),
        "Oferta": tabla["enlace"].replace("", None),
    })


# --------------------------------------------------------------------- gráficos
def grafico_embudo(tabla: pd.DataFrame) -> alt.Chart:
    datos = analisis.embudo(tabla).rename_axis("estado").reset_index(name="candidaturas")
    datos["texto"] = datos["estado"].map(lambda e: ESTADO[e].texto)
    orden = [ESTADO[e].texto for e in ESTADOS]
    colores = [ESTADO[e].hex for e in ESTADOS]
    barras = alt.Chart(datos).mark_bar(cornerRadiusEnd=6, height=22).encode(
        y=alt.Y("texto:N", sort=orden, title=None),
        x=alt.X("candidaturas:Q", title=None, axis=alt.Axis(tickMinStep=1)),
        color=alt.Color("texto:N", scale=alt.Scale(domain=orden, range=colores), legend=None),
        tooltip=[alt.Tooltip("texto:N", title="Estado"), "candidaturas:Q"],
    )
    numeros = barras.mark_text(align="left", dx=5, fontWeight="bold").encode(
        text="candidaturas:Q", color=alt.value(PALETA["texto"]))
    return (barras + numeros).properties(height=260)


def grafico_fuentes(tabla: pd.DataFrame) -> alt.Chart:
    datos = analisis.respuesta_por_fuente(tabla).reset_index()
    datos["texto"] = datos["fuente"].map(con_emoji(FUENTE))
    datos["detalle"] = datos["con_respuesta"].astype(str) + " de " + datos["enviadas"].astype(str)
    base = alt.Chart(datos).encode(
        y=alt.Y("texto:N", sort="-x", title=None),
        x=alt.X("porcentaje:Q", title="% con respuesta", scale=alt.Scale(domain=[0, 100])),
        tooltip=[alt.Tooltip("texto:N", title="Fuente"), "enviadas:Q", "con_respuesta:Q",
                 alt.Tooltip("porcentaje:Q", title="%")],
    )
    barras = base.mark_bar(cornerRadiusEnd=6, height=22, color=PALETA["primario"])
    textos = base.mark_text(align="left", dx=5, color=PALETA["texto"]).encode(text="detalle:N")
    return (barras + textos).properties(height=260)


def grafico_semanas(tabla: pd.DataFrame) -> alt.Chart:
    datos = analisis.envios_por_semana(tabla).rename_axis("semana").reset_index(name="envios")
    return alt.Chart(datos).mark_area(
        line={"color": PALETA["primario"]}, color=PALETA["primario_suave"],
        point={"color": PALETA["primario"]},
    ).encode(
        x=alt.X("semana:T", title=None, axis=alt.Axis(format="%d/%m")),
        y=alt.Y("envios:Q", title="Candidaturas", axis=alt.Axis(tickMinStep=1)),
        tooltip=[alt.Tooltip("semana:T", title="Semana del", format="%d/%m/%Y"),
                 alt.Tooltip("envios:Q", title="Enviadas")],
    ).properties(height=220)


def grafico_modalidad(tabla: pd.DataFrame) -> alt.Chart:
    datos = analisis.por_modalidad(tabla).reset_index()
    datos = datos[datos["candidaturas"] > 0]
    datos["texto"] = datos["modalidad"].map(con_emoji(MODALIDAD))
    datos["salario"] = datos["salario_medio"].map(euros)
    orden = [con_emoji(MODALIDAD)(m) for m in MODALIDAD]
    colores = [estilo.hex for estilo in MODALIDAD.values()]
    return alt.Chart(datos).mark_arc(innerRadius=55, cornerRadius=4, padAngle=0.02).encode(
        theta="candidaturas:Q",
        color=alt.Color("texto:N", scale=alt.Scale(domain=orden, range=colores),
                        legend=alt.Legend(title=None, orient="bottom")),
        tooltip=[alt.Tooltip("texto:N", title="Modalidad"), "candidaturas:Q", "activas:Q",
                 alt.Tooltip("salario:N", title="Salario medio")],
    ).properties(height=240)


# --------------------------------------------------------------------- páginas
def pagina_panel(gestor: GestorCandidaturas) -> None:
    cabecera("🎯 Panel", "Cómo va tu búsqueda de empleo, de un vistazo")
    if not len(gestor):
        st.info("Todavía no hay candidaturas. Empieza en **Nueva candidatura**.",
                icon=":material/rocket_launch:")
        return
    hoy = date.today()
    tabla = analisis.a_tabla(list(gestor))
    datos = analisis.indicadores(tabla, hoy)
    dias = datos["dias_medios_respuesta"]
    metricas = [
        ("📨 Total", datos["total"], "Candidaturas registradas"),
        ("🟢 Activas", datos["activas"], "Enviadas, en entrevista, en prueba o con oferta"),
        ("💬 Tasa de respuesta", f"{datos['tasa_respuesta']} %", "Empresas que han contestado"),
        ("⏱️ Días hasta respuesta", "-" if dias is None else dias, "Media de las que contestaron"),
        ("⏳ Sin respuesta", datos["sin_respuesta"],
         f"En «enviada» desde hace {DIAS_SIN_RESPUESTA} días o más"),
        ("💶 Salario medio", euros(datos["salario_medio"]), "Bruto anual de las que lo indican"),
    ]
    for fila in (metricas[:3], metricas[3:]):
        for columna, (etiqueta, valor, ayuda) in zip(st.columns(3), fila):
            columna.metric(etiqueta, valor, help=ayuda, border=True)

    izquierda, derecha = st.columns(2, gap="large")
    with izquierda.container(border=True):
        st.subheader("Embudo por estado")
        st.altair_chart(grafico_embudo(tabla))
    with derecha.container(border=True):
        st.subheader("Respuesta por fuente")
        st.altair_chart(grafico_fuentes(tabla))

    izquierda, centro, derecha = st.columns([5, 3, 4], gap="large")
    with izquierda.container(border=True):
        st.subheader("Ritmo de envío")
        st.altair_chart(grafico_semanas(tabla))
    with centro.container(border=True):
        st.subheader("Modalidad")
        st.altair_chart(grafico_modalidad(tabla))
    with derecha.container(border=True):
        st.subheader("A quién escribir")
        pendientes = gestor.sin_respuesta(hoy)
        if not pendientes:
            st.success("Todo al día: ninguna candidatura lleva demasiado sin respuesta.",
                       icon=":material/check_circle:")
        for c in pendientes[:4]:
            st.markdown(f"**{c.empresa}** · {c.puesto}  \n"
                        f":red[{c.dias_desde_envio(hoy)} días sin respuesta]")
        if len(pendientes) > 4:
            st.caption(f"y {len(pendientes) - 4} más en **Seguimiento**")


def pagina_tablero(gestor: GestorCandidaturas) -> None:
    cabecera("🗂️ Tablero", "Las candidaturas activas por fase, en orden de revisión")
    hoy = date.today()
    activas = gestor.activas()
    for estado, columna in zip(ACTIVOS, st.columns(len(ACTIVOS), gap="medium")):
        de_este_estado = [c for c in activas if c.estado == estado]
        estilo = ESTADO[estado]
        columna.markdown(
            f'<div class="columna" style="background:{estilo.hex}">'
            f"{estilo.emoji} {estilo.texto} · {len(de_este_estado)}</div>",
            unsafe_allow_html=True,
        )
        for candidatura in de_este_estado:
            with columna.container(border=True):
                tarjeta(candidatura, hoy)
        if not de_este_estado:
            columna.caption("Nada por aquí")


def pagina_listado(gestor: GestorCandidaturas) -> None:
    cabecera("📋 Candidaturas", "Busca y filtra todas tus candidaturas")
    with st.container(border=True):
        texto = st.text_input("Buscar", placeholder="Empresa o puesto",
                              icon=":material/search:", label_visibility="collapsed")
        estados = st.pills("Estado", ESTADOS, selection_mode="multi", format_func=con_emoji(ESTADO))
        fuentes = st.pills("Fuente", FUENTES, selection_mode="multi", format_func=con_emoji(FUENTE))
        modalidades = st.pills("Modalidad", MODALIDADES, selection_mode="multi",
                               format_func=con_emoji(MODALIDAD))
        solo_activas = st.toggle("Solo activas, en orden de revisión")

    candidaturas = gestor.filtrar(estados=estados, fuentes=fuentes, modalidades=modalidades,
                                  texto=texto)
    if solo_activas:
        elegidas = {c.id for c in candidaturas}
        candidaturas = [c for c in gestor.activas() if c.id in elegidas]
    st.caption(f"{len(candidaturas)} de {len(gestor)} candidaturas")
    if not candidaturas:
        st.info("Ninguna candidatura cumple los filtros.", icon=":material/filter_alt_off:")
        return
    vista = tabla_vista(candidaturas, date.today())
    st.dataframe(
        vista, hide_index=True, width="stretch",
        column_config={
            "ID": st.column_config.NumberColumn(width="small"),
            "Envío": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Oferta": st.column_config.LinkColumn(display_text="Abrir ↗"),
            "Días": st.column_config.ProgressColumn(
                "Días desde el envío", format="%d", min_value=0,
                max_value=max(int(vista["Días"].max()), DIAS_SIN_RESPUESTA * 2)),
        },
    )


def pagina_alta(gestor: GestorCandidaturas) -> None:
    cabecera("➕ Nueva candidatura", "Apunta una oferta a la que te acabas de presentar")
    with st.form("alta", clear_on_submit=True):
        oferta, condiciones = st.columns(2, gap="large")
        with oferta:
            st.markdown("##### 📝 La oferta")
            empresa = st.text_input("Empresa *", placeholder="Ej.: Acme Analytics",
                                    icon=":material/business:")
            puesto = st.text_input("Puesto *", placeholder="Ej.: Data Engineer Junior",
                                   icon=":material/work:")
            enlace = st.text_input("Enlace a la oferta", placeholder="https://…",
                                   icon=":material/link:")
            ubicacion = st.text_input("Ubicación", placeholder="Ej.: Madrid",
                                      icon=":material/location_on:")
        with condiciones:
            st.markdown("##### 💶 Condiciones")
            modalidad = st.segmented_control("Modalidad", MODALIDADES,
                                             format_func=con_emoji(MODALIDAD),
                                             help="Déjalo sin marcar si la oferta no lo dice")
            salario = st.number_input("Salario bruto anual (€)", min_value=0, step=1000,
                                      value=None, placeholder="Ej.: 32000",
                                      icon=":material/euro:")
            interes = st.segmented_control("¿Cuánto te interesa?", INTERESES, default="medio",
                                           format_func=con_emoji(INTERES))
            envio = st.date_input("Fecha de envío", value=date.today(), max_value=date.today(),
                                  format="DD/MM/YYYY")
        fuente = st.pills("¿Dónde la has encontrado?", FUENTES, default="linkedin",
                          format_func=con_emoji(FUENTE))
        notas = st.text_area("Notas", placeholder="Contacto, requisitos, impresiones…", height=90)
        st.caption("Los campos con * son obligatorios.")
        enviado = st.form_submit_button("Dar de alta", type="primary",
                                        icon=":material/add_task:")
    if enviado:
        try:
            nueva = gestor.crear(
                empresa, puesto, fuente=fuente or "", interes=interes or "",
                modalidad=modalidad or "", salario=None if salario is None else int(salario),
                ubicacion=ubicacion, enlace=enlace, notas=notas, hoy=envio,
            )
        except ErrorDeCandidaturas as error:
            st.error(str(error), icon=":material/error:")
        else:
            guardar_y_recargar(gestor, f"Creada la candidatura {nueva.id}: {nueva.empresa}")


def pagina_estado(gestor: GestorCandidaturas) -> None:
    cabecera("🔄 Cambiar estado", "Anota en qué punto está cada proceso")
    activas = gestor.activas()
    if not activas:
        st.info("No hay candidaturas activas.", icon=":material/inbox:")
        return
    candidatura = st.selectbox(
        "Candidatura", activas,
        format_func=lambda c: f"{ESTADO[c.estado].emoji} {c.empresa} — {c.puesto}  (n.º {c.id})",
    )
    with st.container(border=True):
        tarjeta(candidatura, date.today())
        if candidatura.notas:
            st.caption(f"📝 {candidatura.notas}")
        st.markdown(camino(candidatura), unsafe_allow_html=True)

    st.subheader("¿Qué ha pasado?")
    opciones = TRANSICIONES[candidatura.estado]
    for nuevo, columna in zip(opciones, st.columns(len(opciones))):
        estilo = ESTADO[nuevo]
        destacado = nuevo in ("entrevista", "prueba_tecnica", "oferta", "aceptada")
        if columna.button(estilo.texto, icon=estilo.icono, key=f"pasar_{nuevo}",
                          type="primary" if destacado else "secondary", width="stretch"):
            cambiar(gestor, candidatura, nuevo)


def pagina_seguimiento(gestor: GestorCandidaturas) -> None:
    cabecera("⏳ Seguimiento",
             f"Candidaturas en «enviada» desde hace {DIAS_SIN_RESPUESTA} días o más")
    hoy = date.today()
    pendientes = gestor.sin_respuesta(hoy)
    if not pendientes:
        st.success("Todo al día: ninguna candidatura lleva demasiado sin respuesta.",
                   icon=":material/check_circle:")
        return
    for candidatura in pendientes:
        with st.container(border=True):
            datos, contacto, descartar = st.columns([4, 1, 1], vertical_alignment="center")
            with datos:
                tarjeta(candidatura, hoy)
            if contacto.button("Me han llamado", icon=":material/forum:",
                               key=f"entrevista_{candidatura.id}", width="stretch"):
                cambiar(gestor, candidatura, "entrevista")
            if descartar.button("Descartar", icon=":material/do_not_disturb_on:",
                                key=f"descartar_{candidatura.id}", width="stretch"):
                cambiar(gestor, candidatura, "descartada")


def pagina_informe(gestor: GestorCandidaturas) -> None:
    cabecera("📄 Informe", "El informe de situación, listo para descargar")
    texto = informes.resumen(gestor, date.today())
    informe, descargas = st.columns([3, 1], gap="large")
    informe.code(texto, language=None)
    descargas.download_button("Informe (.txt)", texto, file_name="informe_candidaturas.txt",
                              icon=":material/download:", width="stretch")
    figura = analisis.figura_embudo(analisis.a_tabla(list(gestor)))
    imagen = io.BytesIO()
    figura.savefig(imagen, format="png")
    plt.close(figura)
    descargas.download_button("Embudo (.png)", imagen.getvalue(), file_name="embudo.png",
                              mime="image/png", icon=":material/bar_chart:", width="stretch")


# ------------------------------------------------------------------ aplicación
def barra_lateral(gestor: GestorCandidaturas) -> None:
    hoy = date.today()
    with st.sidebar:
        st.markdown("### 🎯 Mi búsqueda")
        izquierda, derecha = st.columns(2)
        izquierda.metric("Activas", len(gestor.activas()))
        derecha.metric("Sin respuesta", len(gestor.sin_respuesta(hoy)))
        st.caption(f"Datos guardados en `{ruta_datos().name}`")


def renderizar(pagina) -> None:
    """Carga los datos, pinta lo común y ejecuta la página recibida."""
    st.markdown(CSS, unsafe_allow_html=True)
    try:
        gestor = GestorCandidaturas(almacen.cargar(ruta_datos()))
    except ErrorDeAlmacen as error:
        st.error(f"No se pueden cargar los datos: {error}", icon=":material/error:")
        st.stop()
    barra_lateral(gestor)
    if aviso := st.session_state.pop("aviso", None):
        st.toast(aviso, icon="✅")
    if st.session_state.pop("globos", False):
        st.balloons()
    pagina(gestor)


def crear_pagina(pagina, titulo: str, icono: str, ruta: str, **opciones) -> st.Page:
    return st.Page(lambda: renderizar(pagina), title=titulo, icon=icono, url_path=ruta,
                   **opciones)


def main() -> None:
    st.set_page_config(page_title="Gestor de candidaturas", page_icon="🎯", layout="wide")
    navegacion = st.navigation({
        "Seguimiento": [
            crear_pagina(pagina_panel, "Panel", ":material/dashboard:", "panel", default=True),
            crear_pagina(pagina_tablero, "Tablero", ":material/view_kanban:", "tablero"),
            crear_pagina(pagina_seguimiento, "Sin respuesta", ":material/notifications:",
                         "seguimiento"),
        ],
        "Gestión": [
            crear_pagina(pagina_listado, "Candidaturas", ":material/table_view:", "candidaturas"),
            crear_pagina(pagina_alta, "Nueva candidatura", ":material/add_circle:", "nueva"),
            crear_pagina(pagina_estado, "Cambiar estado", ":material/swap_horiz:", "estado"),
        ],
        "Informes": [
            crear_pagina(pagina_informe, "Informe", ":material/description:", "informe"),
        ],
    })
    navegacion.run()


if __name__ == "__main__":
    main()
