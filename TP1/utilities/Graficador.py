import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize
import csv
from pathlib import Path

class LectorFrecuenciasPedidos:
    def __init__(self, ruta_csv: str | Path):
        self.ruta_csv = Path(ruta_csv)

    def cargar_pedidos(self):
        pedidos = []

        with open(self.ruta_csv, "r", newline="") as f:
            lector = csv.reader(f)
            for fila in lector:
                if not fila:
                    continue
                pedidos.append(np.array([int(v) for v in fila], dtype=int))

        return pedidos

    def calcular_frecuencias(self):
        pedidos = self.cargar_pedidos()
        frecuencias = {}

        for pedido in pedidos:
            for producto in pedido:
                producto = int(producto)
                frecuencias[producto] = frecuencias.get(producto, 0) + 1

        return frecuencias
    

class Layout:

    def __init__(self):
        # Tamaño de celda
        self.w = 30
        self.h = 30

        # Separaciones
        self.sep_col = 5
        self.sep_row = 5

        # Posiciones base de los bloques (ajustadas a tu imagen)
        self.bloques = [
            (80, 30),   # arriba izquierda
            (210, 30),  # arriba centro
            (340, 30),  # arriba derecha
            (80, 180),  # abajo izquierda
            (210, 180), # abajo centro
            (340, 180), # abajo derecha
        ]

    def construir(self, individuo):
        individuo = np.asarray(individuo)

        if len(individuo) != 48:
            raise ValueError("El individuo debe tener 48 elementos")

        casillas = []
        idx = 0

        for (bx, by) in self.bloques:
            for fila in range(4):
                for col in range(2):

                    x = bx + col * (self.w + self.sep_col)
                    y = by + fila * (self.h + self.sep_row)

                    casillas.append({
                        "producto": int(individuo[idx]),
                        "x": x,
                        "y": y
                    })

                    idx += 1

        return casillas
    
class Graficador:

    def __init__(self, layout):
        self.layout = layout

    def graficar(self, individuo, frecuencias=None):

        casillas = self.layout.construir(individuo)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_facecolor("#e6e6e6")

        if frecuencias is None:
            frecuencias = {}

        valores = [frecuencias.get(c["producto"], 0) for c in casillas]

        norm = Normalize(
            vmin=min(valores) if valores else 0,
            vmax=max(valores) if valores else 1
        )

        cmap = plt.get_cmap("Reds")

        # Dibujar casillas
        for c in casillas:
            freq = frecuencias.get(c["producto"], 0)
            color = cmap(norm(freq))

            rect = Rectangle(
                (c["x"], c["y"]),
                30, 30,
                facecolor=color,
                edgecolor="black"
            )
            ax.add_patch(rect)

            ax.text(
                c["x"] + 15,
                c["y"] + 15,
                str(c["producto"]),
                ha="center",
                va="center",
                fontsize=8
            )

        # Dibujar la C (posición inicial)
        rect_c = Rectangle((0, 160), 40, 40, facecolor="yellow", edgecolor="black")
        ax.add_patch(rect_c)
        ax.text(20, 180, "C", ha="center", va="center", fontsize=12, weight="bold")

        ax.set_xlim(0, 430)
        ax.set_ylim(350, 0)
        ax.set_title("Layout del mejor individuo")

        ax.grid(True, alpha=0.2)

        plt.tight_layout()
        plt.show()