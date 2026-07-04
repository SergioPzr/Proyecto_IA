from fasthtml.common import *
from starlette.staticfiles import StaticFiles
import logging
from pathlib import Path
from prediction import predecir_casos, DEPARTAMENTOS_VALIDOS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app, rt = fast_app(pico=False, default_hdrs=True)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

#Declarion de diccionarios para los valores que se pueden ingresar
DIAS_MAP = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

MESES_MAP = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

FRANJAS_MAP = {
    "MADRUGADA": "Madrugada (12am a 6am)",
    "MANANA": "Mañana (6am a 12pm)",
    "TARDE": "Tarde (12pm a 6pm)",
    "NOCHE": "Noche (6pm a 12am)"
}

COLORES_NIVEL = {
    "bajo":  ("var(--nivel-bajo)",  "var(--nivel-bajo-bg)",  "22, 163, 74"),
    "medio": ("var(--nivel-medio)", "var(--nivel-medio-bg)", "217, 119, 6"),
    "alto":  ("var(--nivel-alto)",  "var(--nivel-alto-bg)",  "220, 38, 38"),
}

#Componente del sistema

def header_nav(active_page):
    monograma_svg = NotStr(
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="1.5" style="flex-shrink: 0;">'
        '<path d="M12 2L2 12l10 10 10-10L12 2z"/>'
        '<line x1="7" y1="7" x2="17" y2="17"/>'
        '</svg>'
    )
    return Header(
        Div(cls="franja-identidad"),
        Nav(
            A(monograma_svg, Span("PREDI-FAM"), cls="nav-marca", href="/"),
            Div(cls="enlaces")(
                A("Inicio", cls=f"{'activo' if active_page == 'inicio' else ''}", href="/", id="nav-inicio"),
                A("Consultar", cls=f"{'activo' if active_page == 'consultar' else ''}", href="/consultar", id="nav-consultar"),
                A("Cómo funciona", cls=f"{'activo' if active_page == 'como-funciona' else ''}", href="/como-funciona", id="nav-como-funciona")
            )
        )
    )

def section_label(texto):
    return P(texto, cls="eyebrow")

def stat_card(numero, descripcion):
    return Div(cls="stat-burbuja")(
        P(numero, cls="stat-numero"),
        P(descripcion, cls="stat-descripcion")
    )

def nivel_badge(nivel):
    nivel_lower = nivel.lower()
    color, fondo, _ = COLORES_NIVEL.get(nivel_lower, ("var(--nivel-medio)", "var(--nivel-medio-bg)", "217, 119, 6"))
    return Span(f"Nivel {nivel.capitalize()}", cls="badge-nivel-fluido",
                style=f"--nivel-color:{color};--nivel-bg:{fondo}")

def layout(content, active_page):
    head = Head(
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Meta(name="description", content="Sistema de pronóstico de frecuencia de denuncias de violencia familiar por departamento y horario en el Perú."),
        Title("PREDI-FAM | Pronóstico de Violencia Familiar"),
        Link(rel="stylesheet", href="/static/css/styles.css?v=4.0"),
        Script(src="https://unpkg.com/htmx.org@1.9.12"),
    )
    return Html(
        head,
        Body(
            header_nav(active_page),
            Main(content)
        )
    )

#Pantalla inicial, presenta el sistema y su funcion
@rt("/")
def get():
    foto_hero_url = "https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?w=900&q=80"
    foto_secundaria_url = "https://images.unsplash.com/photo-1516627145497-ae6968895b74?w=900&q=80"

    content = Div(
        Div(cls="presentacion-dos-columnas")(
            Div(cls="burbuja-liquida")(
                section_label("PANTALLA DE INICIO"),
                H1("Apoyo a la planificación de patrullaje preventivo"),
                P(
                    "Una herramienta para estimar la frecuencia esperada de denuncias "
                    "de violencia familiar por zona, día, mes y horario. "
                    "Ayuda a distribuir mejor los recursos de prevención.",
                    cls="subtitulo"
                )
            ),
            Img(src=foto_hero_url, alt="Oficial de policía en la comunidad", cls="marco-gota")
        ),
        Div(cls="stat-burbujas-contenedor")(
            stat_card("25", "Departamentos cubiertos"),
            stat_card("4", "Franjas horarias"),
            stat_card("2019", "Año base de datos")
        ),
        Div(cls="presentacion-dos-columnas")(
            Div(cls="burbuja-liquida")(
                H2("¿A quién beneficia?"),
                P("Personal de planificación policial que necesita saber dónde y cuándo priorizar el patrullaje preventivo.", cls="subtitulo", style="margin-bottom: var(--space-4);"),
                H2("¿Para quién está diseñado?"),
                P("Para personal no técnico. Solo hay que elegir las opciones del formulario y el sistema entrega el resultado de inmediato.", cls="subtitulo", style="margin-bottom: 0;")
            ),
            Img(src=foto_secundaria_url, alt="Familia protegida en su hogar", cls="marco-gota")
        ),
        Div(style="text-align: center; margin-top: var(--space-5); margin-bottom: var(--space-5);")(
            A("Comenzar Consulta", cls="btn-primary", href="/consultar", style="display: inline-flex; width: auto; padding: 0 var(--space-6); margin-bottom: var(--space-5);")
        )
    )
    return layout(content, "inicio")

#Pantalla 2, es el formulario donde se ingresaran los datos para la prediccion
@rt("/consultar")
def get():
    deptos_sorted = sorted(DEPARTAMENTOS_VALIDOS)

    icon_depto  = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.2"/></svg>')
    icon_dia    = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>')
    icon_franja = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>')
    icon_mes    = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>')

    form = Form(hx_post="/predecir", hx_target="#resultado-prediccion", hx_swap="innerHTML", cls="tarjeta-formulario-liquida")(
        Div(cls="grilla-campos-redondeados")(
            Div(cls="campo-redondeado")(
                Label(icon_depto, "Departamento", for_="select-depto"),
                Select(id="select-depto", name="departamento", required=True)(
                    [Option("Seleccione un departamento", value="")] +
                    [Option(d, value=d) for d in deptos_sorted]
                )
            ),
            Div(cls="campo-redondeado")(
                Label(icon_dia, "Día de la semana", for_="select-dia"),
                Select(id="select-dia", name="dia_semana", required=True)(
                    [Option("Seleccione un día", value="")] +
                    [Option(v, value=str(k)) for k, v in DIAS_MAP.items()]
                )
            ),
            Div(cls="campo-redondeado")(
                Label(icon_franja, "Franja Horaria", for_="select-franja"),
                Select(id="select-franja", name="franja_horaria", required=True)(
                    [Option("Seleccione una franja", value="")] +
                    [Option(v, value=k) for k, v in FRANJAS_MAP.items()]
                )
            ),
            Div(cls="campo-redondeado")(
                Label(icon_mes, "Mes", for_="select-mes"),
                Select(id="select-mes", name="mes", required=True)(
                    [Option("Seleccione un mes", value="")] +
                    [Option(v, value=str(k)) for k, v in MESES_MAP.items()]
                )
            )
        ),
        Button("Consultar Frecuencia Esperada", type="submit", id="btn-consultar-frecuencia")
    )

    content = Div(
        section_label("CONSULTA DE FRECUENCIA"),
        H1("Estimación de denuncias esperadas por zona y horario"),
        P("Seleccione los parámetros geográficos y temporales:", cls="subtitulo"),
        form,
        Div(id="resultado-prediccion")
    )
    return layout(content, "consultar")

#Resultado de la prediccion
@rt("/predecir")
def post(departamento: str = None, dia_semana: str = None, franja_horaria: str = None, mes: str = None):
    logger.info(f"Prediction requested: Dept={departamento}, Dia={dia_semana}, Franja={franja_horaria}, Mes={mes}")

    errors = []
    if not departamento:                      errors.append("Debe seleccionar un departamento.")
    if dia_semana is None or dia_semana == "": errors.append("Debe seleccionar un día de la semana.")
    if not franja_horaria:                    errors.append("Debe seleccionar una franja horaria.")
    if mes is None or mes == "":              errors.append("Debe seleccionar un mes.")

    if errors:
        return Div(cls="error-box")(
            H3("Error de Validación", style="color: var(--nivel-alto); font-weight: 500;"),
            Ul(style="margin-left: 1.5rem; color: var(--ink); font-size: 13px;")(
                [Li(e) for e in errors]
            )
        )

    try:
        res = predecir_casos(
            departamento=departamento,
            dia_semana=int(dia_semana),
            franja_horaria=franja_horaria,
            mes=int(mes)
        )

        casos        = res["casos_esperados"]
        nivel        = res["nivel_frecuencia"].upper()
        posicion_pct = res.get("posicion_percentil", 50)
        color, fondo, rgb = COLORES_NIVEL.get(nivel.lower(), ("var(--nivel-medio)", "var(--nivel-medio-bg)", "217, 119, 6"))

        return Div(
            Div(style="text-align: center; margin-bottom: var(--space-4);")(
                P("Número de denuncias esperadas", cls="etiqueta", style="text-align: center;"),
                P(f"{casos}", cls="valor", style="text-align: center; font-size: 42px; margin-top: var(--space-1);"),
                Div(nivel_badge(nivel), style="margin-top: var(--space-2); text-align: center;")
            ),
            Div(
                Div(
                    Span(cls="gauge-tercio bajo"), Span(cls="gauge-tercio medio"), Span(cls="gauge-tercio alto"),
                    Span(cls="gauge-marcador", style=f"left:{posicion_pct}%;"),
                    cls="gauge-track", role="img",
                    aria_label=f"Posición dentro del rango histórico: nivel {nivel}",
                ),
                Div(Span("bajo"), Span("alto"), cls="gauge-etiquetas"),
                cls="gauge",
            ),
            cls="panel-resultado-fluido",
            style=f"--nivel-color:{color};--nivel-bg:{fondo};--nivel-color-shadow:rgba({rgb}, 0.15)"
        )

    except Exception as e:
        logger.error(f"Error executing prediction: {str(e)}", exc_info=True)
        return Div(cls="error-box")(
            H3("Error Interno", style="color: var(--nivel-alto); font-weight: 500;"),
            P("Ocurrió un error al procesar la predicción.", style="font-size: 13px;"),
            P(str(e), style="font-size: 0.85rem; color: var(--muted); font-family: monospace;")
        )

#Pantalla 3, como funciona el modelo
@rt("/como-funciona")
def get():
    content = Div(cls="articulo")(
        section_label("METODOLOGÍA Y FUNCIONAMIENTO"),
        H1("¿Cómo funciona el sistema?"),
        P(
            "PREDI-FAM utiliza inteligencia artificial para identificar cuándo y dónde suelen "
            "ocurrir más denuncias de violencia familiar, ayudando a organizar mejor el trabajo de prevención.",
            style="margin-bottom: var(--space-6);"
        ),

        # Bloque 01
        Div(cls="burbuja-metodo")(
            H2(Span("01", cls="numero-badge"), "¿Qué hace el modelo?"),
            P(
                "PREDI-FAM calcula el número de denuncias por violencia familiar que se esperan "
                "en un departamento, día, mes y hora específicos. Esto lo hace analizando la "
                "información de las denuncias registradas por la policía durante el año 2019."
            )
        ),

        # Bloque 02
        Div(cls="burbuja-metodo")(
            H2(Span("02", cls="numero-badge"), "¿Qué información utiliza?"),
            P("El sistema utiliza cuatro datos del formulario para dar el resultado:"),
            Ul(
                Li(Strong("Departamento:"), " La región del país que se quiere consultar (25 regiones del Perú)."),
                Li(Strong("Día de la semana:"), " Para ver cómo cambian las denuncias según el día (por ejemplo, si suben los fines de semana)."),
                Li(Strong("Hora del día:"), " Divide el día en madrugada, mañana, tarde y noche para ver en qué momentos hay más casos."),
                Li(Strong("Mes:"), " Para considerar las épocas del año donde suben o bajan las denuncias.")
            )
        ),

        # Bloque 03
        Div(cls="burbuja-metodo")(
            H2(Span("03", cls="numero-badge"), "¿Cómo interpretar el resultado?"),
            P("El resultado muestra la cantidad de denuncias esperadas y las clasifica en tres niveles:"),
            Ul(
                Li(Strong("BAJO:"), " Representa los días con menor cantidad de denuncias en el año."),
                Li(Strong("MEDIO:"), " Representa los días con una cantidad de denuncias moderada o promedio."),
                Li(Strong("ALTO:"), " Representa los días con la mayor cantidad de denuncias en el año.")
            )
        ),

        # Bloque 04
        Div(cls="burbuja-metodo")(
            H2(Span("04", cls="numero-badge"), "¿Cómo se construyó el modelo?"),
            P(
                "Para construir el sistema, entrenamos y comparamos dos modelos de inteligencia artificial: "
                "LightGBM (basado en árboles de decisión) y LinearSVR (basado en regresión lineal). "
                "Ambos se evaluaron con los mismos datos y se seleccionó LightGBM "
                "por haber obtenido la mayor precisión en ambos entrenamientos."
            )
        ),

        # Bloque 05
        Div(cls="burbuja-metodo")(
            H2(Span("05", cls="numero-badge"), "Limitaciones del modelo"),
            Div(cls="limitaciones-box-manantial")(
                Ul(style="padding-left: 0; list-style-type: none; margin-bottom: 0;")(
                    Li(Strong("Datos del año 2019:"), " El sistema solo conoce la información de ese año. No puede prever cambios recientes o situaciones fuera de lo común."),
                    Li(Strong("Solo denuncias oficiales:"), " Calcula las denuncias hechas ante la policía, no los casos reales que no se reportaron."),
                    Li(Strong("Zonas amplias (Departamentos):"), " La información es general para todo el departamento, sin detalle de cada distrito o barrio."),
                    Li(Strong("Solo para planificar:"), " Sirve para organizar el trabajo policial, no para predecir el comportamiento de personas.")
                )
            )
        ),

        Div(style="margin-top: var(--space-6); text-align: center; border-top: 1px solid var(--border); padding-top: var(--space-5);")(
            A("Volver al Consultor", href="/consultar", cls="btn-primary", style="display: inline-flex; width: auto; padding: 0 var(--space-5);")
        )
    )
    return layout(content, "como-funciona")

#Inicia el servidor
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
