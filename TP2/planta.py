import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation

# --- CLASE PLANTA ---

class PenduloPlanta:
    def __init__(self, M=1.0, m=0.3, l=0.5, g=9.81, dt=0.015, b=0.05, d=0.05):
        self.M, self.m, self.l, self.g, self.dt = M, m, l, g, dt
        self.b, self.d = b, d
        self.estado = np.array([0.0, 0.0, 0.0, 0.0])
        self.f_imp = 0.0
        self.d_imp = 0

    def aplicar_patada(self, mag):
        self.f_imp = mag
        self.d_imp = 5 

    def calcular_fisica(self, F_ext):
        x, x_p, theta, theta_p = self.estado
        st, ct = np.sin(theta), np.cos(theta)
        F_neta = F_ext - (self.d * x_p)
        temp = (-F_neta - self.m * self.l * (theta_p**2) * st) / (self.M + self.m)
        num_theta = (self.g * st) + (ct * temp) - (self.b * theta_p / (self.m * self.l))
        den_theta = self.l * (4/3 - (self.m * ct**2) / (self.M + self.m))
        theta_pp = num_theta / den_theta
        x_pp = (F_neta + self.m * self.l * (theta_pp * ct - (theta_p**2) * st)) / (self.M + self.m)
        return x_pp, theta_pp

    def actualizar(self):
        F = self.f_imp if self.d_imp > 0 else 0.0
        if self.d_imp > 0: self.d_imp -= 1
        x_pp, theta_pp = self.calcular_fisica(F)
        self.estado[1] += x_pp * self.dt
        self.estado[0] += self.estado[1] * self.dt
        self.estado[3] += theta_pp * self.dt
        self.estado[2] += self.estado[3] * self.dt
        self.estado[2] = (self.estado[2] + np.pi) % (2 * np.pi) - np.pi

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
        self.planta.estado[2] = np.deg2rad(val)
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
            self.s_ang.set_val(np.rad2deg(self.planta.estado[2]))
            self.s_ang.eventson = True
        x, _, theta, _ = self.planta.estado
        px = x + (self.planta.l * 2) * np.sin(theta)
        py = (self.planta.l * 2) * np.cos(theta)
        self.carro.set_xy((x - 0.4, -0.2))
        self.linea.set_data([x, px], [0, py])
        self.ax.set_xlim(x - 4, x + 4)
        return self.linea, self.carro

# --- LANZAMIENTO ---
planta_fisica = PenduloPlanta(M=2, m=0.1, l=0.5, g=9.81, dt=0.015, b=0.05, d=0.05)
sim = Simulador(planta_fisica)
ani = FuncAnimation(sim.fig, sim.loop, interval=15, blit=False)
plt.title("Planta de Péndulo Invertido - Modo Manual")
plt.show()