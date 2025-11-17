"""
Programa principal para ejecutar el Modelo de Dinámica de Sistemas 
del Lago Titicaca.

Uso:
    python main.py              # Ejecuta todas las simulaciones
    python main.py --escenario base  # Ejecuta un escenario específico
    python main.py --graficos   # Genera solo gráficos de resultados existentes
"""

import argparse
import sys
import os

# Añadir directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.runner import RunnerSimulacion
from visualization.graficos import GraficadorTiticaca
from config.escenarios import listar_escenarios


def parsear_argumentos():
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Modelo de Dinámica de Sistemas del Lago Titicaca'
    )
    
    parser.add_argument(
        '--escenario',
        type=str,
        choices=listar_escenarios(),
        help='Ejecutar solo un escenario específico'
    )
    
    parser.add_argument(
        '--tiempo',
        type=int,
        default=20,
        help='Tiempo de simulación en años (default: 20)'
    )
    
    parser.add_argument(
        '--graficos',
        action='store_true',
        help='Solo generar gráficos (requiere resultados previos)'
    )
    
    parser.add_argument(
        '--no-guardar',
        action='store_true',
        help='No guardar resultados en archivos'
    )
    
    parser.add_argument(
        '--dir-resultados',
        type=str,
        default='resultados',
        help='Directorio para guardar resultados (default: resultados)'
    )
    
    parser.add_argument(
        '--dir-graficos',
        type=str,
        default='graficos',
        help='Directorio para guardar gráficos (default: graficos)'
    )
    
    return parser.parse_args()


def main():
    """Función principal."""
    args = parsear_argumentos()
    
    # print("\n" + "="*80)
    # print(" " * 15 + "MODELO DE DINÁMICA DE SISTEMAS")
    # print(" " * 20 + "LAGO TITICACA")
    #print("="*80 + "\n")
    
    # Crear runner
    parametros = {'tiempo_simulacion': args.tiempo}
    runner = RunnerSimulacion(parametros)
    
    # Ejecutar simulaciones
    if not args.graficos:
        if args.escenario:
            # Ejecutar solo un escenario
            runner.ejecutar_escenario(args.escenario, verbose=False)  # ← Cambiar a False
            # print(f"Ejecutando escenario: {args.escenario}\n")
            # runner.ejecutar_escenario(args.escenario)
        else:
            # Ejecutar todos los escenarios
            #print("Ejecutando todos los escenarios...\n")
            runner.ejecutar_todos(verbose=False)
        
        # Mostrar tabla comparativa
     
    # Guardar resultados
    if not args.no_guardar:
           # print("\n" + "="*80)
           # print(" GUARDANDO RESULTADOS")
           # print("="*80 + "\n")
            runner.guardar_resultados(args.dir_resultados)
    
    # Generar gráficos
    if runner.resultados:
        # print("\n" + "="*80)
        # print(" GENERANDO VISUALIZACIONES")
        # print("="*80 + "\n")
        
        graficador = GraficadorTiticaca(runner)
        
        if not args.no_guardar:
            graficador.generar_todos_graficos(args.dir_graficos)
  
    return runner


if __name__ == "__main__":
    try:
        runner = main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)