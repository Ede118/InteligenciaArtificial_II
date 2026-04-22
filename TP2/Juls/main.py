import argparse

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from matplotlib.animation import FuncAnimation

from Controlador import FuzzyController
from planta import PenduloPlanta


def normalizar_angulo(theta):
    return (theta + 180.0) % 360.0 - 180.0


def parsear_argumentos():
    parser = argparse.ArgumentParser(
        description="Simula el pendulo invertido con controlador fuzzy desde un estado inicial configurable."
    )
    parser.add_argument("--x", type=float, default=0.0, help="Posicion inicial del carro en metros.")
    parser.add_argument("--x-p", type=float, default=0.0, help="Velocidad inicial del carro en m/s.")
    parser.add_argument(
        "--theta",
        type=float,
        default=8.0,
        help="Angulo inicial del pendulo en grados. 0 es vertical hacia arriba.",
    )
    parser.add_argument("--theta-p", type=float, default=0.0, help="Velocidad angular inicial en grados/s.")
    parser.add_argument("--duracion", type=float, default=15.0, help="Duracion de la simulacion en segundos.")
    parser.add_argument("--fuerza-max", type=float, default=300.0, help="Saturacion de la fuerza de control en N.")
    return parser.parse_args()


class AdaptadorControladorPlanta:

    def __init__(self, controlador, fuerza_max=300.0):
        self.controlador = controlador
        self.fuerza_max = fuerza_max
        self.control_desactivado = False
        self.desactivar_desde = 80.0
        self.desactivar_hasta = 160.0
        self.reactivar_desde = 170.0

    def configurar_modo_inicial(self, estado):
        _, _, theta, _ = estado
        abs_theta = abs(normalizar_angulo(theta))
        self.control_desactivado = self.desactivar_desde <= abs_theta <= self.desactivar_hasta

    def debe_reactivar(self, theta):
        return abs(normalizar_angulo(theta)) >= self.reactivar_desde

    def calcular_fuerza(self, estado):
        _, _, theta, theta_p = estado
        if self.control_desactivado:
            if self.debe_reactivar(theta):
                self.control_desactivado = False
            else:
                return 0.0

        fuerza = self.controlador.compute_control(theta, theta_p)
        return float(self.fuerza_max * np.tanh(fuerza / self.fuerza_max)) # Limita la fuerza de control a un rango máximo para evitar acciones excesivas en la planta

    def actualizar_planta(self, planta):
        fuerza_control = self.calcular_fuerza(planta.estado)
        fuerza_impulso = planta.f_imp if planta.d_imp > 0 else 0.0
        fuerza = fuerza_control + fuerza_impulso
        planta.f_actual = fuerza
        if planta.d_imp > 0:
            planta.d_imp -= 1

        x_pp, theta_pp = planta.calcular_fisica(fuerza)
        planta.estado[1] += x_pp * planta.dt
        planta.estado[0] += planta.estado[1] * planta.dt
        planta.estado[3] += theta_pp * planta.dt
        planta.estado[2] += planta.estado[3] * planta.dt
        planta.estado[2] = normalizar_angulo(planta.estado[2])

        return fuerza


class SimulacionControlada:
    def __init__(self, planta, adaptador, duracion=10.0, estado_inicial=None):
        self.planta = planta
        self.adaptador = adaptador
        self.duracion = duracion
        self.t = 0.0
        self.corriendo = False
        self.estado_inicial = np.array(
            estado_inicial if estado_inicial is not None else planta.estado,
            dtype=float,
        )

        self.hist_t = []
        self.hist_x = []
        self.hist_x_p = []
        self.hist_theta = []
        self.hist_theta_p = []
        self.hist_fuerza = []

        self.fig = plt.figure(figsize=(15, 7.5))
        grilla = self.fig.add_gridspec(
            5,
            2,
            width_ratios=[1.0, 1.35],
            hspace=0.55,
            wspace=0.28,
        )
        self.ax_pendulo = self.fig.add_subplot(grilla[:, 0])
        self.ax_x = self.fig.add_subplot(grilla[0, 1])
        self.ax_x_p = self.fig.add_subplot(grilla[1, 1], sharex=self.ax_x)
        self.ax_theta = self.fig.add_subplot(grilla[2, 1], sharex=self.ax_x)
        self.ax_theta_p = self.fig.add_subplot(grilla[3, 1], sharex=self.ax_x)
        self.ax_fuerza = self.fig.add_subplot(grilla[4, 1], sharex=self.ax_x)
        self.axes_estados = [
            self.ax_x,
            self.ax_x_p,
            self.ax_theta,
            self.ax_theta_p,
            self.ax_fuerza,
        ]
        plt.subplots_adjust(left=0.06, right=0.98, top=0.92, bottom=0.25)

        self.ax_pendulo.set_title("Pendulo invertido con controlador fuzzy")
        self.ax_pendulo.set_aspect("equal")
        self.ax_pendulo.set_ylim(-1.2, 1.5)
        self.ax_pendulo.grid(True, alpha=0.2, linestyle="--")

        self.carro = plt.Rectangle((-0.4, -0.2), 0.8, 0.4, fc="#9eabac", ec="black", lw=1.5)
        self.ax_pendulo.add_patch(self.carro)
        self.linea_pendulo, = self.ax_pendulo.plot([], [], "o-", lw=6, color="#2c3e50", markersize=12)
        self.texto_estado = self.ax_pendulo.text(
            0.02,
            0.95,
            "",
            transform=self.ax_pendulo.transAxes,
            va="top",
            ha="left",
            fontsize=10,
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#7f8c8d", alpha=0.9),
        )

        self.ax_x.set_title("Posicion lineal")
        self.ax_x_p.set_title("Velocidad lineal")
        self.ax_theta.set_title("Posicion angular")
        self.ax_theta_p.set_title("Velocidad angular")
        self.ax_fuerza.set_title("Fuerza")
        for ax in self.axes_estados:
            ax.grid(True, alpha=0.2, linestyle="--")
            ax.set_xlim(0, self.duracion)
        for ax in self.axes_estados[:-1]:
            ax.tick_params(labelbottom=False)
        self.ax_fuerza.set_xlabel("Tiempo [s]")

        self.ax_x.set_ylabel("x [m]")
        self.ax_x_p.set_ylabel("x_p [m/s]")
        self.ax_theta.set_ylabel("theta [deg]")
        self.ax_theta_p.set_ylabel("theta_p [deg/s]")
        self.ax_fuerza.set_ylabel("F [N]")

        self.linea_x, = self.ax_x.plot([], [], color="#1f77b4")
        self.linea_x_p, = self.ax_x_p.plot([], [], color="#ff7f0e")
        self.linea_theta, = self.ax_theta.plot([], [], color="#2ca02c")
        self.linea_theta_p, = self.ax_theta_p.plot([], [], color="#d62728")
        self.linea_fuerza, = self.ax_fuerza.plot([], [], color="#9467bd")

        self.crear_controles()
        self.reiniciar_estado()

    def crear_controles(self):
        ax_x = plt.axes([0.15, 0.15, 0.65, 0.03])
        self.slider_x = Slider(
            ax_x,
            "x inicial",
            -5.0,
            5.0,
            valinit=self.estado_inicial[0],
            valfmt="%1.2f m",
        )
        self.slider_x.on_changed(self.actualizar_estado_inicial)

        ax_theta = plt.axes([0.15, 0.10, 0.65, 0.03])
        self.slider_theta = Slider(
            ax_theta,
            "theta inicial",
            -180.0,
            180.0,
            valinit=self.estado_inicial[2],
            valfmt="%1.1f deg",
        )
        self.slider_theta.on_changed(self.actualizar_estado_inicial)

        ax_iniciar = plt.axes([0.08, 0.03, 0.16, 0.045])
        self.boton_iniciar = Button(ax_iniciar, "Iniciar", color="#dfe6e9", hovercolor="#b2bec3")
        self.boton_iniciar.on_clicked(self.iniciar)

        ax_pausa = plt.axes([0.29, 0.03, 0.16, 0.045])
        self.boton_pausa = Button(ax_pausa, "Pausa", color="#dfe6e9", hovercolor="#b2bec3")
        self.boton_pausa.on_clicked(self.alternar_pausa)

        ax_reset = plt.axes([0.50, 0.03, 0.16, 0.045])
        self.boton_reset = Button(ax_reset, "Reset", color="#dfe6e9", hovercolor="#b2bec3")
        self.boton_reset.on_clicked(self.resetear)

        ax_desestabilizar = plt.axes([0.71, 0.03, 0.21, 0.045])
        self.boton_desestabilizar = Button(
            ax_desestabilizar,
            "Desestabilizar",
            color="#ffeaa7",
            hovercolor="#fdcb6e",
        )
        self.boton_desestabilizar.on_clicked(self.desestabilizar)

    def estado_desde_controles(self):
        return np.array(
            [
                self.slider_x.val,
                self.estado_inicial[1],
                normalizar_angulo(self.slider_theta.val),
                self.estado_inicial[3],
            ],
            dtype=float,
        )

    def limpiar_historial(self):
        self.t = 0.0
        self.hist_t = []
        self.hist_x = []
        self.hist_x_p = []
        self.hist_theta = []
        self.hist_theta_p = []
        self.hist_fuerza = []

    def reiniciar_estado(self):
        self.planta.estado = self.estado_desde_controles()
        self.planta.f_actual = 0.0
        self.planta.f_imp = 0.0
        self.planta.d_imp = 0
        self.adaptador.configurar_modo_inicial(self.planta.estado)
        self.limpiar_historial()
        self.guardar_estado(self.planta.f_actual)
        self.actualizar_graficos()

    def actualizar_estado_inicial(self, val):
        if self.corriendo:
            return
        self.reiniciar_estado()

    def iniciar(self, event):
        if not self.corriendo:
            self.reiniciar_estado()
            self.corriendo = True

    def alternar_pausa(self, event):
        self.corriendo = not self.corriendo

    def resetear(self, event):
        self.corriendo = False
        self.reiniciar_estado()

    def desestabilizar(self, event):
        self.planta.aplicar_patada(180.0)

    def guardar_estado(self, fuerza):
        x, x_p, theta, theta_p = self.planta.estado
        self.hist_t.append(self.t)
        self.hist_x.append(x)
        self.hist_x_p.append(x_p)
        self.hist_theta.append(theta)
        self.hist_theta_p.append(theta_p)
        self.hist_fuerza.append(fuerza)

    def actualizar_graficos(self):
        x, x_p, theta, theta_p = self.planta.estado
        theta_rad = np.deg2rad(theta)
        largo_visual = self.planta.l * 2
        px = x + largo_visual * np.sin(theta_rad)
        py = largo_visual * np.cos(theta_rad)

        self.carro.set_xy((x - 0.4, -0.2))
        self.linea_pendulo.set_data([x, px], [0, py])
        self.ax_pendulo.set_xlim(x - 3.0, x + 3.0)

        self.texto_estado.set_text(
            f"t:       {self.t:7.2f} s\n"
            f"x:       {x:7.3f} m\n"
            f"x_p:     {x_p:7.3f} m/s\n"
            f"theta:   {theta:7.3f} deg\n"
            f"theta_p: {theta_p:7.3f} deg/s\n"
            f"F:       {self.planta.f_actual:7.3f} N\n"
            f"control: {'OFF' if self.adaptador.control_desactivado else 'ON'}"
        )

        self.linea_x.set_data(self.hist_t, self.hist_x)
        self.linea_x_p.set_data(self.hist_t, self.hist_x_p)
        self.linea_theta.set_data(self.hist_t, self.hist_theta)
        self.linea_theta_p.set_data(self.hist_t, self.hist_theta_p)
        self.linea_fuerza.set_data(self.hist_t, self.hist_fuerza)
        for ax in self.axes_estados:
            ax.relim()
            ax.autoscale_view(scalex=False, scaley=True)

    def loop(self, frame):
        if self.corriendo and self.t <= self.duracion:
            fuerza = self.adaptador.actualizar_planta(self.planta)
            self.guardar_estado(fuerza)
            self.t += self.planta.dt

        self.actualizar_graficos()
        return (
            self.carro,
            self.linea_pendulo,
            self.texto_estado,
            self.linea_x,
            self.linea_x_p,
            self.linea_theta,
            self.linea_theta_p,
            self.linea_fuerza,
        )


def main():
    args = parsear_argumentos()
    planta = PenduloPlanta(M=2.0, m=0.1, l=0.5, g=9.81, dt=0.01, b=0.05, d=0.05)
    planta.estado = np.array(
        [
            args.x,
            args.x_p,
            normalizar_angulo(args.theta),
            args.theta_p,
        ],
        dtype=float,
    )

    controlador = FuzzyController()
    controlador.graficar_funciones_pertenencia()
    controlador.graficar_mapa_decisiones()
    adaptador = AdaptadorControladorPlanta(controlador, fuerza_max=args.fuerza_max)
    simulacion = SimulacionControlada(planta, adaptador, duracion=args.duracion)

    animacion = FuncAnimation(simulacion.fig, simulacion.loop, interval=planta.dt * 1000, blit=False)
    plt.show()
    return animacion


if __name__ == "__main__":
    main()
