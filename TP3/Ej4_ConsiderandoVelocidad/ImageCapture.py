import subprocess
import sys
try:
    import pyscreenshot
except ImportError as err:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyscreenshot'])
    import pyscreenshot

import csv
from pathlib import Path
import pygame
from TensorflowImageUtils import LABELS_FILENAME, get_capture_bbox

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"

class ImageCapture():
    RIGHT_SAVE_EVERY_N_FRAMES = 5

    def __init__(self, screen_spawn_position):
        # Parameters to adjust the window to capture
        self.count = 0
        self.window_left = screen_spawn_position[0]
        self.window_top = screen_spawn_position[1]
        self.right_capture_counter = 0

        # Prepare the directories in which the images are stored
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        (IMAGES_DIR / "up").mkdir(parents=True, exist_ok=True)
        (IMAGES_DIR / "down").mkdir(parents=True, exist_ok=True)
        (IMAGES_DIR / "right").mkdir(parents=True, exist_ok=True)
        (IMAGES_DIR / "live").mkdir(parents=True, exist_ok=True)
        self.labels_path = IMAGES_DIR / LABELS_FILENAME
        self.ensure_labels_file()
        self.sync_count_with_existing_images()

    def ensure_labels_file(self):
        if self.labels_path.exists():
            return

        with self.labels_path.open("w", newline="", encoding="utf-8") as labels_file:
            writer = csv.DictWriter(
                labels_file,
                fieldnames=["relative_path", "class_name", "game_speed", "points"],
            )
            writer.writeheader()

    def sync_count_with_existing_images(self):
        max_count = 0

        for class_name in ["up", "down", "right"]:
            class_dir = IMAGES_DIR / class_name
            for image_path in class_dir.glob("*.png"):
                try:
                    max_count = max(max_count, int(image_path.stem))
                except ValueError:
                    continue

        self.count = max_count

    def take_screenshot(self, key, game_speed=None, points=None):
        screenshot = pyscreenshot.grab(bbox=get_capture_bbox(self.window_left, self.window_top))
        self.save_screenshot(screenshot, key, game_speed, points)

    def save_screenshot(self, screenshot, key, game_speed=None, points=None):
        self.count += 1
        relative_path = "{}/{}.png".format(key, self.count)
        screenshot.save(str(IMAGES_DIR / relative_path))

        if game_speed is not None:
            with self.labels_path.open("a", newline="", encoding="utf-8") as labels_file:
                writer = csv.DictWriter(
                    labels_file,
                    fieldnames=["relative_path", "class_name", "game_speed", "points"],
                )
                writer.writerow(
                    {
                        "relative_path": relative_path.replace("\\", "/"),
                        "class_name": key,
                        "game_speed": game_speed,
                        "points": points if points is not None else "",
                    }
                )

    def capture(self, userInput, game_speed, points):
        # Take a screenshot on command and tag it on the pressed button folder
        screenshot = pyscreenshot.grab(bbox=get_capture_bbox(self.window_left, self.window_top))

        if userInput[pygame.K_UP]:
            self.save_screenshot(screenshot, "up", game_speed, points)

        elif userInput[pygame.K_DOWN]:
            self.save_screenshot(screenshot, "down", game_speed, points)

        else:
            self.right_capture_counter += 1
            if self.right_capture_counter >= self.RIGHT_SAVE_EVERY_N_FRAMES:
                self.right_capture_counter = 0
                self.save_screenshot(screenshot, "right", game_speed, points)

    def capture_live(self):
        # Automatically take a screenshot for the Tensorflow model to work
        screenshot = pyscreenshot.grab(bbox=get_capture_bbox(self.window_left, self.window_top))
        screenshot.save(str(IMAGES_DIR / "live" / "temp.png"))
