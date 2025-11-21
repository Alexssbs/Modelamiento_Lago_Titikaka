"""
Parámetros del Lago Titicaca basados en estudios reales para un modelo hidrológico-ecológico.
Ajustados para evitar dinámica explosiva o reducción instantánea.
"""

# ================================
# PARÁMETROS PRINCIPALES
# ================================
PARAMETROS_INICIALES = {
    # Stocks iniciales
    'volumen_inicial': 8.93e11,         # m³

    # Nutrientes (Fósforo total)
    'nutrientes_inicial': 0.028,        # mg/L

    # Biomasa Lemna
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

    # Contaminación - descargas anuales de fósforo
    'descarga_puno': 15,                # t/año
    'descarga_juliaca': 15,             # t/año
    'descarga_otras': 5,                # t/año
    'concentracion_descarga': 8,        # mg/L

    # Dinámica biológica ajustada
    'tasa_crecimiento_lemna': 0.3,      # reducido (antes 1.2)
    'tasa_mortalidad_lemna': 0.2,       # reducido (antes 1.0)
    'nutrientes_optimo_lemna': 0.05,
    'coef_nutrientes_lemna': 0.0001,    # consumo ajustado
    'capacidad_carga_lemna': 2000,      # ton

    # Oxígeno
    'tasa_reoxigenacion': 1.5,          # más realista
    'oxigeno_saturacion': 8.5,
    'consumo_o2_lemna': 0.001,
    'consumo_o2_descomposicion': 0.02,

    # Simulación
    'tiempo_simulacion': 20,            # años
    'paso_tiempo': 1/12,                # mensual
}

# ================================
# PROCESOS FISICOQUÍMICOS
# ================================
PARAMETROS_ADICIONALES = {
    'tasa_sedimentacion_nutrientes': 0.02,  # antes 0.25 → exagerado
    'tasa_dilution_natural': 0.01,          # antes 0.03
    'coef_dilucion_volumen': 1.5e-5,
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
        'tiempo_simulacion': (0, 200, "Tiempo de simulación debe estar entre 0–200 años"),
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
