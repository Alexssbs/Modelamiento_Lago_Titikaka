"""
Parámetros del Lago Titicaca basados en estudios reales para un modelo hidrológico‑ecológico.
"""

# ================================
# PARÁMETROS PRINCIPALES
# ================================
PARAMETROS_INICIALES = {
    # Stocks iniciales
    'volumen_inicial': 8.93e11,         # m³ (valor real conocido)
    
    # Nutrientes (Fósforo total): basado en estudio de la zona litoral de Juli
    # Olivera Vilca (2022) midió ~0.027–0.028 mg/L en época lluviosa/seca. :contentReference[oaicite:0]{index=0}
    'nutrientes_inicial': 0.028,        

    # Lemna (asumido): no hay dato preciso real reciente, pero ponemos un valor moderado
    'lemna_inicial': 300,                # ton

    # Oxígeno disuelto inicial (valor plausible)
    'oxigeno_inicial': 8.0,              # mg/L

    # Hidrología
    'area_lago': 8.372e9,               # m² (dato real)
    'profundidad_promedio': 107,        # m
    'precipitacion_anual': 0.75,  
    'evaporacion_anual': 1.55,
    'flujo_rios': 6.5e9,
    'extraccion_humana': 1.5e8,

    # Contaminación - descargas de fósforo
    # Se usa un valor bajo-moderado para PTAR, porque algunos estudios sugieren que no todo el P está tratado.
    # Además, el río Coata reporta hasta 10.287 mg/L de P en su afluencia según Quispe et al. (2019). :contentReference[oaicite:1]{index=1}  
    'descarga_puno': 15,                 # t/año P
    'descarga_juliaca': 15,              # t/año P
    'descarga_otras': 5,                  # t/año P

    'concentracion_descarga': 8,          # mg/L de P total (supuesto, coincide con tu modelo original)

    # Dinámica de Lemna
    'tasa_crecimiento_lemna': 1.2,      
    'tasa_mortalidad_lemna': 1.0,
    'nutrientes_optimo_lemna': 0.05,     # mg/L P
    'coef_nutrientes_lemna': 0.001,      # ton de Lemna consume más P (modelo)
    'capacidad_carga_lemna': 2000,

    # Oxígeno
    'tasa_reoxigenacion': 5.0,
    'oxigeno_saturacion': 8.5,
    'consumo_o2_lemna': 0.002,
    'consumo_o2_descomposicion': 0.05,

    # Simulación
    'tiempo_simulacion': 20,
    'paso_tiempo': 0.1,
}

# Procesos fisicoquímicos
PARAMETROS_ADICIONALES = {
    'tasa_sedimentacion_nutrientes': 0.25,  
    'tasa_dilution_natural': 0.03,
    'coef_dilucion_volumen': 1.5e-5,
}

PARAMETROS_DEFAULT = {**PARAMETROS_INICIALES, **PARAMETROS_ADICIONALES}

# Validación
def validar_parametros(params):
    validaciones = {
        'volumen_inicial': (5e11, 1.2e12, "Volumen debe estar entre 500–1200 km³"),
        'nutrientes_inicial': (0.001, 1.0, "Nutrientes deben estar entre 0.001–1.0 mg/L"),
        'lemna_inicial': (0, 5000, "Biomasa debe estar entre 0–5000 ton"),
        'oxigeno_inicial': (0, 12, "Oxígeno debe estar entre 0–12 mg/L"),
        'tiempo_simulacion': (1, 200, "Tiempo de simulación debe estar entre 1–200 años"),
    }

    for param, (min_val, max_val, mensaje) in validaciones.items():
        if param in params:
            valor = params[param]
            if not (min_val <= valor <= max_val):
                raise ValueError(f"{mensaje}. Valor recibido: {valor}")

    return True

def obtener_parametros(modificaciones=None):
    params = PARAMETROS_DEFAULT.copy()
    if modificaciones:
        params.update(modificaciones)
    validar_parametros(params)
    return params
