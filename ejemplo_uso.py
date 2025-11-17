"""
Ejemplos de uso del Modelo de Dinámica de Sistemas del Lago Titicaca.

Este archivo muestra diferentes formas de usar el modelo programáticamente.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.modelo import ModeloTiticaca
from config.parametros import obtener_parametros
from config.escenarios import (obtener_escenario, crear_escenario_personalizado,
                               listar_escenarios)
from simulation.runner import RunnerSimulacion
from visualization.graficos import GraficadorTiticaca
import matplotlib.pyplot as plt


def ejemplo_1_simulacion_simple():
    """
    Ejemplo 1: Ejecutar una simulación simple de un escenario.
    """
    print("\n" + "="*70)
    print("EJEMPLO 1: Simulación Simple")
    print("="*70 + "\n")
    
    # Obtener parámetros y escenario
    params = obtener_parametros()
    escenario = obtener_escenario('tratamiento_80')
    
    # Crear modelo y simular
    modelo = ModeloTiticaca(params, escenario)
    resultado = modelo.simular()
    
    # Obtener métricas
    metricas = modelo.obtener_metricas()
    
    # Mostrar resultados
    print(f"Escenario: {escenario['nombre']}")
    print(f"Tiempo simulado: {params['tiempo_simulacion']} años")
    print(f"\nResultados finales:")
    print(f"  Nutrientes: {metricas['nutrientes_final']:.2f} mg/L")
    print(f"  Reducción: {metricas['reduccion_nutrientes_pct']:.1f}%")
    print(f"  Lemna: {metricas['lemna_final']:.0f} toneladas")
    print(f"  Reducción: {metricas['reduccion_lemna_pct']:.1f}%")
    print(f"  Oxígeno: {metricas['oxigeno_final']:.2f} mg/L")
    print(f"  Mejora: {metricas['mejora_oxigeno_pct']:.1f}%")
    
    return resultado, metricas


def ejemplo_2_escenario_personalizado():
    """
    Ejemplo 2: Crear y simular un escenario personalizado.
    """
    print("\n" + "="*70)
    print("EJEMPLO 2: Escenario Personalizado")
    print("="*70 + "\n")
    
    # Crear escenario personalizado
    escenario_custom = crear_escenario_personalizado(
        nombre="Intermedio",
        eficiencia_puno=0.65,
        eficiencia_juliaca=0.70,
        remocion_lemna=250,
        parametros_adicionales={'descarga_otras': 10}
    )
    
    print(f"Escenario creado: {escenario_custom['nombre']}")
    print(f"Descripción: {escenario_custom['descripcion']}")
    
    # Simular con tiempo personalizado
    params = obtener_parametros({'tiempo_simulacion': 15})
    modelo = ModeloTiticaca(params, escenario_custom)
    resultado = modelo.simular()
    metricas = modelo.obtener_metricas()
    
    print(f"\nReducción de Lemna: {metricas['reduccion_lemna_pct']:.1f}%")
    print(f"Mejora de Oxígeno: {metricas['mejora_oxigeno_pct']:.1f}%")
    
    return resultado, metricas


def ejemplo_3_comparacion_escenarios():
    """
    Ejemplo 3: Comparar múltiples escenarios.
    """
    print("\n" + "="*70)
    print("EJEMPLO 3: Comparación de Escenarios")
    print("="*70 + "\n")
    
    # Crear runner y ejecutar escenarios seleccionados
    runner = RunnerSimulacion()
    
    escenarios_comparar = ['base', 'tratamiento_50', 'tratamiento_95', 'combinado']
    
    print(f"Comparando {len(escenarios_comparar)} escenarios...\n")
    
    for escenario in escenarios_comparar:
        runner.ejecutar_escenario(escenario, verbose=False)
        metricas = runner.metricas[escenario]
        print(f"{escenario:20} | Nutrientes: {metricas['reduccion_nutrientes_pct']:+6.1f}% | "
              f"Lemna: {metricas['reduccion_lemna_pct']:+6.1f}% | "
              f"O₂: {metricas['mejora_oxigeno_pct']:+6.1f}%")
    
    # Generar tabla comparativa
    print("\n" + "-"*70)
    tabla = runner.generar_tabla_comparativa()
    print("\nTabla completa:")
    print(tabla.to_string(index=False))
    
    return runner


def ejemplo_4_analisis_sensibilidad():
    """
    Ejemplo 4: Análisis de sensibilidad de un parámetro.
    """
    print("\n" + "="*70)
    print("EJEMPLO 4: Análisis de Sensibilidad")
    print("="*70 + "\n")
    
    # Probar diferentes eficiencias de tratamiento
    eficiencias = [0.3, 0.5, 0.7, 0.9, 0.95]
    resultados = []
    
    print("Analizando impacto de eficiencia de tratamiento...")
    print(f"{'Eficiencia':>12} | {'Red. Nutrientes':>15} | {'Red. Lemna':>12} | {'Mejora O₂':>10}")
    print("-"*60)
    
    for eff in eficiencias:
        escenario = crear_escenario_personalizado(
            f"Tratamiento {int(eff*100)}%",
            eff, eff, 0
        )
        
        params = obtener_parametros({'tiempo_simulacion': 20})
        modelo = ModeloTiticaca(params, escenario)
        resultado = modelo.simular()
        metricas = modelo.obtener_metricas()
        
        resultados.append({
            'eficiencia': eff,
            'reduccion_nutrientes': metricas['reduccion_nutrientes_pct'],
            'reduccion_lemna': metricas['reduccion_lemna_pct'],
            'mejora_oxigeno': metricas['mejora_oxigeno_pct']
        })
        
        print(f"{eff*100:>10.0f}% | {metricas['reduccion_nutrientes_pct']:>14.1f}% | "
              f"{metricas['reduccion_lemna_pct']:>11.1f}% | "
              f"{metricas['mejora_oxigeno_pct']:>9.1f}%")
    
    return resultados


def ejemplo_5_visualizacion_avanzada():
    """
    Ejemplo 5: Crear visualizaciones personalizadas.
    """
    print("\n" + "="*70)
    print("EJEMPLO 5: Visualización Avanzada")
    print("="*70 + "\n")
    
    # Ejecutar varios escenarios
    runner = RunnerSimulacion()
    runner.ejecutar_todos(verbose=False)
    
    print("Generando visualizaciones...")
    
    # Crear graficador
    graficador = GraficadorTiticaca(runner)
    
    # Generar gráficos
    print("  ✓ Evolución temporal")
    fig1 = graficador.grafico_evolucion_temporal()
    
    print("  ✓ Comparativo final")
    fig2 = graficador.grafico_comparativo_final()
    
    print("  ✓ Dashboard interactivo")
    fig3 = graficador.grafico_interactivo_plotly()
    
    # Guardar dashboard interactivo
    fig3.write_html('dashboard_ejemplo.html')
    print("\n✓ Dashboard guardado en: dashboard_ejemplo.html")
    
    # Mostrar gráficos
    plt.show()
    
    return graficador


def ejemplo_6_exportar_datos():
    """
    Ejemplo 6: Exportar datos para análisis externo.
    """
    print("\n" + "="*70)
    print("EJEMPLO 6: Exportación de Datos")
    print("="*70 + "\n")
    
    # Ejecutar simulación
    runner = RunnerSimulacion()
    runner.ejecutar_escenario('combinado', verbose=False)
    
    # Obtener datos de series temporales
    series = runner.obtener_datos_serie_temporal()
    
    print("Series temporales disponibles:")
    for variable, df in series.items():
        print(f"  - {variable}: {len(df)} puntos temporales")
    
    # Guardar en CSV
    runner.guardar_resultados('resultados_ejemplo')
    
    # Acceder a datos específicos
    resultado = runner.resultados['combinado']
    
    print(f"\nDatos del escenario 'Combinado':")
    print(f"  Tiempo inicial: {resultado['tiempo'][0]} años")
    print(f"  Tiempo final: {resultado['tiempo'][-1]} años")
    print(f"  Puntos de datos: {len(resultado['tiempo'])}")
    print(f"  Variables simuladas: {list(resultado.keys())}")
    
    return series


def ejemplo_7_modificar_parametros():
    """
    Ejemplo 7: Modificar parámetros del modelo.
    """
    print("\n" + "="*70)
    print("EJEMPLO 7: Modificación de Parámetros")
    print("="*70 + "\n")
    
    # Parámetros personalizados
    params_custom = {
        'tiempo_simulacion': 30,
        'descarga_puno': 30,  # Aumentar descarga
        'descarga_juliaca': 50,
        'tasa_crecimiento_lemna': 0.4  # Lemna crece más rápido
    }
    
    print("Parámetros modificados:")
    for key, val in params_custom.items():
        print(f"  {key}: {val}")
    
    # Simular con parámetros modificados
    params = obtener_parametros(params_custom)
    escenario = obtener_escenario('tratamiento_80')
    
    modelo = ModeloTiticaca(params, escenario)
    resultado = modelo.simular()
    metricas = modelo.obtener_metricas()
    
    print(f"\nResultados con parámetros modificados:")
    print(f"  Reducción de Lemna: {metricas['reduccion_lemna_pct']:.1f}%")
    print(f"  (Con crecimiento más rápido de Lemna)")
    
    return resultado


def menu_interactivo():
    """Menú interactivo para ejecutar ejemplos."""
    while True:
        print("\n" + "="*70)
        print(" EJEMPLOS DE USO - MODELO LAGO TITICACA")
        print("="*70)
        print("\n1. Simulación Simple")
        print("2. Escenario Personalizado")
        print("3. Comparación de Escenarios")
        print("4. Análisis de Sensibilidad")
        print("5. Visualización Avanzada")
        print("6. Exportar Datos")
        print("7. Modificar Parámetros")
        print("8. Ejecutar Todos los Ejemplos")
        print("0. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            ejemplo_1_simulacion_simple()
        elif opcion == '2':
            ejemplo_2_escenario_personalizado()
        elif opcion == '3':
            ejemplo_3_comparacion_escenarios()
        elif opcion == '4':
            ejemplo_4_analisis_sensibilidad()
        elif opcion == '5':
            ejemplo_5_visualizacion_avanzada()
        elif opcion == '6':
            ejemplo_6_exportar_datos()
        elif opcion == '7':
            ejemplo_7_modificar_parametros()
        elif opcion == '8':
            print("\nEjecutando todos los ejemplos...")
            ejemplo_1_simulacion_simple()
            ejemplo_2_escenario_personalizado()
            ejemplo_3_comparacion_escenarios()
            ejemplo_4_analisis_sensibilidad()
            ejemplo_6_exportar_datos()
            ejemplo_7_modificar_parametros()
            print("\n✓ Todos los ejemplos completados")
        elif opcion == '0':
            print("\n¡Hasta luego!\n")
            break
        else:
            print("\n⚠️  Opción no válida")
        
        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    menu_interactivo()