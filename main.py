from fasthtml.common import *
from starlette.staticfiles import StaticFiles
import logging
from pathlib import Path
from prediction import predecir_casos, DEPARTAMENTOS_VALIDOS, FRANJAS_VALIDAS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastHTML
app, rt = fast_app(default_hdrs=True)

# Serve static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Days of the week mapped for the user
DIAS_MAP = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

# Months mapped for the user
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

def layout(content, active_page):
    """Layout base global para las 3 pantallas."""
    head = Head(
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Meta(name="description", content="Sistema de Pronóstico de Frecuencia de Denuncias de Violencia Familiar por departamento y horario en el Perú."),
        Title("PREVI-FAM | Pronóstico de Violencia Familiar"),
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Spectral:wght@600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap"),
        Link(rel="stylesheet", href="/static/css/styles.css"),
        # HTMX
        Script(src="https://unpkg.com/htmx.org@1.9.12"),
    )

    nav_header = Header(
        Div(cls="franja-identidad"),
        Nav(
            A(
                NotStr('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: var(--color-accent-line);"><path d="M12 2L2 12l10 10 10-10L12 2z"/><line x1="7" y1="7" x2="17" y2="17"/></svg>'),
                Span("Estimador de Denuncias"), 
                cls="nav-marca", href="/"
            ),
            Div(cls="enlaces")(
                A("consultar", cls=f"{'activo' if active_page == 'consultar' else ''}", href="/consultar", id="nav-consultar"),
                A("cómo funciona", cls=f"{'activo' if active_page == 'como-funciona' else ''}", href="/como-funciona", id="nav-como-funciona")
            )
        )
    )

    footer = Footer(
        P("Fuente: denuncias PNP 2019 · modelo actualizado — v1.0", cls="pie-pagina text-center", style="text-align: center;")
    )

    return Html(
        head,
        Body(
            nav_header,
            Main(content),
            footer
        )
    )

# --- PANTALLA 1: INICIO / PRESENTACIÓN ---
@rt("/")
def get():
    content = Div(
        P("PLANIFICACIÓN DE PATRULLAJE PREVENTIVO", cls="eyebrow"),
        H1("Estimador de frecuencia de denuncias\npor zona y horario", style="white-space: pre-wrap;"),
        P(
            "Una herramienta analítica avanzada diseñada para estimar la frecuencia esperada de denuncias "
            "de violencia familiar por zona geográfica, día de la semana, mes y franja horaria. "
            "Optimice la toma de decisiones y la distribución de recursos preventivos.",
            cls="subtitulo"
        ),
        Img(src="/static/img/presentacion.png", alt="Visualización de Mapas y Analítica de Seguridad", style="max-width: 100%; border-radius: var(--radius-card); margin-bottom: var(--space-5);"),
        H2("¿A quién beneficia?"),
        P("Personal de planificación operativa policial (patrullaje preventivo) y formuladores de políticas de seguridad pública que necesitan priorizar recursos de manera inteligente en el territorio.", cls="subtitulo"),
        H2("¿Para quién está diseñado?"),
        P("Diseñado para personal no técnico. No requiere conocimientos estadísticos ni de programación: simplemente seleccione las opciones del formulario y obtenga un pronóstico inmediato.", cls="subtitulo"),
        Div(cls="mt-4")(
            A("Comenzar Consulta", cls="btn-primary", href="/consultar", style="display: inline-block; padding: 10px 24px; background: var(--color-primary); color: #EEF0EA; border-radius: var(--radius-control); text-decoration: none; font-weight: 600; font-size: 13px;")
        )
    )
    return layout(content, "inicio")

# --- PANTALLA 2: CONSULTAR (Formulario y Resultados) ---
@rt("/consultar")
def get():
    deptos_sorted = sorted(DEPARTAMENTOS_VALIDOS)
    
    icon_depto = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.2"/></svg>')
    icon_dia = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>')
    icon_franja = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>')
    icon_mes = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>')
    
    form = Form(hx_post="/predecir", hx_target="#resultado-prediccion", hx_swap="innerHTML", cls="tarjeta-formulario")(
        Div(cls="grilla-campos")(
            Div(cls="campo")(
                Label(icon_depto, "Departamento", for_="select-depto"),
                Select(id="select-depto", name="departamento", required=True)(
                    [Option("Seleccione un departamento", value="")] + 
                    [Option(d, value=d) for d in deptos_sorted]
                )
            ),
            
            Div(cls="campo")(
                Label(icon_dia, "Día de la semana", for_="select-dia"),
                Select(id="select-dia", name="dia_semana", required=True)(
                    [Option("Seleccione un día", value="")] +
                    [Option(v, value=str(k)) for k, v in DIAS_MAP.items()]
                )
            ),
            
            Div(cls="campo")(
                Label(icon_franja, "Franja Horaria", for_="select-franja"),
                Select(id="select-franja", name="franja_horaria", required=True)(
                    [Option("Seleccione una franja", value="")] +
                    [Option(f.capitalize(), value=f) for f in FRANJAS_VALIDAS]
                )
            ),
            
            Div(cls="campo")(
                Label(icon_mes, "Mes", for_="select-mes"),
                Select(id="select-mes", name="mes", required=True)(
                    [Option("Seleccione un mes", value="")] +
                    [Option(v, value=str(k)) for k, v in MESES_MAP.items()]
                )
            )
        ),
        
        Button("Consultar Frecuencia Esperada", type="submit", id="btn-consultar-frecuencia")
    )
    
    info_panel = Div(id="resultado-prediccion")
    
    content = Div(
        P("PLANIFICACIÓN DE PATRULLAJE PREVENTIVO", cls="eyebrow"),
        H1("Estimador de frecuencia de denuncias\npor zona y horario", style="white-space: pre-wrap;"),
        P("Seleccione los parámetros geográficos y temporales:", cls="subtitulo"),
        form,
        info_panel
    )
    return layout(content, "consultar")

# --- POST PROCESAR PREDICCIÓN ---
COLORES_NIVEL = {
    "bajo":  ("var(--color-alert-bajo)",  "var(--color-alert-bajo-bg)"),
    "medio": ("var(--color-alert-medio)", "var(--color-alert-medio-bg)"),
    "alto":  ("var(--color-alert-alto)",  "var(--color-alert-alto-bg)"),
}
icon_aviso = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>')

@rt("/predecir")
def post(departamento: str = None, dia_semana: str = None, franja_horaria: str = None, mes: str = None):
    logger.info(f"Prediction requested: Dept={departamento}, Dia={dia_semana}, Franja={franja_horaria}, Mes={mes}")
    
    errors = []
    if not departamento: errors.append("Debe seleccionar un departamento.")
    if dia_semana is None or dia_semana == "": errors.append("Debe seleccionar un día de la semana.")
    if not franja_horaria: errors.append("Debe seleccionar una franja horaria.")
    if mes is None or mes == "": errors.append("Debe seleccionar un mes.")
        
    if errors:
        return Div(style="border: 1px solid var(--color-alert-alto); padding: var(--space-4); margin-top: var(--space-4); border-radius: var(--radius-card); background: var(--color-alert-alto-bg);")(
            H3("⚠️ Error de Validación", style="color: var(--color-alert-alto); margin-top: 0; font-family: 'Inter', sans-serif; font-size: 15px;"),
            Ul(style="margin-left: 1.5rem; color: var(--color-ink); font-size: 13px; font-family: 'Inter', sans-serif;")(
                [Li(e) for e in errors]
            )
        )
        
    try:
        dia_int = int(dia_semana)
        mes_int = int(mes)
        
        res = predecir_casos(
            departamento=departamento,
            dia_semana=dia_int,
            franja_horaria=franja_horaria,
            mes=mes_int
        )
        
        casos = res["casos_esperados"]
        nivel = res["nivel_frecuencia"].upper()
        posicion_pct = res.get("posicion_percentil", 50)
        
        color, fondo = COLORES_NIVEL.get(nivel.lower(), ("var(--color-alert-medio)", "var(--color-alert-medio-bg)"))
        
        return Div(
            Div(
                Div(P("Denuncias esperadas", cls="etiqueta"),
                    P(f"≈ {casos}", cls="valor")),
                Span(f"NIVEL {nivel}", cls="badge-nivel",
                     style=f"--nivel-color:{color};--nivel-bg:{fondo}"),
                cls="fila-resultado",
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
            Div(
                icon_aviso,
                Span("Herramienta de apoyo a la planificación de recursos. No reemplaza el criterio del personal encargado ni predice hechos individuales."),
                cls="aviso-responsable"
            ),
            cls="panel-resultado",
            style=f"--nivel-color:{color}"
        )
        
    except Exception as e:
        logger.error(f"Error executing prediction: {str(e)}", exc_info=True)
        return Div(style="border: 1px solid var(--color-alert-alto); padding: var(--space-4); margin-top: var(--space-4); border-radius: var(--radius-card); background: var(--color-alert-alto-bg);")(
            H3("⚠️ Error Interno", style="color: var(--color-alert-alto); margin-top: 0; font-family: 'Inter', sans-serif; font-size: 15px;"),
            P("Ocurrió un error al procesar la predicción.", style="font-family: 'Inter', sans-serif; font-size: 13px;"),
            P(str(e), style="font-size: 0.85rem; color: var(--color-muted); font-family: 'IBM Plex Mono', monospace;")
        )

# --- PANTALLA 3: CÓMO FUNCIONA ---
@rt("/como-funciona")
def get():
    icon_aviso_limitaciones = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-top: 2px; color: var(--color-muted);"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>')
    content = Div(cls="articulo")(
        H1("¿Cómo funciona el sistema?"),
        P(
            "PREVI-FAM utiliza algoritmos de Aprendizaje Automático entrenados con registros agregados de "
            "denuncias policiales para identificar patrones espacio-temporales y estimar el nivel de riesgo/frecuencia."
        ),
        
        H2(Span("01", cls="indice"), "Metodología y Entrenamiento"),
        P(
            "El modelo fue desarrollado entrenando y comparando múltiples algoritmos de regresión sobre "
            "los datos nacionales agregados. El dataset de entrenamiento se estructuró a nivel de: "
            "Departamento × Día de la semana × Franja horaria × Mes, sumando un total de 8,400 registros."
        ),
        P(
            "Se entrenaron y evaluaron por separado dos modelos principales: LightGBM (LGBMRegressor) y "
            "LinearSVR. Tras someterlos a una validación temporal rigurosa, se seleccionó el modelo "
            "con mayor coeficiente de determinación (R²)."
        ),
        
        H2(Span("02", cls="indice"), "Comparativa de Modelos"),
        P(Strong("LightGBM (Modelo Seleccionado): "), "Es un framework basado en árboles de decisión con boosting de gradiente. Permite capturar complejas relaciones no lineales entre variables, como picos específicos de delincuencia en un departamento concreto en ciertas horas de la noche los fines de semana."),
        P(Strong("LinearSVR: "), "Modelo de vectores de soporte lineal que busca ajustar la mejor línea de regresión para estimar los casos. Aunque es robusto y simple, no captura con tanta precisión las interacciones complejas entre departamentos y horarios."),
        
        H2(Span("03", cls="indice"), "¿Qué variables utiliza?"),
        Ul(
            Li(Strong("Departamento:"), " Identifica la zona geográfica. Permite al modelo estimar la densidad base del histórico de denuncias por cada una de las 25 regiones del país."),
            Li(Strong("Día de la Semana:"), " Captura las fluctuaciones de comportamiento semanal (ej: incrementos en fines de semana o domingos)."),
            Li(Strong("Franja Horaria:"), " Clasifica el día en cuatro bandas (Madrugada, Mañana, Tarde, Noche) para identificar el comportamiento horario de las agresiones."),
            Li(Strong("Mes del Año:"), " Permite al modelo ajustar estacionalidades climáticas o festividades a lo largo del año calendario.")
        ),
        
        H2(Span("04", cls="indice"), "Limitaciones del Modelo"),
        Div(cls="limitaciones-box")(
            Div(style="display: flex; gap: var(--space-2);")(
                icon_aviso_limitaciones,
                Div(
                    Ul(style="padding-left: 0; list-style-position: outside; margin-bottom: 0; list-style-type: none;")(
                        Li(Strong("Aprende de un solo año de datos (2019):"), " No asume tendencias a largo plazo ni es capaz de prever alteraciones extremas no contenidas en dicho período histórico."),
                        Li(Strong("Subreporte estructural:"), " El modelo predice denuncias oficiales formalizadas ante comisarías, lo cual difiere de la cantidad de incidentes reales de violencia familiar debido a la cifra negra del delito."),
                        Li(Strong("Granularidad regional:"), " Al operar a nivel departamental, no detalla la incidencia exacta a nivel de distritos, barrios o comisarías específicas."),
                        Li(Strong("Apoyo de planificación:"), " Su diseño es exclusivo para soporte de planificación general y operativa. No debe utilizarse para predecir comportamientos o riesgos de personas individuales.")
                    )
                )
            )
        )
    )
    return layout(content, "como-funciona")

# Start application server
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
