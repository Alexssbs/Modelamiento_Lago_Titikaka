"""
Dashboard interactivo con Streamlit para el Modelo del Lago Titicaca.
VERSIÓN FINAL - Lemna corregida + Todas las funciones originales
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.modelo import ModeloTiticaca
from config.parametros import obtener_parametros
from config.escenarios import (ESCENARIOS, crear_escenario_personalizado, obtener_descripcion_escenarios)
from simulation.runner import RunnerSimulacion
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import glob

def cargar_resultados_guardados():
    """Carga resultados previamente guardados."""
    try:
        df_comparativa = pd.read_csv('resultados/comparativa_escenarios.csv')
        series = {}
        for archivo in glob.glob('resultados/serie_*.csv'):
            var = archivo.split('_')[1].split('.')[0]
            series[var] = pd.read_csv(archivo)
        return df_comparativa, series
    except FileNotFoundError:
        return None, None

# Configuración de página
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

# Sidebar
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
    st.subheader("Tabla Comparativa")
    st.dataframe(st.session_state.df_comparativa, use_container_width=True)
    st.subheader("Series Temporales Guardadas")

# Cache de resultados - INICIALIZACIÓN COMPLETA
if 'resultados_cache' not in st.session_state:
    st.session_state.resultados_cache = {}
if 'modelo_actual' not in st.session_state:
    st.session_state.modelo_actual = None
if 'metricas_cache' not in st.session_state:
    st.session_state.metricas_cache = None
if 'escenario_actual' not in st.session_state:
    st.session_state.escenario_actual = None
if 'params_actual' not in st.session_state:
    st.session_state.params_actual = None
if 'lemna_agregada_total' not in st.session_state:
    st.session_state.lemna_agregada_total = 0.0
if 'metricas_todas_cache' not in st.session_state:
    st.session_state.metricas_todas_cache = {}


def crear_nuevo_modelo(parametros, escenario):
    """Crea un NUEVO modelo - para Ejecutar Simulación o Reiniciar."""
    modelo = ModeloTiticaca(parametros, escenario)
    resultado = modelo.simular()
    metricas = modelo.obtener_metricas()
    st.session_state.modelo_actual = modelo
    return resultado, metricas


def simular_modelo_existente():
    """Simula usando el modelo EXISTENTE - para Añadir/Remover Lemna."""
    if st.session_state.modelo_actual is None:
        raise ValueError("No hay modelo actual")
    resultado = st.session_state.modelo_actual.simular()
    metricas = st.session_state.modelo_actual.obtener_metricas()
    return resultado, metricas


def crear_grafico_variable(resultados_dict, variable, titulo, ylabel, mostrar_critico=False):
    """Crea gráfico de plotly para una variable."""
    fig = go.Figure()
    for nombre, datos in resultados_dict.items():
        fig.add_trace(go.Scatter(
            x=datos['tiempo'], y=datos[variable], name=nombre,
            mode='lines', line=dict(width=3)
        ))
    if mostrar_critico and variable == 'oxigeno':
        fig.add_hline(y=6, line_dash="dash", line_color="red",
                    annotation_text="Nivel Crítico")
    fig.update_layout(
        title=titulo, xaxis_title="Tiempo (años)",
        yaxis_title=ylabel, height=400, hovermode='x unified'
    )
    return fig


def actualizar_resultados_cache(nombre_escenario, resultado, metricas):
    """Función auxiliar para actualizar el cache."""
    st.session_state.resultados_cache[nombre_escenario] = resultado
    st.session_state.metricas_cache = metricas


# ================================
# MODO 1: ESCENARIOS PREDEFINIDOS
# ================================
if modo == "Escenarios Predefinidos":
    st.sidebar.subheader("Selección de Escenario")
    
    descripciones = obtener_descripcion_escenarios()
    opciones = [f"{v['nombre_completo']}" for v in descripciones.values()]
    nombres_tecnicos = list(descripciones.keys())
    
    seleccion = st.sidebar.selectbox("Escenario:", opciones)
    idx = opciones.index(seleccion)
    nombre_escenario = nombres_tecnicos[idx]
    
    escenario = ESCENARIOS[nombre_escenario]
    
    st.sidebar.info(f"**Descripción:** {escenario['descripcion']}")
    st.sidebar.metric("Eficiencia Puno", f"{escenario['eficiencia_tratamiento_puno']*100:.0f}%")
    st.sidebar.metric("Eficiencia Juliaca", f"{escenario['eficiencia_tratamiento_juliaca']*100:.0f}%")
    st.sidebar.metric("Remoción Lemna", f"{escenario['remocion_mecanica_lemna']} ton/año")
    
    # ✅ RESTAURADO: 0 a 100 años
    tiempo_sim = st.sidebar.slider("Tiempo de simulación (años)", 0, 100, 20)
    
    if st.sidebar.button("🚀 Ejecutar Simulación", type="primary"):
        with st.spinner("Simulando..."):
            params = obtener_parametros({'tiempo_simulacion': tiempo_sim})
            
            # ✅ Si hay lemna agregada, incluirla
            if st.session_state.lemna_agregada_total > 0:
                params['lemna_inicial'] = params.get('lemna_inicial', 300) + st.session_state.lemna_agregada_total
            
            resultado, metricas = crear_nuevo_modelo(params, escenario)
            actualizar_resultados_cache(escenario['nombre'], resultado, metricas)
            st.session_state.escenario_actual = escenario
            st.session_state.params_actual = params
    
    # ------------------------------
    # 🌿 CONTROLES DE LEMNA
    # ------------------------------
    if st.session_state.resultados_cache and st.session_state.modelo_actual:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🌿 Control Manual de Lemna")
        
        try:
            lemna_actual = st.session_state.modelo_actual.obtener_lemna_actual()
            pct_absorcion = st.session_state.modelo_actual.porcentaje_absorcion_lemna()
            
            if pct_absorcion < 50:
                emoji, estado = "🟢", "Baja"
            elif pct_absorcion < 80:
                emoji, estado = "🟡", "Media"
            else:
                emoji, estado = "🔴", "Alta"
            
            st.sidebar.info(f"{emoji} **Lemna Actual:** {lemna_actual:.0f} ton\n\n**Densidad:** {pct_absorcion:.1f}% ({estado})")
            
            if st.session_state.lemna_agregada_total > 0:
                st.sidebar.caption(f"📊 Lemna agregada manualmente: {st.session_state.lemna_agregada_total:.0f} ton")
            
        except Exception as e:
            st.sidebar.error(f"Error al leer Lemna: {e}")
        
        # Botón remover (reset completo)
        if st.sidebar.button("🧹 Remover Toda la Lemna", use_container_width=True):
            try:
                st.session_state.lemna_agregada_total = 0.0
                
                # Usar función del modelo que mantiene nutrientes y resetea oxígeno
                st.session_state.modelo_actual.remover_lemna_total()
                
                resultado_nuevo, metricas_nuevo = simular_modelo_existente()
                nombre_esc = st.session_state.escenario_actual['nombre']
                actualizar_resultados_cache(nombre_esc, resultado_nuevo, metricas_nuevo)
                st.sidebar.success("✅ Lemna removida - Nutrientes mantenidos")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
        
        # ✅ NUEVO: Botón para nuevo escenario (mantiene nutrientes, permite probar otra estrategia)
        if st.sidebar.button("🔄 Remover Lemna (Nuevo Escenario)", use_container_width=True):
            try:
                st.session_state.lemna_agregada_total = 0.0
                
                # Guardar nutrientes actuales
                nutrientes_guardados = st.session_state.modelo_actual.remover_lemna_para_escenario()
                
                resultado_nuevo, metricas_nuevo = simular_modelo_existente()
                nombre_esc = st.session_state.escenario_actual['nombre']
                actualizar_resultados_cache(nombre_esc, resultado_nuevo, metricas_nuevo)
                
                st.sidebar.success(f"✅ Lemna removida\n📊 Nutrientes: {nutrientes_guardados:.4f} mg/L\n🔄 Listo para nuevo escenario")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
        
        # Añadir Lemna
        st.sidebar.markdown("**Añadir Biomasa:**")
        cantidad_agregar = st.sidebar.number_input(
            "Cantidad (ton)", min_value=0.0, max_value=10000.0,
            value=0.0, step=100.0, key="cantidad_lemna_pred"
        )
        
        if st.sidebar.button("➕ Añadir Lemna al Sistema", use_container_width=True) and cantidad_agregar > 0:
            try:
                # ✅ CORREGIDO: Agregar al contador y resetear estado
                st.session_state.lemna_agregada_total += cantidad_agregar
                
                params = st.session_state.params_actual
                lemna_base = params.get('lemna_inicial', 300)
                
                # Si lemna_inicial ya incluye agregadas anteriores, usar base original
                if 'lemna_inicial_original' not in st.session_state:
                    st.session_state.lemna_inicial_original = 300
                
                nueva_lemna = st.session_state.lemna_inicial_original + st.session_state.lemna_agregada_total
                
                st.session_state.modelo_actual.estado_actual = np.array([
                    params.get('volumen_inicial', 8.93e11),
                    params.get('nutrientes_inicial', 0.028),
                    nueva_lemna,
                    params.get('oxigeno_inicial', 8.0)
                ])
                
                resultado_nuevo, metricas_nuevo = simular_modelo_existente()
                nombre_esc = st.session_state.escenario_actual['nombre']
                actualizar_resultados_cache(nombre_esc, resultado_nuevo, metricas_nuevo)
                
                st.sidebar.success(f"✅ Añadidas {cantidad_agregar:.0f} ton de Lemna")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
        
        # Reiniciar
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Reiniciar Simulación", use_container_width=True):
            st.session_state.lemna_agregada_total = 0.0
            if 'lemna_inicial_original' in st.session_state:
                del st.session_state.lemna_inicial_original
            
            with st.spinner("Reiniciando..."):
                params = obtener_parametros({'tiempo_simulacion': tiempo_sim})
                resultado_limpio, metricas_limpio = crear_nuevo_modelo(params, escenario)
                actualizar_resultados_cache(escenario['nombre'], resultado_limpio, metricas_limpio)
                st.session_state.params_actual = params
            st.sidebar.success("✅ Simulación reiniciada")
            st.rerun()

    # ------------------------------
    # MOSTRAR RESULTADOS
    # ------------------------------
    if st.session_state.resultados_cache and st.session_state.metricas_cache:
        st.success("✅ Simulación completada")
        
        metricas = st.session_state.metricas_cache
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Reducción de Nutrientes",
                      f"{metricas['reduccion_nutrientes_pct']:.1f}%",
                      delta=f"{metricas['nutrientes_final']:.4f} mg/L",
                      delta_color="inverse")
        with col2:
            st.metric("Biomasa Lemna Final",
                      f"{metricas['lemna_final']:.0f} ton",
                      delta=f"{metricas['reduccion_lemna_pct']:+.1f}%")
        with col3:
            st.metric("Mejora de Oxígeno",
                      f"{metricas['mejora_oxigeno_pct']:.1f}%",
                      delta=f"{metricas['oxigeno_final']:.2f} mg/L")

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'nutrientes',
                'Concentración de Nutrientes', 'Nutrientes (mg/L)'), use_container_width=True)
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'lemna',
                'Biomasa de Lenteja de Agua', 'Lemna (ton)'), use_container_width=True)

        with col2:
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'oxigeno',
                'Oxígeno Disuelto', 'mg/L', mostrar_critico=True), use_container_width=True)
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'volumen',
                'Volumen del Lago', 'm³'), use_container_width=True)


# ================================
# MODO 2: ESCENARIO PERSONALIZADO
# ================================
elif modo == "Escenario Personalizado":
    st.sidebar.subheader("Configuración Personalizada")
    
    eff_puno = st.sidebar.slider("Eficiencia Tratamiento Puno (%)", 0, 100, 50, 5) / 100
    eff_juliaca = st.sidebar.slider("Eficiencia Tratamiento Juliaca (%)", 0, 100, 50, 5) / 100
    remocion = st.sidebar.slider("Remoción Mecánica Lemna (ton/año)", 0, 2000, 0, 100)
    
    st.sidebar.markdown("---")
    tiempo_sim = st.sidebar.slider("Tiempo de simulación (años)", 0, 100, 20)
    
    if st.sidebar.button("🚀 Ejecutar Simulación", type="primary"):
        with st.spinner("Simulando escenario personalizado..."):
            escenario = crear_escenario_personalizado("Personalizado", eff_puno, eff_juliaca, remocion)
            params = obtener_parametros({'tiempo_simulacion': tiempo_sim})
            
            if st.session_state.lemna_agregada_total > 0:
                params['lemna_inicial'] = params.get('lemna_inicial', 300) + st.session_state.lemna_agregada_total
            
            resultado, metricas = crear_nuevo_modelo(params, escenario)
            actualizar_resultados_cache("Escenario Personalizado", resultado, metricas)
            st.session_state.escenario_actual = escenario
            st.session_state.params_actual = params
    
    # Controles de Lemna
    if st.session_state.resultados_cache and st.session_state.modelo_actual:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🌿 Control Manual de Lemna")
        
        try:
            lemna_actual = st.session_state.modelo_actual.obtener_lemna_actual()
            pct_absorcion = st.session_state.modelo_actual.porcentaje_absorcion_lemna()
            
            if pct_absorcion < 50:
                emoji, estado = "🟢", "Baja"
            elif pct_absorcion < 80:
                emoji, estado = "🟡", "Media"
            else:
                emoji, estado = "🔴", "Alta"
            
            st.sidebar.info(f"{emoji} **Lemna Actual:** {lemna_actual:.0f} ton\n\n**Densidad:** {pct_absorcion:.1f}% ({estado})")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
        
        if st.sidebar.button("🧹 Remover Toda la Lemna", key="remover_pers", use_container_width=True):
            try:
                st.session_state.lemna_agregada_total = 0.0
                st.session_state.modelo_actual.remover_lemna_total()
                resultado_nuevo, metricas_nuevo = simular_modelo_existente()
                actualizar_resultados_cache("Escenario Personalizado", resultado_nuevo, metricas_nuevo)
                st.sidebar.success("✅ Lemna removida - Nutrientes mantenidos")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
        
        # Botón nuevo escenario
        if st.sidebar.button("🔄 Remover Lemna (Nuevo Escenario)", key="nuevo_esc_pers", use_container_width=True):
            try:
                st.session_state.lemna_agregada_total = 0.0
                nutrientes_guardados = st.session_state.modelo_actual.remover_lemna_para_escenario()
                resultado_nuevo, metricas_nuevo = simular_modelo_existente()
                actualizar_resultados_cache("Escenario Personalizado", resultado_nuevo, metricas_nuevo)
                st.sidebar.success(f"✅ Nutrientes: {nutrientes_guardados:.4f} mg/L")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
        
        st.sidebar.markdown("**Añadir Biomasa:**")
        cantidad_agregar = st.sidebar.number_input(
            "Cantidad (ton)", min_value=0.0, max_value=10000.0,
            value=0.0, step=100.0, key="cantidad_lemna_pers"
        )
        
        if st.sidebar.button("➕ Añadir Lemna al Sistema", key="agregar_pers", use_container_width=True) and cantidad_agregar > 0:
            try:
                st.session_state.lemna_agregada_total += cantidad_agregar
                
                params = st.session_state.params_actual
                if 'lemna_inicial_original' not in st.session_state:
                    st.session_state.lemna_inicial_original = 300
                
                nueva_lemna = st.session_state.lemna_inicial_original + st.session_state.lemna_agregada_total
                
                st.session_state.modelo_actual.estado_actual = np.array([
                    params.get('volumen_inicial', 8.93e11),
                    params.get('nutrientes_inicial', 0.028),
                    nueva_lemna,
                    params.get('oxigeno_inicial', 8.0)
                ])
                
                resultado_nuevo, metricas_nuevo = simular_modelo_existente()
                actualizar_resultados_cache("Escenario Personalizado", resultado_nuevo, metricas_nuevo)
                st.sidebar.success(f"✅ Añadidas {cantidad_agregar:.0f} ton")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
        
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Reiniciar Simulación", key="reset_pers", use_container_width=True):
            st.session_state.lemna_agregada_total = 0.0
            with st.spinner("Reiniciando..."):
                escenario = crear_escenario_personalizado("Personalizado", eff_puno, eff_juliaca, remocion)
                params = obtener_parametros({'tiempo_simulacion': tiempo_sim})
                resultado_limpio, metricas_limpio = crear_nuevo_modelo(params, escenario)
                actualizar_resultados_cache("Escenario Personalizado", resultado_limpio, metricas_limpio)
            st.sidebar.success("✅ Reiniciado")
            st.rerun()
    
    # Mostrar resultados
    if st.session_state.resultados_cache and st.session_state.metricas_cache:
        st.success("✅ Simulación completada")
        
        col1, col2, col3 = st.columns(3)
        metricas = st.session_state.metricas_cache
        
        with col1:
            st.metric("Reducción de Nutrientes", f"{metricas['reduccion_nutrientes_pct']:.1f}%",
                      delta=f"{metricas['nutrientes_final']:.4f} mg/L", delta_color="inverse")
        with col2:
            st.metric("Biomasa Lemna Final", f"{metricas['lemna_final']:.0f} ton",
                      delta=f"{metricas['reduccion_lemna_pct']:+.1f}%")
        with col3:
            st.metric("Mejora de Oxígeno", f"{metricas['mejora_oxigeno_pct']:.1f}%",
                      delta=f"{metricas['oxigeno_final']:.2f} mg/L")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'nutrientes',
                'Concentración de Nutrientes', 'Nutrientes (mg/L)'), use_container_width=True)
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'lemna',
                'Biomasa de Lemna', 'Lemna (toneladas)'), use_container_width=True)
        
        with col2:
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'oxigeno',
                'Oxígeno Disuelto', 'Oxígeno (mg/L)', mostrar_critico=True), use_container_width=True)
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'volumen',
                'Volumen del Lago', 'Volumen (m³)'), use_container_width=True)


# ================================
# MODO 3: COMPARACIÓN MÚLTIPLE
# ================================
elif modo == "Comparación Múltiple":
    st.sidebar.subheader("Selección de Escenarios")
    
    escenarios_disponibles = list(ESCENARIOS.keys())
    escenarios_nombres = [ESCENARIOS[e]['nombre'] for e in escenarios_disponibles]
    
    seleccionados = st.sidebar.multiselect(
        "Escenarios a comparar:",
        escenarios_nombres,
        default=escenarios_nombres[:3]
    )
    
    tiempo_sim = st.sidebar.slider("Tiempo de simulación (años)", 0, 100, 20)
    
    if st.sidebar.button("🚀 Ejecutar Comparación", type="primary"):
        if not seleccionados:
            st.warning("⚠️ Seleccione al menos un escenario")
        else:
            with st.spinner(f"Simulando {len(seleccionados)} escenarios..."):
                params = obtener_parametros({'tiempo_simulacion': tiempo_sim})
                resultados = {}
                metricas_todas = {}
                
                for nombre_mostrar in seleccionados:
                    idx = escenarios_nombres.index(nombre_mostrar)
                    nombre_tecnico = escenarios_disponibles[idx]
                    escenario = ESCENARIOS[nombre_tecnico]
                    
                    modelo = ModeloTiticaca(params, escenario)
                    resultado = modelo.simular()
                    metricas = modelo.obtener_metricas()
                    
                    resultados[escenario['nombre']] = resultado
                    metricas_todas[escenario['nombre']] = metricas
                
                st.session_state.resultados_cache = resultados
                st.session_state.metricas_todas_cache = metricas_todas
    
    # Mostrar comparación
    if st.session_state.resultados_cache and st.session_state.metricas_todas_cache:
        st.success(f"✅ Comparación completada: {len(st.session_state.resultados_cache)} escenarios")
        
        # Tabla comparativa
        st.subheader("📊 Tabla Comparativa de Resultados")
        
        tabla_datos = []
        for nombre, metricas in st.session_state.metricas_todas_cache.items():
            tabla_datos.append({
                'Escenario': nombre,
                'Nutrientes Final (mg/L)': f"{metricas['nutrientes_final']:.4f}",
                'Reducción Nutrientes (%)': f"{metricas['reduccion_nutrientes_pct']:.1f}",
                'Lemna Final (ton)': f"{metricas['lemna_final']:.0f}",
                'Cambio Lemna (%)': f"{-metricas['reduccion_lemna_pct']:.1f}",
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
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'nutrientes',
                'Nutrientes', 'mg/L'), use_container_width=True)
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'lemna',
                'Biomasa de Lemna', 'toneladas'), use_container_width=True)
        
        with col2:
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'oxigeno',
                'Oxígeno Disuelto', 'mg/L', mostrar_critico=True), use_container_width=True)
            st.plotly_chart(crear_grafico_variable(
                st.session_state.resultados_cache, 'volumen',
                'Volumen del Lago', 'm³'), use_container_width=True)


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🌊 <strong>Modelo de Dinámica de Sistemas para la Gestión del Lago Titicaca</strong></p>
    <p>Desarrollado para la evaluación de políticas ambientales</p>
    <p><strong>VERSIÓN FINAL</strong> ✅</p>
    <p><em>Control de Lemna corregido | Todas las funciones restauradas</em></p>
</div>
""", unsafe_allow_html=True)