from fasthtml.common import *
from starlette.staticfiles import StaticFiles
import logging
from pathlib import Path
from prediction import predecir_casos, DEPARTAMENTOS_VALIDOS, FRANJAS_VALIDAS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastHTML
app, rt = fast_app(pico=False, default_hdrs=True)

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

# Friendly mapping for timeframes with Spanish Ñ and hour ranges
FRANJAS_MAP = {
    "MADRUGADA": "Madrugada (12 a.m. a 6 a.m.)",
    "MANANA": "Mañana (6 a.m. a 12 p.m.)",
    "TARDE": "Tarde (12 p.m. a 6 p.m.)",
    "NOCHE": "Noche (6 p.m. a 12 a.m.)"
}

# Colors for prediction levels (Manantial Design)
COLORES_NIVEL = {
    "bajo":  ("var(--nivel-bajo)",  "var(--nivel-bajo-bg)",  "22, 163, 74"),
    "medio": ("var(--nivel-medio)", "var(--nivel-medio-bg)", "217, 119, 6"),
    "alto":  ("var(--nivel-alto)",  "var(--nivel-alto-bg)",  "220, 38, 38"),
}

# --- REUSABLE COMPONENTS ---

def header_nav(active_page):
    """Barra superior translúcida con logo monograma y enlaces de navegación."""
    monograma_svg = NotStr(
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="1.5" style="flex-shrink: 0;">'
        '<path d="M12 2L2 12l10 10 10-10L12 2z"/>'
        '<line x1="7" y1="7" x2="17" y2="17"/>'
        '</svg>'
    )
    
    return Header(
        Div(cls="franja-identidad"),
        Nav(
            A(
                monograma_svg,
                Span("PREDI-FAM"), 
                cls="nav-marca", href="/"
            ),
            Div(cls="enlaces")(
                A("Inicio", cls=f"{'activo' if active_page == 'inicio' else ''}", href="/", id="nav-inicio"),
                A("Consultar", cls=f"{'activo' if active_page == 'consultar' else ''}", href="/consultar", id="nav-consultar"),
                A("Cómo funciona", cls=f"{'activo' if active_page == 'como-funciona' else ''}", href="/como-funciona", id="nav-como-funciona")
            )
        )
    )

def section_label(texto):
    """Etiqueta pequeña superior en turquesa."""
    return P(texto, cls="eyebrow")

def stat_card(numero, descripcion):
    """Tarjeta de estadística en forma de burbuja líquida flotante."""
    return Div(cls="stat-burbuja")(
        P(numero, cls="stat-numero"),
        P(descripcion, cls="stat-descripcion")
    )

def nivel_badge(nivel):
    """Etiqueta redondeada líquida del nivel de alerta."""
    nivel_lower = nivel.lower()
    color, fondo, _ = COLORES_NIVEL.get(nivel_lower, ("var(--nivel-medio)", "var(--nivel-medio-bg)", "217, 119, 6"))
    return Span(f"Nivel {nivel.capitalize()}", cls="badge-nivel-fluido",
                style=f"--nivel-color:{color};--nivel-bg:{fondo}")

def aviso_responsable():
    """Caja informativa legal."""
    icon_aviso = NotStr(
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">'
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/>'
        '<line x1="12" y1="17" x2="12.01" y2="17"/>'
        '</svg>'
    )
    return Div(
        icon_aviso,
        Span("Herramienta de apoyo a la planificación de recursos. No reemplaza el criterio profesional ni predice hechos individuales."),
        cls="aviso-responsable"
    )

def footer():
    """Pie de página unificado."""
    return Footer(
        P("Fuente: denuncias de la Policía Nacional del Perú en 2019, modelo actualizado, versión 1.0", cls="pie-pagina")
    )

# --- GLOBAL LAYOUT ---

def layout(content, active_page):
    """Layout global para Horizonte."""
    head = Head(
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Meta(name="description", content="Sistema de pronóstico de frecuencia de denuncias de violencia familiar por departamento y horario en el Perú."),
        Title("PREDI-FAM | Pronóstico de Violencia Familiar"),
        Link(rel="stylesheet", href="/static/css/styles.css?v=4.0"),
        # HTMX
        Script(src="https://unpkg.com/htmx.org@1.9.12"),
    )

    return Html(
        head,
        Body(
            header_nav(active_page),
            Main(content),
            footer()
        )
    )

# --- PANTALLA 1: INICIO ---
@rt("/")
def get():
    # Fotos reales de familias felices (enlaces válidos de Unsplash)
    foto_hero_url = "https://images.unsplash.com/photo-1542037104857-ffbb0b9155fb?w=900&q=80"
    foto_secundaria_url = "https://plus.unsplash.com/premium_photo-1661475916373-5aaaeb4a5393?w=900&q=80"

    content = Div(
        # 1. Presentación asimétrica a dos columnas
        Div(cls="presentacion-dos-columnas")(
            Div(cls="burbuja-liquida")(
                section_label("PANTALLA DE INICIO"),
                H1("Apoyo a la planificación de patrullaje preventivo"),
                P(
                    "Una herramienta analítica avanzada diseñada para estimar la frecuencia esperada de denuncias "
                    "de violencia familiar por zona geográfica, día de la semana, mes y franja horaria. "
                    "Optimice la toma de decisiones y la distribución de recursos preventivos.",
                    cls="subtitulo"
                )
            ),
            Img(src=foto_hero_url, alt="Familia feliz al aire libre que proyecta seguridad", cls="marco-gota")
        ),
        
        # 2. Burbujas de estadísticas flotantes asimétricas
        Div(cls="stat-burbujas-contenedor")(
            stat_card("25", "Departamentos cubiertos"),
            stat_card("4", "Franjas horarias"),
            stat_card("2019", "Año base de datos")
        ),
        
        # 3. Bloque de beneficios alternativo
        Div(cls="presentacion-dos-columnas")(
            Div(cls="burbuja-liquida")(
                H2("¿A quién beneficia?"),
                P("Personal de planificación operativa policial de patrullaje preventivo y formuladores de políticas de seguridad pública que necesitan priorizar recursos de manera inteligente en el territorio.", cls="subtitulo", style="margin-bottom: var(--space-4);"),
                
                H2("¿Para quién está diseñado?"),
                P("Diseñado para personal no técnico. No requiere conocimientos estadísticos ni de programación, simplemente seleccione las opciones del formulario y obtenga un pronóstico inmediato.", cls="subtitulo", style="margin-bottom: 0;")
            ),
            Img(src=foto_secundaria_url, alt="Familia en un entorno hogareño pacífico", cls="marco-gota")
        ),
        
        # 4. Botón centrado y aviso legal
        Div(style="text-align: center; margin-top: var(--space-5); margin-bottom: var(--space-5);")(
            A("Comenzar Consulta", cls="btn-primary", href="/consultar", style="display: inline-flex; width: auto; padding: 0 var(--space-6); margin-bottom: var(--space-5);"),
            aviso_responsable()
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
    
    info_panel = Div(id="resultado-prediccion")
    
    content = Div(
        section_label("CONSULTA DE FRECUENCIA"),
        H1("Estimación de denuncias esperadas por zona y horario"),
        P("Seleccione los parámetros geográficos y temporales:", cls="subtitulo"),
        form,
        info_panel
    )
    return layout(content, "consultar")

# --- POST PROCESAR PREDICCIÓN ---
@rt("/predecir")
def post(departamento: str = None, dia_semana: str = None, franja_horaria: str = None, mes: str = None):
    logger.info(f"Prediction requested: Dept={departamento}, Dia={dia_semana}, Franja={franja_horaria}, Mes={mes}")
    
    errors = []
    if not departamento: errors.append("Debe seleccionar un departamento.")
    if dia_semana is None or dia_semana == "": errors.append("Debe seleccionar un día de la semana.")
    if not franja_horaria: errors.append("Debe seleccionar una franja horaria.")
    if mes is None or mes == "": errors.append("Debe seleccionar un mes.")
        
    if errors:
        return Div(cls="error-box")(
            H3("Error de Validación", style="color: var(--nivel-alto); font-weight: 500;"),
            Ul(style="margin-left: 1.5rem; color: var(--ink); font-size: 13px;")(
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
        
        color, fondo, rgb = COLORES_NIVEL.get(nivel.lower(), ("var(--nivel-medio)", "var(--nivel-medio-bg)", "217, 119, 6"))
        
        return Div(
            Div(
                Div(P("Denuncias esperadas", cls="etiqueta"),
                    P(f"≈ {casos}", cls="valor")),
                nivel_badge(nivel),
                cls="fila-resultado-fluida",
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
            aviso_responsable(),
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

# --- PANTALLA 3: CÓMO FUNCIONA ---
@rt("/como-funciona")
def get():
    icon_aviso_limitaciones = NotStr(
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" stroke-width="1.5" style="margin-top: 2px; flex-shrink: 0;">'
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/>'
        '<line x1="12" y1="17" x2="12.01" y2="17"/>'
        '</svg>'
    )
    
    content = Div(cls="articulo")(
        section_label("METODOLOGÍA Y FUNCIONAMIENTO"),
        H1("¿Cómo funciona el sistema?"),
        P(
            "PREDI-FAM utiliza algoritmos de Aprendizaje Automático entrenados con registros agregados de "
            "denuncias policiales para identificar patrones espacio-temporales y estimar el nivel de riesgo/frecuencia."
        ),
        
        # Bloque 01
        Div(cls="burbuja-metodo")(
            H2(Span("01", cls="numero-badge"), "¿Qué hace el modelo?"),
            P(
                "PREDI-FAM estima cuántas denuncias de violencia familiar son esperables "
                "en un departamento, día de la semana, mes y franja horaria determinados, "
                "aprendiendo de los patrones históricos de los registros policiales del año 2019."
            )
        ),
        
        # Bloque 02
        Div(cls="burbuja-metodo")(
            H2(Span("02", cls="numero-badge"), "¿Qué información utiliza?"),
            P(
                "El sistema procesa cuatro variables clave del formulario para generar la estimación:"
            ),
            Ul(
                Li(Span("Variable: ", style="color: var(--muted); font-size: 11px; text-transform: uppercase; font-family: monospace; margin-right: 8px;"), Strong("Departamento:"), " identifica la zona geográfica de análisis (25 regiones del país)."),
                Li(Span("Variable: ", style="color: var(--muted); font-size: 11px; text-transform: uppercase; font-family: monospace; margin-right: 8px;"), Strong("Día de la semana:"), " captura variaciones de comportamiento semanal (ej. incrementos en fines de semana)."),
                Li(Span("Variable: ", style="color: var(--muted); font-size: 11px; text-transform: uppercase; font-family: monospace; margin-right: 8px;"), Strong("Franja horaria:"), " divide el día en Madrugada, Mañana, Tarde y Noche para rastrear fluctuaciones horarias."),
                Li(Span("Variable: ", style="color: var(--muted); font-size: 11px; text-transform: uppercase; font-family: monospace; margin-right: 8px;"), Strong("Mes del año:"), " permite al modelo ajustar estacionalidades y festividades a lo largo del año calendarizado.")
            )
        ),
        
        # Bloque 03
        Div(cls="burbuja-metodo")(
            H2(Span("03", cls="numero-badge"), "¿Cómo interpretar el resultado?"),
            P(
                "El resultado muestra una estimación numérica de casos esperados en las condiciones seleccionadas "
                "y clasifica la frecuencia esperada en tres niveles según la distribución histórica del año base:"
            ),
            Ul(
                Li(Span("Nivel: ", style="color: var(--muted); font-size: 11px; text-transform: uppercase; font-family: monospace; margin-right: 8px;"), Strong("BAJO:"), " menor o igual al percentil 33 histórico de casos."),
                Li(Span("Nivel: ", style="color: var(--muted); font-size: 11px; text-transform: uppercase; font-family: monospace; margin-right: 8px;"), Strong("MEDIO:"), " mayor al percentil 33 y menor o igual al percentil 66 histórico."),
                Li(Span("Nivel: ", style="color: var(--muted); font-size: 11px; text-transform: uppercase; font-family: monospace; margin-right: 8px;"), Strong("ALTO:"), " mayor al percentil 66 histórico.")
            )
        ),
        
        # Bloque 04
        Div(cls="burbuja-metodo")(
            H2(Span("04", cls="numero-badge"), "¿Cómo se construyó el modelo?"),
            P(
                "Se entrenaron y evaluaron por separado dos modelos matemáticos sobre los mismos datos: "
                "LightGBM, basado en árboles de decisión que se corrigen sucesivamente, y LinearSVR, "
                "una regresión de vectores de soporte que ajusta una línea de tendencia tolerando un margen de error. "
                "Se compararon bajo una validación temporal estricta y se seleccionó el algoritmo con el "
                "mejor coeficiente de determinación (R²), resultando ganador LightGBM. No existe combinación de modelos, "
                "solo se sirve el de mejor rendimiento."
            )
        ),
        
        # Bloque 05
        Div(cls="burbuja-metodo")(
            H2(Span("05", cls="numero-badge"), "Limitaciones del modelo"),
            Div(cls="limitaciones-box-manantial")(
                Div(style="display: flex; gap: var(--space-2);")(
                    icon_aviso_limitaciones,
                    Div(
                        Ul(style="padding-left: 0; list-style-position: outside; margin-bottom: 0; list-style-type: none;")(
                            Li(Strong("Datos históricos (2019):"), " el modelo aprende únicamente de un año de información. No captura tendencias de largo plazo ni eventos excepcionales fuera de ese periodo."),
                            Li(Strong("Cifra negra del delito:"), " estima denuncias registradas formalmente ante comisarías policiales, no incidentes reales de violencia familiar, los cuales sufren de subreporte."),
                            Li(Strong("Escala geográfica:"), " la granularidad es a nivel departamental, por lo que no detalla incidencia a nivel de distrito, barrio o comisaría."),
                            Li(Strong("Propósito exclusivo:"), " sirve como herramienta de apoyo en planificación operativa general. No debe usarse para predecir comportamientos de personas específicas.")
                        )
                    )
                )
            )
        ),
        
        Div(style="margin-top: var(--space-6); text-align: center; border-top: 1px solid var(--border); padding-top: var(--space-5);")(
            P("¿Listo para probar una consulta con estos parámetros?", style="font-size: 13px; color: var(--muted); margin-bottom: var(--space-3);"),
            A("Volver al Consultor", href="/consultar", cls="btn-primary", style="display: inline-flex; width: auto; padding: 0 var(--space-5);")
        )
    )
    return layout(content, "como-funciona")

# Start application server
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
