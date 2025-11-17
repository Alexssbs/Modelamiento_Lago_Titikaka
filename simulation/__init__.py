"""
Archivos __init__.py para todos los módulos.

Crear estos archivos en cada directorio:
- config/__init__.py
- core/__init__.py
- simulation/__init__.py
- visualization/__init__.py
"""

# ============================================================================
# simulation/__init__.py
# ============================================================================
"""
Módulo de ejecución de simulaciones.
"""

from .runner import RunnerSimulacion

__all__ = ['RunnerSimulacion']

