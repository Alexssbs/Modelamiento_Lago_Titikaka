"""
Definición de escenarios de políticas ambientales para el Lago Titicaca.
"""

ESCENARIOS = {
    'base': {
        'nombre': 'Escenario Base',
        'descripcion': 'Continuación de la situación actual sin intervención',
        'eficiencia_tratamiento_puno': 0.0,
        'eficiencia_tratamiento_juliaca': 0.0,
        'remocion_mecanica_lemna': 0.0,
        'color': '#e74c3c',
        'parametros': {}
    },
    
    'tratamiento_50': {
        'nombre': 'Tratamiento 50%',
        'descripcion': 'Plantas de tratamiento con 50% de eficiencia',
        'eficiencia_tratamiento_puno': 0.50,
        'eficiencia_tratamiento_juliaca': 0.50,
        'remocion_mecanica_lemna': 0.0,
        'color': '#f39c12',
        'parametros': {}
    },
    
    'tratamiento_80': {
        'nombre': 'Tratamiento 80%',
        'descripcion': 'Plantas de tratamiento con 80% de eficiencia',
        'eficiencia_tratamiento_puno': 0.80,
        'eficiencia_tratamiento_juliaca': 0.80,
        'remocion_mecanica_lemna': 0.0,
        'color': '#3498db',
        'parametros': {}
    },
    
    'tratamiento_95': {
        'nombre': 'Tratamiento 95%',
        'descripcion': 'Plantas de tratamiento con 95% de eficiencia (óptimo)',
        'eficiencia_tratamiento_puno': 0.95,
        'eficiencia_tratamiento_juliaca': 0.95,
        'remocion_mecanica_lemna': 0.0,
        'color': '#2ecc71',
        'parametros': {}
    },
    
    'combinado': {
        'nombre': 'Intervención Combinada',
        'descripcion': 'Tratamiento 95% + remoción mecánica de Lemna',
        'eficiencia_tratamiento_puno': 0.95,
        'eficiencia_tratamiento_juliaca': 0.95,
        'remocion_mecanica_lemna': 500,  # toneladas/año removidas
        'color': '#9b59b6',
        'parametros': {}
    },
    
    'optimista': {
        'nombre': 'Escenario Optimista',
        'descripcion': 'Máxima intervención: Tratamiento 95% + remoción agresiva + reducción de descargas',
        'eficiencia_tratamiento_puno': 0.95,
        'eficiencia_tratamiento_juliaca': 0.95,
        'remocion_mecanica_lemna': 1000,  # toneladas/año
        'color': '#1abc9c',
        'parametros': {
            'descarga_otras': 5,  # Reducción de otras fuentes
        }
    }
}


def obtener_escenario(nombre):
    """
    Obtiene la configuración de un escenario específico.
    
    Args:
        nombre (str): Nombre del escenario
        
    Returns:
        dict: Configuración del escenario
        
    Raises:
        ValueError: Si el escenario no existe
    """
    if nombre not in ESCENARIOS:
        raise ValueError(f"Escenario '{nombre}' no encontrado. "
                        f"Escenarios disponibles: {list(ESCENARIOS.keys())}")
    
    return ESCENARIOS[nombre].copy()


def listar_escenarios():
    """
    Lista todos los escenarios disponibles.
    
    Returns:
        list: Lista de nombres de escenarios
    """
    return list(ESCENARIOS.keys())


def obtener_descripcion_escenarios():
    """
    Obtiene descripciones de todos los escenarios.
    
    Returns:
        dict: Diccionario con nombre y descripción de cada escenario
    """
    return {
        nombre: {
            'nombre_completo': config['nombre'],
            'descripcion': config['descripcion']
        }
        for nombre, config in ESCENARIOS.items()
    }


def crear_escenario_personalizado(nombre, eficiencia_puno, eficiencia_juliaca, 
                                  remocion_lemna=0, parametros_adicionales=None):
    """
    Crea un escenario personalizado.
    
    Args:
        nombre (str): Nombre del escenario
        eficiencia_puno (float): Eficiencia de tratamiento en Puno (0-1)
        eficiencia_juliaca (float): Eficiencia de tratamiento en Juliaca (0-1)
        remocion_lemna (float): Remoción mecánica de Lemna en ton/año
        parametros_adicionales (dict, optional): Parámetros adicionales del modelo
        
    Returns:
        dict: Configuración del escenario personalizado
    """
    if not (0 <= eficiencia_puno <= 1):
        raise ValueError("Eficiencia de Puno debe estar entre 0 y 1")
    if not (0 <= eficiencia_juliaca <= 1):
        raise ValueError("Eficiencia de Juliaca debe estar entre 0 y 1")
    if remocion_lemna < 0:
        raise ValueError("Remoción de Lemna debe ser no negativa")
    
    escenario = {
        'nombre': nombre,
        'descripcion': f'Escenario personalizado: Puno {eficiencia_puno*100:.0f}%, '
                    f'Juliaca {eficiencia_juliaca*100:.0f}%, '
                    f'Remoción {remocion_lemna} ton/año',
        'eficiencia_tratamiento_puno': eficiencia_puno,
        'eficiencia_tratamiento_juliaca': eficiencia_juliaca,
        'remocion_mecanica_lemna': remocion_lemna,
        'color': '#95a5a6',
        'parametros': parametros_adicionales or {}
    }
    
    return escenario