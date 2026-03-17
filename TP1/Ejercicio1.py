"""
# Montacargas.
El algoritmo de montacargas debe ser diseñado con el paradigma de programación orientada a objetos.
Se le deben dar 2 parámetros:
@param Casilla de inicio
@param Casilla de destino

El algoritmo debe retornar una lista de casillas que representan el camino a seguir para llegar al destino.
Se debe utilizar el algoritmo de búsqueda A* para encontrar el camino más corto entre las casillas de inicio y destino,
teniendo en cuenta las restricciones del montacargas.

Se deben desarrollar las restricciones y objetivos.
"""

import heapq
import pygame
import sys
from unittest import case
import numpy as np

def csv_to_array(ruta: str) -> np.ndarray:
    with open(ruta, 'r') as f:
        lines = f.readlines()
    array = np.array([[int(dato) for dato in line.strip().split(',')] for line in lines])
    return array

def casilla_a_coordenadas(
    casilla: int,
    matriz_casillas: np.ndarray
    ) -> tuple[int, int]:
    "Devuelve entre 0-size[0] (iterador en python)"
    x, y = np.where(matriz_casillas == casilla)
    if x.size == 0:
        raise ValueError(f"La casilla {casilla} no se encuentra en la matriz.")
    x0: int = x[0]
    y0: int = y[0]
    return (x0, y0)  # Convertir a coordenadas 1-indexadas

class Almacen:
    """ 
    Define la "grilla"/"almacen" donde se encuentran los estantes, caminos y posición de inicio de la carga.
    """
    SUELO = 0
    ESTANTE = 1
    CARGA = 2

    def __init__(
        self, 
        grid,
        estante_objetivo: int,
        *,
        lista_modificada: any | None,
        flag_almacen: bool = False
        ):
        """ 
        @param grid: Matriz de 0/1 con posiciones de estantes
        @param estante_objetivo: número de estante objetivo
        """
        self.grid = grid        
        self.ROWS = len(grid)
        self.COLS = len(grid[0]) if self.ROWS > 0 else 0

        if not 1 <= estante_objetivo <= 48 :
            print("[WARNING]El estante objetivo debe estar entre 1 y 48.")
            if estante_objetivo < 1:
                estante_objetivo = 1
            if estante_objetivo > 48:
                estante_objetivo = 48
                
        #Numero de estante
        self.estante_objetivo = estante_objetivo 
        #Posicion del estante objetivo
        self.pos_estante = None
        #Contador de estantes para encontrar la posición del estante objetivo
        self.idx_estante = 0
        
        if flag_almacen is None:
            flag_almacen = False
            lista_modificada = None

        #cuando 
        for i in range(self.ROWS):
            for j in range(self.COLS):
                if self.grid[i][j] == self.ESTANTE:
                    self.idx_estante += 1
                    
                    if flag_almacen:
                        almacen_numero = lista_modificada[self.idx_estante-1]
                    else:
                        almacen_numero = self.idx_estante
                    
                    if almacen_numero == self.estante_objetivo:
                        self.pos_estante = (i, j)
                        break
            if self.pos_estante is not None:
                break

        self.casilla_objetivo: tuple[int, int] | None

        #Entorno debe saber que si seleccionamos una estanteria, solo se puede estar 
        #del lado derecho o del lado izquierdo, dependiendo de la posicion del estante_objetivo
        #Si a la derecha es estante, entonces asignamos la casilla izquierda
        if self.grid[self.pos_estante[0]][self.pos_estante[1] + 1] == self.ESTANTE:
            self.casilla_objetivo = (self.pos_estante[0], self.pos_estante[1] - 1)
        else:
            self.casilla_objetivo = (self.pos_estante[0], self.pos_estante[1] + 1)

    def vecinos(self, nodo):
        row, col = nodo
        posibles_vecinos = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
        vecinos_validos = []

        for vecino in posibles_vecinos:
            if 0 <= vecino[0] < self.ROWS and 0 <= vecino[1] < self.COLS:
                if self.grid[vecino[0]][vecino[1]] != self.ESTANTE:
                    vecinos_validos.append(vecino)

        return vecinos_validos

class Montacargas:
    """
    Agente que realiza el algoritmo de busqueda global.
    """
    def __init__(
        self, 
        grilla: Almacen,
        casilla_inicial: tuple[int, int]
        ):
        
        self.grilla = grilla
        self.casilla_inicial = casilla_inicial # posicion inicial
        self.OPEN = [] #por explorar 
        heapq.heappush(self.OPEN, (0, self.casilla_inicial))
        self.CLOSED = set() #explorados
        self.g = {self.casilla_inicial: 0}
        self.padres = {}

    def heuristica(self, nodo):
        return abs(nodo[0] - self.grilla.casilla_objetivo[0]) + abs(nodo[1] - self.grilla.casilla_objetivo[1])
    
    def reconstruir_camino(self, nodo: tuple[int, int]) -> list[tuple[int, int]]:
        """
        @param nodo: tuple[int, int] - Nodo objetivo
        @return: list[tuple[int, int]] - Lista de Nodos 
        """
        camino = [nodo]

        while nodo in self.padres:
            nodo = self.padres[nodo]
            camino.append(nodo)

        camino.reverse()
        return camino
    
    def execute(self, *, print_costo:bool=False) -> tuple[list[tuple[int, int]], int]:
        """ 
        @param: None
        
        @return: tuple[list[tuple[int, int]], int] - Lista de Nodos y costo total del camino
        """
        while self.OPEN:

            _, nodo_actual = heapq.heappop(self.OPEN)

            if nodo_actual in self.CLOSED:
                continue


            if nodo_actual == self.grilla.casilla_objetivo:
                nodos_solucion = self.reconstruir_camino(nodo_actual)
                h_manhattan = len(nodos_solucion) - 1
                if print_costo:
                    print(f"Camino encontrado: {nodos_solucion}")
                    print(f"Costo total: {h_manhattan}")
                return nodos_solucion, h_manhattan

            self.CLOSED.add(nodo_actual)

            for vecino in self.grilla.vecinos(nodo_actual):

                if vecino in self.CLOSED:
                    continue

                nuevo_g = self.g[nodo_actual] + 1

                if vecino not in self.g or nuevo_g < self.g[vecino]:

                    self.padres[vecino] = nodo_actual
                    self.g[vecino] = nuevo_g

                    f = nuevo_g + self.heuristica(vecino)

                    heapq.heappush(self.OPEN, (f, vecino))
        
        raise ValueError("No se encontró un camino al objetivo.")

class Simulacion:

    SUELO = 0
    ESTANTE = 1
    CARGA = 2

    def __init__(self, grid):

        pygame.init()

        self.grid = grid
        self.ROWS = len(grid)
        self.COLS = len(grid[0])

        self.TAM_CELL = 60

        self.pantalla = pygame.display.set_mode(
            (self.COLS*self.TAM_CELL, self.ROWS*self.TAM_CELL)
        )

        pygame.display.set_caption("Entorno de simulación")

        self.fuente = pygame.font.SysFont("Arial", 16)

        self.cargar_assets()

        self.camino = None
        self.costo = None

    def cargar_assets(self):

        self.suelo = pygame.image.load("TP1/utilities/suelo.png")
        self.estanteria = pygame.image.load("TP1/utilities/estanteria.png")
        self.carga = pygame.image.load("TP1/utilities/carga.png")

        self.suelo = pygame.transform.scale(self.suelo, (self.TAM_CELL, self.TAM_CELL))
        self.estanteria = pygame.transform.scale(self.estanteria, (self.TAM_CELL, self.TAM_CELL))
        self.carga = pygame.transform.scale(self.carga, (self.TAM_CELL, self.TAM_CELL))

    def calcular_camino(
        self,
        estante: int,
        casilla0: tuple[int, int] = (5, 0),
        *,
        flag: bool = False,
        orden: np.ndarray | list
        ):

        entorno = Almacen(
            self.grid, 
            estante_objetivo=estante,
            flag_almacen=flag,
            lista_modificada=orden
        )
        
        agente = Montacargas(
            grilla=entorno,
            casilla_inicial=casilla0
        )

        self.camino, self.costo = agente.execute(print_costo=True)

    def draw_entorno(self, camino):

        contador_estantes = 1

        for row in range(self.ROWS):
            for col in range(self.COLS):

                rect = pygame.Rect(
                    col*self.TAM_CELL,
                    row*self.TAM_CELL,
                    self.TAM_CELL,
                    self.TAM_CELL
                )

                celda = self.grid[row][col]

                if celda == self.SUELO:
                    self.pantalla.blit(self.suelo, rect)

                elif celda == self.ESTANTE:

                    self.pantalla.blit(self.estanteria, rect)

                    texto = self.fuente.render(
                        str(contador_estantes), True, (0,0,0)
                    )

                    self.pantalla.blit(
                        texto,
                        (col*self.TAM_CELL+38, row*self.TAM_CELL+6)
                    )

                    contador_estantes += 1

                elif celda == self.CARGA:
                    self.pantalla.blit(self.carga, rect)

                pygame.draw.rect(self.pantalla, (200,200,200), rect, 1)

        if camino:
            self.draw_camino(camino)

    def draw_camino(self, camino):

        overlay = pygame.Surface((self.TAM_CELL, self.TAM_CELL), pygame.SRCALPHA)
        overlay.fill((0,255,0,120))

        for row, col in camino:
            self.pantalla.blit(
                overlay,
                (col*self.TAM_CELL, row*self.TAM_CELL)
            )

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.pantalla.fill((0,0,0))
            self.draw_entorno(self.camino)

            pygame.display.flip()
            
if __name__ == "__main__":
    
    entorno_estatico = csv_to_array("TP1/utilities/casillas.csv")
    print("Bienvenido al simulador de montacargas.")
    print("La casilla de carga \"C\" es (5,0).")
    casilla_inicial = tuple(int(x) for x in input("Ingrese la casilla inicial (fila,columna): ").split(","))
    estante = int(input("Ingrese el número del estante objetivo (1-48): "))
    
    mod_list = [x+1 for x in range(48)]
    
    mod_list[0] = 2
    mod_list[1] = 1
    
    agente = Montacargas(
        grilla=Almacen(
            entorno_estatico, 
            estante_objetivo=estante,
            flag_almacen=False,
            lista_modificada= None
        ),
        casilla_inicial=casilla_inicial
    )
    
    camino, costo = agente.execute(print_costo=False)
    
    simulacion = Simulacion(entorno_estatico)
    simulacion.calcular_camino(
        estante, 
        casilla0=casilla_inicial,
        flag=False,
        orden=None
    )
    simulacion.run()
    
    print("Lo que sea")