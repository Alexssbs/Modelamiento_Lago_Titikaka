"""
Parámetros realistas del Lago Titicaca para un modelo hidrológico-ecológico simplificado.
"""

# ================================
# PARÁMETROS HIDROLÓGICOS REALES
# ================================
PARAMETROS_INICIALES = {
    # Stocks iniciales (estado del lago)
    'volumen_inicial': 8.93e11,         # m³ (893 km³, dato oficial ALT)
    'nutrientes_inicial': 0.03,         # mg/L P total (lago oligotrófico)
    'lemna_inicial': 300,               # ton biomasa (presencia marginal en bahías)
    'oxigeno_inicial': 8.0,             # mg/L (altiplano, aguas frías)

    # Hidrología (valores oficiales ALT + ANA)
    'area_lago': 8.372e9,               # m² (8,372 km²)
    'profundidad_promedio': 107,        # m
    'precipitacion_anual': 0.75,        # m/año
    'evaporacion_anual': 1.55,          # m/año
    'flujo_rios': 6.5e9,                # m³/año (aporte total Ramis + Huancané + Suchez + Ilave)
    'extraccion_humana': 1.5e8,         # m³/año (Perú + Bolivia)

    # ================================
    # CONTAMINACIÓN REALISTA
    # ================================
    # Aportes anuales de fósforo (t/año)
    'descarga_puno': 12,                # t/año P (PTAR operando parcialmente)
    'descarga_juliaca': 20,             # t/año P (PTAR en operación + fugas residuales)
    'descarga_otras': 10,               # t/año P (poblaciones menores + agricultura)

    # Concentración de aguas residuales
    'concentracion_descarga': 8,        # mg/L de P total (usualmente 5–10 mg/L)

    # ================================
    # DINÁMICA DE LEMNA/MACRÓFITAS
    # ================================
    # Nota: Lemna no es dominante en Titicaca, se usa como "genérico" de macrófita superficial
    'tasa_crecimiento_lemna': 1.2,      # 1/año (aprox. 0.0033 /día)
    'tasa_mortalidad_lemna': 1.0,       # 1/año
    'nutrientes_optimo_lemna': 0.1,     # mg/L de P (macrófitas responden con muy poco P)
    'coef_nutrientes_lemna': 0.0001,    # consumo P por tonelada
    'capacidad_carga_lemna': 2000,      # ton máx (limitado al área de bahías)

    # ================================
    # OXÍGENO
    # ================================
    'tasa_reoxigenacion': 5.0,          # 1/año (≈0.014/día, lago ventilado por viento)
    'oxigeno_saturacion': 8.5,          # mg/L a 3,800 msnm
    'consumo_o2_lemna': 0.002,          # mg/L por tonelada
    'consumo_o2_descomposicion': 0.05,  # mg/L por mg/L de P

    # ================================
    # SIMULACIÓN
    # ================================
    'tiempo_simulacion': 20,            # años
    'paso_tiempo': 0.1,                 # años (36 días)
}

# ================================
# PROCESOS FISICOQUÍMICOS
# ================================
PARAMETROS_ADICIONALES = {
    'tasa_sedimentacion_nutrientes': 0.25,   # 1/año (lagos someros y fríos sedimentan rápido P)
    'tasa_dilution_natural': 0.03,           # 1/año (renovación lenta pero significativa)
    'coef_dilucion_volumen': 1.5e-5,         # ajuste fino por volumen ≥ 10¹¹
}

PARAMETROS_DEFAULT = {**PARAMETROS_INICIALES, **PARAMETROS_ADICIONALES}


# ================================
# VALIDACIÓN
# ================================
def validar_parametros(params):
    validaciones = {
        'volumen_inicial': (5e11, 1.2e12, "Volumen debe estar entre 500–1200 km³"),
        'nutrientes_inicial': (0.001, 0.5, "Nutrientes deben estar entre 0.001–0.5 mg/L"),
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
