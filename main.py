from fasthtml.common import *
import logging
from prediction import predecir_casos, DEPARTAMENTOS_VALIDOS, FRANJAS_VALIDAS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastHTML — static_path='.' means URLs like /static/css/style.css
# are served from ./static/css/style.css (correct).  Using 'static' would
# double up the path and produce 404s.
app, rt = fast_app(static_path='.', default_hdrs=True)

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
    """Layout base global para las 3 pantallas.
    
    Retorna un Html completo con Head (CSS, meta, title) y Body,
    de modo que el CSS personalizado se incluya en cada página.
    """
    head = Head(
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Meta(name="description", content="Sistema de Pronóstico de Frecuencia de Denuncias de Violencia Familiar por departamento y horario en el Perú."),
        Title("PREVI-FAM | Pronóstico de Violencia Familiar"),
        Link(rel="stylesheet", href="/static/css/style.css"),
        # HTMX (incluido por fast_app default_hdrs, pero lo re-declaramos por si acaso)
        Script(src="https://unpkg.com/htmx.org@1.9.12"),
    )

    nav_header = Header(
        Div(class_="nav-container")(
            A(class_="logo-link", href="/")(
                Span(class_="logo-text")("PREVI-FAM")
            ),
            Nav(
                Ul(class_="nav-menu")(
                    Li(A(class_=f"nav-link {'active' if active_page == 'inicio' else ''}", href="/", id="nav-inicio")("Inicio")),
                    Li(A(class_=f"nav-link {'active' if active_page == 'consultar' else ''}", href="/consultar", id="nav-consultar")("Consultar")),
                    Li(A(class_=f"nav-link {'active' if active_page == 'como-funciona' else ''}", href="/como-funciona", id="nav-como-funciona")("Cómo funciona"))
                )
            )
        )
    )

    footer = Footer(
        P("© 2026 PREVI-FAM — Estimador de Frecuencia de Denuncias de Violencia Familiar."),
        P("Herramienta analítica de planificación. Todos los derechos reservados.")
    )

    return Html(
        head,
        Body(
            nav_header,
            Main(class_="content-wrapper fade-in")(content),
            footer
        )
    )

# --- PANTALLA 1: INICIO / PRESENTACIÓN ---
@rt("/")
def get():
    content = Div(class_="grid-2")(
        Div(class_="hero-text-content")(
            H1(class_="hero-title")("Estimador de Frecuencia de Denuncias de Violencia Familiar"),
            P(class_="hero-subtitle")(
                "Una herramienta analítica avanzada diseñada para estimar la frecuencia esperada de denuncias "
                "de violencia familiar por zona geográfica, día de la semana, mes y franja horaria. "
                "Optimice la toma de decisiones y la distribución de recursos preventivos."
            ),
            Div(class_="highlight-card card mb-8")(
                H3("¿A quién beneficia?"),
                P("Personal de planificación operativa policial (patrullaje preventivo) y formuladores de políticas de seguridad pública que necesitan priorizar recursos de manera inteligente en el territorio."),
                H3("¿Para quién está diseñado?"),
                P("Diseñado para personal no técnico. No requiere conocimientos estadísticos ni de programación: simplemente seleccione las opciones del formulario y obtenga un pronóstico inmediato.")
            ),
            A(class_="btn-primary", href="/consultar", id="btn-comenzar-consulta")("Comenzar Consulta ➔")
        ),
        Div(class_="hero-img-container")(
            Img(src="/static/img/presentacion.png", alt="Visualización de Mapas y Analítica de Seguridad", id="hero-image")
        )
    )
    return layout(content, "inicio")

# --- PANTALLA 2: CONSULTAR (Formulario y Resultados) ---
@rt("/consultar")
def get():
    # Sort departments for display, ensuring a neat alphabetized list
    deptos_sorted = sorted(DEPARTAMENTOS_VALIDOS)
    
    # hx_post handles the submit via HTMX; action/method are fallback for no-JS
    form = Form(hx_post="/predecir", hx_target="#resultado-prediccion", hx_swap="innerHTML", class_="card")(
        H2("Parámetros de Consulta"),
        P("Seleccione los parámetros geográficos y temporales para estimar la frecuencia de denuncias:"),
        
        # Departamento
        Div(class_="form-group")(
            Label(for_="select-depto", class_="form-label")("Departamento"),
            Select(id="select-depto", name="departamento", class_="form-select", required=True)(
                [Option(value="")("Seleccione un departamento")] + 
                [Option(value=d)(d) for d in deptos_sorted]
            )
        ),
        
        # Día de la semana
        Div(class_="form-group")(
            Label(for_="select-dia", class_="form-label")("Día de la semana"),
            Select(id="select-dia", name="dia_semana", class_="form-select", required=True)(
                [Option(value="")("Seleccione un día")] +
                [Option(value=str(k))(v) for k, v in DIAS_MAP.items()]
            )
        ),
        
        # Franja horaria
        Div(class_="form-group")(
            Label(for_="select-franja", class_="form-label")("Franja Horaria"),
            Select(id="select-franja", name="franja_horaria", class_="form-select", required=True)(
                [Option(value="")("Seleccione una franja")] +
                [Option(value=f)(f.capitalize()) for f in FRANJAS_VALIDAS]
            )
        ),
        
        # Mes
        Div(class_="form-group")(
            Label(for_="select-mes", class_="form-label")("Mes"),
            Select(id="select-mes", name="mes", class_="form-select", required=True)(
                [Option(value="")("Seleccione un mes")] +
                [Option(value=str(k))(v) for k, v in MESES_MAP.items()]
            )
        ),
        
        Button(type="submit", class_="btn-primary", style="width: 100%; margin-top: 1rem;", id="btn-consultar-frecuencia")("Consultar Frecuencia Esperada")
    )
    
    # Right panel containing instructions initially and predictions later
    info_panel = Div(id="resultado-prediccion", class_="card", style="height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; border-style: dashed; border-width: 2px; min-height: 400px;")(
        Span(style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.6;")("📊"),
        H3("Esperando Consulta"),
        P("Complete el formulario de la izquierda y haga clic en 'Consultar Frecuencia Esperada' para visualizar el resultado de la predicción y el nivel de prioridad.")
    )
    
    content = Div(class_="grid-2")(
        form,
        info_panel
    )
    return layout(content, "consultar")

# --- POST PROCESAR PREDICCIÓN ---
@rt("/predecir")
def post(departamento: str = None, dia_semana: str = None, franja_horaria: str = None, mes: str = None):
    # Log incoming parameters
    logger.info(f"Prediction requested: Dept={departamento}, Dia={dia_semana}, Franja={franja_horaria}, Mes={mes}")
    
    # Validation of parameters
    errors = []
    if not departamento:
        errors.append("Debe seleccionar un departamento.")
    if dia_semana is None or dia_semana == "":
        errors.append("Debe seleccionar un día de la semana.")
    if not franja_horaria:
        errors.append("Debe seleccionar una franja horaria.")
    if mes is None or mes == "":
        errors.append("Debe seleccionar un mes.")
        
    if errors:
        return Div(class_="result-box alto", style="text-align: left;")(
            H3("⚠️ Error de Validación"),
            Ul(style="margin-left: 1.5rem; color: #f43f5e;")(
                [Li()(e) for e in errors]
            )
        )
        
    try:
        dia_int = int(dia_semana)
        mes_int = int(mes)
        
        # Predict using our module
        res = predecir_casos(
            departamento=departamento,
            dia_semana=dia_int,
            franja_horaria=franja_horaria,
            mes=mes_int
        )
        
        casos = res["casos_esperados"]
        nivel = res["nivel_frecuencia"]
        nivel_lower = nivel.lower() # bajo / medio / alto for CSS class
        
        # Friendly text summaries
        dia_nombre = DIAS_MAP.get(dia_int, str(dia_int))
        mes_nombre = MESES_MAP.get(mes_int, str(mes_int))
        
        disclaimer = Div(class_="disclaimer-box")(
            Span(class_="disclaimer-icon")("ℹ️"),
            P("Aviso de uso responsable: Este pronóstico estima denuncias registradas con base en patrones históricos de 2019. Apoya la planificación estratégica, pero no reemplaza el juicio profesional de los analistas ni predice incidentes individuales de violencia.")
        )
        
        return Div(class_=f"result-box {nivel_lower}")(
            Span(class_="badge")(f"Prioridad: {nivel}"),
            H3("Frecuencia Estimada"),
            Div(class_="result-number")(f"≈ {casos}"),
            P(class_="mb-4")(f"Denuncias esperadas en el departamento de "),
            Strong(style="color: var(--color-text-primary); font-size: 1.2rem;")(f"{departamento}"),
            P(style="font-size: 0.95rem; margin-top: 0.5rem;")(f"Filtros: {dia_nombre} • {franja_horaria.capitalize()} • {mes_nombre}"),
            disclaimer
        )
        
    except Exception as e:
        logger.error(f"Error executing prediction: {str(e)}", exc_info=True)
        return Div(class_="result-box alto")(
            H3("⚠️ Error Interno"),
            P("Ocurrió un error al procesar la predicción en el servidor."),
            P(style="font-size: 0.85rem; color: rgba(255,255,255,0.7);")(str(e))
        )

# --- PANTALLA 3: CÓMO FUNCIONA ---
@rt("/como-funciona")
def get():
    content = Div(class_="fade-in")(
        H1(class_="page-title")("¿Cómo funciona el sistema?"),
        P(style="font-size: 1.1rem; margin-bottom: 2rem; max-width: 800px;")(
            "PREVI-FAM utiliza algoritmos de Aprendizaje Automático entrenados con registros agregados de "
            "denuncias policiales para identificar patrones espacio-temporales y estimar el nivel de riesgo/frecuencia."
        ),
        
        Div(class_="grid-2 mb-8")(
            Div(class_="card highlight-card")(
                H2("Metodología y Entrenamiento"),
                P(
                    "El modelo fue desarrollado entrenando y comparando múltiples algoritmos de regresión sobre "
                    "los datos nacionales agregados. El dataset de entrenamiento se estructuró a nivel de: "
                    "Departamento × Día de la semana × Franja horaria × Mes, sumando un total de 8,400 registros."
                ),
                P(
                    "Se entrenaron y evaluaron por separado dos modelos principales: LightGBM (LGBMRegressor) y "
                    "LinearSVR. Tras someterlos a una validación temporal rigurosa (utilizando los últimos 3 meses de 2019 "
                    "como set de prueba no visto), se seleccionó el modelo con mayor coeficiente de determinación (R²)."
                )
            ),
            Div(class_="card")(
                H2("Comparativa de Modelos"),
                H3("LightGBM (Modelo Seleccionado)"),
                P("Es un framework basado en árboles de decisión con boosting de gradiente. Permite capturar complejas relaciones no lineales entre variables, como picos específicos de delincuencia en un departamento concreto en ciertas horas de la noche los fines de semana."),
                H3("LinearSVR"),
                P("Modelo de vectores de soporte lineal que busca ajustar la mejor línea de regresión para estimar los casos. Aunque es robusto y simple, no captura con tanta precisión las interacciones complejas entre departamentos y horarios.")
            )
        ),
        
        H2("¿Qué variables utiliza?"),
        Div(class_="features-container mb-8")(
            Div(class_="feature-card")(
                Div(class_="feature-icon")("📍"),
                H3("Departamento"),
                P("Identifica la zona geográfica. Permite al modelo estimar la densidad base del histórico de denuncias por cada una de las 25 regiones del país.")
            ),
            Div(class_="feature-card")(
                Div(class_="feature-icon")("📅"),
                H3("Día de la Semana"),
                P("Captura las fluctuaciones de comportamiento semanal (ej: incrementos en fines de semana o domingos).")
            ),
            Div(class_="feature-card")(
                Div(class_="feature-icon")("⏰"),
                H3("Franja Horaria"),
                P("Clasifica el día en cuatro bandas (Madrugada, Mañana, Tarde, Noche) para identificar el comportamiento horario de las agresiones.")
            ),
            Div(class_="feature-card")(
                Div(class_="feature-icon")("🍂"),
                H3("Mes del Año"),
                P("Permite al modelo ajustar estacionalidades climáticas o festividades a lo largo del año calendario.")
            )
        ),
        
        Div(class_="card mb-8", style="border-color: rgba(244, 63, 94, 0.2); background: rgba(244, 63, 94, 0.03);")(
            H2(style="color: var(--color-high);")("Limitaciones del Modelo"),
            Ul(class_="bullet-list")(
                Li()("Aprende de un solo año de datos (2019): No asume tendencias a largo plazo ni es capaz de prever alteraciones extremas no contenidas en dicho período histórico."),
                Li()("Subreporte estructural: El modelo predice denuncias oficiales formalizadas ante comisarías, lo cual difiere de la cantidad de incidentes reales de violencia familiar debido a la cifra negra del delito."),
                Li()("Granularidad regional: Al operar a nivel departamental, no detalla la incidencia exacta a nivel de distritos, barrios o comisarías específicas."),
                Li()("Apoyo de planificación: Su diseño es exclusivo para soporte de planificación general y operativa. No debe utilizarse para predecir comportamientos o riesgos de personas individuales.")
            )
        )
    )
    return layout(content, "como-funciona")

# Start application server
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
