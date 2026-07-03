# PREVI-FAM — Sistema de Pronóstico de Violencia Familiar

Estimador de frecuencia de denuncias de violencia familiar en el Perú por departamento, día de la semana, franja horaria y mes. Este sistema está construido sobre un modelo de aprendizaje automático LightGBM (`LGBMRegressor`) y expuesto a través de una interfaz web rápida, elegante e interactiva con **FastHTML**.

## Propósito del Proyecto
Apoyar al personal de planificación operativa policial (patrullaje preventivo) y a analistas de seguridad pública en la estimación del volumen de denuncias de violencia familiar que podrían registrarse bajo ciertas condiciones de tiempo y espacio. Su objetivo es facilitar la asignación eficiente de recursos en las zonas y horarios prioritarios.

---

## Estructura de Pantallas de la Aplicación

El sistema consta de 3 pantallas accesibles mediante un menú de navegación persistente:

1. **Inicio / Presentación (`/`)**: Introducción al sistema, explicación de beneficiarios y destinatarios (personal no técnico), y acceso directo a la consulta.
2. **Consultar (`/consultar`)**: Formulario para seleccionar departamento, día de la semana, franja horaria y mes, que al enviarse muestra en tiempo real la predicción estimada de casos junto a su nivel de prioridad (Bajo/Medio/Alto) con códigos de color.
3. **Cómo funciona (`/como-funciona`)**: Explicación metodológica simple de los modelos evaluados (LightGBM vs LinearSVR), los datos que se procesan y las limitaciones del sistema.

---

## Estructura de Carpetas

```
proyecto-pronostico-denuncias/
├── models/
│   ├── modelo_conteo_final.joblib      # Modelo LightGBM entrenado
│   └── metadata_conteo.json            # Columnas del modelo, percentiles y configuración
├── static/
│   ├── css/
│   │   └── style.css                   # Diseño CSS premium oscuro
│   └── img/
│       └── presentacion.png            # Imagen decorativa de la pantalla de inicio
├── prediction.py                       # Módulo de predicción y clasificación por percentiles
├── main.py                             # Aplicación principal FastHTML (rutas y renderizado)
├── requirements.txt                    # Dependencias de Python
├── Procfile                            # Comando para despliegue en servicios cloud
├── .gitignore                          # Archivo de exclusión de Git
└── README.md                           # Documentación general (este archivo)
```

---

## Instrucciones para Ejecución Local

Siga los siguientes pasos para ejecutar la aplicación en su máquina local:

### 1. Prerrequisitos
- Python instalado (se recomienda Python 3.10 o superior).

### 2. Clonar el repositorio y acceder a la carpeta
```bash
git clone <url-del-repositorio>
cd Proyecto_IA
```

### 3. Crear y activar el entorno virtual
En Windows (PowerShell):
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar las dependencias
```bash
pip install -r requirements.txt
```

### 5. Ejecutar la aplicación
```bash
python main.py
```

La aplicación se iniciará y estará disponible en su navegador en:
**http://localhost:5000**

---

## Notas de Desarrollo y Limitaciones

- **Modelo Seleccionado**: Se utiliza `LightGBM` tras compararlo con `LinearSVR` y obtener un mejor coeficiente de determinación ($R^2$) sobre el set de testeo temporal (últimos 3 meses de 2019).
- **Categorización de Prioridad**: El nivel de prioridad se determina evaluando la predicción contra los percentiles históricos 33 y 66 del total de combinaciones del conjunto de datos:
  - **Bajo**: $\le 12$ denuncias esperadas.
  - **Medio**: $> 12$ y $\le 28$ denuncias esperadas.
  - **Alto**: $> 28$ denuncias esperadas.
- **Datos Históricos**: El modelo aprende de registros oficiales del año 2019, por lo que no captura variaciones de años posteriores.
- **Uso Responsable**: Es una herramienta informativa de apoyo y planificación general. No predice incidentes delictivos individuales.
