import copy
import pygame
import numpy as np
import Ejercicio1 as E1

class MontacargasInteligente:
    def __init__(
        self, 
        id_robot: int, 
        grid: np.ndarray, 
        estante0: int,
        inicio: tuple[int, int] = (0,5)
        ):

        self.id = id_robot
        self.inicio = inicio
        self.grid = grid
        self.estante_objetivo = estante0

        self.camino = None


    def planificar(self):
        """ 
        @param None
        @return self.camino: Lista de nodos (tuple[int, int]) los cuales son el camino desde la casilla de inicio hasta el estante objetivo.
        """
        entorno = E1.Almacen(
            grid=self.grid, 
            estante_objetivo=self.estante_objetivo, 
            casilla_inicial=self.inicio)
        
        astar = E1.Montacargas(grilla=entorno)
        self.camino, _= astar.execute()

        return self.camino


    def replanificar(self, celdas_bloqueadas):

        grid_temp = copy.deepcopy(self.grid)

        for row, col in celdas_bloqueadas:
            grid_temp[row][col] = E1.Almacen.ESTANTE

        entorno = E1.Almacen(
            grid=self.grid, 
            estante_objetivo=self.estante_objetivo, 
            casilla_inicial=self.inicio)
        
        astar = E1.Montacargas(entorno)
        self.camino, _= astar.execute()

        return self.camino



class Coordinador:

    def __init__(self, grid, robots):

        self.grid = grid
        self.robots = robots


    def detectar_conflicto(self, camino1, camino2):

        tiempo = min(len(camino1), len(camino2))

        for t in range(tiempo):

            if camino1[t] == camino2[t]:
                return True
            if t>0:
                 if camino1[t] == camino2[t-1] and camino1[t-1] == camino2[t]:
                  return True

        return False


    def planificar_rutas(self):

        robot_prioridad = self.robots[0]
        robot_secundario = self.robots[1]

        camino1 = robot_prioridad.planificar()

        camino2 = robot_secundario.planificar()

        if self.detectar_conflicto(camino1, camino2):

            print("Conflicto detectado → Replanificando robot 2")

            camino2 = robot_secundario.replanificar(camino1)

        return camino1, camino2

class SimulacionMulti(E1.Simulacion):

    def __init__(self, grid):

        super().__init__(grid)

        self.camino_robot1 = None
        self.camino_robot2 = None


    def set_caminos(self, camino1, camino2):

        self.camino_robot1 = camino1
        self.camino_robot2 = camino2


    def draw_entorno(self, camino):

        super().draw_entorno(self.camino_robot1)

        if self.camino_robot2:

            overlay = pygame.Surface(
                (self.TAM_CELL, self.TAM_CELL),
                pygame.SRCALPHA
            )

            overlay.fill((0,0,255,120))

            for row, col in self.camino_robot2:

                self.pantalla.blit(
                    overlay,
                    (col*self.TAM_CELL, row*self.TAM_CELL)
                )

if __name__ == "__main__":

    entorno_estatico = E1.csv_to_array("TP1/utilities/casillas.csv")
    estante1 = int(input("Estante robot 1: "))
    estante2 = int(input("Estante robot 2: "))

    robot1 = MontacargasInteligente(
        id_robot=1,
        grid=entorno_estatico,
        estante0=estante1,
        inicio=(5,0)
    )
    
    robot2 = MontacargasInteligente(
        id_robot=2,
        grid=entorno_estatico,
        estante0=estante2,
        inicio=(5,12)
    )
    

    coord = Coordinador(entorno_estatico,[robot1,robot2])

    camino1, camino2 = coord.planificar_rutas()

    sim = SimulacionMulti(entorno_estatico)

    sim.set_caminos(camino1,camino2)

    sim.run()