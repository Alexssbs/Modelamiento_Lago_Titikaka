"""
Modelo de dinámica de sistemas para la gestión del Lago Titicaca.
"""

import numpy as np
from scipy.integrate import solve_ivp


class ModeloTiticaca:
    """
    Modelo de simulación de dinámica de sistemas para el Lago Titicaca.
    
    Variables principales:
    1. Volumen de agua
    2. Concentración de nutrientes
    3. Biomasa de lenteja de agua (Lemna)
    4. Oxígeno disuelto
    """
    
    def __init__(self, parametros, escenario):
        """
        Inicializa el modelo con parámetros y escenario.
        """
        self.params = parametros.copy()
        self.escenario = escenario.copy()
        
        if 'parametros' in escenario and escenario['parametros']:
            self.params.update(escenario['parametros'])
        
        # Inicializar Lemna con valor positivo para consumo de nutrientes
        lemna_inicial = max(self.params['lemna_inicial'], 1.0)
        
        self.estado_inicial = np.array([
            self.params['volumen_inicial'],
            self.params['nutrientes_inicial'],
            lemna_inicial,
            self.params['oxigeno_inicial']
        ])
        
        self.resultado = None
    
    def flujo_entrada_agua(self, volumen):
        precipitacion = self.params['area_lago'] * self.params['precipitacion_anual']
        rios = self.params['flujo_rios']
        return precipitacion + rios
    
    def flujo_salida_agua(self, volumen):
        evaporacion = self.params['area_lago'] * self.params['evaporacion_anual']
        extraccion = self.params['extraccion_humana']
        return evaporacion + extraccion
    
    def descarga_contaminantes(self):
        eff_puno = self.escenario.get('eficiencia_tratamiento_puno', 0)
        eff_juliaca = self.escenario.get('eficiencia_tratamiento_juliaca', 0)
        
        descarga_puno = self.params['descarga_puno'] * (1 - eff_puno)
        descarga_juliaca = self.params['descarga_juliaca'] * (1 - eff_juliaca)
        descarga_otras = self.params.get('descarga_otras', 0)  # permitir cero
        
        return descarga_puno + descarga_juliaca + descarga_otras
    
    def crecimiento_lemna(self, nutrientes, lemna):
        """
        Calcula tasa de crecimiento de Lemna según nutrientes y capacidad de carga.
        """
        factor_nutrientes = nutrientes / (nutrientes + self.params['nutrientes_optimo_lemna'])
        K = self.params['capacidad_carga_lemna']
        factor_capacidad = max(0, 1 - lemna / K)
        
        tasa_crecimiento = self.params['tasa_crecimiento_lemna'] * factor_nutrientes * factor_capacidad
        tasa_mortalidad = self.params['tasa_mortalidad_lemna']
        
        crecimiento_neto = lemna * (tasa_crecimiento - tasa_mortalidad)
        
        # Remoción mecánica
        remocion = self.escenario.get('remocion_mecanica_lemna', 0)
        crecimiento_neto_final = crecimiento_neto - min(remocion, lemna + crecimiento_neto)
        
        # Limitar a no eliminar más Lemna de la disponible
        return max(crecimiento_neto_final, -lemna)
    
    def consumo_nutrientes_lemna(self, nutrientes, lemna):
        """
        Nutrientes consumidos por crecimiento de Lemna.
        """
        if lemna <= 0 or nutrientes <= 0:
            return 0
        crecimiento = max(0, self.crecimiento_lemna(nutrientes, lemna))
        consumo = crecimiento * self.params['coef_nutrientes_lemna']
        return min(consumo, nutrientes)  # puede consumir hasta los nutrientes disponibles
    
    def dinamica_oxigeno(self, oxigeno, lemna, nutrientes):
        """
        Cambio neto de oxígeno disuelto.
        """
        O2_sat = self.params['oxigeno_saturacion']
        reoxigenacion = self.params['tasa_reoxigenacion'] * (O2_sat - oxigeno)
        consumo_lemna = self.params['consumo_o2_lemna'] * lemna
        consumo_descomp = self.params['consumo_o2_descomposicion'] * nutrientes
        return reoxigenacion - consumo_lemna - consumo_descomp
    
    def ecuaciones(self, t, y):
        volumen, nutrientes, lemna, oxigeno = y
        
        volumen = max(volumen, 1e9)
        nutrientes = max(nutrientes, 0)
        lemna = max(lemna, 0)
        oxigeno = max(oxigeno, 0)
        
        dV_dt = self.flujo_entrada_agua(volumen) - self.flujo_salida_agua(volumen)
        carga_nutrientes = (self.descarga_contaminantes() * 1e9) / volumen
        consumo_nutrientes = self.consumo_nutrientes_lemna(nutrientes, lemna)
        sedimentacion = self.params['tasa_sedimentacion_nutrientes'] * nutrientes
        dilucion_volumen = -nutrientes * (dV_dt / volumen) if volumen > 0 else 0
        dN_dt = carga_nutrientes - consumo_nutrientes - sedimentacion + dilucion_volumen
        
        dL_dt = self.crecimiento_lemna(nutrientes, lemna)
        dO_dt = self.dinamica_oxigeno(oxigeno, lemna, nutrientes)
        
        return np.array([dV_dt, dN_dt, dL_dt, dO_dt])
    
    def simular(self):
        t_final = self.params['tiempo_simulacion']
        t_eval = np.arange(0, t_final + self.params['paso_tiempo'], self.params['paso_tiempo'])
        
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
        if self.resultado is None:
            raise ValueError("Debe ejecutar simular() primero")
        
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
        
        metricas = {
            'reduccion_nutrientes_pct': ((inicial['nutrientes'] - final['nutrientes']) / inicial['nutrientes'] * 100)
                                        if inicial['nutrientes'] != 0 else 0,
            'reduccion_lemna_pct': ((inicial['lemna'] - final['lemna']) / inicial['lemna'] * 100)
                                   if inicial['lemna'] != 0 else 0,
            'mejora_oxigeno_pct': ((final['oxigeno'] - inicial['oxigeno']) / inicial['oxigeno'] * 100)
                                  if inicial['oxigeno'] != 0 else 0,
            'nutrientes_final': final['nutrientes'],
            'lemna_final': final['lemna'],
            'oxigeno_final': final['oxigeno'],
            'tiempo_simulacion': self.params['tiempo_simulacion']
        }
        
        return metricas
