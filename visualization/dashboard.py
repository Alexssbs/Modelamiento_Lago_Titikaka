"""
Dashboard interactivo con Streamlit para el Modelo del Lago Titicaca.

Ejecutar con: streamlit run visualization/dashboard.py
"""

import streamlit as st
import sys
import os

# Añadir directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.modelo import ModeloTiticaca
from config.parametros import obtener_parametros
from config.escenarios import (ESCENARIOS, crear_escenario_personalizado, 
                               obtener_descripcion_escenarios)
from simulation.runner import RunnerSimulacion
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import glob

def cargar_resultados_guardados():
    """Carga resultados previamente guardados."""
    try:
        # Cargar tabla comparativa
        df_comparativa = pd.read_csv('resultados/comparativa_escenarios.csv')
        
        # Cargar series temporales
        series = {}
        for archivo in glob.glob('resultados/serie_*.csv'):
            var = archivo.split('_')[1].split('.')[0]
            series[var] = pd.read_csv(archivo)
        
        return df_comparativa, series
    except FileNotFoundError:
        return None, None

# Configuración de la página
st.set_page_config(
    page_title="Modelo Lago Titicaca",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Título principal
st.title("🌊 Modelo de Dinámica de Sistemas - Lago Titicaca")
st.markdown("### Sistema de Simulación para Gestión de Calidad del Agua")
st.markdown("---")


# Sidebar - Controles
st.sidebar.header("⚙️ Configuración de Simulación")

# Selector de modo
modo = st.sidebar.radio(
    "Modo de Simulación",
    ["Escenarios Predefinidos", "Escenario Personalizado", "Comparación Múltiple"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Resultados Guardados")

if st.sidebar.button("🔄 Cargar Resultados Existentes"):
    df_comparativa, series = cargar_resultados_guardados()
    if df_comparativa is not None:
        st.session_state.df_comparativa = df_comparativa
        st.session_state.series_temporales = series
        st.sidebar.success("✅ Resultados cargados exitosamente")
    else:
        st.sidebar.error("❌ No se encontraron resultados guardados")

if 'df_comparativa' in st.session_state:
    st.header("📊 Resultados Guardados")
    
    # Mostrar tabla comparativa
    st.subheader("Tabla Comparativa")
    st.dataframe(st.session_state.df_comparativa, use_container_width=True)
    
    # Mostrar gráficos de series temporales
    st.subheader("Series Temporales Guardadas")

# Variables para almacenar resultados
if 'resultados_cache' not in st.session_state:
    st.session_state.resultados_cache = {}

def cargar_resultados_guardados():
    """Carga resultados previamente guardados."""
    try:
        # Cargar tabla comparativa
        df_comparativa = pd.read_csv('resultados/comparativa_escenarios.csv')
        
        # Cargar series temporales
        series = {}
        for archivo in glob.glob('resultados/serie_*.csv'):
            var = archivo.split('_')[1].split('.')[0]
            series[var] = pd.read_csv(archivo)
        
        return df_comparativa, series
    except FileNotFoundError:
        return None, None

def simular_modelo(parametros, escenario):
    """Simula el modelo y devuelve resultados."""
    modelo = ModeloTiticaca(parametros, escenario)
    resultado = modelo.simular()
    metricas = modelo.obtener_metricas()
    return resultado, metricas


def crear_grafico_variable(resultados_dict, variable, titulo, ylabel, mostrar_critico=False):
    """Crea gráfico para una variable específica."""
    fig = go.Figure()
    
    for nombre, datos in resultados_dict.items():
        fig.add_trace(go.Scatter(
            x=datos['tiempo'],
            y=datos[variable],
            name=nombre,
            mode='lines',
            line=dict(width=3)
        ))
    
    if mostrar_critico and variable == 'oxigeno':
        fig.add_hline(y=6, line_dash="dash", line_color="red", 
                     annotation_text="Nivel Crítico")
    
    fig.update_layout(
        title=titulo,
        xaxis_title="Tiempo (años)",
        yaxis_title=ylabel,
        hovermode='x unified',
        height=400
    )
    
    return fig


# MODO 1: Escenarios Predefinidos
if modo == "Escenarios Predefinidos":
    st.sidebar.subheader("Selección de Escenario")
    
    descripciones = obtener_descripcion_escenarios()
    opciones = [f"{v['nombre_completo']}" for v in descripciones.values()]
    nombres_tecnicos = list(descripciones.keys())
    
    seleccion = st.sidebar.selectbox("Escenario:", opciones)
    idx = opciones.index(seleccion)
    nombre_escenario = nombres_tecnicos[idx]
    
    escenario = ESCENARIOS[nombre_escenario]
    
    # Mostrar información del escenario
    st.sidebar.info(f"**Descripción:** {escenario['descripcion']}")
    st.sidebar.metric("Eficiencia Puno", f"{escenario['eficiencia_tratamiento_puno']*100:.0f}%")
    st.sidebar.metric("Eficiencia Juliaca", f"{escenario['eficiencia_tratamiento_juliaca']*100:.0f}%")
    st.sidebar.metric("Remoción Lemna", f"{escenario['remocion_mecanica_lemna']} ton/año")
    
    # Parámetros de simulación
    st.sidebar.markdown("---")
    st.sidebar.subheader("Parámetros de Simulación")
    tiempo_sim = st.sidebar.slider("Tiempo de simulación (años)", 5, 50, 20)
    
    # Botón de simulación
    if st.sidebar.button("🚀 Ejecutar Simulación", type="primary"):
        with st.spinner("Simulando..."):
            params = obtener_parametros({'tiempo_simulacion': tiempo_sim})
            resultado, metricas = simular_modelo(params, escenario)
            
            st.session_state.resultados_cache = {
                escenario['nombre']: resultado
            }
            st.session_state.metricas_cache = metricas
    
    # Mostrar resultados
    if st.session_state.resultados_cache:
        st.success("✅ Simulación completada")
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        metricas = st.session_state.metricas_cache
        
        with col1:
            st.metric(
                "Reducción de Nutrientes",
                f"{metricas['reduccion_nutrientes_pct']:.1f}%",
                delta=f"{metricas['nutrientes_final']:.1f} mg/L final"
            )
        
        with col2:
            st.metric(
                "Reducción de Lemna",
                f"{metricas['reduccion_lemna_pct']:.1f}%",
                delta=f"{metricas['lemna_final']:.0f} ton final"
            )
        
        with col3:
            st.metric(
                "Mejora de Oxígeno",
                f"{metricas['mejora_oxigeno_pct']:.1f}%",
                delta=f"{metricas['oxigeno_final']:.2f} mg/L final"
            )
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = crear_grafico_variable(
                st.session_state.resultados_cache,
                'nutrientes',
                'Concentración de Nutrientes',
                'Nutrientes (mg/L)'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            fig2 = crear_grafico_variable(
                st.session_state.resultados_cache,
                'lemna',
                'Biomasa de Lenteja de Agua',
                'Lemna (toneladas)'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            fig3 = crear_grafico_variable(
                st.session_state.resultados_cache,
                'oxigeno',
                'Oxígeno Disuelto',
                'Oxígeno (mg/L)',
                mostrar_critico=True
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            fig4 = crear_grafico_variable(
                st.session_state.resultados_cache,
                'volumen',
                'Volumen del Lago',
                'Volumen (m³)'
            )
            st.plotly_chart(fig4, use_container_width=True)


# MODO 2: Escenario Personalizado
elif modo == "Escenario Personalizado":
    st.sidebar.subheader("Configuración Personalizada")
    
    eff_puno = st.sidebar.slider(
        "Eficiencia Tratamiento Puno (%)",
        0, 100, 50, 5
    ) / 100
    
    eff_juliaca = st.sidebar.slider(
        "Eficiencia Tratamiento Juliaca (%)",
        0, 100, 50, 5
    ) / 100
    
    remocion = st.sidebar.slider(
        "Remoción Mecánica Lemna (ton/año)",
        0, 2000, 0, 100
    )
    
    st.sidebar.markdown("---")
    tiempo_sim = st.sidebar.slider("Tiempo de simulación (años)", 5, 50, 20)
    
    # Botón de simulación
    if st.sidebar.button("🚀 Ejecutar Simulación", type="primary"):
        with st.spinner("Simulando escenario personalizado..."):
            escenario = crear_escenario_personalizado(
                "Personalizado",
                eff_puno,
                eff_juliaca,
                remocion
            )
            
            params = obtener_parametros({'tiempo_simulacion': tiempo_sim})
            resultado, metricas = simular_modelo(params, escenario)
            
            st.session_state.resultados_cache = {
                "Escenario Personalizado": resultado
            }
            st.session_state.metricas_cache = metricas
    
    # Mostrar resultados (similar al modo 1)
    if st.session_state.resultados_cache:
        st.success("✅ Simulación completada")
        
        col1, col2, col3 = st.columns(3)
        metricas = st.session_state.metricas_cache
        
        with col1:
            st.metric(
                "Reducción de Nutrientes",
                f"{metricas['reduccion_nutrientes_pct']:.1f}%",
                delta=f"{metricas['nutrientes_final']:.1f} mg/L"
            )
        
        with col2:
            st.metric(
                "Reducción de Lemna",
                f"{metricas['reduccion_lemna_pct']:.1f}%",
                delta=f"{metricas['lemna_final']:.0f} ton"
            )
        
        with col3:
            st.metric(
                "Mejora de Oxígeno",
                f"{metricas['mejora_oxigeno_pct']:.1f}%",
                delta=f"{metricas['oxigeno_final']:.2f} mg/L"
            )
        
        st.markdown("---")
        
        # Gráficos en 2x2
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = crear_grafico_variable(
                st.session_state.resultados_cache, 'nutrientes',
                'Concentración de Nutrientes', 'Nutrientes (mg/L)'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            fig2 = crear_grafico_variable(
                st.session_state.resultados_cache, 'lemna',
                'Biomasa de Lemna', 'Lemna (toneladas)'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            fig3 = crear_grafico_variable(
                st.session_state.resultados_cache, 'oxigeno',
                'Oxígeno Disuelto', 'Oxígeno (mg/L)', mostrar_critico=True
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            fig4 = crear_grafico_variable(
                st.session_state.resultados_cache, 'volumen',
                'Volumen del Lago', 'Volumen (m³)'
            )
            st.plotly_chart(fig4, use_container_width=True)


# MODO 3: Comparación Múltiple
elif modo == "Comparación Múltiple":
    st.sidebar.subheader("Selección de Escenarios")
    
    escenarios_disponibles = list(ESCENARIOS.keys())
    escenarios_nombres = [ESCENARIOS[e]['nombre'] for e in escenarios_disponibles]
    
    seleccionados = st.sidebar.multiselect(
        "Escenarios a comparar:",
        escenarios_nombres,
        default=escenarios_nombres[:3]
    )
    
    tiempo_sim = st.sidebar.slider("Tiempo de simulación (años)", 5, 50, 20)
    
    if st.sidebar.button("🚀 Ejecutar Comparación", type="primary"):
        if not seleccionados:
            st.warning("Seleccione al menos un escenario")
        else:
            with st.spinner(f"Simulando {len(seleccionados)} escenarios..."):
                params = obtener_parametros({'tiempo_simulacion': tiempo_sim})
                resultados = {}
                metricas_todas = {}
                
                for nombre_mostrar in seleccionados:
                    idx = escenarios_nombres.index(nombre_mostrar)
                    nombre_tecnico = escenarios_disponibles[idx]
                    escenario = ESCENARIOS[nombre_tecnico]
                    
                    resultado, metricas = simular_modelo(params, escenario)
                    resultados[escenario['nombre']] = resultado
                    metricas_todas[escenario['nombre']] = metricas
                
                st.session_state.resultados_cache = resultados
                st.session_state.metricas_todas_cache = metricas_todas
    
    # Mostrar comparación
    if st.session_state.resultados_cache:
        st.success(f"✅ Comparación completada: {len(st.session_state.resultados_cache)} escenarios")
        
        # Tabla comparativa
        st.subheader("📊 Tabla Comparativa de Resultados")
        
        tabla_datos = []
        for nombre, metricas in st.session_state.metricas_todas_cache.items():
            tabla_datos.append({
                'Escenario': nombre,
                'Nutrientes Final (mg/L)': f"{metricas['nutrientes_final']:.2f}",
                'Reducción Nutrientes (%)': f"{metricas['reduccion_nutrientes_pct']:.1f}",
                'Lemna Final (ton)': f"{metricas['lemna_final']:.0f}",
                'Reducción Lemna (%)': f"{metricas['reduccion_lemna_pct']:.1f}",
                'Oxígeno Final (mg/L)': f"{metricas['oxigeno_final']:.2f}",
                'Mejora Oxígeno (%)': f"{metricas['mejora_oxigeno_pct']:.1f}"
            })
        
        df_tabla = pd.DataFrame(tabla_datos)
        st.dataframe(df_tabla, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Gráficos comparativos
        st.subheader("📈 Evolución Temporal Comparativa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = crear_grafico_variable(
                st.session_state.resultados_cache, 'nutrientes',
                'Nutrientes', 'mg/L'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            fig2 = crear_grafico_variable(
                st.session_state.resultados_cache, 'lemna',
                'Biomasa de Lemna', 'toneladas'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            fig3 = crear_grafico_variable(
                st.session_state.resultados_cache, 'oxigeno',
                'Oxígeno Disuelto', 'mg/L', mostrar_critico=True
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            fig4 = crear_grafico_variable(
                st.session_state.resultados_cache, 'volumen',
                'Volumen del Lago', 'm³'
            )
            st.plotly_chart(fig4, use_container_width=True)


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Modelo de Dinámica de Sistemas para la Gestión del Lago Titicaca</p>
    <p>Desarrollado para la evaluación de políticas ambientales</p>
</div>
""", unsafe_allow_html=True)