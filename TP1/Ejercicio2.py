import TP1.draw_new_entorno as Sim
import TP1.MultiAgente as MA

import copy
import Astar_OO as Astar

import pygame
import draw_entorno as Draw



class Montacargas:

    def __init__(self, id_robot, inicio, grid, estante):

        self.id = id_robot
        self.inicio = inicio
        self.grid = grid
        self.estante = estante

        self.camino = None


    def planificar(self):

        entorno = Astar.Entorno(self.grid, self.estante)

        astar = Astar.Astar(entorno)


        self.camino = astar.execute(self.inicio)

        return self.camino


    def replanificar(self, celdas_bloqueadas):

        grid_temp = copy.deepcopy(self.grid)

        for row, col in celdas_bloqueadas:
            grid_temp[row][col] = Astar.Entorno.ESTANTE

        entorno = Astar.Entorno(grid_temp, self.estante)

        astar = Astar.Astar(entorno)


        self.camino = astar.execute(self.inicio)

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

class SimulacionMulti(Draw.Simulacion):

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

    entorno_estatico = [[0,0,0,0,0,0,0,0,0,0,0,0,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [2,0,0,0,0,0,0,0,0,0,0,0,2], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,0,0,0,0,0,0,0,0,0,0,0]]

    estante1 = int(input("Estante robot 1: "))
    estante2 = int(input("Estante robot 2: "))

    robot1 = MA.Montacargas(1,(5,0),entorno_estatico,estante1)
    robot2 = MA.Montacargas(2,(5,12),entorno_estatico,estante2)

    coord = MA.Coordinador(entorno_estatico,[robot1,robot2])

    camino1, camino2 = coord.planificar_rutas()

    sim = Sim.SimulacionMulti(entorno_estatico)

    sim.set_caminos(camino1,camino2)

    sim.run()