"""
Módulo de visualización para el modelo del Lago Titicaca.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class GraficadorTiticaca:
    """
    Clase para generar visualizaciones profesionales del modelo.
    """
    
    def __init__(self, runner):
        """
        Inicializa el graficador con resultados de simulación.
        
        Args:
            runner: Instancia de RunnerSimulacion con resultados
        """
        self.runner = runner
        self.resultados = runner.resultados
        
        # Configuración de estilo
        plt.style.use('seaborn-v0_8-darkgrid')
        self.figsize = (14, 10)
    
    def grafico_evolucion_temporal(self, guardar=False, archivo='evolucion_temporal.png'):
        """
        Genera gráfico de evolución temporal de todas las variables.
        
        Args:
            guardar (bool): Si True, guarda la figura
            archivo (str): Nombre del archivo
        """
        from config.escenarios import ESCENARIOS
        
        fig = plt.figure(figsize=self.figsize)
        gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        # Subgráficos
        ax1 = fig.add_subplot(gs[0, 0])  # Nutrientes
        ax2 = fig.add_subplot(gs[0, 1])  # Lemna
        ax3 = fig.add_subplot(gs[1, 0])  # Oxígeno
        ax4 = fig.add_subplot(gs[1, 1])  # Volumen
        
        # Graficar cada escenario
        for nombre, resultado in self.resultados.items():
            escenario = ESCENARIOS[nombre]
            tiempo = resultado['tiempo']
            color = escenario['color']
            label = escenario['nombre']
            
            ax1.plot(tiempo, resultado['nutrientes'], color=color, 
                    label=label, linewidth=2)
            ax2.plot(tiempo, resultado['lemna'], color=color, 
                    label=label, linewidth=2)
            ax3.plot(tiempo, resultado['oxigeno'], color=color, 
                    label=label, linewidth=2)
            ax4.plot(tiempo, resultado['volumen']/1e9, color=color, 
                    label=label, linewidth=2)
        
        # Configurar subgráficos
        ax1.set_title('Concentración de Nutrientes', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Tiempo (años)')
        ax1.set_ylabel('Nutrientes (mg/L)')
        ax1.legend(loc='best', fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        ax2.set_title('Biomasa de Lenteja de Agua', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Tiempo (años)')
        ax2.set_ylabel('Lemna (toneladas)')
        ax2.legend(loc='best', fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        ax3.set_title('Oxígeno Disuelto', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Tiempo (años)')
        ax3.set_ylabel('Oxígeno (mg/L)')
        ax3.axhline(y=6, color='red', linestyle='--', alpha=0.5, label='Crítico')
        ax3.legend(loc='best', fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        ax4.set_title('Volumen del Lago', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Tiempo (años)')
        ax4.set_ylabel('Volumen (km³)')
        ax4.legend(loc='best', fontsize=8)
        ax4.grid(True, alpha=0.3)
        
        fig.suptitle('Evolución Temporal del Lago Titicaca - Comparación de Escenarios', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        if guardar:
            plt.savefig(archivo, dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico guardado: {archivo}")
        
        plt.tight_layout()
        return fig
    
    def grafico_comparativo_final(self, guardar=False, archivo='comparativo_final.png'):
        """
        Genera gráfico de barras comparativo de estados finales.
        
        Args:
            guardar (bool): Si True, guarda la figura
            archivo (str): Nombre del archivo
        """
        from config.escenarios import ESCENARIOS
        
        metricas = self.runner.metricas
        
        # Preparar datos
        escenarios_nombres = [ESCENARIOS[k]['nombre'] for k in metricas.keys()]
        nutrientes_final = [v['nutrientes_final'] for v in metricas.values()]
        lemna_final = [v['lemna_final'] for v in metricas.values()]
        oxigeno_final = [v['oxigeno_final'] for v in metricas.values()]
        colores = [ESCENARIOS[k]['color'] for k in metricas.keys()]
        
        # Crear figura
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        # Gráfico 1: Nutrientes
        axes[0].bar(range(len(escenarios_nombres)), nutrientes_final, 
                   color=colores, alpha=0.7, edgecolor='black')
        axes[0].set_title('Nutrientes al Final de Simulación', 
                         fontsize=12, fontweight='bold')
        axes[0].set_ylabel('Concentración (mg/L)')
        axes[0].set_xticks(range(len(escenarios_nombres)))
        axes[0].set_xticklabels(escenarios_nombres, rotation=45, ha='right')
        axes[0].grid(axis='y', alpha=0.3)
        
        # Gráfico 2: Lemna
        axes[1].bar(range(len(escenarios_nombres)), lemna_final, 
                   color=colores, alpha=0.7, edgecolor='black')
        axes[1].set_title('Biomasa de Lemna al Final', 
                         fontsize=12, fontweight='bold')
        axes[1].set_ylabel('Biomasa (toneladas)')
        axes[1].set_xticks(range(len(escenarios_nombres)))
        axes[1].set_xticklabels(escenarios_nombres, rotation=45, ha='right')
        axes[1].grid(axis='y', alpha=0.3)
        
        # Gráfico 3: Oxígeno
        axes[2].bar(range(len(escenarios_nombres)), oxigeno_final, 
                   color=colores, alpha=0.7, edgecolor='black')
        axes[2].axhline(y=6, color='red', linestyle='--', linewidth=2, 
                       label='Nivel Crítico')
        axes[2].set_title('Oxígeno Disuelto al Final', 
                         fontsize=12, fontweight='bold')
        axes[2].set_ylabel('Concentración (mg/L)')
        axes[2].set_xticks(range(len(escenarios_nombres)))
        axes[2].set_xticklabels(escenarios_nombres, rotation=45, ha='right')
        axes[2].legend()
        axes[2].grid(axis='y', alpha=0.3)
        
        fig.suptitle('Comparación de Estados Finales por Escenario', 
                    fontsize=16, fontweight='bold')
        
        if guardar:
            plt.savefig(archivo, dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico guardado: {archivo}")
        
        plt.tight_layout()
        return fig
    
    def grafico_interactivo_plotly(self):
        """
        Genera gráfico interactivo con Plotly.
        
        Returns:
            go.Figure: Figura de Plotly
        """
        from config.escenarios import ESCENARIOS
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Nutrientes (mg/L)', 'Biomasa de Lemna (ton)',
                          'Oxígeno Disuelto (mg/L)', 'Volumen del Lago (km³)'),
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # Añadir trazas para cada escenario
        for nombre, resultado in self.resultados.items():
            escenario = ESCENARIOS[nombre]
            tiempo = resultado['tiempo']
            color = escenario['color']
            label = escenario['nombre']
            
            # Nutrientes
            fig.add_trace(
                go.Scatter(x=tiempo, y=resultado['nutrientes'], 
                          name=label, line=dict(color=color, width=2),
                          legendgroup=label, showlegend=True),
                row=1, col=1
            )
            
            # Lemna
            fig.add_trace(
                go.Scatter(x=tiempo, y=resultado['lemna'], 
                          name=label, line=dict(color=color, width=2),
                          legendgroup=label, showlegend=False),
                row=1, col=2
            )
            
            # Oxígeno
            fig.add_trace(
                go.Scatter(x=tiempo, y=resultado['oxigeno'], 
                          name=label, line=dict(color=color, width=2),
                          legendgroup=label, showlegend=False),
                row=2, col=1
            )
            
            # Volumen
            fig.add_trace(
                go.Scatter(x=tiempo, y=resultado['volumen']/1e9, 
                          name=label, line=dict(color=color, width=2),
                          legendgroup=label, showlegend=False),
                row=2, col=2
            )
        
        # Línea crítica de oxígeno
        tiempo_max = max([r['tiempo'][-1] for r in self.resultados.values()])
        fig.add_trace(
            go.Scatter(x=[0, tiempo_max], y=[6, 6],
                      name='Nivel Crítico O₂',
                      line=dict(color='red', dash='dash', width=2)),
            row=2, col=1
        )
        
        # Actualizar ejes
        fig.update_xaxes(title_text="Tiempo (años)", row=2, col=1)
        fig.update_xaxes(title_text="Tiempo (años)", row=2, col=2)
        
        # Layout
        fig.update_layout(
            title_text="Simulación del Lago Titicaca - Vista Interactiva",
            title_font_size=18,
            height=700,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, 
                       xanchor="center", x=0.5)
        )
        
        return fig
    
    def generar_todos_graficos(self, directorio='graficos'):
        """
        Genera y guarda todos los gráficos.
        
        Args:
            directorio (str): Directorio donde guardar los gráficos
        """
        import os
        
        os.makedirs(directorio, exist_ok=True)
        
        # print("\nGenerando gráficos...")
        
        # Gráfico de evolución temporal
        self.grafico_evolucion_temporal(guardar=True, 
                                       archivo=f'{directorio}/evolucion_temporal.png')
        
        # Gráfico comparativo final
        self.grafico_comparativo_final(guardar=True, 
                                       archivo=f'{directorio}/comparativo_final.png')
        
        # Gráfico interactivo (guardar como HTML)
        fig_plotly = self.grafico_interactivo_plotly()
        fig_plotly.write_html(f'{directorio}/dashboard_interactivo.html')
        # print(f"✓ Dashboard interactivo: {directorio}/dashboard_interactivo.html")
        
        # print(f"\nTodos los gráficos guardados en: {directorio}/")
        
        plt.close('all')