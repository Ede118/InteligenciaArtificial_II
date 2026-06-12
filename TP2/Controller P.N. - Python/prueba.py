import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- IMPORTACIÓN DE TUS CLASES ---
from controlador_nico import ControladorDifuso
from planta import PenduloPlanta, Simulador

class SimuladorControlado(Simulador):
    def __init__(self, planta, controlador):
        super().__init__(planta)
        self.controlador = controlador

    def loop(self, frame):
        fuerza_u = 0.0
        acc_ang = 0.0

        if not self.agarrado:
            # 1. OBTENER ESTADO COMPLETO
            x_pos = self.planta.estado[0]
            x_vel = self.planta.estado[1]
            theta = self.planta.estado[2]
            omega = self.planta.estado[3]

            # 2. EVALUAR CONTROLADOR
            fuerza_u = self.controlador.evaluar(theta, omega, x_pos, x_vel)

            # 3. ACTUALIZAR FÍSICA
            x_pp, acc_ang = self.planta.calcular_fisica(fuerza_u)
            
            # Integración de Euler
            self.planta.estado[1] += x_pp * self.planta.dt
            self.planta.estado[0] += self.planta.estado[1] * self.planta.dt
            self.planta.estado[3] += acc_ang * self.planta.dt
            self.planta.estado[2] += self.planta.estado[3] * self.planta.dt
            
            self.planta.estado[2] = (self.planta.estado[2] + np.pi) % (2 * np.pi) - np.pi

            # Sincronizar el slider visual (invertido para que coincida con la física)
            self.s_ang.eventson = False
            self.s_ang.set_val(np.rad2deg(-self.planta.estado[2]))
            self.s_ang.eventson = True

        # --- NOVEDAD: ACTUALIZAR TELEMETRÍA ---
        # Pasamos los datos a los buffers de la clase padre (Simulador)
        datos = [self.planta.estado[2], self.planta.estado[3], acc_ang, fuerza_u]
        for i in range(4):
            val = np.rad2deg(datos[i]) if i == 0 else datos[i]
            self.buffers[i] = np.roll(self.buffers[i], -1)
            self.buffers[i][-1] = val
            self.lines_tele[i].set_ydata(self.buffers[i])
            # Autoescala dinámica para velocidad y aceleración
            if i == 1 or i == 2:
                self.axs_tele[i].relim()
                self.axs_tele[i].autoscale_view()

        # 4. RENDERIZADO DEL PÉNDULO
        x, _, theta, _ = self.planta.estado
        px = x + (self.planta.l * 2) * np.sin(theta)
        py = (self.planta.l * 2) * np.cos(theta)
        
        self.carro.set_xy((x - 0.4, -0.2))
        self.linea.set_data([x, px], [0, py])
        self.ax_sim.set_xlim(x - 4, x + 4)
        
        return self.linea, self.carro

if __name__ == "__main__":
    planta_fisica = PenduloPlanta(M=2, m=0.1, l=0.5, dt=0.015)
    cerebro_hibrido = ControladorDifuso()
    
    sim_final = SimuladorControlado(planta_fisica, cerebro_hibrido)
    
    ani = FuncAnimation(sim_final.fig, sim_final.loop, interval=15, blit=False)
    plt.show()