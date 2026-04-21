import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation

# --- CLASE PLANTA ---

def normalizar_angulo(theta): # Asegura que el ángulo esté siempre entre -180 y 180 grados
    return (theta + 180.0) % 360.0 - 180.0


class PenduloPlanta:
    """Modelo físico de un péndulo invertido sobre un carro, con fricción y fuerza de control externa."""
    def __init__(self, M=1.0, m=0.3, l=0.5, g=9.81, dt=0.015, b=0.05, d=0.05):
        # Parámetros físicos y de simulación
        self.M, self.m, self.l, self.g, self.dt = M, m, l, g, dt
        self.b, self.d = b, d
        self.estado = np.array([0.0, 0.0, 0.0, 0.0])  #[x, x_p, theta_deg, theta_p_deg_s]
        self.f_imp = 0.0
        self.f_actual = 0.0
        self.d_imp = 0

    def aplicar_patada(self, mag): # Aplica una fuerza de impulso instantánea al sistema, que se mantiene durante un número limitado de actualizaciones
        self.f_imp = mag # Establece la fuerza a aplicar medida en Newtons
        self.d_imp = 5 #Número de actualizaciones durante las cuales se aplicará la fuerza de impulso

    def calcular_fisica(self, F_ext):  #Calcula las aceleraciones lineal y angular
        x, x_p, theta_deg, theta_p_deg = self.estado
        theta = np.deg2rad(theta_deg) #Convierte el ángulo de grados a radianes 
        theta_p = np.deg2rad(theta_p_deg) #Convierte la velocidad angular de grados/s a radianes/s
        st, ct = np.sin(theta), np.cos(theta) 
        #Calcula el seno y coseno del ángulo para simplificar las fórmulas de la dinámica
        F_neta = F_ext - (self.d * x_p) 
        #Calcula la fuerza neta aplicada al carro, restando la fuerza de fricción proporcional a la velocidad del carro
        temp = (-F_neta - self.m * self.l * (theta_p**2) * st) / (self.M + self.m) 
        #Calcula un término temporal que representa la contribución de la fuerza neta y la fuerza centrífuga del péndulo
        num_theta = (self.g * st) + (ct * temp) - (self.b * theta_p / (self.m * self.l)) 
        #Calcula el numerador para la aceleración angular del péndulo, que incluye la contribución de la gravedad, la fuerza neta y la fricción angular
        den_theta = self.l * (4/3 - (self.m * ct**2) / (self.M + self.m)) 
        #Calcula el denominador para la aceleración angular del péndulo, que depende de la longitud del péndulo y la relación entre las masas
        theta_pp = num_theta / den_theta
        x_pp = (F_neta + self.m * self.l * (theta_pp * ct - (theta_p**2) * st)) / (self.M + self.m) 
        #Calcula la aceleración lineal del carro, que depende de la fuerza neta y la contribución de la aceleración angular del péndulo
        return x_pp, np.rad2deg(theta_pp) 
        # Devuelve la aceleración lineal del carro y la aceleración angular del péndulo convertida a grados/s^2

    def actualizar(self): #Actualiza el estado del sistema en cada paso de tiempo
        F = self.f_imp if self.d_imp > 0 else 0.0
        self.f_actual = F 
        #Actualiza la fuerza actual que se está aplicando al sistema, que es la fuerza de impulso si aún está activa, o cero si ya ha terminado
        if self.d_imp > 0: self.d_imp -= 1 # Decrementa el contador de duración de la fuerza de impulso, para que se aplique durante un número limitado de actualizaciones
        x_pp, theta_pp = self.calcular_fisica(F) #Calcula las aceleraciones lineal y angular usando la función de física
        self.estado[1] += x_pp * self.dt #Actualiza la velocidad del carro sumando la aceleración lineal multiplicada por el paso de tiempo
        self.estado[0] += self.estado[1] * self.dt #Actualiza la posición del carro sumando la velocidad multiplicada por el paso de tiempo
        self.estado[3] += theta_pp * self.dt #Actualiza la velocidad angular del péndulo sumando la aceleración angular multiplicada por el paso de tiempo
        self.estado[2] += self.estado[3] * self.dt #Actualiza el ángulo del péndulo sumando la velocidad angular multiplicada por el paso de tiempo
        self.estado[2] = normalizar_angulo(self.estado[2]) # Normaliza el ángulo del péndulo para que siempre esté entre -180 y 180 grados

# --- CLASE SIMULADOR ---

class Simulador:
    def __init__(self, planta):
        self.planta = planta
        self.agarrado = False
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        plt.subplots_adjust(bottom=0.35, left=0.1, right=0.9)
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-1.5, 2.0)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.2, linestyle='--')
        self.linea, = self.ax.plot([], [], 'o-', lw=6, color='#2c3e50', markersize=12)
        self.carro = plt.Rectangle((-0.4, -0.2), 0.8, 0.4, fc="#9eabac", ec='black', lw=1.5)
        self.ax.add_patch(self.carro)
        self.leyenda_valores = self.ax.text(
            0.02,
            0.96,
            "",
            transform=self.ax.transAxes,
            va="top",
            ha="left",
            fontsize=11,
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#7f8c8d", alpha=0.9),
        )
        
        # --- ZONA DE CONTROL (WIDGETS) ---

        ax_ang = plt.axes([0.15, 0.22, 0.65, 0.03])
        self.s_ang = Slider(ax_ang, 'θ ', -180.0, 180.0, valinit=0.0, valfmt='%1.1f°', color='#3498db')
        self.s_ang.on_changed(self.agarrar_pendulo)
        ax_sol = plt.axes([0.90, 0.22, 0.07, 0.035])
        self.btn_soltar = Button(ax_sol, 'FREE', color='#ecf0f1', hovercolor='#bdc3c7')
        self.btn_soltar.on_clicked(self.soltar_pendulo)
        ax_izq = plt.axes([0.2, 0.07, 0.25, 0.08])
        self.btn_izq = Button(ax_izq, '<<< PUSH IZQ', color='#e74c3c', hovercolor='#c0392b')
        self.btn_izq.on_clicked(lambda x: self.dar_patada(-25))
        ax_der = plt.axes([0.55, 0.07, 0.25, 0.08])
        self.btn_der = Button(ax_der, 'PUSH DER >>>', color='#2ecc71', hovercolor='#27ae60')
        self.btn_der.on_clicked(lambda x: self.dar_patada(25))

    def agarrar_pendulo(self, val):
        self.agarrado = True
        self.planta.estado[2] = -val
        self.planta.estado[3] = 0
        self.planta.estado[1] = 0

    def soltar_pendulo(self, event):
        self.agarrado = False

    def dar_patada(self, magnitud):
        self.agarrado = False 
        self.planta.aplicar_patada(magnitud)

    def loop(self, frame):
        if not self.agarrado:
            self.planta.actualizar()
            self.s_ang.eventson = False
            self.s_ang.set_val(self.planta.estado[2])
            self.s_ang.eventson = True
        else:
            self.planta.f_actual = 0.0
        x, _, theta, theta_p = self.planta.estado
        theta_rad = np.deg2rad(theta)
        px = x + (self.planta.l * 2) * np.sin(theta_rad)
        py = (self.planta.l * 2) * np.cos(theta_rad)
        self.carro.set_xy((x - 0.4, -0.2))
        self.linea.set_data([x, px], [0, py])
        self.leyenda_valores.set_text(
            f"Fuerza: {self.planta.f_actual:7.2f} N\n"
            f"Posicion: {x:7.2f} m\n"
            f"Vel. ang.: {theta_p:7.2f} deg/s"
        )
        self.ax.set_xlim(x - 4, x + 4)
        return self.linea, self.carro, self.leyenda_valores


if __name__ == "__main__":
    planta_fisica = PenduloPlanta(M=2, m=0.1, l=0.5, g=9.81, dt=0.015, b=0.05, d=0.05)
    sim = Simulador(planta_fisica)
    ani = FuncAnimation(sim.fig, sim.loop, interval=15, blit=False)
    plt.title("Planta de Péndulo Invertido - Modo Manual")
    plt.show()
