"""
Modelo de dinámica de sistemas para la gestión del Lago Titicaca.
VERSIÓN CORREGIDA - Comportamiento REAL de Lemna:
1. Al 100% o 0 ton: NO absorbe nutrientes
2. Al 100%: Oxígeno BAJA
3. Remoción: Mantiene nutrientes, oxígeno vuelve a inicial
"""

import numpy as np
from scipy.integrate import solve_ivp


class ModeloTiticaca:
    def __init__(self, parametros, escenario):
        self.params = parametros.copy() if parametros else {}
        self.escenario = escenario.copy() if escenario else {}
        
        if 'parametros' in self.escenario and self.escenario['parametros']:
            self.params.update(self.escenario['parametros'])

        self.params.setdefault('limite_absorcion_lemna',
                               self.params.get('capacidad_carga_lemna', 2000))

        lemna_inicial = max(float(self.params.get('lemna_inicial', 1.0)), 1.0)

        self.estado_inicial = np.array([
            float(self.params.get('volumen_inicial', 1e9)),
            float(self.params.get('nutrientes_inicial', 0.0)),
            lemna_inicial,
            float(self.params.get('oxigeno_inicial', 8.0))
        ], dtype=float)
        
        self.estado_actual = self.estado_inicial.copy()
        
        # Guardar oxígeno inicial para restaurar
        self.oxigeno_base = float(self.params.get('oxigeno_inicial', 8.0))
        
        self.params.setdefault('tasa_absorcion_nutrientes_lemna', 1e-8)
        self.params.setdefault('km_absorcion_lemna', 0.02)
        self.params.setdefault('tasa_sedimentacion_nutrientes', 0.02)
        self.params.setdefault('tasa_reoxigenacion', 1.0)
        self.params.setdefault('consumo_o2_lemna', 0.001)
        self.params.setdefault('consumo_o2_descomposicion', 0.02)
        
        # Umbral de saturación (95% = 0.95)
        self.UMBRAL_SATURACION = 0.95

        self.resultado = None

    def flujo_entrada_agua(self, volumen):
        precipitacion = self.params.get('area_lago', 0.0) * self.params.get('precipitacion_anual', 0.0)
        rios = self.params.get('flujo_rios', 0.0)
        return precipitacion + rios

    def flujo_salida_agua(self, volumen):
        evaporacion = self.params.get('area_lago', 0.0) * self.params.get('evaporacion_anual', 0.0)
        extraccion = self.params.get('extraccion_humana', 0.0)
        return evaporacion + extraccion

    def descarga_contaminantes(self):
        eff_puno = self.escenario.get('eficiencia_tratamiento_puno', 0.0)
        eff_juliaca = self.escenario.get('eficiencia_tratamiento_juliaca', 0.0)
        descarga_puno = float(self.params.get('descarga_puno', 0.0)) * (1.0 - eff_puno)
        descarga_juliaca = float(self.params.get('descarga_juliaca', 0.0)) * (1.0 - eff_juliaca)
        descarga_otras = float(self.params.get('descarga_otras', 0.0))
        return max(0.0, descarga_puno + descarga_juliaca + descarga_otras)

    def calcular_porcentaje_capacidad(self, lemna_ton):
        """Calcula qué porcentaje de la capacidad máxima ocupa la lemna."""
        capacidad = float(self.params.get('capacidad_carga_lemna', 2000.0))
        if capacidad <= 0:
            return 0.0
        return lemna_ton / capacidad  # 0.0 a 1.0+

    def crecimiento_lemna(self, nutrientes_mgL, lemna_ton):
        if lemna_ton <= 0:
            return 0.0
        
        Km = float(self.params.get('nutrientes_optimo_lemna', 0.05))
        factor_nutrientes = nutrientes_mgL / (nutrientes_mgL + Km)
        
        K = max(float(self.params.get('capacidad_carga_lemna', 2000.0)), 1.0)
        factor_capacidad = max(0.0, 1.0 - (lemna_ton / K))
        
        tasa_crecimiento = float(self.params.get('tasa_crecimiento_lemna', 0.3))
        tasa_mortalidad_base = float(self.params.get('tasa_mortalidad_lemna', 0.2))
        tasa_mortalidad = tasa_mortalidad_base * (1 - factor_nutrientes)
        
        crecimiento_neto = lemna_ton * (tasa_crecimiento * factor_nutrientes * factor_capacidad - tasa_mortalidad)
        return max(crecimiento_neto, -lemna_ton)

    def consumo_nutrientes_lemna(self, nutrientes_mgL, lemna_ton, volumen_m3):
        """
        ★★★ REGLA 1: NO absorbe nutrientes si lemna = 0 o lemna >= 95% capacidad ★★★
        """
        # SIN LEMNA = SIN ABSORCIÓN
        if lemna_ton <= 1.0:
            return 0.0
        
        if nutrientes_mgL <= 0 or volumen_m3 <= 0:
            return 0.0
        
        # Calcular porcentaje de capacidad
        pct = self.calcular_porcentaje_capacidad(lemna_ton)
        
        # ★★★ AL 95% O MÁS = NO ABSORBE NUTRIENTES ★★★
        if pct >= self.UMBRAL_SATURACION:
            return 0.0
        
        # Absorción normal (solo si está entre 0% y 95%)
        tasa_abs = float(self.params.get('tasa_absorcion_nutrientes_lemna', 1e-6))
        Km = float(self.params.get('km_absorcion_lemna', 0.02))
        factor_saturacion = nutrientes_mgL / (nutrientes_mgL + Km)
        
        # Factor de eficiencia basado en densidad
        # Máxima eficiencia al 50%, decrece hacia 0% y hacia 95%
        if pct < 0.5:
            factor_eficiencia = pct * 2.0  # 0 a 1
        else:
            factor_eficiencia = (self.UMBRAL_SATURACION - pct) / (self.UMBRAL_SATURACION - 0.5)  # 1 a 0
        
        factor_eficiencia = max(0.0, min(1.0, factor_eficiencia))
        
        absorcion_ton = tasa_abs * lemna_ton * factor_saturacion * factor_eficiencia
        absorcion_mg = absorcion_ton * 1e9
        volumen_L = volumen_m3 * 1000.0
        consumo = absorcion_mg / volumen_L
        
        return max(0.0, min(consumo, nutrientes_mgL * 0.1))

    def dinamica_oxigeno(self, oxigeno_mgL, lemna_ton, nutrientes_mgL):
        """
        ★★★ REGLA 2: Oxígeno BAJA cuando lemna >= 95% capacidad ★★★
        - Antes del 95%: Lemna MEJORA oxígeno (fotosíntesis)
        - Al 95% o más: Lemna REDUCE oxígeno (tapa superficie)
        """
        O2_sat = float(self.params.get('oxigeno_saturacion', 8.5))
        tasa_reox = float(self.params.get('tasa_reoxigenacion', 1.0))
        
        pct = self.calcular_porcentaje_capacidad(lemna_ton)
        
        # Reoxigenación natural del agua
        reox_natural = tasa_reox * (O2_sat - oxigeno_mgL)
        
        if pct < self.UMBRAL_SATURACION:
            # ★ ANTES DEL 95%: Lemna MEJORA el oxígeno ★
            # Fotosíntesis produce oxígeno
            produccion_o2 = 0.05 * lemna_ton * (pct / self.UMBRAL_SATURACION)
            
            # Consumo mínimo
            consumo_respiracion = 0.001 * lemna_ton
            
            dO_dt = reox_natural + produccion_o2 - consumo_respiracion
        else:
            # ★★★ AL 95% O MÁS: Lemna REDUCE el oxígeno ★★★
            # La lemna tapa la superficie, bloquea intercambio de gases
            
            # Reducir drásticamente la reoxigenación (la superficie está tapada)
            factor_bloqueo = min((pct - self.UMBRAL_SATURACION) / 0.05, 1.0)  # 0 a 1 entre 95% y 100%
            reox_reducida = reox_natural * (1.0 - factor_bloqueo * 0.9)  # Reduce hasta 90%
            
            # Consumo alto por respiración de tanta biomasa
            consumo_alto = 0.01 * lemna_ton
            
            # Sin fotosíntesis efectiva (demasiado densa, se auto-sombrea)
            produccion_o2 = 0.0
            
            dO_dt = reox_reducida + produccion_o2 - consumo_alto
        
        # Consumo por descomposición de materia orgánica
        consumo_descomp = float(self.params.get('consumo_o2_descomposicion', 0.02)) * nutrientes_mgL
        
        return dO_dt - consumo_descomp

    def ecuaciones(self, t, y):
        volumen_m3, nutrientes_mgL, lemna_ton, oxigeno_mgL = y
        volumen_m3 = max(volumen_m3, 1.0)
        nutrientes_mgL = max(nutrientes_mgL, 0.0)
        lemna_ton = max(lemna_ton, 0.0)
        oxigeno_mgL = max(oxigeno_mgL, 0.0)

        # Volumen
        dV_dt = self.flujo_entrada_agua(volumen_m3) - self.flujo_salida_agua(volumen_m3)
        
        # Nutrientes
        carga_mass = self.descarga_contaminantes()
        carga_conc = (carga_mass * 1e6) / volumen_m3
        
        # ★ Consumo de nutrientes (0 si lemna=0 o lemna>=95%)
        consumo_lemna = self.consumo_nutrientes_lemna(nutrientes_mgL, lemna_ton, volumen_m3)
        
        sedimentacion = float(self.params.get('tasa_sedimentacion_nutrientes', 0.02)) * nutrientes_mgL
        dilucion = -nutrientes_mgL * (dV_dt / volumen_m3) if volumen_m3 > 0 else 0.0
        
        dN_dt = carga_conc - consumo_lemna - sedimentacion + dilucion
        
        # Lemna
        dL_dt = self.crecimiento_lemna(nutrientes_mgL, lemna_ton)
        
        remocion = max(0.0, self.escenario.get('remocion_mecanica_lemna', 0.0))
        if remocion > 0.0:
            dL_dt -= min(remocion, max(lemna_ton + dL_dt, 0.0))

        # ★ Oxígeno (mejora antes del 95%, BAJA después)
        dO_dt = self.dinamica_oxigeno(oxigeno_mgL, lemna_ton, nutrientes_mgL)

        return np.array([dV_dt, dN_dt, dL_dt, dO_dt], dtype=float)

    def simular(self):
        t_final = float(self.params.get('tiempo_simulacion', 20.0))
        paso = float(self.params.get('paso_tiempo', 0.1))

        if t_final <= 0.0:
            self.resultado = {
                'tiempo': np.array([0.0]),
                'volumen': np.array([self.estado_actual[0]]),
                'nutrientes': np.array([self.estado_actual[1]]),
                'lemna': np.array([self.estado_actual[2]]),
                'oxigeno': np.array([self.estado_actual[3]]),
                'escenario': self.escenario.get('nombre', 'default'),
                'exito': True
            }
            return self.resultado

        num_pasos = int(t_final / paso) + 1
        t_eval = np.linspace(0.0, t_final, num_pasos)

        solucion = solve_ivp(
            fun=self.ecuaciones,
            t_span=(0.0, t_final),
            y0=self.estado_actual.astype(float),
            method='RK45',
            t_eval=t_eval,
            rtol=1e-6,
            atol=1e-9
        )

        if not solucion.success:
            raise RuntimeError(f"Error: {solucion.message}")

        self.resultado = {
            'tiempo': solucion.t,
            'volumen': solucion.y[0],
            'nutrientes': solucion.y[1],
            'lemna': solucion.y[2],
            'oxigeno': solucion.y[3],
            'escenario': self.escenario.get('nombre', 'default'),
            'exito': True
        }

        self.estado_actual = solucion.y[:, -1].copy()
        return self.resultado

    def obtener_metricas(self):
        if self.resultado is None:
            raise ValueError("Ejecute simular() primero")

        inicial = {
            'nutrientes': float(self.resultado['nutrientes'][0]),
            'lemna': float(self.resultado['lemna'][0]),
            'oxigeno': float(self.resultado['oxigeno'][0])
        }
        final = {
            'nutrientes': float(self.resultado['nutrientes'][-1]),
            'lemna': float(self.resultado['lemna'][-1]),
            'oxigeno': float(self.resultado['oxigeno'][-1])
        }

        capacidad = float(self.params.get('capacidad_carga_lemna', 2000.0))
        pct_capacidad = (final['lemna'] / capacidad) * 100.0 if capacidad > 0 else 0.0

        return {
            'reduccion_nutrientes_pct': ((inicial['nutrientes'] - final['nutrientes']) / inicial['nutrientes'] * 100.0) if inicial['nutrientes'] != 0 else 0.0,
            'reduccion_lemna_pct': ((inicial['lemna'] - final['lemna']) / inicial['lemna'] * 100.0) if inicial['lemna'] != 0 else 0.0,
            'mejora_oxigeno_pct': ((final['oxigeno'] - inicial['oxigeno']) / inicial['oxigeno'] * 100.0) if inicial['oxigeno'] != 0 else 0.0,
            'nutrientes_final': final['nutrientes'],
            'lemna_final': final['lemna'],
            'oxigeno_final': final['oxigeno'],
            'tiempo_simulacion': self.params.get('tiempo_simulacion', 20.0),
            'nutrientes_inicial': inicial['nutrientes'],
            'lemna_inicial': inicial['lemna'],
            'oxigeno_inicial': inicial['oxigeno'],
            'porcentaje_capacidad_lemna': pct_capacidad,
        }

    def porcentaje_absorcion_lemna(self):
        limite = self.params.get('capacidad_carga_lemna', 2000.0)
        if limite <= 0:
            return 0.0
        return min((self.estado_actual[2] / limite) * 100.0, 100.0)

    def obtener_lemna_actual(self):
        return float(self.estado_actual[2])

    def remover_lemna_total(self):
        """
        ★★★ REGLA 3 y 4: Remueve lemna, MANTIENE nutrientes, oxígeno al inicial ★★★
        """
        # ★ GUARDAR nutrientes actuales
        nutrientes_actuales = float(self.estado_actual[1])
        volumen_actual = float(self.estado_actual[0])
        
        # Resetear lemna a casi 0
        self.estado_actual[2] = 1.0
        
        # ★ MANTENER nutrientes EXACTAMENTE igual
        self.estado_actual[1] = nutrientes_actuales
        
        # ★ Oxígeno vuelve al INICIAL (mejora = 0%)
        self.estado_actual[3] = self.oxigeno_base
        
        # Mantener volumen
        self.estado_actual[0] = volumen_actual
        
        return True

    def remover_lemna_para_escenario(self):
        """Para nuevo escenario: quita lemna, mantiene nutrientes, oxígeno inicial."""
        nutrientes_guardados = float(self.estado_actual[1])
        self.remover_lemna_total()
        return nutrientes_guardados

    def agregar_lemna(self, cantidad):
        try:
            cantidad = float(cantidad)
        except (ValueError, TypeError):
            return False
        if cantidad <= 0:
            return False
        self.estado_actual[2] += cantidad
        return True

    def resetear_estado(self):
        self.estado_actual = self.estado_inicial.copy()
        self.resultado = None

    def obtener_porcentaje_nutrientes_restantes(self):
        inicial = float(self.estado_inicial[1])
        final = float(self.estado_actual[1])
        if inicial == 0:
            return 0.0
        return (final / inicial) * 100.0