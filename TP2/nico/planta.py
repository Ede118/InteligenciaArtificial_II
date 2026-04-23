import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec

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

    def actualizar(self, F_ext=None):
        if F_ext is None:
            F = self.f_imp if self.d_imp > 0 else 0.0
            if self.d_imp > 0: self.d_imp -= 1
        else:
            F = F_ext

        x_pp, theta_pp = self.calcular_fisica(F)
        self.estado[1] += x_pp * self.dt
        self.estado[0] += self.estado[1] * self.dt
        self.estado[3] += theta_pp * self.dt
        self.estado[2] += self.estado[3] * self.dt
        self.estado[2] = (self.estado[2] + np.pi) % (2 * np.pi) - np.pi
        return F, theta_pp

# --- CLASE SIMULADOR INTEGRADO ---
class Simulador:
    def __init__(self, planta):
        self.planta = planta
        self.agarrado = False
        self.max_pts = 200 # Más puntos para mejor resolución temporal
        
        self.fig = plt.figure(figsize=(14, 9))
        gs = gridspec.GridSpec(4, 2, figure=self.fig, width_ratios=[1.3, 1], hspace=0.5, wspace=0.3)

        # 1. Ventana del Péndulo
        self.ax_sim = self.fig.add_subplot(gs[:, 0])
        self.ax_sim.set_xlim(-5, 5); self.ax_sim.set_ylim(-1.5, 2.0)
        self.ax_sim.set_aspect('equal')
        self.ax_sim.grid(True, alpha=0.2, linestyle='--')
        self.linea, = self.ax_sim.plot([], [], 'o-', lw=6, color='#2c3e50', markersize=12, zorder=3)
        self.carro = plt.Rectangle((-0.4, -0.2), 0.8, 0.4, fc="#9eabac", ec='black', lw=2, zorder=2)
        self.ax_sim.add_patch(self.carro)

        # 2. Telemetría
        self.axs_tele = [self.fig.add_subplot(gs[i, 1]) for i in range(4)]
        titulos = ['Pos. Angular (deg)', 'Vel. Angular (rad/s)', 'Acc. Angular (rad/s²)', 'Fuerza (N)']
        colores = ['#3498db', '#e67e22', '#e74c3c', '#2ecc71']
        self.lines_tele = []
        self.t_axis = np.linspace(-self.max_pts * planta.dt, 0, self.max_pts)
        self.buffers = [np.zeros(self.max_pts) for _ in range(4)]

        for i, ax in enumerate(self.axs_tele):
            line, = ax.plot(self.t_axis, self.buffers[i], color=colores[i], lw=1.8)
            self.lines_tele.append(line)
            ax.set_title(titulos[i], fontsize=10, fontweight='bold', loc='left')
            ax.grid(True, alpha=0.3)
            # Límites en Y mejorados
            if i == 0: ax.set_ylim(-200, 200)
            elif i == 1: ax.set_ylim(-12, 12) # Eje de velocidad más amplio
            elif i == 3: ax.set_ylim(-150, 150)

        plt.subplots_adjust(bottom=0.2, left=0.05, right=0.95, top=0.93)

        # --- WIDGETS ---
        ax_ang = plt.axes([0.1, 0.1, 0.35, 0.03])
        self.s_ang = Slider(ax_ang, 'θ ', -180.0, 180.0, valinit=0.0, color='#3498db')
        self.s_ang.on_changed(self.agarrar_pendulo)
        
        # Botón FREE
        ax_sol = plt.axes([0.47, 0.1, 0.05, 0.03])
        self.btn_soltar = Button(ax_sol, 'FREE', color='#ecf0f1', hovercolor='#bdc3c7')
        self.btn_soltar.on_clicked(self.soltar_pendulo)
        
        ax_izq = plt.axes([0.1, 0.03, 0.12, 0.05])
        self.btn_izq = Button(ax_izq, '<<< PUSH', color='#e74c3c', hovercolor='#c0392b')
        self.btn_izq.on_clicked(lambda x: self.dar_patada(-60))
        
        ax_der = plt.axes([0.33, 0.03, 0.12, 0.05])
        self.btn_der = Button(ax_der, 'PUSH >>>', color='#2ecc71', hovercolor='#27ae60')
        self.btn_der.on_clicked(lambda x: self.dar_patada(60))

    def agarrar_pendulo(self, val):
        self.agarrado = True
        self.planta.estado[2] = np.deg2rad(-val)
        self.planta.estado[3] = 0; self.planta.estado[1] = 0

    def soltar_pendulo(self, event):
        self.agarrado = False

    def dar_patada(self, mag):
        self.agarrado = False
        self.planta.aplicar_patada(mag)

    def loop(self, frame):
        fuerza, acc_ang = 0.0, 0.0
        if not self.agarrado:
            fuerza, acc_ang = self.planta.actualizar()
            self.s_ang.eventson = False
            self.s_ang.set_val(np.rad2deg(-self.planta.estado[2]))
            self.s_ang.eventson = True
        
        # Telemetría
        datos = [self.planta.estado[2], self.planta.estado[3], acc_ang, fuerza]
        for i in range(4):
            val = np.rad2deg(datos[i]) if i == 0 else datos[i]
            self.buffers[i] = np.roll(self.buffers[i], -1); self.buffers[i][-1] = val
            self.lines_tele[i].set_ydata(self.buffers[i])
            # Autoescala dinámica para aceleración y velocidad si superan los límites
            if i == 1 or i == 2:
                self.axs_tele[i].relim()
                self.axs_tele[i].autoscale_view()

        # Visual Péndulo
        x, _, theta, _ = self.planta.estado
        px = x + (self.planta.l*2)*np.sin(theta)
        py = (self.planta.l*2)*np.cos(theta)
        self.carro.set_xy((x - 0.4, -0.2))
        self.linea.set_data([x, px], [0, py])
        self.ax_sim.set_xlim(x - 4, x + 4)
        return self.linea, self.carro

if __name__ == "__main__":
    p = PenduloPlanta(M=2, m=0.2, dt=0.015)
    sim = Simulador(p)
    ani = FuncAnimation(sim.fig, sim.loop, interval=15, blit=False)
    plt.show()