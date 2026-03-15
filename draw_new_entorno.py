import pygame
import draw_entorno as Draw


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