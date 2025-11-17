"""
Modelo de dinámica de sistemas para la gestión del Lago Titicaca.
"""

import numpy as np
from scipy.integrate import solve_ivp


class ModeloTiticaca:
    """
    Modelo de simulación de dinámica de sistemas para el Lago Titicaca.
    
    Este modelo simula la evolución de cuatro variables principales:
    1. Volumen de agua
    2. Concentración de nutrientes
    3. Biomasa de lenteja de agua (Lemna)
    4. Oxígeno disuelto
    """
    
    def __init__(self, parametros, escenario):
        """
        Inicializa el modelo con parámetros y escenario.
        
        Args:
            parametros (dict): Parámetros del modelo
            escenario (dict): Configuración del escenario
        """
        self.params = parametros.copy()
        self.escenario = escenario.copy()
        
        # Aplicar parámetros específicos del escenario
        if 'parametros' in escenario and escenario['parametros']:
            self.params.update(escenario['parametros'])
        
        # Estado inicial [volumen, nutrientes, lemna, oxigeno]
        self.estado_inicial = np.array([
            self.params['volumen_inicial'],
            self.params['nutrientes_inicial'],
            self.params['lemna_inicial'],
            self.params['oxigeno_inicial']
        ])
        
        self.resultado = None
    
    def flujo_entrada_agua(self, volumen):
        """Calcula flujo de entrada de agua (precipitación + ríos)."""
        precipitacion = self.params['area_lago'] * self.params['precipitacion_anual']
        rios = self.params['flujo_rios']
        return precipitacion + rios
    
    def flujo_salida_agua(self, volumen):
        """Calcula flujo de salida de agua (evaporación + extracción)."""
        evaporacion = self.params['area_lago'] * self.params['evaporacion_anual']
        extraccion = self.params['extraccion_humana']
        return evaporacion + extraccion
    
    def descarga_contaminantes(self):
        """
        Calcula descarga efectiva de nutrientes considerando tratamiento.
        
        Returns:
            float: Descarga neta de nutrientes en ton/año
        """
        # Eficiencias de tratamiento del escenario
        eff_puno = self.escenario.get('eficiencia_tratamiento_puno', 0)
        eff_juliaca = self.escenario.get('eficiencia_tratamiento_juliaca', 0)
        
        # Descarga de cada fuente con tratamiento
        descarga_puno = self.params['descarga_puno'] * (1 - eff_puno)
        descarga_juliaca = self.params['descarga_juliaca'] * (1 - eff_juliaca)
        descarga_otras = self.params['descarga_otras']
        
        return descarga_puno + descarga_juliaca + descarga_otras
    
    def crecimiento_lemna(self, nutrientes, lemna):
        """
        Calcula tasa de crecimiento de Lemna (modelo logístico con limitación por nutrientes).
        
        Args:
            nutrientes (float): Concentración de nutrientes (mg/L)
            lemna (float): Biomasa actual de Lemna (toneladas)
            
        Returns:
            float: Tasa de crecimiento neta de Lemna (ton/año)
        """
        # Factor de limitación por nutrientes (función de Monod)
        factor_nutrientes = nutrientes / (nutrientes + self.params['nutrientes_optimo_lemna'])
        
        # Factor de capacidad de carga (logístico)
        K = self.params['capacidad_carga_lemna']
        factor_capacidad = max(0, 1 - lemna / K)
        
        # Crecimiento
        tasa_crecimiento = (self.params['tasa_crecimiento_lemna'] * 
                           factor_nutrientes * factor_capacidad)
        
        # Mortalidad natural
        tasa_mortalidad = self.params['tasa_mortalidad_lemna']
        
        # Remoción mecánica (intervención humana)
        remocion = self.escenario.get('remocion_mecanica_lemna', 0)
        
        # Tasa neta
        crecimiento_neto = lemna * (tasa_crecimiento - tasa_mortalidad)
        
        return crecimiento_neto - remocion
    
    def consumo_nutrientes_lemna(self, nutrientes, lemna):
        """Calcula consumo de nutrientes por crecimiento de Lemna."""
        if lemna <= 0 or nutrientes <= 0:
            return 0
        
        # Crecimiento positivo consume nutrientes
        crecimiento = max(0, self.crecimiento_lemna(nutrientes, lemna))
        consumo = crecimiento * self.params['coef_nutrientes_lemna']
        
        return min(consumo, nutrientes * 0.1)  # Máximo 10% por paso
    
    def dinamica_oxigeno(self, oxigeno, lemna, nutrientes):
        """
        Calcula cambio neto de oxígeno disuelto.
        
        Args:
            oxigeno (float): Concentración actual de O₂ (mg/L)
            lemna (float): Biomasa de Lemna (toneladas)
            nutrientes (float): Concentración de nutrientes (mg/L)
            
        Returns:
            float: Cambio neto de oxígeno (mg/L por año)
        """
        # Reoxigenación atmosférica
        O2_sat = self.params['oxigeno_saturacion']
        reoxigenacion = self.params['tasa_reoxigenacion'] * (O2_sat - oxigeno)
        
        # Consumo por Lemna (respiración nocturna)
        consumo_lemna = self.params['consumo_o2_lemna'] * lemna
        
        # Consumo por descomposición de materia orgánica
        consumo_descomp = self.params['consumo_o2_descomposicion'] * nutrientes
        
        return reoxigenacion - consumo_lemna - consumo_descomp
    
    def ecuaciones(self, t, y):
        """
        Sistema de ecuaciones diferenciales del modelo.
        
        Args:
            t (float): Tiempo actual
            y (array): Estado actual [volumen, nutrientes, lemna, oxigeno]
            
        Returns:
            array: Derivadas [dV/dt, dN/dt, dL/dt, dO/dt]
        """
        volumen, nutrientes, lemna, oxigeno = y
        
        # Asegurar valores no negativos
        volumen = max(volumen, 1e9)
        nutrientes = max(nutrientes, 0)
        lemna = max(lemna, 0)
        oxigeno = max(oxigeno, 0)
        
        # 1. VOLUMEN DE AGUA
        entrada_agua = self.flujo_entrada_agua(volumen)
        salida_agua = self.flujo_salida_agua(volumen)
        dV_dt = entrada_agua - salida_agua
        
        # 2. NUTRIENTES
        # Carga de contaminantes (convertir ton/año a mg/L considerando volumen)
        carga_nutrientes = (self.descarga_contaminantes() * 1e9) / volumen  # mg/L por año
        
        # Consumo por Lemna
        consumo_nutrientes = self.consumo_nutrientes_lemna(nutrientes, lemna)
        
        # Sedimentación natural
        sedimentacion = self.params['tasa_sedimentacion_nutrientes'] * nutrientes
        
        # Dilución por cambio de volumen
        dilucion_volumen = -nutrientes * (dV_dt / volumen) if volumen > 0 else 0
        
        dN_dt = carga_nutrientes - consumo_nutrientes - sedimentacion + dilucion_volumen
        
        # 3. BIOMASA DE LEMNA
        dL_dt = self.crecimiento_lemna(nutrientes, lemna)
        
        # 4. OXÍGENO DISUELTO
        dO_dt = self.dinamica_oxigeno(oxigeno, lemna, nutrientes)
        
        return np.array([dV_dt, dN_dt, dL_dt, dO_dt])
    
    def simular(self):
        """
        Ejecuta la simulación del modelo.
        
        Returns:
            dict: Resultados de la simulación
        """
        t_final = self.params['tiempo_simulacion']
        t_eval = np.arange(0, t_final + self.params['paso_tiempo'], 
                          self.params['paso_tiempo'])
        
        # Resolver sistema de ecuaciones diferenciales
        solucion = solve_ivp(
            fun=self.ecuaciones,
            t_span=(0, t_final),
            y0=self.estado_inicial,
            method='RK45',
            t_eval=t_eval,
            rtol=1e-6,
            atol=1e-9
        )
        
        if not solucion.success:
            raise RuntimeError(f"Error en la simulación: {solucion.message}")
        
        # Organizar resultados
        self.resultado = {
            'tiempo': solucion.t,
            'volumen': solucion.y[0],
            'nutrientes': solucion.y[1],
            'lemna': solucion.y[2],
            'oxigeno': solucion.y[3],
            'escenario': self.escenario['nombre'],
            'exito': solucion.success
        }
        
        return self.resultado
    
    def obtener_metricas(self):
        """
        Calcula métricas de impacto del escenario.
        
        Returns:
            dict: Métricas calculadas
        """
        if self.resultado is None:
            raise ValueError("Debe ejecutar simular() primero")
        
        # Valores iniciales y finales
        inicial = {
            'nutrientes': self.resultado['nutrientes'][0],
            'lemna': self.resultado['lemna'][0],
            'oxigeno': self.resultado['oxigeno'][0]
        }
        
        final = {
            'nutrientes': self.resultado['nutrientes'][-1],
            'lemna': self.resultado['lemna'][-1],
            'oxigeno': self.resultado['oxigeno'][-1]
        }
        
        # Calcular cambios porcentuales
        metricas = {
            'reduccion_nutrientes_pct': ((inicial['nutrientes'] - final['nutrientes']) / 
                                        inicial['nutrientes'] * 100),
            'reduccion_lemna_pct': ((inicial['lemna'] - final['lemna']) / 
                                   inicial['lemna'] * 100),
            'mejora_oxigeno_pct': ((final['oxigeno'] - inicial['oxigeno']) / 
                                  inicial['oxigeno'] * 100),
            'nutrientes_final': final['nutrientes'],
            'lemna_final': final['lemna'],
            'oxigeno_final': final['oxigeno'],
            'tiempo_simulacion': self.params['tiempo_simulacion']
        }
        
        return metricas