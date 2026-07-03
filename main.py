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
        Link(rel="stylesheet", href="/static/css/tokens.css"),
        Link(rel="stylesheet", href="/static/css/styles.css"),
        # HTMX
        Script(src="https://unpkg.com/htmx.org@1.9.12"),
    )

    nav_header = Nav(
        A("PREVI-FAM", cls="navbar-brand", href="/"),
        Div(cls="nav-links")(
            A("Inicio", cls=f"nav-link {'active' if active_page == 'inicio' else ''}", href="/", id="nav-inicio"),
            A("Consultar", cls=f"nav-link {'active' if active_page == 'consultar' else ''}", href="/consultar", id="nav-consultar"),
            A("Cómo funciona", cls=f"nav-link {'active' if active_page == 'como-funciona' else ''}", href="/como-funciona", id="nav-como-funciona")
        ),
        cls="navbar"
    )

    footer = Footer(
        P("© 2026 PREVI-FAM — Estimador de Frecuencia de Denuncias de Violencia Familiar."),
        P("Herramienta analítica de planificación. Todos los derechos reservados.")
    )

    return Html(
        head,
        Body(
            nav_header,
            Main(content, cls="container fade-in"),
            footer
        )
    )

# --- PANTALLA 1: INICIO / PRESENTACIÓN ---
@rt("/")
def get():
    content = Div(cls="text-center content-article")(
        H1("Estimador de Frecuencia de Denuncias de Violencia Familiar"),
        P(
            "Una herramienta analítica avanzada diseñada para estimar la frecuencia esperada de denuncias "
            "de violencia familiar por zona geográfica, día de la semana, mes y franja horaria. "
            "Optimice la toma de decisiones y la distribución de recursos preventivos."
        ),
        Img(src="/static/img/presentacion.png", alt="Visualización de Mapas y Analítica de Seguridad", style="max-width: 100%; border-radius: var(--radius-card); margin: var(--space-md) 0; box-shadow: var(--shadow-card);"),
        H3("¿A quién beneficia?"),
        P("Personal de planificación operativa policial (patrullaje preventivo) y formuladores de políticas de seguridad pública que necesitan priorizar recursos de manera inteligente en el territorio."),
        H3("¿Para quién está diseñado?"),
        P("Diseñado para personal no técnico. No requiere conocimientos estadísticos ni de programación: simplemente seleccione las opciones del formulario y obtenga un pronóstico inmediato."),
        Div(cls="mt-4")(
            A("Comenzar Consulta", cls="btn-primary", href="/consultar", id="btn-comenzar-consulta")
        )
    )
    return layout(content, "inicio")

# --- PANTALLA 2: CONSULTAR (Formulario y Resultados) ---
@rt("/consultar")
def get():
    deptos_sorted = sorted(DEPARTAMENTOS_VALIDOS)
    
    form = Form(hx_post="/predecir", hx_target="#resultado-prediccion", hx_swap="innerHTML", cls="form-card")(
        H2("Parámetros de Consulta", cls="text-center", style="margin-bottom: var(--space-sm); font-size: var(--font-size-lg); border-bottom: none;"),
        P("Seleccione los parámetros geográficos y temporales:", cls="text-center mb-4"),
        
        Div(cls="form-field")(
            Label("Departamento", for_="select-depto"),
            Select(id="select-depto", name="departamento", required=True)(
                [Option("Seleccione un departamento", value="")] + 
                [Option(d, value=d) for d in deptos_sorted]
            )
        ),
        
        Div(cls="form-field")(
            Label("Día de la semana", for_="select-dia"),
            Select(id="select-dia", name="dia_semana", required=True)(
                [Option("Seleccione un día", value="")] +
                [Option(v, value=str(k)) for k, v in DIAS_MAP.items()]
            )
        ),
        
        Div(cls="form-field")(
            Label("Franja Horaria", for_="select-franja"),
            Select(id="select-franja", name="franja_horaria", required=True)(
                [Option("Seleccione una franja", value="")] +
                [Option(f.capitalize(), value=f) for f in FRANJAS_VALIDAS]
            )
        ),
        
        Div(cls="form-field")(
            Label("Mes", for_="select-mes"),
            Select(id="select-mes", name="mes", required=True)(
                [Option("Seleccione un mes", value="")] +
                [Option(v, value=str(k)) for k, v in MESES_MAP.items()]
            )
        ),
        
        Button("Consultar Frecuencia Esperada", type="submit", cls="btn-primary", id="btn-consultar-frecuencia")
    )
    
    info_panel = Div(id="resultado-prediccion", cls="result-card", style="display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 250px; background-color: transparent; border: 2px dashed var(--color-border); box-shadow: none;")(
        Span("📊", style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"),
        H3("Esperando Consulta", style="color: var(--color-text-secondary);"),
        P("Complete el formulario superior para visualizar el resultado.", style="color: var(--color-text-secondary); margin-bottom: 0;")
    )
    
    content = Div(
        form,
        info_panel
    )
    return layout(content, "consultar")

# --- POST PROCESAR PREDICCIÓN ---
NIVEL_CLASE = {
    "BAJO": "badge-bajo",
    "MEDIO": "badge-medio",
    "ALTO": "badge-alto",
}

@rt("/predecir")
def post(departamento: str = None, dia_semana: str = None, franja_horaria: str = None, mes: str = None):
    logger.info(f"Prediction requested: Dept={departamento}, Dia={dia_semana}, Franja={franja_horaria}, Mes={mes}")
    
    errors = []
    if not departamento: errors.append("Debe seleccionar un departamento.")
    if dia_semana is None or dia_semana == "": errors.append("Debe seleccionar un día de la semana.")
    if not franja_horaria: errors.append("Debe seleccionar una franja horaria.")
    if mes is None or mes == "": errors.append("Debe seleccionar un mes.")
        
    if errors:
        return Div(cls="result-card", style="border: 1px solid var(--color-nivel-alto);")(
            H3("⚠️ Error de Validación", style="color: var(--color-nivel-alto); text-align: left; margin-top: 0;"),
            Ul(style="margin-left: 1.5rem; text-align: left; color: var(--color-text-secondary);")(
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
        clase = NIVEL_CLASE.get(nivel, "badge-medio")
        
        dia_nombre = DIAS_MAP.get(dia_int, str(dia_int))
        mes_nombre = MESES_MAP.get(mes_int, str(mes_int))
        
        return Div(cls="result-card")(
            P(f"≈ {casos} denuncias esperadas", cls="result-number"),
            Span(nivel, cls=f"badge-nivel {clase}"),
            Div(style="font-size: 0.95rem; color: var(--color-text-secondary); margin-bottom: var(--space-xs);")(
                f"{departamento} • {dia_nombre} • {franja_horaria.capitalize()} • {mes_nombre}"
            ),
            Div(cls="aviso-responsable")(
                Span("⚠", style="font-size: 1.2rem; color: var(--color-aviso-border);"),
                Span("Herramienta de apoyo a la planificación de recursos. No reemplaza el criterio del personal encargado ni predice hechos individuales.")
            )
        )
        
    except Exception as e:
        logger.error(f"Error executing prediction: {str(e)}", exc_info=True)
        return Div(cls="result-card", style="border: 1px solid var(--color-nivel-alto);")(
            H3("⚠️ Error Interno", style="color: var(--color-nivel-alto); margin-top: 0;"),
            P("Ocurrió un error al procesar la predicción."),
            P(str(e), style="font-size: 0.85rem; color: var(--color-text-secondary);")
        )

# --- PANTALLA 3: CÓMO FUNCIONA ---
@rt("/como-funciona")
def get():
    content = Div(cls="content-article fade-in")(
        H1("¿Cómo funciona el sistema?"),
        P(
            "PREVI-FAM utiliza algoritmos de Aprendizaje Automático entrenados con registros agregados de "
            "denuncias policiales para identificar patrones espacio-temporales y estimar el nivel de riesgo/frecuencia."
        ),
        
        H2("Metodología y Entrenamiento"),
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
        
        H2("Comparativa de Modelos"),
        H3("LightGBM (Modelo Seleccionado)"),
        P("Es un framework basado en árboles de decisión con boosting de gradiente. Permite capturar complejas relaciones no lineales entre variables, como picos específicos de delincuencia en un departamento concreto en ciertas horas de la noche los fines de semana."),
        H3("LinearSVR"),
        P("Modelo de vectores de soporte lineal que busca ajustar la mejor línea de regresión para estimar los casos. Aunque es robusto y simple, no captura con tanta precisión las interacciones complejas entre departamentos y horarios."),
        
        H2("¿Qué variables utiliza?"),
        Ul(
            Li(Strong("Departamento:"), " Identifica la zona geográfica. Permite al modelo estimar la densidad base del histórico de denuncias por cada una de las 25 regiones del país."),
            Li(Strong("Día de la Semana:"), " Captura las fluctuaciones de comportamiento semanal (ej: incrementos en fines de semana o domingos)."),
            Li(Strong("Franja Horaria:"), " Clasifica el día en cuatro bandas (Madrugada, Mañana, Tarde, Noche) para identificar el comportamiento horario de las agresiones."),
            Li(Strong("Mes del Año:"), " Permite al modelo ajustar estacionalidades climáticas o festividades a lo largo del año calendario.")
        ),
        
        H2("Limitaciones del Modelo"),
        Ul(
            Li("Aprende de un solo año de datos (2019): No asume tendencias a largo plazo ni es capaz de prever alteraciones extremas no contenidas en dicho período histórico."),
            Li("Subreporte estructural: El modelo predice denuncias oficiales formalizadas ante comisarías, lo cual difiere de la cantidad de incidentes reales de violencia familiar debido a la cifra negra del delito."),
            Li("Granularidad regional: Al operar a nivel departamental, no detalla la incidencia exacta a nivel de distritos, barrios o comisarías específicas."),
            Li("Apoyo de planificación: Su diseño es exclusivo para soporte de planificación general y operativa. No debe utilizarse para predecir comportamientos o riesgos de personas individuales.")
        )
    )
    return layout(content, "como-funciona")

# Start application server
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
