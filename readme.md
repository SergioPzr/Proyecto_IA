# Sistema de Pronóstico de Violencia Familiar

Estimador de frecuencia de denuncias de violencia familiar en el Perú por departamento, día de la semana, franja horaria y mes. Este sistema está construido sobre un modelo de aprendizaje automático LightGBM (`LGBMRegressor`) y expuesto a través de una interfaz web rápida, elegante e interactiva con **FastHTML**.

## Propósito del Proyecto
Apoyar al personal de planificación operativa policial (patrullaje preventivo) y a analistas de seguridad pública en la estimación del volumen de denuncias de violencia familiar que podrían registrarse bajo ciertas condiciones de tiempo y espacio. Su objetivo es facilitar la asignación eficiente de recursos en las zonas y horarios prioritarios.

## Instrucciones para Ejecución Local

### 1. Clonar el repositorio y acceder a la carpeta
```bash
git clone <url-del-repositorio>
cd Proyecto_IA
```

### 2. Crear y activar el entorno virtual
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

### 3. Instalar las dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
python main.py
```

La aplicación se iniciará y estará disponible en:
**http://localhost:5000**
