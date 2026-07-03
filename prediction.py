import os
import json
import joblib
import pandas as pd
import numpy as np

# Define paths relative to the script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_PATH = os.path.join(BASE_DIR, 'models', 'metadata_conteo.json')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'modelo_conteo_final.joblib')

# Load metadata once on startup
if not os.path.exists(METADATA_PATH):
    raise FileNotFoundError(f"No se encontró el archivo de metadata en {METADATA_PATH}")

with open(METADATA_PATH, 'r') as f:
    metadata = json.load(f)

# Load model once on startup
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el modelo entrenado en {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

# Retrieve features list and percentiles
columnas_entrada = metadata.get('columnas_entrada', [])
percentil_33 = metadata.get('percentil_33')
percentil_66 = metadata.get('percentil_66')

# Valid categories for validation
DEPARTAMENTOS_VALIDOS = [
    "AMAZONAS", "ANCASH", "APURIMAC", "AREQUIPA", "AYACUCHO", "CAJAMARCA", 
    "CALLAO", "CUSCO", "HUANCAVELICA", "HUANUCO", "ICA", "JUNIN", 
    "LA LIBERTAD", "LAMBAYEQUE", "LIMA", "LORETO", "MADRE DE DIOS", 
    "MOQUEGUA", "PASCO", "PIURA", "PUNO", "SAN MARTIN", "TACNA", 
    "TUMBES", "UCAYALI"
]

FRANJAS_VALIDAS = ["MADRUGADA", "MANANA", "TARDE", "NOCHE"]

def predecir_casos(departamento: str, dia_semana: int, franja_horaria: str, mes: int):
    """
    Realiza la predicción del número de denuncias y clasifica la frecuencia.
    
    Parámetros:
    - departamento: Nombre del departamento en mayúsculas (ej: 'LIMA')
    - dia_semana: Entero de 0 (Lunes) a 6 (Domingo)
    - franja_horaria: Una de 'MADRUGADA', 'MANANA', 'TARDE', 'NOCHE'
    - mes: Entero de 1 a 12
    
    Retorna:
    - Un diccionario con 'casos_esperados' y 'nivel_frecuencia'
    """
    # 1. Validaciones
    departamento_upper = departamento.strip().upper()
    franja_upper = franja_horaria.strip().upper()
    
    if departamento_upper not in DEPARTAMENTOS_VALIDOS:
        raise ValueError(f"Departamento no reconocido: '{departamento}'. Debe ser uno de {DEPARTAMENTOS_VALIDOS}")
        
    if franja_upper not in FRANJAS_VALIDAS:
        raise ValueError(f"Franja horaria no reconocida: '{franja_horaria}'. Debe ser una de {FRANJAS_VALIDAS}")
        
    if not (0 <= dia_semana <= 6):
        raise ValueError(f"Día de la semana no válido: {dia_semana}. Debe estar entre 0 (Lunes) y 6 (Domingo)")
        
    if not (1 <= mes <= 12):
        raise ValueError(f"Mes no válido: {mes}. Debe estar entre 1 (Enero) y 12 (Diciembre)")

    # 2. Construir DataFrame de una fila inicializado con ceros
    input_data = pd.DataFrame(0, index=[0], columns=columnas_entrada)
    
    # Asignar variables numéricas principales
    input_data['DIA_SEMANA'] = dia_semana
    input_data['MES_NUM'] = mes
    
    # Asignar 1 a las columnas dummy si corresponden
    # Si departamento es AMAZONAS (baseline), no hay columna en columnas_entrada y se queda en 0.
    if departamento_upper in columnas_entrada:
        input_data[departamento_upper] = 1
        
    # Si franja_horaria es MADRUGADA (baseline), no hay columna en columnas_entrada y se queda en 0.
    if franja_upper in columnas_entrada:
        input_data[franja_upper] = 1

    # 3. Realizar predicción
    # LGBMRegressor retorna un array numpy de predicciones
    pred_raw = model.predict(input_data)[0]
    
    # Evitar números de denuncias negativos
    pred_clipped = max(0.0, float(pred_raw))
    casos_esperados = int(round(pred_clipped))
    
    # 4. Clasificación según percentiles históricos
    # Si no se han definido percentiles en la metadata, usamos valores por defecto preventivos
    p33 = percentil_33 if percentil_33 is not None else 10.0
    p66 = percentil_66 if percentil_66 is not None else 25.0
    
    if casos_esperados <= p33:
        nivel_frecuencia = "BAJO"
    elif casos_esperados <= p66:
        nivel_frecuencia = "MEDIO"
    else:
        nivel_frecuencia = "ALTO"
        
    return {
        "casos_esperados": casos_esperados,
        "nivel_frecuencia": nivel_frecuencia
    }
