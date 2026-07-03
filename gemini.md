# Plan de Implementación — Interfaz Web (FastHTML)
## Sistema de Pronóstico de Frecuencia de Denuncias de Violencia Familiar

> Este documento condensa y actualiza los documentos 00, 01, 03 y 04 del proyecto en un solo plan de implementación, ajustado a la estructura de **3 pantallas** y al estado actual: el notebook, el modelo ganador (LightGBM o LinearSVR) y sus archivos de exportación **ya están listos**.

---

## 1. Estado actual del proyecto (punto de partida)

- El notebook `Proyecto_IA_2_.ipynb` ya entrenó y comparó **LightGBM (`LGBMRegressor`)** vs. **LinearSVR** sobre el dataset agregado (Departamento × Día de la semana × Franja horaria × Mes, 8,400 filas).
- Ya se seleccionó el modelo ganador según **mejor R²** sobre el test temporal (últimos 3 meses de 2019).
- Ya se exportaron los artefactos del modelo (metadata en JSON + modelo entrenado). **Tarea pendiente antes de programar:** confirmar en qué formato quedó el modelo ganador (`.joblib` es lo definido en el plan original; si en la práctica se exportó como `.json` — p. ej. `Booster.save_model()` en el caso de LightGBM — ajustar la carga en `prediccion.py` en consecuencia). El `metadata_conteo.json` (o su equivalente) contiene como mínimo:
  - `modelo_seleccionado`: `"LightGBM"` o `"LinearSVR"`
  - `requiere_escalado`: `true`/`false`
  - `columnas_escalado`: `["DIA_SEMANA", "MES_NUM"]`
  - `columnas_entrada`: lista ordenada y exacta de columnas que espera el modelo (incluye los departamentos y franjas horarias como columnas booleanas de `get_dummies`)
- **Pendiente de agregar/verificar en el notebook:** los percentiles 33 y 66 de la columna `CASOS`, necesarios para calcular el nivel de frecuencia (Bajo/Medio/Alto). Si no están exportados, agregar una celda con `violencia['CASOS'].quantile([0.33, 0.66])` y volver a exportar la metadata.
- No se combinan modelos: solo el ganador se conecta a la web. El descartado queda solo como evidencia en el notebook.

---

## 2. Decisiones de fondo (heredadas, sin cambios)

| Decisión | Elección |
|---|---|
| Variable objetivo | `CASOS`: número de denuncias por Departamento × Día × Franja horaria × Mes |
| Granularidad geográfica | **Departamento** (25 zonas), no comisaría ni distrito — el formulario debe decir "Departamento", no "Comisaría" |
| Modelos comparados | LightGBM (`LGBMRegressor`) vs. LinearSVR — se queda el de mejor R² |
| Métricas | R² (criterio de selección) y MAE (más fácil de comunicar) |
| Interacción usuario-modelo | Formulario estructurado con selectores (sin texto libre) |
| Stack web | **FastHTML** (Python puro; un solo proceso sirve HTML + ejecuta el modelo, sin API JSON separada) |
| Despliegue | **GitHub Pages NO sirve** (solo archivos estáticos; FastHTML necesita un proceso servidor). Usar Render, Railway, Fly.io o PythonAnywhere. Código fuente en GitHub; app en vivo en el servicio elegido. |

---

## 3. Cambio respecto al plan original: ahora son 3 pantallas

El plan anterior definía 2 pantallas (Presentación+Consulta / Explicación). **Se actualiza a 3 pantallas independientes**, para simplificar aún más la experiencia:

| # | Pantalla | Contenido |
|---|---|---|
| 1 | **Inicio / Presentación** | Qué es el sistema, a quién beneficia, público objetivo, una imagen simple. Sin formularios. |
| 2 | **Consultar** | Formulario (Departamento, Día de la semana, Franja horaria, Mes) + panel de resultado de la predicción |
| 3 | **Cómo funciona** | Explicación sencilla de LightGBM y LinearSVR, y limitaciones del modelo |

Navegación fija de 3 elementos siempre visibles (ej. header): **Inicio | Consultar | Cómo funciona**.

---

### Pantalla 1 — Inicio / Presentación

Contenido sugerido (solo lectura, sin interacción):

- **Título y una línea de propósito:** "Estimador de frecuencia de denuncias de violencia familiar por zona y horario."
- **¿A quién beneficia?** Personal de planificación operativa policial (patrullaje preventivo), que necesita saber dónde y cuándo priorizar recursos.
- **¿Para quién es esta herramienta?** No técnico: solo requiere elegir opciones de un formulario, no interpretar código ni estadística avanzada.
- **Una imagen simple** de apoyo (ilustración o ícono relacionado a mapas/seguridad/planificación — no depende del modelo, es decorativa).
- **Botón/enlace destacado** hacia la pantalla "Consultar".
- Puede incluir 2-3 líneas de aviso de uso responsable (el pronóstico apoya la planificación, no reemplaza el criterio profesional ni predice hechos individuales) — este aviso también debe repetirse en la Pantalla 2, junto al resultado.

Ruta sugerida: `@rt("/")`.

---

### Pantalla 2 — Consultar (formulario + predicción)

**Formulario**, un campo por variable:

| Campo | Control | Corresponde a | Valores |
|---|---|---|---|
| Departamento | Selector desplegable (25 opciones, ver nota) | `DPTO_HECHO` | Tomar literalmente de `columnas_entrada`, filtrando `DIA_SEMANA`, `MES_NUM` y las 4 franjas; el resto son departamentos. El departamento base de `get_dummies(drop_first=True)` no aparece como columna pero sigue siendo opción válida (todas las columnas de depto en 0). |
| Día de la semana | Selector: Lunes ... Domingo | `DIA_SEMANA` | 0 (lunes) a 6 (domingo) |
| Franja horaria | Selector: Madrugada / Mañana / Tarde / Noche | `HORA_BANDA` | `"MADRUGADA"`, `"MANANA"`, `"TARDE"`, `"NOCHE"` |
| Mes | Selector: Enero ... Diciembre | `MES_NUM` | 1 a 12 |

**Botón principal:** "Consultar Frecuencia Esperada" — grande, visible, única acción de la pantalla.

**Panel de resultado** (aparece tras enviar el formulario):
- Número esperado de denuncias, en texto grande (ej. "≈ 42 denuncias esperadas").
- Nivel de frecuencia (Bajo/Medio/Alto) por percentiles históricos de `CASOS`.
- Código de color de apoyo (ej. azul/amarillo/rojo) — propuesta visual, no escala oficial.
- Aviso de uso responsable, siempre visible junto al resultado.

**Flujo:**
```
Usuario completa el formulario
        │
        ▼
Presiona "Consultar Frecuencia Esperada"
        │
        ▼
POST → función predecir_casos() (ver sección 4)
        │
        ▼
Se muestra: número esperado + nivel + color
```

Ruta sugerida: `@rt("/consultar")` (GET, muestra el form) y `@rt("/predecir")` (POST, procesa y devuelve el fragmento de resultado vía HTMX, sin recargar la página).

---

### Pantalla 3 — Cómo funciona (explicación simple)

Contenido de solo lectura, en lenguaje simple, sin formularios:

1. **Qué hace el modelo:** estima cuántas denuncias son esperables en un departamento y horario dados, aprendiendo de patrones históricos de 2019.
2. **Qué información utiliza:** las 4 variables del formulario y por qué importan.
3. **Cómo interpretar el resultado:** qué es el número de casos esperado y qué significa cada nivel (Bajo/Medio/Alto).
4. **Cómo se construyó el modelo — LightGBM vs. LinearSVR, en simple:**
   - *LightGBM:* "muchos árboles de decisión pequeños que se van corrigiendo entre sí"; suma las contribuciones de todos los árboles para llegar al número final. Bueno para capturar combinaciones no obvias (ej. cierto departamento con picos los fines de semana en la noche).
   - *LinearSVR:* "la mejor línea recta que se ajusta al número de casos"; combina las variables con pesos ajustados durante el entrenamiento, tolerando un pequeño margen de error sin penalizar. Funciona bien porque departamento y franja horaria ya vienen en formato 0/1.
   - Ambos se entrenaron y evaluaron por separado sobre los mismos meses de prueba (nunca vistos en entrenamiento); **se conserva solo el de mejor R²** — no hay combinación de modelos.
5. **Limitaciones**, en lenguaje simple:
   - Aprende de un solo año de datos (2019); no captura tendencias multianuales ni eventos atípicos.
   - Pronostica denuncias *registradas*, no incidentes reales (que pueden estar subreportados).
   - Granularidad a nivel Departamento, no distrito ni comisaría.
   - Es apoyo a la planificación, no reemplaza el criterio de un planificador ni predice hechos individuales.

Ruta sugerida: `@rt("/como-funciona")`.

---

## 4. Integración del modelo con la app (Backend FastHTML)

Con FastHTML **no hace falta una API separada**: el mismo proceso Python sirve el HTML y ejecuta el modelo.

### Al iniciar la app (una sola vez, no por solicitud)
1. Cargar el modelo ganador (ajustar según formato real de exportación: `joblib.load(...)` o carga específica si quedó en `.json`, p. ej. `Booster().load_model(...)` según el framework).
2. Cargar `metadata_conteo.json` (o equivalente).
3. Cargar el `scaler` **solo si** `metadata["requiere_escalado"]` es `true` (solo aplica si ganó LinearSVR).
4. Si los percentiles 33/66 no están en la metadata, cargarlos desde donde se hayan exportado (ver sección 1).

### Función `predecir_casos(departamento, dia_semana, franja_horaria, mes)`
1. Construye una fila con todas las columnas de `columnas_entrada` inicializadas en 0.
2. Asigna `DIA_SEMANA` y `MES_NUM`.
3. Pone en 1 la columna del departamento recibido, si existe (si no existe, es el departamento base — se deja todo en 0 en las columnas de depto).
4. Pone en 1 la columna de la franja horaria recibida, si existe.
5. Si `requiere_escalado` es `true`, aplica `scaler.transform(...)` sobre `columnas_escalado`.
6. Llama a `modelo.predict(entrada)`, redondea a entero (no hay denuncias fraccionarias).
7. Clasifica el nivel de frecuencia contra los percentiles 33/66:
   - `≤ percentil_33` → `"BAJO"`
   - `percentil_33 < x ≤ percentil_66` → `"MEDIO"`
   - `> percentil_66` → `"ALTO"`
8. Devuelve `{"casos_esperados": ..., "nivel_frecuencia": ...}`.

### Contrato de datos interno

**Entrada:**

| Parámetro | Tipo | Valores válidos |
|---|---|---|
| `departamento` | `str` | Uno de los 25 departamentos, en mayúsculas (ej. `"LIMA"`) |
| `dia_semana` | `int` | 0 (lunes) a 6 (domingo) |
| `franja_horaria` | `str` | `"MADRUGADA"`, `"MANANA"`, `"TARDE"`, `"NOCHE"` |
| `mes` | `int` | 1 a 12 |

**Salida:**
```json
{
  "casos_esperados": 42,
  "nivel_frecuencia": "ALTO"
}
```

### Manejo de errores
- Campos vacíos: validar que los 4 parámetros lleguen con valor; mensaje claro si falta alguno.
- Departamento no reconocido (no está en `columnas_entrada` ni es el departamento base): tratar como error de validación, no fallar silenciosamente.
- Modelo no cargado al iniciar: la app debe fallar de forma visible en logs, no quedar "viva" sin poder predecir.

---

## 5. Estructura de carpetas del proyecto

Adaptada del plan original (documento 04) e inspirada en la organización usada por un compañero en un proyecto similar (con un modelo distinto):

```
proyecto-pronostico-denuncias/
├── notebook/
│   └── Proyecto_IA_2_.ipynb
├── models/
│   ├── modelo_conteo_final.joblib      # o .json/.txt según formato real de exportación
│   ├── scaler_conteo.joblib            # solo si ganó LinearSVR
│   └── metadata_conteo.json            # columnas_entrada, requiere_escalado, percentiles, etc.
├── static/
│   └── img/                            # imagen simple de la Pantalla 1
├── prediction.py                       # función predecir_casos()
├── main.py                             # app FastHTML: rutas, formulario, layout, 3 pantallas
├── requirements.txt
├── Procfile                            # o equivalente, según servicio de despliegue
├── .gitignore
├── .env                                # variables de entorno si aplica (no versionar)
└── README.md
```

`requirements.txt` mínimo:
```
python-fasthtml
scikit-learn
lightgbm
joblib
pandas
numpy
```

> Nota: a diferencia del ejemplo del compañero (que separa `models/` y usa `prediction.py` en la raíz junto a `main.py`), aquí se mantiene esa misma organización plana por simplicidad, ya que el proyecto es pequeño (3 pantallas, sin autenticación ni historial).

---

## 6. Despliegue

- **GitHub Pages no es compatible** con FastHTML: solo sirve archivos estáticos, y FastHTML necesita un proceso Python corriendo continuamente (ASGI/Uvicorn) para procesar el formulario en cada solicitud.
- **Código fuente:** repositorio GitHub normal (notebook, `models/`, `main.py`, etc.).
- **App en ejecución (URL pública):** desplegar en un servicio que ejecute procesos Python:

| Servicio | Ventaja | A verificar antes de usar |
|---|---|---|
| Render | Plan gratuito para "Web Services"; despliega desde GitHub automáticamente | Límites vigentes del plan gratuito (puede dormir tras inactividad) |
| Railway | Detecta apps Python, despliega desde GitHub | Créditos/límites gratuitos vigentes |
| Fly.io | Contenedores pequeños, plan gratuito limitado | Requiere `Dockerfile` o `fly.toml` |
| PythonAnywhere | Pensado para apps Python | Confirmar soporte ASGI (FastHTML) en el plan gratuito, no solo WSGI |

- Opcionalmente, GitHub Pages puede alojar una landing **estática** que enlace a la app real (no reemplaza el despliegue funcional).

---

## 7. Checklist de implementación

- [ ] Confirmar formato final del modelo exportado (`.joblib` vs `.json`) y ajustar la carga en `prediction.py`.
- [ ] Confirmar que `metadata_conteo.json` incluye `columnas_entrada`, `requiere_escalado`, `columnas_escalado`, y los percentiles 33/66 de `CASOS` (agregar al notebook si faltan).
- [ ] Implementar `prediction.py` con `predecir_casos()`.
- [ ] Implementar `main.py` con las 3 rutas: `/` (Inicio), `/consultar` + `/predecir` (formulario y resultado), `/como-funciona`.
- [ ] Cargar el modelo una sola vez al iniciar la app, no en cada solicitud.
- [ ] Probar casos límite: departamento base de `get_dummies`, cada franja horaria, meses/días extremos.
- [ ] Elegir servicio de despliegue (no GitHub Pages) y publicar la URL.
- [ ] Código fuente completo en GitHub.
- [ ] Probar el flujo completo (Inicio → Consultar → resultado → Cómo funciona) sobre la URL pública.
