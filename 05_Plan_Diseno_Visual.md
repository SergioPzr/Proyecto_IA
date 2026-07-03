# Plan de Implementación de Diseño Visual — Estimador de Frecuencia de Denuncias (v2)

## Propósito de este documento

Este documento **complementa** a `03_Plan_Pagina_Web.md` (estructura, dos pantallas, esqueleto FastHTML) y especifica la estética visual completa: paleta, tipografía, sistema de espaciado, iconografía, componentes y el CSS listo para integrar. Reemplaza la v1 de este mismo documento con un sistema más elaborado — mismos principios, ejecución más cuidada. No cambia estructura, campos ni rutas del documento 03.

---

## Fundamento de la dirección de diseño

**Audiencia:** oficial que atiende una denuncia puntual, y personal de planificación operativa — personas dentro de una institución policial, a menudo bajo presión de tiempo, que leen esto como leen un parte o una constancia, no como una app de consumo.

Un diseño "profesional" para esta audiencia no es una superficie con más adornos — es una pieza que se comporta como un documento institucional bien producido: jerarquía precisa, alineación exacta, un sistema de espaciado consistente, y un solo gesto de autoría (el panel de resultado) en vez de varios elementos compitiendo por atención. La v1 resolvía la estructura correctamente pero se quedaba en "tarjeta blanca con borde"; esta versión añade lo que distingue a una pieza bien producida de una plantilla: una cabecera con identidad propia, iconografía de línea propia (no genérica), un indicador de posición dentro del rango histórico (no solo una etiqueta de color), y un sistema tipográfico con más carácter y más disciplina a la vez.

---

## Sistema de tokens

### Color

| Token | Valor | Uso |
|---|---|---|
| `--color-bg` | `#EEF0EA` | Fondo general — papel institucional con matiz verde-gris frío |
| `--color-surface` | `#FCFCFA` | Fondo de tarjetas |
| `--color-surface-raised` | `#FFFFFF` | Panel de resultado (la superficie más alta de la jerarquía) |
| `--color-primary` | `#173B2C` | Verde institucional — cabecera, nav, botón principal |
| `--color-primary-dark` | `#0E271D` | Hover/activo del botón principal |
| `--color-primary-soft` | `#E4EAE4` | Fondos suaves sobre superficies claras (chips, hover de nav) |
| `--color-accent-line` | `#B08D3E` | Dorado apagado — línea de acento institucional, uso mínimo y deliberado |
| `--color-ink` | `#1E2422` | Texto principal |
| `--color-muted` | `#5F6B64` | Texto secundario, etiquetas |
| `--color-faint` | `#8B968F` | Texto terciario, metadatos de pie de página |
| `--color-border` | `#CBD2C7` | Bordes de inputs y tarjetas |
| `--color-border-strong` | `#A9B3A4` | Bordes con más peso (separadores de sección) |
| `--color-alert-bajo` | `#2D6A4F` | Nivel Bajo |
| `--color-alert-bajo-bg` | `#E4EFE8` | Fondo del badge/gauge Bajo |
| `--color-alert-medio` | `#96690A` | Nivel Medio |
| `--color-alert-medio-bg` | `#F2E9D8` | Fondo del badge/gauge Medio |
| `--color-alert-alto` | `#8F2226` | Nivel Alto |
| `--color-alert-alto-bg` | `#F3E3E3` | Fondo del badge/gauge Alto |

**Por qué este ajuste sobre la v1:** se añade `--color-accent-line` (dorado apagado, tipo insignia) como segundo acento institucional, de uso muy restringido — una sola línea de 2px bajo el logotipo/monograma de cabecera y nada más. Es el tipo de detalle que separa un sistema con dirección de arte de uno que solo tiene "un color primario y ya". El verde se oscurece ligeramente (`#173B2C` vs `#1B4332` de la v1) para dar más peso y contraste con el dorado.

### Tipografía

| Rol | Fuente | Peso | Uso |
|---|---|---|---|
| Display | `Spectral` | 600 / 700 | Título de página, títulos de sección — tiene el carácter de un documento oficial impreso, más distintivo que una serif genérica |
| Interfaz / cuerpo | `Inter` | 400 / 500 / 600 | Navegación, etiquetas, párrafos, botones — extremadamente legible a tamaños pequeños, estándar de facto en productos institucionales serios |
| Datos | `IBM Plex Mono` | 500 / 600 | El número de denuncias esperadas, el badge de nivel, metadatos de pie de página — cifras tabulares, look de "lectura de reporte" |

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
```

**Escala tipográfica** (rem, base 16px):

| Token | Tamaño | Uso |
|---|---|---|
| `--text-xs` | 0.6875rem (11px) | Metadatos, pie de página, etiquetas de campo |
| `--text-sm` | 0.8125rem (13px) | Cuerpo de interfaz, opciones de formulario |
| `--text-base` | 0.9375rem (15px) | Cuerpo de lectura (Pantalla 2) |
| `--text-lg` | 1.125rem (18px) | Títulos de sección |
| `--text-xl` | 1.5rem (24px) | Título de página |
| `--text-display` | 2.125rem (34px) | Número de resultado |

### Espaciado (escala de 8px)

`--space-1: 4px` · `--space-2: 8px` · `--space-3: 12px` · `--space-4: 16px` · `--space-5: 24px` · `--space-6: 32px` · `--space-7: 48px`

Usar exclusivamente estos valores para padding y márgenes mantiene el ritmo vertical consistente entre pantallas — otro detalle que distingue un sistema de una serie de estilos improvisados por componente.

### Radio y elevación

- `--radius-control: 4px` (inputs, botones)
- `--radius-card: 10px` (tarjetas, panel de resultado)
- Elevación: **sin sombras decorativas.** Un único `box-shadow: 0 1px 2px rgba(23,59,44,0.06)` muy sutil solo en el panel de resultado, para separarlo del fondo sin romper el lenguaje "documento plano". Todo lo demás se separa por borde, no por sombra.

---

## Iconografía

Set propio de 5 iconos de línea (stroke 1.5px, `currentColor`, 18×18), en vez de un set genérico de terceros — coherente con "esta pieza tiene autoría propia":

- **Departamento** — un pin de mapa simplificado a dos trazos (silueta + punto).
- **Día de la semana** — un cuadrado con una línea superior corta (metáfora de casilla de calendario).
- **Franja horaria** — un círculo con una sola manecilla corta (reloj minimalista, sin números).
- **Mes** — el mismo cuadrado de calendario, con dos líneas superiores (encabezado de mes).
- **Aviso** — un triángulo de trazo fino con un punto, para el aviso de uso responsable.

Cada icono se coloca a la izquierda de la etiqueta del campo, 16px, `color: var(--color-muted)`. Ejemplo SVG (Departamento):

```html
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
  <path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/>
  <circle cx="12" cy="9.5" r="2.2"/>
</svg>
```

---

## Pantalla 1 — Consulta (especificación visual)

```
┌ franja superior 4px, degradé sólido verde→dorado apagado (identidad) ┐
├ cabecera verde institucional ─────────────────────────────────────┤
│ ◆ monograma  ESTIMADOR DE DENUNCIAS      consultar · cómo funciona │
├──────────────────────────────────────────────────────────────────┤
│  PLANIFICACIÓN DE PATRULLAJE PREVENTIVO           (eyebrow, dorado) │
│  Estimador de frecuencia de denuncias                              │
│  por zona y horario                    (Spectral 700, 24px, verde)  │
│  texto de apoyo breve, gris                                        │
│                                                                    │
│  ┌ tarjeta formulario ──────────────────────────────────────────┐ │
│  │  📍 Departamento          🗓 Día de la semana                  │ │
│  │  [ selector ]             [ selector ]                        │ │
│  │  🕐 Franja horaria         🗓 Mes                              │ │
│  │  [ selector ]             [ selector ]                        │ │
│  │  [   Consultar frecuencia esperada   ]                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┏━ panel de resultado (sombra sutil, borde izq. de color) ━━━━┓ │
│  ┃  Denuncias esperadas                    [ NIVEL ALTO ]         ┃ │
│  ┃  ≈ 42                          (IBM Plex Mono, 34px)           ┃ │
│  ┃  ─────────────────────────────────────────────────────        ┃ │
│  ┃  bajo ▭▭▭▭▭▭▭▭●▭▭▭ alto     (gauge de posición histórica)      ┃ │
│  ┃  ⚠ Herramienta de apoyo a la planificación de recursos.         ┃ │
│  ┃  No reemplaza el criterio del personal encargado.               ┃ │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                                                    │
│  Fuente: denuncias PNP 2019 · modelo actualizado — v1.0    (pie)   │
└──────────────────────────────────────────────────────────────────┘
```

### Elemento de firma: el gauge de posición histórica

Este es el elemento nuevo que eleva el panel de resultado por encima de "número + badge de color": una barra horizontal delgada (6px de alto) que representa el rango completo de valores históricos de `CASOS`, dividida visualmente en tres tercios de color (bajo/medio/alto, en los mismos tonos apagados de la paleta), con un punto marcador (`●`, 10px, `var(--color-ink)`, borde blanco de 2px) en la posición exacta del valor consultado dentro de ese rango.

Justificación: el documento 03 ya pide mostrar el número exacto además del nivel, "para no perder información útil para el planificador" (ver sección de justificación del documento 03). El gauge hace visible *cuánto* margen hay dentro de la categoría — no es lo mismo un "Alto" en el borde inferior del rango que uno en el extremo superior — sin añadir una sola palabra más de texto. Los percentiles ya se calculan en el documento 04, así que el gauge no requiere ningún dato adicional.

```html
<div class="gauge" role="img" aria-label="Posición dentro del rango histórico de denuncias: nivel alto">
  <div class="gauge-track">
    <span class="gauge-tercio bajo"></span>
    <span class="gauge-tercio medio"></span>
    <span class="gauge-tercio alto"></span>
    <span class="gauge-marcador" style="left: 78%;"></span>
  </div>
  <div class="gauge-etiquetas">
    <span>bajo</span><span>alto</span>
  </div>
</div>
```

### Cabecera con identidad propia

En vez de una barra de navegación plana, la cabecera tiene dos capas:

1. **Franja de identidad** (4px de alto, todo el ancho): un degradé sólido de `--color-primary` a `--color-accent-line` — el único degradé permitido en toda la pieza, reservado exclusivamente para este detalle de marca.
2. **Barra de navegación** (fondo `--color-primary`): a la izquierda, un monograma geométrico simple (un rombo con un trazo diagonal, dibujado en SVG propio — no un escudo ni una insignia real) junto al nombre corto de la herramienta en versalitas; a la derecha, los dos enlaces de navegación ya definidos en el documento 03.

---

## Pantalla 2 — Cómo funciona (especificación visual)

Misma cabecera de dos capas. Contenido en una sola columna, `max-width: 640px`, sin tarjeta contenedora.

- Títulos de sección en `Spectral` 700, 18px, color `--color-primary`, precedidos por un pequeño índice numérico en `IBM Plex Mono` (`01`, `02`, `03`...) en `--color-accent-line` — aquí sí se justifica la numeración porque el documento 03 ya presenta estas cinco secciones como una secuencia de lectura fija (qué hace → qué usa → cómo interpretar → cómo se construyó → limitaciones).
- Cuerpo en `Inter` 400, 15px, `line-height: 1.65`, color `--color-ink`, máximo 68 caracteres por línea para facilitar lectura.
- La sección "Limitaciones" lleva un borde izquierdo de 2px en `--color-muted` (no un color de alerta — es contexto, no una advertencia urgente) y el icono de aviso de línea definido arriba.

---

## CSS listo para integrar

```css
:root {
  --color-bg: #EEF0EA;
  --color-surface: #FCFCFA;
  --color-surface-raised: #FFFFFF;
  --color-primary: #173B2C;
  --color-primary-dark: #0E271D;
  --color-primary-soft: #E4EAE4;
  --color-accent-line: #B08D3E;
  --color-ink: #1E2422;
  --color-muted: #5F6B64;
  --color-faint: #8B968F;
  --color-border: #CBD2C7;
  --color-border-strong: #A9B3A4;
  --color-alert-bajo: #2D6A4F;
  --color-alert-bajo-bg: #E4EFE8;
  --color-alert-medio: #96690A;
  --color-alert-medio-bg: #F2E9D8;
  --color-alert-alto: #8F2226;
  --color-alert-alto-bg: #F3E3E3;

  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-5: 24px; --space-6: 32px; --space-7: 48px;

  --radius-control: 4px;
  --radius-card: 10px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--color-bg);
  color: var(--color-ink);
  font-family: 'Inter', system-ui, sans-serif;
}

.franja-identidad {
  height: 4px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent-line));
}

nav {
  background: var(--color-primary);
  padding: var(--space-3) var(--space-5);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.nav-marca { display: flex; align-items: center; gap: var(--space-2); }
.nav-marca span {
  color: #EEF0EA;
  font-family: 'Inter', sans-serif;
  font-size: var(--text-xs, 11px);
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
nav .enlaces { display: flex; gap: var(--space-5); }
nav a { color: #D6DED6; font-size: 13px; font-weight: 500; text-decoration: none; }
nav a.activo { color: #EEF0EA; border-bottom: 2px solid var(--color-accent-line); padding-bottom: 2px; }

main { max-width: 680px; margin: 0 auto; padding: var(--space-6) var(--space-5) var(--space-7); }

.eyebrow {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-accent-line);
  margin: 0 0 var(--space-2);
}

h1, h2 { font-family: 'Spectral', serif; color: var(--color-primary); margin: 0 0 var(--space-2); }
h1 { font-weight: 700; font-size: 24px; line-height: 1.25; }
h2 { font-weight: 700; font-size: 18px; margin-top: var(--space-6); }
h2 .indice { font-family: 'IBM Plex Mono', monospace; color: var(--color-accent-line); font-weight: 600; margin-right: var(--space-2); }

.subtitulo { font-size: 13px; color: var(--color-muted); margin: 0 0 var(--space-5); max-width: 46ch; }

.tarjeta-formulario {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  padding: var(--space-5);
}

.grilla-campos { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
@media (max-width: 640px) { .grilla-campos { grid-template-columns: 1fr; } }

.campo label {
  display: flex; align-items: center; gap: var(--space-1);
  font-size: 11px; color: var(--color-muted); margin-bottom: var(--space-2);
}
.campo select {
  width: 100%; height: 36px;
  border: 1px solid var(--color-border); border-radius: var(--radius-control);
  background: #fff; color: var(--color-ink); font-size: 13px; padding: 0 var(--space-3);
}
.campo select:focus { outline: none; box-shadow: 0 0 0 2px var(--color-primary); }

button[type="submit"] {
  margin-top: var(--space-4); width: 100%; height: 40px;
  background: var(--color-primary); color: #EEF0EA; border: none;
  border-radius: var(--radius-control); font-size: 13px; font-weight: 600;
  font-family: 'Inter', sans-serif; cursor: pointer;
}
button[type="submit"]:hover { background: var(--color-primary-dark); }
button[type="submit"]:focus-visible { outline: 3px solid var(--color-primary-dark); outline-offset: 2px; }

.panel-resultado {
  margin-top: var(--space-5);
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--nivel-color, var(--color-alert-medio));
  border-radius: 0 var(--radius-card) var(--radius-card) 0;
  padding: var(--space-4) var(--space-5);
  box-shadow: 0 1px 2px rgba(23,59,44,0.06);
}
.fila-resultado { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: var(--space-3); }
.etiqueta { font-size: 11px; color: var(--color-muted); margin: 0 0 var(--space-1); }
.valor { font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 34px; margin: 0; }
.badge-nivel {
  font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase; border-radius: 2px;
  padding: var(--space-1) var(--space-3);
  color: var(--nivel-color, var(--color-alert-medio));
  background: var(--nivel-bg, var(--color-alert-medio-bg));
  border: 1px solid var(--nivel-color, var(--color-alert-medio));
}

.gauge { margin: var(--space-4) 0 var(--space-3); }
.gauge-track { position: relative; height: 6px; border-radius: 3px; display: flex; overflow: visible; }
.gauge-tercio { flex: 1; height: 100%; }
.gauge-tercio.bajo { background: var(--color-alert-bajo-bg); border-radius: 3px 0 0 3px; }
.gauge-tercio.medio { background: var(--color-alert-medio-bg); }
.gauge-tercio.alto { background: var(--color-alert-alto-bg); border-radius: 0 3px 3px 0; }
.gauge-marcador {
  position: absolute; top: 50%; width: 10px; height: 10px; border-radius: 50%;
  background: var(--color-ink); border: 2px solid #fff;
  transform: translate(-50%, -50%);
}
.gauge-etiquetas { display: flex; justify-content: space-between; margin-top: var(--space-1); font-size: 10px; color: var(--color-faint); text-transform: uppercase; letter-spacing: 0.04em; }

.aviso-responsable {
  display: flex; gap: var(--space-2); align-items: flex-start;
  font-size: 11px; color: var(--color-muted); font-style: italic;
  margin: var(--space-4) 0 0; border-top: 1px solid var(--color-border); padding-top: var(--space-3);
}

.pie-pagina {
  margin-top: var(--space-4);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px; color: var(--color-faint); letter-spacing: 0.02em;
}
```

### Mapeo de nivel a color y posición del gauge (lógica de la ruta `/predecir`)

```python
COLORES_NIVEL = {
    "bajo":  ("var(--color-alert-bajo)",  "var(--color-alert-bajo-bg)"),
    "medio": ("var(--color-alert-medio)", "var(--color-alert-medio-bg)"),
    "alto":  ("var(--color-alert-alto)",  "var(--color-alert-alto-bg)"),
}
color, fondo = COLORES_NIVEL[resultado["nivel_frecuencia"].lower()]

# posicion_pct: 0-100, calculado en documento 04 a partir del percentil
# del valor consultado sobre la columna CASOS del dataset agregado.
posicion_pct = resultado["posicion_percentil"]

return Div(
    Div(
        Div(P("Denuncias esperadas", cls="etiqueta"),
            P(f"≈ {resultado['casos_esperados']}", cls="valor")),
        Span(f"NIVEL {resultado['nivel_frecuencia'].upper()}", cls="badge-nivel",
             style=f"--nivel-color:{color};--nivel-bg:{fondo}"),
        cls="fila-resultado",
    ),
    Div(
        Div(
            Span(cls="gauge-tercio bajo"), Span(cls="gauge-tercio medio"), Span(cls="gauge-tercio alto"),
            Span(cls="gauge-marcador", style=f"left:{posicion_pct}%;"),
            cls="gauge-track", role="img",
            aria_label=f"Posición dentro del rango histórico: nivel {resultado['nivel_frecuencia']}",
        ),
        Div(Span("bajo"), Span("alto"), cls="gauge-etiquetas"),
        cls="gauge",
    ),
    P("Herramienta de apoyo a la planificación de recursos. "
      "No reemplaza el criterio del personal encargado ni predice hechos individuales.",
      cls="aviso-responsable"),
    cls="panel-resultado",
    style=f"--nivel-color:{color}",
)
```

**Nota:** si el documento 04 aún no expone `posicion_percentil` como parte del resultado, es un cálculo trivial adicional sobre la misma tabla de percentiles ya usada para determinar Bajo/Medio/Alto (percentil del valor actual respecto a la distribución de `CASOS`) — no requiere reentrenar ni cambiar el modelo.

---

## Accesibilidad

- Contraste `--color-primary` sobre `--color-bg` y sobre blanco: AA holgado en texto normal y grande.
- Foco visible en todos los controles interactivos (`box-shadow` / `outline`), nunca solo cambio de color.
- El nivel de frecuencia nunca depende solo del color: badge con texto explícito + gauge con etiquetas "bajo"/"alto" en texto, para daltonismo e impresión en blanco y negro.
- El gauge lleva `role="img"` y `aria-label` describiendo la posición en palabras, para lectores de pantalla.
- Texto mínimo 10px reservado solo al pie de página técnico; todo el contenido operativo en 13px+.
- Grilla del formulario colapsa a una columna por debajo de 640px; el número de resultado no se recorta en pantallas angostas.
- `prefers-reduced-motion`: si se añade cualquier transición (por ejemplo, aparición del panel de resultado), debe respetar `@media (prefers-reduced-motion: reduce) { transition: none; }`.

---

## Qué no cambia respecto al documento 03

- Estructura de dos pantallas, rutas `@rt("/")` y `@rt("/como-funciona")`, uso de HTMX (`hx_post`, `hx_target`).
- Los cuatro campos del formulario y sus valores (Departamento, Día de la semana, Franja horaria, Mes).
- El aviso de uso responsable, siempre visible.

Este documento añade la capa visual completa (tokens, tipografía, iconografía, gauge de posición histórica, CSS) sobre esa estructura ya definida — sin tocar lógica, rutas ni campos.
