"""
Sistema de ejecución de simulaciones múltiples.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.modelo import ModeloTiticaca
from config.parametros import obtener_parametros
from config.escenarios import ESCENARIOS, obtener_escenario
import pandas as pd
from datetime import datetime


class RunnerSimulacion:
    """
    Clase para ejecutar y gestionar múltiples simulaciones.
    """
    
    def __init__(self, parametros=None):
        """
        Inicializa el runner.
        
        Args:
            parametros (dict, optional): Parámetros base para las simulaciones
        """
        self.parametros = obtener_parametros(parametros)
        self.resultados = {}
        self.metricas = {}
    
    def ejecutar_escenario(self, nombre_escenario, verbose=False):
        """
        Ejecuta simulación para un escenario específico.
        
        Args:
            nombre_escenario (str): Nombre del escenario
            verbose (bool): Mostrar información de progreso
            
        Returns:
            dict: Resultados de la simulación
        """
        if verbose:
            print(f"\n{'='*60}")    
            print(f"Ejecutando: {nombre_escenario}")
            print(f"{'='*60}")
        
        escenario = obtener_escenario(nombre_escenario)
        
        if verbose:
            print(f"Descripción: {escenario['descripcion']}")
            print(f"Eficiencia Puno: {escenario['eficiencia_tratamiento_puno']*100:.0f}%")
            print(f"Eficiencia Juliaca: {escenario['eficiencia_tratamiento_juliaca']*100:.0f}%")
            print(f"Remoción Lemna: {escenario['remocion_mecanica_lemna']} ton/año")
        
        # Crear y ejecutar modelo
        modelo = ModeloTiticaca(self.parametros, escenario)
        
        if verbose:
            print("Simulando...")
        
        resultado = modelo.simular()
        metricas = modelo.obtener_metricas()
        
        # Guardar resultados
        self.resultados[nombre_escenario] = resultado
        self.metricas[nombre_escenario] = metricas
        
        if verbose:
            print("\nResultados:")
            print(f"  Nutrientes: {metricas['nutrientes_final']:.2f} mg/L "
                  f"({metricas['reduccion_nutrientes_pct']:+.1f}%)")
            print(f"  Lemna: {metricas['lemna_final']:.0f} ton "
                  f"({metricas['reduccion_lemna_pct']:+.1f}%)")
            print(f"  Oxígeno: {metricas['oxigeno_final']:.2f} mg/L "
                  f"({metricas['mejora_oxigeno_pct']:+.1f}%)")
        
        return resultado
    
    def ejecutar_todos(self, escenarios=None, verbose=False):
        """
        Ejecuta simulaciones para todos los escenarios.
        
        Args:
            escenarios (list, optional): Lista de nombres de escenarios. 
                                        Si None, ejecuta todos.
            verbose (bool): Mostrar información de progreso
        """
        if escenarios is None:
            escenarios = list(ESCENARIOS.keys())
        if verbose:
            print(f"\n{'#'*60}")
            print(f"# SIMULACIÓN DEL LAGO TITICACA")
            print(f"# Total de escenarios: {len(escenarios)}")
            print(f"# Tiempo de simulación: {self.parametros['tiempo_simulacion']} años")
            print(f"# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'#'*60}\n")
        
        for i, nombre in enumerate(escenarios, 1):
            if verbose:
                print(f"\n[{i}/{len(escenarios)}] ", end="")
            
            try:
                self.ejecutar_escenario(nombre, verbose=verbose)
            except Exception as e:
                print(f"ERROR en escenario '{nombre}': {str(e)}")
                continue
        
        if verbose:
            print(f"\n{'='*60}")
            print("SIMULACIONES COMPLETADAS")
            print(f"{'='*60}\n")
    
    def generar_tabla_comparativa(self):
        """
        Genera tabla comparativa de métricas de todos los escenarios.
        
        Returns:
            pd.DataFrame: Tabla con métricas comparativas
        """
        if not self.metricas:
            raise ValueError("No hay resultados. Ejecute simulaciones primero.")
        
        datos = []
        for nombre, metricas in self.metricas.items():
            escenario = ESCENARIOS[nombre]
            
            fila = {
                'Escenario': escenario['nombre'],
                'Efic. Puno (%)': escenario['eficiencia_tratamiento_puno'] * 100,
                'Efic. Juliaca (%)': escenario['eficiencia_tratamiento_juliaca'] * 100,
                'Remoción Lemna (ton/año)': escenario['remocion_mecanica_lemna'],
                'Nutrientes Final (mg/L)': metricas['nutrientes_final'],
                'Reducción Nutrientes (%)': metricas['reduccion_nutrientes_pct'],
                'Lemna Final (ton)': metricas['lemna_final'],
                'Reducción Lemna (%)': metricas['reduccion_lemna_pct'],
                'Oxígeno Final (mg/L)': metricas['oxigeno_final'],
                'Mejora Oxígeno (%)': metricas['mejora_oxigeno_pct']
            }
            
            datos.append(fila)
        
        df = pd.DataFrame(datos)
        return df
    
    def obtener_datos_serie_temporal(self):
        """
        Obtiene datos de series temporales en formato DataFrame.
        
        Returns:
            dict: Diccionario de DataFrames por variable
        """
        if not self.resultados:
            raise ValueError("No hay resultados. Ejecute simulaciones primero.")
        
        # Crear DataFrames para cada variable
        dfs = {}
        variables = ['nutrientes', 'lemna', 'oxigeno', 'volumen']
        
        for var in variables:
            data = {}
            tiempo = None
            
            for nombre, resultado in self.resultados.items():
                if tiempo is None:
                    tiempo = resultado['tiempo']
                
                data[ESCENARIOS[nombre]['nombre']] = resultado[var]
            
            df = pd.DataFrame(data)
            df.insert(0, 'Tiempo (años)', tiempo)
            dfs[var] = df
        
        return dfs
    
    def guardar_resultados(self, directorio='resultados'):
        """
        Guarda todos los resultados en archivos CSV.
        
        Args:
            directorio (str): Directorio donde guardar los archivos
        """
        import os
        
        os.makedirs(directorio, exist_ok=True)
        
        # Guardar tabla comparativa
        tabla = self.generar_tabla_comparativa()
        tabla.to_csv(f'{directorio}/comparativa_escenarios.csv', index=False)
        # print(f"✓ Guardada tabla comparativa: {directorio}/comparativa_escenarios.csv")
        
        # Guardar series temporales
        series = self.obtener_datos_serie_temporal()
        for var, df in series.items():
            archivo = f'{directorio}/serie_{var}.csv'
            df.to_csv(archivo, index=False)
            # print(f"✓ Guardada serie temporal de {var}: {archivo}")
        
        # print(f"\nTodos los resultados guardados en: {directorio}/")
    
    def mejor_escenario(self, criterio='reduccion_nutrientes_pct'):
        """
        Identifica el mejor escenario según un criterio.
        
        Args:
            criterio (str): Métrica a usar ('reduccion_nutrientes_pct', 
                           'reduccion_lemna_pct', 'mejora_oxigeno_pct')
            
        Returns:
            tuple: (nombre_escenario, valor_metrica)
        """
        if not self.metricas:
            raise ValueError("No hay resultados. Ejecute simulaciones primero.")
        
        mejor = max(self.metricas.items(), key=lambda x: x[1].get(criterio, 0))
        return mejor[0], mejor[1][criterio]


def main():
    """Función principal para ejecutar simulaciones desde línea de comandos."""
    print("\n" + "="*70)
    print(" MODELO DE DINÁMICA DE SISTEMAS - LAGO TITICACA")
    print("="*70)
    
    # Crear runner y ejecutar todas las simulaciones
    runner = RunnerSimulacion()
    runner.ejecutar_todos()
    
    # Mostrar tabla comparativa
    print("\n" + "="*70)
    print(" TABLA COMPARATIVA DE ESCENARIOS")
    print("="*70 + "\n")
    
    tabla = runner.generar_tabla_comparativa()
    print(tabla.to_string(index=False))
    
    # Identificar mejor escenario
    print("\n" + "="*70)
    print(" MEJORES ESCENARIOS POR CRITERIO")
    print("="*70)
    
    criterios = [
        ('reduccion_nutrientes_pct', 'Reducción de Nutrientes'),
        ('reduccion_lemna_pct', 'Reducción de Lemna'),
        ('mejora_oxigeno_pct', 'Mejora de Oxígeno')
    ]
    
    for crit, nombre in criterios:
        mejor, valor = runner.mejor_escenario(crit)
        print(f"\n{nombre}:")
        print(f"  Escenario: {ESCENARIOS[mejor]['nombre']}")
        print(f"  Valor: {valor:+.2f}%")
    
    # Guardar resultados
    print("\n" + "="*70)
    runner.guardar_resultados()
    
    print("\n✓ Simulación completada exitosamente\n")
    
    return runner


if __name__ == "__main__":
    runner = main()