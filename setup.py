"""
Script de configuración e instalación del proyecto.

Uso:
    python setup.py install  # Instala dependencias
    python setup.py test     # Ejecuta tests de validación
    python setup.py demo     # Ejecuta demo completo
"""

import os
import sys
import subprocess
from pathlib import Path


class InstaladorTiticaca:
    """Clase para gestionar la instalación del proyecto."""
    
    def __init__(self):
        self.proyecto_dir = Path(__file__).parent
        self.directorios = ['config', 'core', 'simulation', 'visualization', 
                        'resultados', 'graficos']
    
    def crear_estructura(self):
        """Crea la estructura de directorios del proyecto."""
        print("\n📁 Creando estructura de directorios...")
        
        for directorio in self.directorios:
            dir_path = self.proyecto_dir / directorio
            dir_path.mkdir(exist_ok=True)
            print(f"  ✓ {directorio}/")
            
            # Crear __init__.py en módulos de código
            if directorio not in ['resultados', 'graficos']:
                init_file = dir_path / '__init__.py'
                if not init_file.exists():
                    init_file.touch()
                    print(f"    ✓ {directorio}/__init__.py")
        
        print("\n✓ Estructura de directorios creada")
    
    def instalar_dependencias(self):
        """Instala las dependencias del proyecto."""
        print("\n📦 Instalando dependencias...")
        
        requirements_file = self.proyecto_dir / 'requirements.txt'
        
        if not requirements_file.exists():
            print("  ⚠️  Archivo requirements.txt no encontrado")
            return False
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ])
            print("\n✓ Dependencias instaladas correctamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error instalando dependencias: {e}")
            return False
    
    def verificar_instalacion(self):
        """Verifica que todas las dependencias estén instaladas."""
        print("\n🔍 Verificando instalación...")
        
        paquetes_requeridos = [
            'numpy', 'scipy', 'pandas', 'matplotlib', 
            'plotly', 'streamlit'
        ]
        
        todos_ok = True
        for paquete in paquetes_requeridos:
            try:
                __import__(paquete)
                print(f"  ✓ {paquete}")
            except ImportError:
                print(f"  ❌ {paquete} - NO INSTALADO")
                todos_ok = False
        
        if todos_ok:
            print("\n✓ Todos los paquetes están instalados")
        else:
            print("\n⚠️  Algunos paquetes faltan. Ejecute: python setup.py install")
        
        return todos_ok
    
    def ejecutar_tests(self):
        """Ejecuta tests básicos de validación."""
        print("\n🧪 Ejecutando tests de validación...")
        
        try:
            # Test 1: Importar módulos
            print("\n  Test 1: Importando módulos...")
            from config.parametros import obtener_parametros
            from config.escenarios import obtener_escenario
            from core.modelo import ModeloTiticaca
            print("    ✓ Módulos importados correctamente")
            
            # Test 2: Crear modelo
            print("\n  Test 2: Creando modelo...")
            params = obtener_parametros()
            escenario = obtener_escenario('base')
            modelo = ModeloTiticaca(params, escenario)
            print("    ✓ Modelo creado correctamente")
            
            # Test 3: Simulación rápida
            print("\n  Test 3: Ejecutando simulación corta...")
            params_test = obtener_parametros({'tiempo_simulacion': 5})
            modelo_test = ModeloTiticaca(params_test, escenario)
            resultado = modelo_test.simular()
            print(f"    ✓ Simulación completada ({len(resultado['tiempo'])} pasos)")
            
            # Test 4: Métricas
            print("\n  Test 4: Calculando métricas...")
            metricas = modelo_test.obtener_metricas()
            print(f"    ✓ Métricas calculadas")
            print(f"      - Nutrientes final: {metricas['nutrientes_final']:.2f} mg/L")
            print(f"      - Lemna final: {metricas['lemna_final']:.0f} ton")
            
            print("\n✓ Todos los tests pasaron exitosamente")
            return True
            
        except Exception as e:
            print(f"\n❌ Error en tests: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def ejecutar_demo(self):
        """Ejecuta una demostración completa del sistema."""
        print("\n🎬 Ejecutando demostración completa...")
        print("="*70)
        
        try:
            from simulation.runner import RunnerSimulacion
            
            # Ejecutar 3 escenarios representativos
            print("\n1️⃣  Ejecutando escenarios de demostración...")
            runner = RunnerSimulacion()
            
            escenarios_demo = ['base', 'tratamiento_80', 'combinado']
            runner.ejecutar_todos(escenarios_demo, verbose=True)
            
            # Mostrar tabla comparativa
            print("\n2️⃣  Tabla comparativa:")
            print("-"*70)
            tabla = runner.generar_tabla_comparativa()
            print(tabla.to_string(index=False))
            
            # Guardar resultados
            print("\n3️⃣  Guardando resultados...")
            runner.guardar_resultados('resultados_demo')
            
            # Generar gráficos
            print("\n4️⃣  Generando visualizaciones...")
            from visualization.graficos import GraficadorTiticaca
            graficador = GraficadorTiticaca(runner)
            graficador.generar_todos_graficos('graficos_demo')
            
            print("\n" + "="*70)
            print("✓ DEMOSTRACIÓN COMPLETADA")
            print("="*70)
            print("\nArchivos generados:")
            print("  📁 resultados_demo/")
            print("  📁 graficos_demo/")
            print("\nPara ver el dashboard interactivo:")
            print("  streamlit run visualization/dashboard.py")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error en demostración: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def mostrar_ayuda(self):
        """Muestra información de ayuda."""
        print("\n" + "="*70)
        print(" INSTALADOR - MODELO LAGO TITICACA")
        print("="*70)
        print("\nComandos disponibles:")
        print("\n  python setup.py install")
        print("    Instala todas las dependencias del proyecto")
        print("\n  python setup.py verify")
        print("    Verifica que las dependencias estén instaladas")
        print("\n  python setup.py test")
        print("    Ejecuta tests de validación")
        print("\n  python setup.py demo")
        print("    Ejecuta una demostración completa")
        print("\n  python setup.py structure")
        print("    Crea la estructura de directorios")
        print("\n  python setup.py all")
        print("    Ejecuta instalación completa (estructura + dependencias + tests + demo)")
        print("\n" + "="*70 + "\n")


def main():
    """Función principal del instalador."""
    instalador = InstaladorTiticaca()
    
    if len(sys.argv) < 2:
        instalador.mostrar_ayuda()
        return
    
    comando = sys.argv[1].lower()
    
    if comando == 'structure':
        instalador.crear_estructura()
    
    elif comando == 'install':
        instalador.crear_estructura()
        instalador.instalar_dependencias()
    
    elif comando == 'verify':
        instalador.verificar_instalacion()
    
    elif comando == 'test':
        if instalador.verificar_instalacion():
            instalador.ejecutar_tests()
        else:
            print("\n  Instale las dependencias primero: python setup.py install")
    
    elif comando == 'demo':
        if instalador.verificar_instalacion():
            instalador.ejecutar_demo()
        else:
            print("\n  Instale las dependencias primero: python setup.py install")
    
    elif comando == 'all':
        print("\n INSTALACIÓN COMPLETA")
        print("="*70 + "\n")
        
        instalador.crear_estructura()
        
        if instalador.instalar_dependencias():
            if instalador.verificar_instalacion():
                if instalador.ejecutar_tests():
                    instalador.ejecutar_demo()
                    
                    print("\n" + "="*70)
                    print(" ✓ INSTALACIÓN Y CONFIGURACIÓN COMPLETAS")
                    print("="*70)
                    print("\nEl proyecto está listo para usar:")
                    print("  • python main.py              (simulaciones)")
                    print("  • python ejemplo_uso.py       (ejemplos)")
                    print("  • streamlit run visualization/dashboard.py  (dashboard)")
                    print("\n")
    
    elif comando in ['help', '--help', '-h']:
        instalador.mostrar_ayuda()
    
    else:
        print(f"\n  Comando desconocido: {comando}")
        instalador.mostrar_ayuda()


if __name__ == "__main__":
    main()