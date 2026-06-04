import pygame
import os
import random
from pathlib import Path
from Obstacle import Obstacle

# Bring images from assets
BASE_DIR = Path(__file__).resolve().parent
LARGE_CACTUS = [
    pygame.image.load(str(BASE_DIR / "Assets" / "Cactus" / "LargeCactus1.png")),
    pygame.image.load(str(BASE_DIR / "Assets" / "Cactus" / "LargeCactus2.png")),
    pygame.image.load(str(BASE_DIR / "Assets" / "Cactus" / "LargeCactus3.png")),
]

class LargeCactus(Obstacle):
    def __init__(self, screen_width, game_speed, obstacles):
        # Charge the base class with information, select the cactus' amount and the image shown when appears
        self.type = random.randint(0, 2)
        super().__init__(LARGE_CACTUS, self.type, screen_width, game_speed, obstacles)
        self.rect.y = 300
