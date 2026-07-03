import os
import json
import joblib
import pandas as pd
import numpy as np

# Carpeta absoluta donde está este script (sirve de base para armar rutas completas)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ruta absoluta al archivo JSON con columnas de entrada y percentiles del entrenamiento
METADATA_PATH = os.path.join(BASE_DIR, 'models', 'metadata_conteo.json')
# Ruta absoluta al modelo LightGBM entrenado y guardado con joblib
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'modelo_conteo_final.joblib')

# Verifica que exista el archivo de metadata antes de leerlo
if not os.path.exists(METADATA_PATH):
    raise FileNotFoundError(f"No se encontró el archivo de metadata en {METADATA_PATH}")

# Carga el JSON con columnas de entrada y percentiles calculados en el entrenamiento
with open(METADATA_PATH, 'r') as f:
    metadata = json.load(f)

# Verifica que exista el modelo entrenado antes de cargarlo
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el modelo entrenado en {MODEL_PATH}")

# Carga el modelo LightGBM (LGBMRegressor) ya entrenado, listo para predecir
model = joblib.load(MODEL_PATH)

# Lista de columnas exactas (nombre y orden) que el modelo espera como entrada
columnas_entrada = metadata.get('columnas_entrada', [])
# Percentil 33 de casos históricos, usado para clasificar como BAJO
percentil_33 = metadata.get('percentil_33')
# Percentil 66 de casos históricos, usado para clasificar como MEDIO/ALTO
percentil_66 = metadata.get('percentil_66')

# Departamentos válidos para validar la entrada del usuario
DEPARTAMENTOS_VALIDOS = [
    "AMAZONAS", "ANCASH", "APURIMAC", "AREQUIPA", "AYACUCHO", "CAJAMARCA", 
    "CALLAO", "CUSCO", "HUANCAVELICA", "HUANUCO", "ICA", "JUNIN", 
    "LA LIBERTAD", "LAMBAYEQUE", "LIMA", "LORETO", "MADRE DE DIOS", 
    "MOQUEGUA", "PASCO", "PIURA", "PUNO", "SAN MARTIN", "TACNA", 
    "TUMBES", "UCAYALI"
]

# Franjas horarias válidas para validar la entrada del usuario
FRANJAS_VALIDAS = ["MADRUGADA", "MANANA", "TARDE", "NOCHE"]

def predecir_casos(departamento: str, dia_semana: int, franja_horaria: str, mes: int):
    # Normaliza texto: sin espacios extra y en mayúsculas
    departamento_upper = departamento.strip().upper()
    franja_upper = franja_horaria.strip().upper()
    
    # Valida que el departamento sea uno de los conocidos por el modelo
    if departamento_upper not in DEPARTAMENTOS_VALIDOS:
        raise ValueError(f"Departamento no reconocido: '{departamento}'. Debe ser uno de {DEPARTAMENTOS_VALIDOS}")
        
    # Valida que la franja horaria sea una de las conocidas por el modelo
    if franja_upper not in FRANJAS_VALIDAS:
        raise ValueError(f"Franja horaria no reconocida: '{franja_horaria}'. Debe ser una de {FRANJAS_VALIDAS}")
        
    # Valida que el día de la semana esté en rango (0=Lunes a 6=Domingo)
    if not (0 <= dia_semana <= 6):
        raise ValueError(f"Día de la semana no válido: {dia_semana}. Debe estar entre 0 (Lunes) y 6 (Domingo)")
        
    # Valida que el mes esté en rango (1 a 12)
    if not (1 <= mes <= 12):
        raise ValueError(f"Mes no válido: {mes}. Debe estar entre 1 (Enero) y 12 (Diciembre)")

    # Construir DataFrame de una fila inicializado con ceros
    # Fila de entrada con las mismas columnas que vio el modelo al entrenar, todo en 0
    input_data = pd.DataFrame(0, index=[0], columns=columnas_entrada)
    
    # Asignar variables numéricas principales
    # Coloca el día de la semana real en su columna
    input_data['DIA_SEMANA'] = dia_semana
    # Coloca el mes real en su columna
    input_data['MES_NUM'] = mes
    
    # Asignar 1 a las columnas dummy si corresponden
    # Si departamento es AMAZONAS (baseline), no hay columna en columnas_entrada y se queda en 0.
    # Activa con un 1 la columna del departamento recibido (one-hot encoding)
    if departamento_upper in columnas_entrada:
        input_data[departamento_upper] = 1
        
    # Si franja_horaria es MADRUGADA (baseline), no hay columna en columnas_entrada y se queda en 0.
    # Activa con un 1 la columna de la franja horaria recibida (one-hot encoding)
    if franja_upper in columnas_entrada:
        input_data[franja_upper] = 1

    # 3. Realizar predicción
    # LGBMRegressor retorna un array numpy de predicciones
    # Ejecuta la predicción del modelo LightGBM y toma el único valor devuelto
    pred_raw = model.predict(input_data)[0]
    
    # Evitar números de denuncias negativos
    # Recorta negativos a 0 y redondea a entero (un conteo de casos)
    pred_clipped = max(0.0, float(pred_raw))
    casos_esperados = int(round(pred_clipped))
    
    # 4. Clasificación según percentiles históricos
    # Si no se han definido percentiles en la metadata, usamos valores por defecto preventivos
    # Usa valores de respaldo si la metadata no trajo percentiles
    p33 = percentil_33 if percentil_33 is not None else 10.0
    p66 = percentil_66 if percentil_66 is not None else 25.0
    
    # Etiqueta el resultado comparándolo contra los percentiles históricos
    if casos_esperados <= p33:
        nivel_frecuencia = "BAJO"
        # Interpolación: de 0 a p33 corresponde a 0% a 33.3%
        posicion_percentil = (casos_esperados / p33) * 33.3 if p33 > 0 else 0
    elif casos_esperados <= p66:
        nivel_frecuencia = "MEDIO"
        # Interpolación: de p33 a p66 corresponde a 33.3% a 66.6%
        rango_valor = p66 - p33
        posicion_percentil = 33.3 + ((casos_esperados - p33) / rango_valor) * 33.3 if rango_valor > 0 else 33.3
    else:
        nivel_frecuencia = "ALTO"
        # Extrapolación: p66 en adelante. Estimamos que el doble del p66 es ~98% para evitar llegar a 100%
        max_estimado = p66 * 2.5 # Un valor conservador
        if casos_esperados >= max_estimado:
            posicion_percentil = 98.0
        else:
            rango_valor = max_estimado - p66
            posicion_percentil = 66.6 + ((casos_esperados - p66) / rango_valor) * (98.0 - 66.6) if rango_valor > 0 else 66.6
            
    # Redondeamos a un decimal para presentación visual
    posicion_percentil = round(posicion_percentil, 1)
        
    # Devuelve el número predicho y su nivel de frecuencia como diccionario
    return {
        "casos_esperados": casos_esperados,
        "nivel_frecuencia": nivel_frecuencia,
        "posicion_percentil": posicion_percentil
    }