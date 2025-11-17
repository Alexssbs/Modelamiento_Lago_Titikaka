"""
Archivos __init__.py para todos los módulos.

Crear estos archivos en cada directorio:
- config/__init__.py
- core/__init__.py
- simulation/__init__.py
- visualization/__init__.py
"""

# ============================================================================
# config/__init__.py
# ============================================================================
"""
Módulo de configuración del modelo.
"""

from .parametros import (
    PARAMETROS_DEFAULT,
    obtener_parametros,
    validar_parametros
)

from .escenarios import (
    ESCENARIOS,
    obtener_escenario,
    listar_escenarios,
    crear_escenario_personalizado
)

__all__ = [
    'PARAMETROS_DEFAULT',
    'obtener_parametros',
    'validar_parametros',
    'ESCENARIOS',
    'obtener_escenario',
    'listar_escenarios',
    'crear_escenario_personalizado'
]


