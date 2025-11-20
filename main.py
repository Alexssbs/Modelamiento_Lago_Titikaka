"""
Programa principal para ejecutar el Modelo de Dinámica de Sistemas 
del Lago Titicaca.

Nuevos parámetros añadidos:
    --remocion-mecanica   → Habilita la remoción automática de Lemna
    --anadir-lemna X      → Añade X toneladas de Lemna cuando la absorción llega a 100%

Uso:
    python main.py
    python main.py --escenario base
    python main.py --remocion-mecanica
    python main.py --anadir-lemna 500
"""

import argparse
import sys
import os

# Añadir directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.runner import RunnerSimulacion
from visualization.graficos import GraficadorTiticaca
from config.escenarios import listar_escenarios


# ============================
# PARSEADOR DE ARGUMENTOS
# ============================
def parsear_argumentos():
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
        '--remocion-mecanica',
        action='store_true',
        help='Activa remoción mecánica cuando Lemna llega a 100% de absorción'
    )

    parser.add_argument(
        '--anadir-lemna',
        type=float,
        help='Añade X toneladas de Lemna cada vez que la absorción llegue a 100%'
    )

    parser.add_argument(
        '--dir-resultados',
        type=str,
        default='resultados',
        help='Directorio para guardar resultados'
    )
    
    parser.add_argument(
        '--dir-graficos',
        type=str,
        default='graficos',
        help='Directorio para guardar gráficos'
    )
    
    return parser.parse_args()



# ============================
# FUNCIÓN PRINCIPAL
# ============================
def main():
    args = parsear_argumentos()

    # Construimos parámetros adicionales según tus nuevas funciones:
    parametros = {
        'tiempo_simulacion': args.tiempo,
        'usar_remocion_mecanica': args.remocion_mecanica,
        'cantidad_anadir_lemna': args.anadir_lemna if args.anadir_lemna else 0
    }

    # Creamos el runner
    runner = RunnerSimulacion(parametros)

    # ============================
    # 1. EJECUTAR SIMULACIONES
    # ============================
    if not args.graficos:
        if args.escenario:
            # Solo un escenario
            runner.ejecutar_escenario(args.escenario, verbose=False)
        else:
            # Todos los escenarios
            runner.ejecutar_todos(verbose=False)

    # ============================
    # 2. GUARDAR RESULTADOS
    # ============================
    if not args.no_guardar:
        runner.guardar_resultados(args.dir_resultados)

    # ============================
    # 3. GENERAR GRÁFICOS
    # ============================
    if runner.resultados:
        graficador = GraficadorTiticaca(runner)
        
        if not args.no_guardar:
            graficador.generar_todos_graficos(args.dir_graficos)

    return runner



# ============================
# EJECUCIÓN DEL PROGRAMA
# ============================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
