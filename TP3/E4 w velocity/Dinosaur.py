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
    "two_layer_relu": (
        BASE_DIR / "tensorflow_nn_two_layer_relu.h5",
        BASE_DIR / "tensorflow_nn_two_layer_relu_metadata.json",
    ),
    "binary_relu_sigmoid_up_down": (
        BASE_DIR / "tensorflow_nn_binary_relu_sigmoid_up_down.h5",
        BASE_DIR / "tensorflow_nn_binary_relu_sigmoid_up_down_metadata.json",
    ),
    "default": (
        BASE_DIR / "tensorflow_nn.h5",
        BASE_DIR / MODEL_METADATA_FILENAME,
    ),
}
DEFAULT_MODEL_PRIORITY = ["lightweight_relu", "two_layer_relu", "default"]

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
    BINARY_PREDICTION_SMOOTHING = 0.65
    BINARY_UP_THRESHOLD = 0.97
    BINARY_DOWN_THRESHOLD = 0.85
    BINARY_NEUTRAL_BAND = 0.08
    BINARY_REACTION_FRAMES = 7
    BINARY_EMERGENCY_FRAMES = 3
    BINARY_DISTANCE_BUFFER = 35
    AIR_OBSTACLE_BOTTOM_THRESHOLD = 300

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

    def is_binary_up_down_model(self):
        if self.model_metadata is None:
            return False

        if self.model_metadata.get("task") == "binary_up_down":
            return True

        classes = self.model_metadata.get("classes")
        return classes == ["up", "down"]

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
        self.binary_down_probability = 0.5
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

    def choose_binary_action(self, down_probability):
        return self.choose_binary_action_with_obstacle(down_probability, None, None)

    def get_binary_obstacle_context(self, obstacle, game_speed):
        if obstacle is None or game_speed is None:
            return None

        distance_x = obstacle.rect.x - self.dino_rect.right
        reaction_distance = (
            game_speed * self.BINARY_REACTION_FRAMES
            + obstacle.rect.width
            + self.BINARY_DISTANCE_BUFFER
        )
        emergency_distance = (
            game_speed * self.BINARY_EMERGENCY_FRAMES
            + obstacle.rect.width // 2
        )
        is_air_obstacle = obstacle.rect.bottom <= self.AIR_OBSTACLE_BOTTOM_THRESHOLD

        return {
            "distance_x": distance_x,
            "reaction_distance": reaction_distance,
            "emergency_distance": emergency_distance,
            "is_air_obstacle": is_air_obstacle,
        }

    def choose_binary_fallback_action(self, obstacle_context):
        if obstacle_context is None:
            return "RIGHT"
        if obstacle_context["is_air_obstacle"]:
            return "DUCK"
        return "JUMP"

    def should_hold_duck_for_obstacle(self, obstacle_context, obstacle):
        if not self.dino_duck or obstacle_context is None or obstacle is None:
            return False
        if not obstacle_context["is_air_obstacle"]:
            return False

        return obstacle.rect.x <= self.dino_rect.right + obstacle.rect.width

    def commit_binary_action(self, action):
        if action == "JUMP":
            self.jump_signal_frames += 1
            self.duck_signal_frames = 0
        elif action == "DUCK":
            self.duck_signal_frames += 1
            self.jump_signal_frames = 0
        else:
            self.jump_signal_frames = 0
            self.duck_signal_frames = 0

        if self.jump_signal_frames >= self.SIGNAL_FRAMES_REQUIRED:
            self.jump_signal_frames = 0
            self.duck_signal_frames = 0
            return "JUMP"

        if self.duck_signal_frames >= self.SIGNAL_FRAMES_REQUIRED:
            self.duck_signal_frames = 0
            return "DUCK"

        return "RIGHT"

    def choose_binary_action_with_obstacle(self, down_probability, obstacle, game_speed):
        if self.dino_jump:
            self.jump_signal_frames = 0
            self.duck_signal_frames = 0
            return "RIGHT"

        obstacle_context = self.get_binary_obstacle_context(obstacle, game_speed)
        if obstacle_context is None:
            self.jump_signal_frames = 0
            self.duck_signal_frames = 0
            return "RIGHT"

        if self.should_hold_duck_for_obstacle(obstacle_context, obstacle):
            return self.commit_binary_action("DUCK")

        if obstacle_context["distance_x"] > obstacle_context["reaction_distance"]:
            self.jump_signal_frames = 0
            self.duck_signal_frames = 0
            return "RIGHT"

        fallback_action = self.choose_binary_fallback_action(obstacle_context)
        distance_to_center = abs(down_probability - 0.5)

        if down_probability >= self.BINARY_DOWN_THRESHOLD:
            proposed_action = "DUCK"
        elif down_probability <= self.BINARY_UP_THRESHOLD:
            proposed_action = "JUMP"
        elif (
            distance_to_center <= self.BINARY_NEUTRAL_BAND
            and obstacle_context["distance_x"] > obstacle_context["emergency_distance"]
        ):
            proposed_action = "RIGHT"
        else:
            proposed_action = fallback_action

        if (
            obstacle_context["distance_x"] <= obstacle_context["emergency_distance"]
            and proposed_action != fallback_action
        ):
            proposed_action = fallback_action

        return self.commit_binary_action(proposed_action)

    # When playing in automatic mode using the tensorflow model, takes a frame and sends it to the model to define the next action
    def predict(self, game_speed=None, obstacle=None, img_array=None):
        self.autoPlay = True
        
        # Usa exactamente el mismo preprocesado que el entrenamiento.
        if img_array is None:
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

        if self.is_binary_up_down_model():
            down_probability = float(np.asarray(predictions).reshape(-1)[0])
            self.binary_down_probability = (
                self.BINARY_PREDICTION_SMOOTHING * self.binary_down_probability
                + (1.0 - self.BINARY_PREDICTION_SMOOTHING) * down_probability
            )
            action = self.choose_binary_action_with_obstacle(
                self.binary_down_probability,
                obstacle,
                game_speed,
            )
        else:
            self.smoothed_probabilities = (
                self.PREDICTION_SMOOTHING * self.smoothed_probabilities
                + (1.0 - self.PREDICTION_SMOOTHING) * predictions
            )
            action = self.choose_action(self.smoothed_probabilities)

        # Call the update method with the result
        self.update(action)
