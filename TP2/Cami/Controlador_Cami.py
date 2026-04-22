import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
# Importamos tus clases originales desde el archivo base
from planta import PenduloPlanta, Simulador

class ControladorFuzzy:
    def __init__(self):
        # Centros de los conjuntos de salida (Fuerza)
        self.fuerza_centros = {
            'NG': -55, 'NM': -30, 'NP': -12, 
            'Z': 0, 
            'PP': 12, 'PM': 30, 'PG': 55
        }

    # --- FUNCIONES DE MEMBRESÍA ---
    def trimf(self, x, a, b, c):
        """Función de membresía Triangular"""
        return max(0, min((x - a) / (b - a + 1e-9), (c - x) / (c - b + 1e-9)))

    def trapmf(self, x, a, b, c, d):
        """Función de membresía Trapezoidal"""
        return max(0, min((x - a) / (b - a + 1e-9), 1, (d - x) / (d - c + 1e-9)))

    def fuzzificar_angulo(self, theta_deg):
        return {
            'NG': self.trapmf(theta_deg, -160, -155, -110, -100),
            'NM': self.trimf(theta_deg, -75, -44, -15),
            'NP': self.trimf(theta_deg, -20, -10, -1),
            'Z':  self.trimf(theta_deg, -3, 0, 3),
            'PP': self.trimf(theta_deg, 1, 10, 20),
            'PM': self.trimf(theta_deg, 15, 44, 75),
            'PG': self.trapmf(theta_deg, 100, 110, 155, 160)
        }

    def fuzzificar_velocidad(self, vel_deg):
        return {
            'NR': self.trapmf(vel_deg, -500, -400, -110, -80),
            'NL': self.trimf(vel_deg, -100, -50, 5),
            'VZ': self.trimf(vel_deg, -10, 0, 10),
            'PL': self.trimf(vel_deg, -5, 50, 100),
            'PR': self.trapmf(vel_deg, 80, 110, 400, 500)
        }

    def obtener_fuerza_nitida(self, estado):
        x, _, theta_rad, theta_p_rad = estado
        t_deg = np.rad2deg(theta_rad)
        v_deg = np.rad2deg(theta_p_rad)

        mu_a = self.fuzzificar_angulo(t_deg)
        mu_v = self.fuzzificar_velocidad(v_deg)

        activaciones = []

        # --- BASE DE REGLAS (Ejemplos representativos) ---
        
        # 1. Reglas de Estabilidad (Ángulo + Velocidad en misma dirección = Acción Fuerte)
        # Si cae a la izq (PP/PM) y se mueve a la izq (PL/PR) -> Empuja fuerte Izq (PM/PG)
        p1 = min(mu_a['PP'], mu_v['PL']); activaciones.append((p1, self.fuerza_centros['PP']))
        p2 = min(mu_a['PM'], mu_v['PL']); activaciones.append((p2, self.fuerza_centros['PM']))
        p3 = min(mu_a['PM'], mu_v['PR']); activaciones.append((p3, self.fuerza_centros['PG']))
        
        # 2. Reglas de Amortiguación (Ángulo y Velocidad opuestos = Acción Nula/Leve)
        # Si está a la izq (PP) pero ya está volviendo (NL) -> No acelerar el regreso
        p4 = min(mu_a['PP'], mu_v['NL']); activaciones.append((p4, self.fuerza_centros['Z']))
        
        # 3. Reglas de Lado Derecho (Simétricas)
        p5 = min(mu_a['NP'], mu_v['NL']); activaciones.append((p5, self.fuerza_centros['NP']))
        p6 = min(mu_a['NM'], mu_v['NL']); activaciones.append((p6, self.fuerza_centros['NM']))
        p7 = min(mu_a['NM'], mu_v['NR']); activaciones.append((p7, self.fuerza_centros['NG']))
        p8 = min(mu_a['NP'], mu_v['PL']); activaciones.append((p8, self.fuerza_centros['Z']))

        # 4. Regla de Verticalidad (Cero)
        p9 = mu_a['Z']; activaciones.append((p9, self.fuerza_centros['Z']))
        
        # 5. Regla de Rescate (Grande)
        p10 = mu_a['PG']; activaciones.append((p10, self.fuerza_centros['PG']))
        p11 = mu_a['NG']; activaciones.append((p11, self.fuerza_centros['NG']))

        # --- DESFUZZIFICACIÓN (Promedio de Centros) ---
        numerador = sum(peso * centro for peso, centro in activaciones)
        denominador = sum(peso for peso, centro in activaciones)

        if denominador == 0: return 0
        return numerador / denominador

# --- INTEGRACIÓN CON TU PLANTA ---

def simular():
    planta = PenduloPlanta(M=2.0, m=0.2, l=0.5, dt=0.015)
    controlador = ControladorFuzzy()
    sim = Simulador(planta)
    
    loop_original = sim.loop

    def loop_controlado(frame):
        if not sim.agarrado:
            f = controlador.obtener_fuerza_nitida(planta.estado)
            # Solo aplicamos si la fuerza es significativa para no saturar
            if abs(f) > 0.1:
                planta.aplicar_patada(f)
        
        return loop_original(frame)

    ani = FuncAnimation(sim.fig, loop_controlado, interval=15, blit=False)
    plt.title("Control Difuso: Inferencia y Desfuzzificación por Centroide")
    plt.show()

if __name__ == "__main__":
    simular()