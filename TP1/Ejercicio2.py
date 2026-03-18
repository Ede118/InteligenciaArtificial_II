import copy
from PIL.ImageChops import overlay
import pygame
import numpy as np
import Ejercicio1 as E1
import sys

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
            flag_almacen=False,
            lista_modificada0=None
        )
        
        astar = E1.Montacargas(
            grilla=entorno,
            casilla_inicial=self.inicio
        )
        
        camino_ida, _ = astar.execute()

        # generar camino de vuelta
        camino_vuelta = camino_ida[-2::-1]
        
        self.camino = camino_ida + camino_vuelta

        return self.camino

    def replanificar(self, trayectoria_robot1):
        # P2 inicial: Trayectoria ideal del robot 2
        p2 = self.planificar()
        p1 = trayectoria_robot1
    
        t = 0
       
        while t < min(len(p1), len(p2)) - 1:
            
            p1_t, p1_next = p1[t], p1[t+1]
            p2_t, p2_next = p2[t], p2[t+1]

            # VERIFICAR SWAP (Intercambio frontal)
            if p1_t == p2_next and p1_next == p2_t:
                print(f"Swap detectado entre {p2_t} y {p2_next}. Bloqueando celda y recalculando desde base.")

                pos_conflicto = p2_t
            
                # Actualizamos mapa: la casilla de P2(t) ahora es un obstáculo (1)
                grid_temp = copy.deepcopy(self.grid)
                grid_temp[pos_conflicto[0]][pos_conflicto[1]] = 99
            
                # Recalculamos desde la base (inicio) con el nuevo mapa
                entorno_nuevo = E1.Almacen(grid=grid_temp, estante_objetivo=self.estante_objetivo, lista_modificada0=[])
                astar = E1.Montacargas(grilla=entorno_nuevo, casilla_inicial=self.inicio)
            
                camino_ida, _ = astar.execute()
                camino_vuelta = camino_ida[-2::-1]
                p2 = camino_ida + camino_vuelta
            
                t = 0
                continue

            #VERIFICAR CHOQUE
            elif p1_t == p2_t:
                print(f"Choque detectado en {p2_t}. Robot 2 espera.")
            
                pos_espera = p2[t-1] if t > 0 else p2[0]
                p2.insert(t, pos_espera)

                continue

            t += 1
        
        return p2

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

        self.t = 0
        self.velocidad = 30  # frames por paso
        self.frame_count = 0
        super().__init__(grid)

        self.camino_robot1 = None
        self.camino_robot2 = None


    def set_caminos(self, camino1, camino2):

        self.camino_robot1 = camino1
        self.camino_robot2 = camino2
        self.t = 0
        self.max_t = max(len(camino1), len(camino2))

    def draw_entorno(self, camino):

        super().draw_entorno(None)

         # posiciones actuales
        if self.camino_robot1:
            pos1 = self.camino_robot1[min(self.t, len(self.camino_robot1)-1)]
            self.draw_robot(pos1, (0,255,0))  

        if self.camino_robot2:
            pos2 = self.camino_robot2[min(self.t, len(self.camino_robot2)-1)]
            self.draw_robot(pos2, (0,0,255))  
    
    def draw_robot(self, pos, color):

        overlay = pygame.Surface(
         (self.TAM_CELL, self.TAM_CELL),
         pygame.SRCALPHA
         )

        overlay.fill((*color,180))

        row, col = pos

        self.pantalla.blit(
            overlay,
            (col*self.TAM_CELL, row*self.TAM_CELL)
        )
    
    def run(self):

      clock = pygame.time.Clock()

      while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.pantalla.fill((0,0,0))

        self.draw_entorno(None)

        pygame.display.flip()

        # control de tiempo
        self.frame_count += 1

        if self.frame_count >= self.velocidad:
            self.frame_count = 0

            if self.t < self.max_t - 1:
                self.t += 1

        clock.tick(60)


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