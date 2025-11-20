"""
Parámetros del Lago Titicaca basados en estudios reales para un modelo hidrológico-ecológico.
"""

# ================================
# PARÁMETROS PRINCIPALES
# ================================
PARAMETROS_INICIALES = {
    # Stocks iniciales
    'volumen_inicial': 8.93e11,         # m³ (valor real aproximado)

    # Nutrientes (Fósforo total): valores medidos en zona litoral (lluvias/seca)
    'nutrientes_inicial': 0.028,        # mg/L

    # Biomasa Lemna (supuesto)
    'lemna_inicial': 300,               # ton

    # Oxígeno disuelto inicial
    'oxigeno_inicial': 8.0,             # mg/L

    # Hidrología
    'area_lago': 8.372e9,               # m²
    'profundidad_promedio': 107,        # m
    'precipitacion_anual': 0.75,        # m/año
    'evaporacion_anual': 1.55,          # m/año
    'flujo_rios': 6.5e9,                # m³/año
    'extraccion_humana': 1.5e8,         # m³/año

    # Contaminación - descargas de fósforo
    'descarga_puno': 15,                # t/año P
    'descarga_juliaca': 15,             # t/año P
    'descarga_otras': 5,                # t/año P

    # Concentración de fósforo en aguas residuales
    'concentracion_descarga': 8,        # mg/L

    # Dinámica de Lemna
    'tasa_crecimiento_lemna': 1.2,
    'tasa_mortalidad_lemna': 1.0,
    'nutrientes_optimo_lemna': 0.05,    # mg/L
    'coef_nutrientes_lemna': 0.001,     # consumo de P
    'capacidad_carga_lemna': 2000,      # ton

    # Oxígeno
    'tasa_reoxigenacion': 5.0,
    'oxigeno_saturacion': 8.5,
    'consumo_o2_lemna': 0.002,
    'consumo_o2_descomposicion': 0.05,

    # Parámetros de simulación
    'tiempo_simulacion': 20,            # años
    'paso_tiempo': 0.1,                 # resolución (años)
}

# ================================
# PROCESOS FISICOQUÍMICOS
# ================================
PARAMETROS_ADICIONALES = {
    'tasa_sedimentacion_nutrientes': 0.25,  # fracción/año
    'tasa_dilution_natural': 0.03,          # fracción/año
    'coef_dilucion_volumen': 1.5e-5,        # coef. de mezcla
}

# Mezcla final
PARAMETROS_DEFAULT = {**PARAMETROS_INICIALES, **PARAMETROS_ADICIONALES}

# ================================
# VALIDACIÓN DE PARÁMETROS
# ================================
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

# ================================
# FUNCIÓN PARA OBTENER PARÁMETROS
# ================================
def obtener_parametros(modificaciones=None):
    params = PARAMETROS_DEFAULT.copy()

    if modificaciones:
        params.update(modificaciones)

    validar_parametros(params)
    return params
