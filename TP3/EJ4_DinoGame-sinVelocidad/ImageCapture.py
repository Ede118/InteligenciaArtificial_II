import subprocess
import sys
try:
    import pyscreenshot
except ImportError as err:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyscreenshot'])
    import pyscreenshot

import uuid
from pathlib import Path
import pygame
from TensorflowImageUtils import get_capture_bbox

class ImageCapture():
    def __init__(self, screen_spawn_position):
        # Parameters to adjust the window to capture
        self.count = 0
        self.window_left = screen_spawn_position[0]
        self.window_top = screen_spawn_position[1]

        # Prepare the directories in which the images are stored
        Path("./images/").mkdir(parents=True, exist_ok=True)
        Path("./images/up/").mkdir(parents=True, exist_ok=True)
        Path("./images/down/").mkdir(parents=True, exist_ok=True)
        Path("./images/right/").mkdir(parents=True, exist_ok=True)
        Path("./images/live/").mkdir(parents=True, exist_ok=True)
        self.ss_id = uuid.uuid4()

    def take_screenshot(self, key):
        # Save the screenshot
        self.count += 1
        screenshot = pyscreenshot.grab(bbox=get_capture_bbox(self.window_left, self.window_top))
        screenshot.save("./images/{}/{}.png".format(key, self.count))

    def capture(self, userInput):
        # Take a screenshot on command and tag it on the pressed button folder
        if userInput[pygame.K_UP]:
            self.take_screenshot("up")

        elif userInput[pygame.K_DOWN]:
            self.take_screenshot("down")

        else:
            self.take_screenshot("right")

    def capture_live(self):
        # Automatically take a screenshot for the Tensorflow model to work
        screenshot = pyscreenshot.grab(bbox=get_capture_bbox(self.window_left, self.window_top))
        screenshot.save("./images/live/temp.png")
