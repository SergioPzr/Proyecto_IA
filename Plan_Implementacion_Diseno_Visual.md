# Plan de Implementación del Diseño Visual (FastHTML)

## Estimador de Frecuencia de Denuncias

## 0. Alcance de este documento

Este documento **no reemplaza** `03_Plan_Pagina_Web.md`; lo complementa. Aquel define la estructura, las rutas y el flujo de datos de la aplicación FastHTML. **Este documento se enfoca únicamente en el aspecto visual** (CSS, tipografía, colores, espaciado, layout de tarjetas), replicando el estilo observado en el prototipo de referencia (`plan-to-visual-spark.lovable.app`), para que la aplicación FastHTML final se vea como ese diseño.

No incluye backend, modelo de predicción ni lógica de negocio — eso ya está cubierto en los documentos 00, 01 y 04.

**Importante:** solo pude leer el **contenido textual** de la página de referencia (no su hoja de estilos real). Los valores de color/tipografía que propongo abajo son una interpretación razonable del estilo tipo "dashboard institucional" que describe la página, no los valores CSS exactos. Antes de dar por cerrada la Fase 2, quien implemente debe abrir las DevTools del navegador (`Inspeccionar` → pestaña `Elements`/`Computed`) sobre el sitio real y confirmar/ajustar los valores exactos de color, fuente y espaciado.

---

## 1. Resumen del diseño de referencia

Componentes identificados en la página Lovable:

- **Barra de navegación superior fija**, con dos enlaces de texto ("Consultar" / "Cómo funciona").
- **Título + subtítulo** breve explicando el propósito de la herramienta.
- **Formulario vertical de 4 selectores**: Departamento, Día de la semana, Franja horaria, Mes — con etiquetas claras encima de cada campo.
- **Botón de acción principal**, grande, con color de énfasis, texto tipo "Consultar Frecuencia Esperada".
- **Tarjeta de resultado**, que aparece debajo del formulario, con:
  - Número grande y destacado ("≈ 42 denuncias esperadas").
  - Un **badge/etiqueta de nivel** con color semántico (Bajo / Medio / Alto).
  - Datos secundarios de apoyo (percentil, variación % vs. la media de la zona).
  - Una **caja de aviso** visualmente diferenciada (borde o fondo distinto) con el texto de uso responsable.
- **Pantalla "Cómo funciona"**: contenido de lectura, con jerarquía clara de encabezados, sin formularios.
- Estilo general: minimalista, tipo panel de gestión pública/institucional, tarjetas con bordes suaves y sombra ligera, espaciado generoso, sin elementos decorativos innecesarios.

---

## 2. Sistema de diseño (design tokens) propuesto

Definir estos valores en un solo archivo CSS de variables para que todo el sitio use la misma paleta.

```css
:root {
  /* Color base */
  --color-bg: #f7f8fa;
  --color-surface: #ffffff;
  --color-border: #e2e5ea;
  --color-text-primary: #1a1f2b;
  --color-text-secondary: #5b6472;

  /* Color de marca / acción */
  --color-primary: #2563eb;      /* botón principal, enlaces activos */
  --color-primary-hover: #1d4ed8;

  /* Semáforo de niveles de frecuencia */
  --color-nivel-bajo: #16a34a;   /* verde */
  --color-nivel-bajo-bg: #ecfdf3;
  --color-nivel-medio: #d97706;  /* ámbar */
  --color-nivel-medio-bg: #fffaeb;
  --color-nivel-alto: #dc2626;   /* rojo */
  --color-nivel-alto-bg: #fef2f2;

  /* Aviso de uso responsable */
  --color-aviso-bg: #fff8e6;
  --color-aviso-border: #f2c94c;

  /* Tipografía */
  --font-base: "Inter", system-ui, -apple-system, sans-serif;
  --font-size-base: 16px;
  --font-size-lg: 1.25rem;
  --font-size-xl: 2rem;
  --font-size-number: 3rem;

  /* Espaciado */
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: 1.5rem;
  --space-lg: 2.5rem;

  /* Bordes y sombra */
  --radius-card: 12px;
  --radius-input: 8px;
  --shadow-card: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
}
```

> Nota: estos son valores de partida razonables (paleta azul/verde/ámbar/rojo, tipografía Inter, tarjetas con sombra suave). Ajustar en Fase 1 según lo observado en el sitio real.

---

## 3. Estructura de archivos en el proyecto FastHTML

```
proyecto/
├── main.py                  # rutas (definidas en 03_Plan_Pagina_Web.md)
├── static/
│   ├── css/
│   │   ├── tokens.css        # variables de diseño (sección 2)
│   │   └── styles.css        # estilos de componentes (sección 4)
│   └── fonts/                # si se auto-hospeda Inter u otra tipografía
```

FastHTML sirve archivos estáticos automáticamente desde `/static` si se usa `fast_app(static_path="static")` (verificar sintaxis vigente en la documentación de `fasthtml`). En el `layout()` compartido, se agregan los `Link` a las hojas de estilo:

```python
def layout(*contenido):
    return Titled(
        "Pronóstico de Denuncias",
        Link(rel="stylesheet", href="/static/css/tokens.css"),
        Link(rel="stylesheet", href="/static/css/styles.css"),
        Nav(
            A("Consultar", href="/", cls="nav-link"),
            A("Cómo funciona", href="/como-funciona", cls="nav-link"),
            cls="navbar",
        ),
        Main(*contenido, cls="container"),
    )
```

---

## 4. Componentes a estilizar (mapeo directo al esqueleto de 03)

| Componente FastHTML | Clase CSS sugerida | Notas de estilo |
|---|---|---|
| `Nav(...)` | `.navbar` | Fondo `--color-surface`, borde inferior `--color-border`, fija arriba (`position: sticky; top: 0;`), enlaces con `--color-text-secondary` y activo en `--color-primary`. |
| `Main(...)` (wrapper) | `.container` | `max-width: 640px`, centrado, padding `--space-lg`. |
| `Form(...)` | `.form-card` | Fondo `--color-surface`, `border-radius: var(--radius-card)`, `box-shadow: var(--shadow-card)`, padding `--space-md`. |
| Cada `Select` + su label | `.form-field` / `.form-field select` | Label en `--color-text-secondary`, tamaño pequeño, encima del select; select con `border-radius: var(--radius-input)`, borde `--color-border`, altura cómoda (≥ 44px, criterio táctil). |
| `Button("Consultar...")` | `.btn-primary` | Ancho completo o grande, `background: var(--color-primary)`, texto blanco, `:hover` a `--color-primary-hover`, `border-radius: var(--radius-input)`. |
| `Div(id="resultado")` | `.result-card` | Igual estilo de tarjeta que `.form-card`, aparece con transición suave (`opacity`/`transform`) al insertarse vía HTMX. |
| Número esperado | `.result-number` | `font-size: var(--font-size-number)`, peso bold, color `--color-text-primary`. |
| Badge de nivel | `.badge-nivel` con modificador `.badge-bajo` / `.badge-medio` / `.badge-alto` | Fondo y texto según la tabla de la sección 2; forma de "pill" (`border-radius: 999px`), padding `0.25rem 0.75rem`. |
| Aviso de uso responsable | `.aviso-responsable` | Fondo `--color-aviso-bg`, borde izquierdo grueso `--color-aviso-border`, ícono ⚠ + texto en `--color-text-secondary`, tamaño de fuente algo menor que el resto. |
| Contenido de "Cómo funciona" | `.content-article` | `max-width: 680px`, interlineado `1.6`, jerarquía clara con `h2`/`h3`, espaciado entre secciones `--space-lg`. |

---

## 5. Lógica de color dinámico según el nivel

El backend (documento 04) ya devuelve `nivel_frecuencia` como texto (`"Bajo"`, `"Medio"`, `"Alto"`). En la plantilla de resultado, mapear ese valor a una clase CSS:

```python
NIVEL_CLASE = {
    "Bajo": "badge-bajo",
    "Medio": "badge-medio",
    "Alto": "badge-alto",
}

def panel_resultado(resultado):
    clase = NIVEL_CLASE.get(resultado["nivel_frecuencia"], "badge-medio")
    return Div(
        P(f"≈ {resultado['casos_esperados']} denuncias esperadas", cls="result-number"),
        Span(resultado["nivel_frecuencia"].upper(), cls=f"badge-nivel {clase}"),
        Div(
            "⚠ Herramienta de apoyo a la planificación de recursos. "
            "No reemplaza el criterio del personal encargado ni predice hechos individuales.",
            cls="aviso-responsable",
        ),
        cls="result-card",
    )
```

Esto reproduce visualmente el código de color azul/amarillo/rojo (o verde/ámbar/rojo) que se ve en el prototipo, sin acoplar el color a texto libre.

---

## 6. Responsive

- Layout de una sola columna en todo momento (formulario y resultado ya son verticales; no requiere breakpoints complejos).
- `.container` con `padding` fluido: reducir `--space-lg` a `--space-sm` bajo `max-width: 480px` con una media query simple.
- Botón principal siempre a ancho completo en pantallas angostas (`width: 100%` bajo `max-width: 480px`) para uso táctil en campo.

```css
@media (max-width: 480px) {
  .container { padding: var(--space-sm); }
  .btn-primary { width: 100%; }
}
```

---

## 7. Accesibilidad (refuerzo visual de lo ya definido en 03)

- Contraste mínimo AA entre texto y fondo (verificar los tonos de la sección 2 con una herramienta como WebAIM Contrast Checker).
- Cada `Select` debe tener un `Label` asociado por `for`/`id`, no solo texto suelto encima.
- Estado `:focus-visible` visible en selects y botón (outline con `--color-primary`), para navegación por teclado.
- El badge de nivel no debe depender solo del color: incluir siempre el texto ("ALTO", "MEDIO", "BAJO") además del color, como ya está previsto.

---

## 8. Fases de implementación

**Fase 1 — Verificación del diseño real (0.5 día)**
Abrir `plan-to-visual-spark.lovable.app` con DevTools, confirmar/ajustar colores exactos, tipografía y espaciados de la sección 2. Documentar cualquier cambio respecto a los valores propuestos.

**Fase 2 — Tokens y base CSS (0.5 día)**
Crear `static/css/tokens.css` con las variables ya validadas. Crear `static/css/styles.css` vacío con el reset básico (`box-sizing`, márgenes, `font-family: var(--font-base)`).

**Fase 3 — Layout y navegación (0.5 día)**
Estilizar `.navbar` y `.container` en el `layout()` compartido. Verificar que se vea igual en ambas rutas (`/` y `/como-funciona`).

**Fase 4 — Formulario (Pantalla 1) (1 día)**
Estilizar `.form-card`, `.form-field` y `.btn-primary` según la tabla de la sección 4.

**Fase 5 — Panel de resultado (1 día)**
Estilizar `.result-card`, `.result-number`, `.badge-nivel` (con sus 3 variantes) y `.aviso-responsable`. Probar los 3 niveles con datos de prueba.

**Fase 6 — Pantalla "Cómo funciona" (0.5 día)**
Estilizar `.content-article` para buena legibilidad de texto largo.

**Fase 7 — Responsive y accesibilidad (0.5 día)**
Aplicar la media query de la sección 6, revisar contraste y estados de foco.

**Fase 8 — QA visual comparativo (0.5 día)**
Comparar lado a lado (captura de pantalla) la app FastHTML contra el prototipo Lovable en desktop y mobile; ajustar diferencias finas de espaciado/color.

**Estimado total: ~4-5 días** de trabajo de una persona con conocimientos de CSS, sin contar la lógica de predicción (ya cubierta en otros documentos).

---

## 9. Checklist final antes de dar por cerrado el diseño

- [ ] Colores confirmados contra el sitio real (no solo estimados)
- [ ] Los 4 selectores del formulario se ven y funcionan igual en desktop y mobile
- [ ] El badge de nivel cambia correctamente de color según Bajo/Medio/Alto
- [ ] El aviso de uso responsable es visualmente distinto y siempre visible junto al resultado
- [ ] Contraste de texto verificado (AA mínimo)
- [ ] Navegación entre "Consultar" y "Cómo funciona" mantiene el mismo estilo de header
- [ ] Comparación visual final contra el prototipo Lovable aprobada
