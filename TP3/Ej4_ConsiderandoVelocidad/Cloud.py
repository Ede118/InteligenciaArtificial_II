import pygame
import os
import random
from pathlib import Path

# Bring images from assets
BASE_DIR = Path(__file__).resolve().parent
CLOUD = pygame.image.load(str(BASE_DIR / "Assets" / "Other" / "Cloud.png"))

class Cloud:
    def __init__(self, screen_width, game_speed):
        self.game_speed = game_speed
        self.screen_width = screen_width
        self.x = self.screen_width + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    # Update the cloud's position on screen
    def update(self):
        self.x -= self.game_speed
        if self.x < -self.width:
            self.x = self.screen_width + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    # Draw the element on screen
    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))
