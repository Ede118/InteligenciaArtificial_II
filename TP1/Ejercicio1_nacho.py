
import pygame
import sys

import A_star

pygame.init()

# Definición del entorno estático
# suelo -> 0
# estante -> 1
# carga -> 2

SUELO = 0
ESTANTE = 1
CARGA = 2

entorno_estatico = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [2,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0]
]


camino = [(5,0),(5,1),(5,2),(5,0)]


fuente = pygame.font.SysFont("Arial", 16)



ROWS = len(entorno_estatico)
COLS = len(entorno_estatico[0])
TAM_CELL = 60
suelo = pygame.image.load("suelo.png")
estanteria = pygame.image.load("estanteria.png")
carga = pygame.image.load("carga.png")


suelo = pygame.transform.scale(suelo, (TAM_CELL, TAM_CELL))
estanteria = pygame.transform.scale(estanteria, (TAM_CELL, TAM_CELL))
carga = pygame.transform.scale(carga, (TAM_CELL, TAM_CELL))


pantalla = pygame.display.set_mode((COLS * TAM_CELL, ROWS * TAM_CELL))
pygame.display.set_caption("Entorno de simulación")


YELLOW = (255,255,0)
WHITE = (255,255,255)
GRAY = (200,200,200)
BLACK = (0,0,0)

def draw_grid():
    contador_estantes = 1
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col*TAM_CELL, row*TAM_CELL, TAM_CELL, TAM_CELL)
            if entorno_estatico[row][col] == SUELO:
                pantalla.blit(suelo, rect)
                
            if entorno_estatico[row][col] == ESTANTE:
                pantalla.blit(estanteria, rect)

                texto = fuente.render(str(contador_estantes), True, BLACK)
                pantalla.blit(texto, (col*TAM_CELL + 38, row*TAM_CELL + 6))

                contador_estantes += 1

            if entorno_estatico[row][col] == CARGA:
                pantalla.blit(carga, rect)
            pygame.draw.rect(pantalla, GRAY, rect, 1)


def draw_camino(camino):

    overlay = pygame.Surface((TAM_CELL, TAM_CELL), pygame.SRCALPHA)
    overlay.fill((0,255,0,120))

    for nodo in camino:
        row, col = nodo
        pantalla.blit(overlay, (col*TAM_CELL, row*TAM_CELL))


if __name__ == "__main__":

    inicio_fila = int(input("Ingrese la fila de la posición inicial: "))
    inicio_columna = int(input("Ingrese la columna de la posición inicial: "))
    inicio = (inicio_fila, inicio_columna)

    objetivo_fila = int(input("Ingrese la fila de la posición objetivo: "))
    objetivo_columna = int(input("Ingrese la columna de la posición objetivo: "))
    objetivo = (objetivo_fila, objetivo_columna)

    camino = A_star.a_estrella(inicio, objetivo)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pantalla.fill(BLACK)
        draw_grid()
        draw_camino(camino)

        pygame.display.flip()
