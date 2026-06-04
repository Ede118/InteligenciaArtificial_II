import subprocess
import sys
try:
    import tensorflow as tf
except ImportError as err:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tensorflow'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])
    import tensorflow as tf

import json
import pygame
import os
from pathlib import Path
from NeuralNetwork import NeuralNetwork
import numpy as np
from TensorflowImageUtils import (
    IMAGE_SIZE,
    MODEL_METADATA_FILENAME,
    MODEL_OUTPUT_CLASSES,
    load_and_preprocess_image,
    normalize_speed,
)

# Bring images from assets
CLASSES = MODEL_OUTPUT_CLASSES
BASE_DIR = Path(__file__).resolve().parent
LIVE_CAPTURE_PATH = BASE_DIR / "images" / "live" / "temp.png"
RUNNING = [
    str(BASE_DIR / "Assets" / "Dino" / "DinoRun1.png"),
    str(BASE_DIR / "Assets" / "Dino" / "DinoRun2.png"),
]
JUMPING = [str(BASE_DIR / "Assets" / "Dino" / "DinoJump.png")]
DUCKING = [
    str(BASE_DIR / "Assets" / "Dino" / "DinoDuck1.png"),
    str(BASE_DIR / "Assets" / "Dino" / "DinoDuck2.png"),
]
MODEL_CONFIGS = {
    "lightweight_relu": (
        BASE_DIR / "tensorflow_nn_lightweight_relu.h5",
        BASE_DIR / "tensorflow_nn_lightweight_relu_metadata.json",
    ),
    "default": (
        BASE_DIR / "tensorflow_nn.h5",
        BASE_DIR / MODEL_METADATA_FILENAME,
    ),
}
DEFAULT_MODEL_PRIORITY = ["lightweight_relu", "default"]

class Dinosaur(NeuralNetwork):
    # Define as global the starting position for the dinosaur
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5
    PREDICTION_SMOOTHING = 0.35
    JUMP_CONFIDENCE_THRESHOLD = 0.45
    DUCK_CONFIDENCE_THRESHOLD = 0.35
    ACTION_MARGIN = 0.05
    SIGNAL_FRAMES_REQUIRED = 1

    def __init__(self, id, mask_color = None, autoplay = False, model_preference=None):
        # As 'NeuralNetwork' serves as base class for the dinosaur, start its 'brain'
        super().__init__()
        
        self.id = id
        self.color = mask_color
        self.autoPlay = autoplay
        self.duck_img = self.load_images(DUCKING)
        self.run_img = self.load_images(RUNNING)
        self.jump_img = self.load_images(JUMPING)
        self.model_preference = model_preference
        self.loaded_model_name = None
        self.loaded_model_path = None

        self.resetStatus()
        self.model_metadata = None
        self.uses_speed_input = False
        
        self.load_preferred_model()

    def load_preferred_model(self):
        selected_model_path = None
        selected_metadata_path = None
        selected_model_name = None

        model_priority = []
        if self.model_preference is not None:
            model_priority.append(self.model_preference)
        model_priority.extend(
            model_name for model_name in DEFAULT_MODEL_PRIORITY if model_name not in model_priority
        )

        for model_name in model_priority:
            config = MODEL_CONFIGS.get(model_name)
            if config is None:
                continue
            model_path, metadata_path = config
            if model_path.is_file():
                selected_model_name = model_name
                selected_model_path = model_path
                selected_metadata_path = metadata_path
                break

        if selected_model_path is None:
            fallback_models = sorted(BASE_DIR.glob("*.h5"))
            if not fallback_models:
                return
            selected_model_name = "fallback"
            selected_model_path = fallback_models[0]
            selected_metadata_path = BASE_DIR / MODEL_METADATA_FILENAME

        self.model = tf.keras.models.load_model(selected_model_path, compile=False)
        self.uses_speed_input = isinstance(self.model.input_shape, list)
        self.loaded_model_name = selected_model_name
        self.loaded_model_path = selected_model_path
        self.load_model_metadata(selected_metadata_path)

    def set_model_preference(self, model_preference):
        self.model_preference = model_preference
        self.model_metadata = None
        self.uses_speed_input = False
        self.loaded_model_name = None
        self.loaded_model_path = None
        self.load_preferred_model()

    def load_model_metadata(self, metadata_path):
        metadata_path = Path(metadata_path)
        if not metadata_path.is_file():
            return

        with metadata_path.open("r", encoding="utf-8") as metadata_file:
            self.model_metadata = json.load(metadata_file)

    # Basic state the dinosaur is in when spawning
    def resetStatus(self):
        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

        self.alive = True
        self.score = 0
        self.smoothed_probabilities = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        self.jump_signal_frames = 0
        self.duck_signal_frames = 0

    # Load the image form assets masking it with a layer of the selected color for this dino
    def load_images(self, base_name):
        images = []
        for image_path in base_name:
            result = pygame.image.load(image_path).convert_alpha()

            # Apply the color mask if a color is selected
            if self.color:
                result.fill(self.color, special_flags=pygame.BLEND_ADD)
            images.append(result)

        return images

    # Update the dinosaur's status
    def update(self, userInput):
        # Execute the corresponding actions for the current state
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        # Set the next state for the dinosaur. The selection mode depends on the playmode selected for the game.
        if self.autoPlay:
            if userInput == "JUMP" and not self.dino_jump:
                self.dino_duck = False
                self.dino_run = False
                self.dino_jump = True
            elif userInput == "DUCK":
                self.dino_duck = True
                self.dino_run = False
                self.dino_jump = False
            elif not (self.dino_jump or userInput == "DUCK"):
                self.dino_duck = False
                self.dino_run = True
                self.dino_jump = False
        else:
            if userInput[pygame.K_UP] and not self.dino_jump:
                self.dino_duck = False
                self.dino_run = False
                self.dino_jump = True
            elif userInput[pygame.K_DOWN]:
                self.dino_duck = True
                self.dino_run = False
                self.dino_jump = False
            elif not (self.dino_jump or userInput[pygame.K_DOWN]):
                self.dino_duck = False
                self.dino_run = True
                self.dino_jump = False

        # Avoid cloud-walking
        if not self.dino_jump and self.dino_rect.y < self.Y_POS:
            self.dino_rect.y += 8
            if self.dino_rect.y >= self.Y_POS:
                self.dino_rect.y = self.Y_POS

    def duck(self):
        # Change the image every 5 frames to walk
        self.image = self.duck_img[self.step_index // 5]

        # If we duck on mid-air, fall faster by aumenting rapidly the dinosaur's height until reaching ground
        if (self.dino_rect.y < self.Y_POS):
            self.dino_rect.y += self.JUMP_VEL * 6
            if (self.dino_rect.y >= self.Y_POS_DUCK):
                self.dino_rect.y = self.Y_POS_DUCK
        # Set the ducking position when grounded
        else:
            self.dino_rect = self.image.get_rect()
            self.dino_rect.x = self.X_POS
            self.dino_rect.y = self.Y_POS_DUCK
            self.jump_vel = self.JUMP_VEL

        self.step_index += 1

    def run(self):
        # Change the image every 5 frames to walk
        self.image = self.run_img[self.step_index // 5]

        # Set the running position
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

        self.step_index += 1

    def jump(self):
        # Change the image
        self.image = self.jump_img[0]

        # Reduce the dinosaur's position until the jumping speed is negative; then fall 
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8

            # Prevent going through the ground
            if self.dino_rect.y >= self.Y_POS:
                self.dino_rect.y = self.Y_POS
                self.dino_jump = False
                self.jump_vel = self.JUMP_VEL

    # Draw the element on screen
    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

    def choose_action(self, probabilities):
        jump_prob, duck_prob, right_prob = probabilities

        if self.dino_jump:
            self.jump_signal_frames = 0
            self.duck_signal_frames = 0
            return "RIGHT"

        jump_margin = jump_prob - max(duck_prob, right_prob)
        duck_margin = duck_prob - max(jump_prob, right_prob)

        if jump_prob >= self.JUMP_CONFIDENCE_THRESHOLD and jump_margin >= self.ACTION_MARGIN:
            self.jump_signal_frames += 1
        else:
            self.jump_signal_frames = 0

        if duck_prob >= self.DUCK_CONFIDENCE_THRESHOLD and duck_margin >= self.ACTION_MARGIN:
            self.duck_signal_frames += 1
        else:
            self.duck_signal_frames = 0

        if self.jump_signal_frames >= self.SIGNAL_FRAMES_REQUIRED:
            self.jump_signal_frames = 0
            self.duck_signal_frames = 0
            return "JUMP"

        if self.duck_signal_frames >= self.SIGNAL_FRAMES_REQUIRED:
            self.duck_signal_frames = 0
            return "DUCK"

        return "RIGHT"

    # When playing in automatic mode using the tensorflow model, takes a frame and sends it to the model to define the next action
    def predict(self, game_speed=None):
        self.autoPlay = True
        
        # Usa exactamente el mismo preprocesado que el entrenamiento.
        img_array = load_and_preprocess_image(str(LIVE_CAPTURE_PATH), IMAGE_SIZE, normalize=True)
        img_array = np.expand_dims(img_array, axis=0)  # Agrega una dimensión extra para el batch

        # Use the model to make a decision based on the screenshot
        if self.uses_speed_input:
            if self.model_metadata is None:
                raise ValueError(
                    "El modelo espera una entrada de velocidad pero falta tensorflow_nn_metadata.json."
                )
            if game_speed is None:
                raise ValueError(
                    "El modelo espera la velocidad actual del juego para predecir."
                )

            speed_value = normalize_speed(
                game_speed,
                self.model_metadata["speed_min"],
                self.model_metadata["speed_max"],
            )
            speed_array = np.asarray([[speed_value]], dtype=np.float32)
            predictions = self.model.predict([img_array, speed_array], verbose=0)[0]
        else:
            predictions = self.model.predict(img_array, verbose=0)[0]
        self.smoothed_probabilities = (
            self.PREDICTION_SMOOTHING * self.smoothed_probabilities
            + (1.0 - self.PREDICTION_SMOOTHING) * predictions
        )
        action = self.choose_action(self.smoothed_probabilities)

        # Call the update method with the result
        self.update(action)
