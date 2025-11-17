"""
Archivos __init__.py para todos los módulos.

Crear estos archivos en cada directorio:
- config/__init__.py
- core/__init__.py
- simulation/__init__.py
- visualization/__init__.py
"""

# ============================================================================
# visualization/__init__.py
# ============================================================================
"""
Módulo de visualización y reportes.
"""

from .graficos import GraficadorTiticaca

__all__ = ['GraficadorTiticaca']