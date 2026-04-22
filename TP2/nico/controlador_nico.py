import numpy as np
import matplotlib.pyplot as plt

class ControladorDifuso:
    def __init__(self):
        # --- 1. CONFIGURACIÓN DEL BALANCE (LOGICA DIFUSA) ---
        # Cobertura analítica con solapamiento del 50%
        self.sets_theta = {
            'NG': [-4.0, -4.0, -1.57, -0.6],
            'NM': [-1.57, -0.6, -0.3],
            'NP': [-0.6, -0.3, 0.0],
            'CE': [-0.2, 0.0, 0.2],
            'PP': [0.0, 0.3, 0.6],
            'PM': [0.3, 0.6, 1.57],
            'PG': [0.6, 1.57, 4.0, 4.0]
        }
        
        self.sets_omega = {
            'NG': [-20.0, -20.0, -2.0, -1.0],
            'NP': [-2.0, -1.0, 0.0],
            'CE': [-1.0, 0.0, 1.0],
            'PP': [0.0, 1.0, 2.0],
            'PG': [1.0, 2.0, 20.0, 20.0]
        }

        # Niveles de fuerza para Sugeno (N)
        self.F_levels = {
            'FM-': -100.0, 
            'FD-': -50.0,  
            'CE': 0.0, 
            'FD+': 50.0, 
            'FM+': 100.0
        }

        # Matriz de reglas pura
        self.reglas = {
            'NG': {'NG':'FM-', 'NP':'FM-', 'CE':'FM-', 'PP':'FM-', 'PG':'FM-'},
            'NM': {'NG':'FM-', 'NP':'FM-', 'CE':'FM-', 'PP':'FM-', 'PG':'FM-'},
            'NP': {'NG':'FM-', 'NP':'FD-', 'CE':'FD-', 'PP':'CE',   'PG':'FD+'},
            'CE': {'NG':'FM-', 'NP':'FD-', 'CE':'CE',   'PP':'FD+', 'PG':'FM+'},
            'PP': {'NG':'FD-', 'NP':'CE',   'CE':'FD+', 'PP':'FM+', 'PG':'FM+'},
            'PM': {'NG':'FM+', 'NP':'FM+', 'CE':'FM+', 'PP':'FM+', 'PG':'FM+'},
            'PG': {'NG':'FM+', 'NP':'FM+', 'CE':'FM+', 'PP':'FM+', 'PG':'FM+'}
        }

        # --- 2. CONFIGURACIÓN DEL SWING-UP (ENERGÍA) ---
        self.umbral_captura = np.deg2rad(70)  # A los 70° el difuso toma el control
        self.k_swing = -6                  # Ganancia de inyección de energía
        self.k_centrado = 2                # Resorte virtual para el carro
        self.k_amortiguacion = 1.5           # Amortiguador virtual para el carro

    def _mu(self, x, p):
        """Función de pertenencia analítica pura."""
        eps = 1e-9
        if len(p) == 3: # Triangular
            return max(0, min((x - p[0]) / (p[1] - p[0] + eps), (p[2] - x) / (p[2] - p[1] + eps)))
        else: # Trapezoidal
            return max(0, min((x - p[0]) / (p[1] - p[0] + eps), 1, (p[3] - x) / (p[3] - p[2] + eps)))

    def evaluar_balance(self, theta, omega):
        """Inferencia de Sugeno para el equilibrio superior."""
        t_in = np.clip(theta, -1.57, 1.57)
        m_t = {k: self._mu(t_in, v) for k, v in self.sets_theta.items()}
        m_w = {k: self._mu(omega, v) for k, v in self.sets_omega.items()}
        
        num, den = 0.0, 0.0
        for t_lab, mu_t in m_t.items():
            if mu_t == 0: continue
            for w_lab, mu_w in m_w.items():
                w = mu_t * mu_w
                if w == 0: continue
                num += w * self.F_levels[self.reglas[t_lab][w_lab]]
                den += w
        return num / den if den > 0 else 0.0

    def evaluar(self, theta, omega, x_pos, x_vel):
        """
        Lógica de control unificada:
        Detecta si el péndulo está en la zona de captura o si debe balancearse.
        """
        
        # 1. MODO BALANCE (Difuso activo en el cono superior)
        if abs(theta) < self.umbral_captura:
            return self.evaluar_balance(theta, omega)
        
        # 2. MODO SWING-UP (Inyección de energía por debajo del umbral)
        else:
            # Ley de control basada en energía:
            # La fuerza es proporcional a la velocidad angular para 'empujar' hacia arriba
            fuerza_swing = self.k_swing * omega * np.cos(theta)
            
            # Control de posición del carro para evitar que se escape de la pantalla
            fuerza_centrado = -self.k_centrado * x_pos - self.k_amortiguacion * x_vel
            
            # Limitamos la fuerza de swing-up para que sea rítmica y no caótica
            return np.clip(fuerza_swing + fuerza_centrado, -70, 70)

def graficar_superficie():
    ctrl = ControladorDifuso()
    res = 100
    th = np.linspace(-1.57, 1.57, res)
    om = np.linspace(-4.0, 4.0, res)
    Z = np.array([[ctrl.evaluar_balance(t, o) for t in th] for o in om])
    
    plt.figure(figsize=(10, 7))
    plt.pcolormesh(np.rad2deg(th), om, Z, cmap='coolwarm', shading='gouraud')
    plt.colorbar(label='Fuerza Sugeno (N)')
    plt.title("Superficie de Control: Modo Balance (±40°)")
    plt.xlabel("Ángulo θ (grados)"); plt.ylabel("Velocidad ω (rad/s)")
    plt.show()

if __name__ == "__main__":
    graficar_superficie()