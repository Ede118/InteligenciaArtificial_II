import subprocess
try:
    import pygame
except ImportError as err:
    subprocess.check_call(['pip', 'install', 'pygame'])
    import pygame

import os
import random
from Dinosaur import Dinosaur
from Cloud import Cloud
from Bird import Bird
from SmallCactus import SmallCactus
from LargeCactus import LargeCactus
from Genetic import updateNetwork
from ImageCapture import ImageCapture
import numpy as np


screen_spawn_position = (100, 100)
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % screen_spawn_position
pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DinoGame")
generation = 1
bestScore = 0
playMode = "X"

imageCapture = ImageCapture(screen_spawn_position)

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

def populate(population_size):
    population = []
    for i in range(population_size):
        while True:
            R = random.randint(0, 255)
            G = random.randint(0, 255)
            B = random.randint(0, 255)
            brightness = 0.299 * R + 0.587 * G + 0.114 * B
            if brightness < 180:  # Evitar colores demasiado claros
                break
        color = (R, G, B)
        population.append(Dinosaur(i, color, True))
    return population

# ======================== SELECT THE POPULATION NUMBER PLAYING AT THE SAME TIME ======================
population_number = 200
# =====================================================================================================
population = populate(population_number)
player = Dinosaur(0)
callUpdateNetwork = False

def gameScreen():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, population, callUpdateNetwork, generation, bestScore, playMode
    run = True
    clock = pygame.time.Clock()
    game_speed = 20
    cloud = Cloud(SCREEN_WIDTH, game_speed)
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    callUpdateNetwork = True

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Puntos: " + str(points), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

    def countSurviving():
        global population
        text = font.render("Vivos: " + str(count_alive(population)), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 65)
        SCREEN.blit(text, textRect)

    def currentGeneration():
        global generation
        text = font.render("Generación: " + str(generation), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 90)
        SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    def deathUpdates(player, obstacle):
        global generation, points, bestScore
        obstacle_params = obstacle.rect
        SCREEN.fill((255, 255, 255))
        background()
        score()
        cloud.draw(SCREEN)
        cloud.update()
        SCREEN.blit(player.image, (player.dino_rect.x, player.dino_rect.y))
        SCREEN.blit(obstacle.image[obstacle.type], (obstacle_params.x, obstacle_params.y))
        pygame.draw.rect(SCREEN, (255, 0, 0), player.dino_rect, 2)
        pygame.draw.rect(SCREEN, (0, 0, 255), obstacle_params, 2)
        pygame.display.update()
        pygame.time.delay(1000)
        generation += 1
        if points > bestScore:
            bestScore = points
        menu()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))

        if playMode == 'm' or playMode == 'c':
            userInput = pygame.key.get_pressed()
            player.draw(SCREEN)
            player.update(userInput)
            if playMode == 'c':
                imageCapture.capture(userInput)

        elif playMode == 'a':
            if player.alive:
                player.draw(SCREEN)
                imageCapture.capture_live()
                player.predict()

        else:
            obstacle_types = {
                Bird:         [1, 0, 0],
                LargeCactus:  [0, 1, 0],
                SmallCactus:  [0, 0, 1]
            }
            for dino in population:
                if dino.alive:
                    dino.draw(SCREEN)
                
                for obstacle in obstacles:
                    obstacle_params = obstacle.rect
                    dino_params = dino.dino_rect
                    # ========================== ACTUALIZAR LA FUNCIÓN 'think' CON LOS PARÁMETROS DE ENTRADA DE LA RED ===================
                    Y_REF = 250
                    T_COLLISION_NORM = 10 # constante de normalización para el tiempo hasta la colisión, ajustada empíricamente para que los valores estén en un rango adecuado para la red

                    y_dino = (Y_REF - dino_params.y) / Y_REF # normalizamos respecto a la altura de duck, que es el movimiento vertical más bajo que hace el dinosaurio
                    x_obstacle = obstacle_params.x / SCREEN_WIDTH # normalizamos respecto al ancho de la pantalla, que es la distancia máxima a la que puede estar el obstáculo
                    t_collision = (obstacle_params.x - dino_params.x) / (game_speed * T_COLLISION_NORM) # tiempo estimado hasta la colisión, normalizado respecto a la velocidad del juego
                    

                    y_obstacle = (obstacle_params.y - Y_REF) / Y_REF # normalizamos respecto a una referencia vertical, que podría ser la altura de un cactus pequeño, para que la red pueda aprender a diferenciar entre obstáculos altos y bajos
                    #obstacle_width = obstacle_params.width / 150 # normalizamos respecto a un ancho máximo de obstáculo, que podría ser el ancho de un cactus grande o un pájaro, dependiendo de cuál sea mayor
                    #cos_x_obs = np.cos(obstacle_params.x - dino_params.x)
                    #sin_x_obs = np.sin(obstacle_params.x - dino_params.x)

                    cos_t_collision = np.cos(t_collision) # función coseno del tiempo hasta la colisión, para introducir una no linealidad que permita a la red aprender a anticipar los obstáculos
                    sin_t_collision = np.sin(t_collision) # función seno del tiempo hasta la colisión, para introducir una no linealidad que permita a la red aprender a anticipar los obstáculos

                    is_bird = 1.0 if isinstance(obstacle, Bird) else -1.0

                    dino.update(dino.think(y_dino, x_obstacle, is_bird, t_collision, y_obstacle)) 
                    # ====================================================================================================================

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SCREEN_WIDTH, game_speed, obstacles))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(SCREEN_WIDTH, game_speed, obstacles))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(SCREEN_WIDTH, game_speed, obstacles))
        

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            obstacle_params = obstacle.rect

            # debug datos
            print("Obstacle position: ", obstacle_params)

            if playMode == 'm' or playMode == 'c' or playMode == 'a':
                if player.dino_rect.colliderect(obstacle_params):
                    player.alive = False
                    
            else:
                for dino in population:
                    dino_params = dino.dino_rect
                    if dino.alive and dino_params.colliderect(obstacle_params):
                        dino.score = points
                        dino.alive = False

                        if (count_alive(population) == 0):
                            last_dino = dino

        if ((playMode == 'm' or playMode == 'c' or playMode == 'a') and player.alive == False):
            deathUpdates(player, obstacle)
        elif (playMode != 'm' and playMode != 'c' and playMode != 'a' and count_alive(population) == 0):
            countSurviving()
            currentGeneration()
            deathUpdates(last_dino, obstacle)

        background()

        cloud.draw(SCREEN)
        cloud.update()

        score()

        if (playMode != 'm' and playMode != 'c' and playMode != 'a'):
            countSurviving()
            currentGeneration()

        #clock.tick(30)
        pygame.display.update()

def menu():
    global callUpdateNetwork, generation, bestScore, playMode, population, population_number
    run = True

    if playMode == 'm' or playMode == 'c' or playMode == 'a':
        player.resetStatus()
    elif playMode != 'm' and playMode != 'c' and playMode != 'a' and callUpdateNetwork:
        updateNetwork(population, generation)
        callUpdateNetwork = False
        for dino in population:
            dino.resetStatus()
        
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if generation == 1:
            text = font.render("Pulse 'm' para jugar manualmente", True, (0, 0, 0))

            auxText = font.render("'c' para capturar imágenes", True, (0, 0, 0))
            auxTextRect = auxText.get_rect()
            auxTextRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(auxText, auxTextRect)

            auxText = font.render("'a' para usar el modelo generado por Tensorflow", True, (0, 0, 0))
            auxTextRect = auxText.get_rect()
            auxTextRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
            SCREEN.blit(auxText, auxTextRect)

            auxText = font.render("o cualquier otra letra para jugar automáticamente", True, (0, 0, 0))
            auxTextRect = auxText.get_rect()
            auxTextRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150)
            SCREEN.blit(auxText, auxTextRect)
        elif generation > 1:
            text = font.render("Pulse cualquier tecla para reiniciar", True, (0, 0, 0))
            score = font.render("Mejor puntuación: " + str(bestScore), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)


        textRect = text.get_rect()

        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if generation == 1:
                    playMode = pygame.key.name(event.key)

                    if playMode == 'm' or playMode == 'c' or playMode == 'a':
                        population = []
                gameScreen()

def count_alive(population):
    alive = 0
    for dino in population:
        if dino.alive:
            alive += 1
    return alive

if __name__ == "__main__":
    menu()
