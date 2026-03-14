import pygame
import sys
import Astar_OO as Astar


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


    def cargar_assets(self):

        self.suelo = pygame.image.load("suelo.png")
        self.estanteria = pygame.image.load("estanteria.png")
        self.carga = pygame.image.load("carga.png")

        self.suelo = pygame.transform.scale(self.suelo, (self.TAM_CELL, self.TAM_CELL))
        self.estanteria = pygame.transform.scale(self.estanteria, (self.TAM_CELL, self.TAM_CELL))
        self.carga = pygame.transform.scale(self.carga, (self.TAM_CELL, self.TAM_CELL))


    def calcular_camino(self, estante):

        entorno = Astar.Entorno(self.grid, estante)
        astar = Astar.Astar(entorno)

        self.camino = astar.execute()


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

