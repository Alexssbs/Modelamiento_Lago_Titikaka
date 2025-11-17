"""
Archivos __init__.py para todos los módulos.

Crear estos archivos en cada directorio:
- config/__init__.py
- core/__init__.py
- simulation/__init__.py
- visualization/__init__.py
"""

# ============================================================================
# core/__init__.py
# ============================================================================
"""
Módulo central con el modelo de simulación.
"""

from .modelo import ModeloTiticaca

__all__ = ['ModeloTiticaca']


