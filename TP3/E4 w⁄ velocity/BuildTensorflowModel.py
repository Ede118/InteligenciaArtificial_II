import csv
import json
import os
import random
import shutil
import subprocess
import sys

try:
    import numpy as np
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy as np

try:
    import tensorflow as tf
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflow"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    import tensorflow as tf

from tensorflow.keras.preprocessing.image import save_img
from TensorflowImageUtils import (
    CLASS_FOLDER_NAMES,
    IMAGE_SIZE,
    LABELS_FILENAME,
    MODEL_METADATA_FILENAME,
    MODEL_OUTPUT_CLASSES,
    load_and_preprocess_image,
    normalize_speed,
)


SOURCE_DIR = "images"
TRAIN_DIR = os.path.join(SOURCE_DIR, "train")
TEST_DIR = os.path.join(SOURCE_DIR, "test")
SOURCE_LABELS_PATH = os.path.join(SOURCE_DIR, LABELS_FILENAME)
TRAIN_LABELS_PATH = os.path.join(TRAIN_DIR, LABELS_FILENAME)
TEST_LABELS_PATH = os.path.join(TEST_DIR, LABELS_FILENAME)
MODEL_PATH = "tensorflow_nn.h5"

CLASSES = CLASS_FOLDER_NAMES
TRAIN_RATIO = 0.8
BATCH_SIZE = 32
EPOCHS = 15
IMAGE_SIZE = IMAGE_SIZE
INPUT_SHAPE = IMAGE_SIZE + (1,)


def reset_split_directories():
    for split_dir in [TRAIN_DIR, TEST_DIR]:
        if os.path.isdir(split_dir):
            shutil.rmtree(split_dir)
        os.makedirs(split_dir, exist_ok=True)

        for class_name in CLASSES:
            os.makedirs(os.path.join(split_dir, class_name), exist_ok=True)


def load_capture_metadata(metadata_path):
    if not os.path.isfile(metadata_path):
        raise FileNotFoundError(
            f"No se encontro {metadata_path}. "
            "Para esta version del modelo hace falta capturar imagenes junto con su game_speed."
        )

    rows = []
    with open(metadata_path, "r", newline="", encoding="utf-8") as metadata_file:
        reader = csv.DictReader(metadata_file)
        required_columns = {"relative_path", "class_name", "game_speed"}
        missing_columns = required_columns.difference(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(
                "El archivo de labels no tiene las columnas necesarias: "
                + ", ".join(sorted(missing_columns))
            )

        for row in reader:
            class_name = row["class_name"].strip()
            if class_name not in CLASSES:
                continue

            relative_path = row["relative_path"].replace("/", os.sep).replace("\\", os.sep)
            image_path = os.path.join(SOURCE_DIR, relative_path)
            if not os.path.isfile(image_path):
                continue

            rows.append(
                {
                    "source_image_path": image_path,
                    "class_name": class_name,
                    "game_speed": float(row["game_speed"]),
                    "points": row.get("points", "").strip(),
                }
            )

    if not rows:
        raise ValueError("No se encontraron capturas validas en el archivo de labels.")

    return rows


def stratified_split(rows, train_ratio):
    train_rows = []
    test_rows = []

    for class_name in CLASSES:
        class_rows = [row for row in rows if row["class_name"] == class_name]
        random.shuffle(class_rows)

        split_index = int(len(class_rows) * train_ratio)
        if split_index <= 0 and len(class_rows) > 1:
            split_index = 1
        if split_index >= len(class_rows) and len(class_rows) > 1:
            split_index = len(class_rows) - 1

        train_rows.extend(class_rows[:split_index])
        test_rows.extend(class_rows[split_index:])

    if not train_rows or not test_rows:
        raise ValueError(
            "No se pudo generar una division train/test valida. "
            "Asegurate de tener varias capturas por clase."
        )

    return train_rows, test_rows


def save_split_rows(rows, split_dir, labels_path):
    saved_rows = []

    with open(labels_path, "w", newline="", encoding="utf-8") as labels_file:
        writer = csv.DictWriter(
            labels_file,
            fieldnames=["relative_path", "class_name", "game_speed", "points"],
        )
        writer.writeheader()

        for index, row in enumerate(rows, start=1):
            original_name = os.path.basename(row["source_image_path"])
            destination_name = f"{index:05d}_{original_name}"
            destination_relative_path = os.path.join(row["class_name"], destination_name)
            destination_path = os.path.join(split_dir, destination_relative_path)

            image_array = load_and_preprocess_image(row["source_image_path"], IMAGE_SIZE)
            save_img(destination_path, image_array)

            saved_row = {
                "relative_path": destination_relative_path.replace("\\", "/"),
                "class_name": row["class_name"],
                "game_speed": row["game_speed"],
                "points": row["points"],
            }
            writer.writerow(saved_row)

            saved_rows.append(
                {
                    "image_path": destination_path,
                    "class_name": row["class_name"],
                    "game_speed": row["game_speed"],
                    "points": row["points"],
                }
            )

    return saved_rows


def build_dataset(rows, speed_min, speed_max):
    images = []
    speeds = []
    labels = []

    for row in rows:
        image_array = load_and_preprocess_image(
            row["image_path"],
            IMAGE_SIZE,
            normalize=True,
        )
        normalized_speed = normalize_speed(row["game_speed"], speed_min, speed_max)

        images.append(image_array)
        speeds.append([normalized_speed])
        labels.append(CLASSES.index(row["class_name"]))

    x_images = np.asarray(images, dtype=np.float32)
    x_speeds = np.asarray(speeds, dtype=np.float32)
    y_labels = tf.keras.utils.to_categorical(labels, num_classes=len(CLASSES))
    return x_images, x_speeds, y_labels


def build_model():
    image_input = tf.keras.Input(shape=INPUT_SHAPE, name="image")
    x = tf.keras.layers.Conv2D(32, (3, 3), activation="relu")(image_input)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(64, (3, 3), activation="relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(128, (3, 3), activation="relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Flatten()(x)

    speed_input = tf.keras.Input(shape=(1,), name="speed")
    speed_branch = tf.keras.layers.Dense(16, activation="relu")(speed_input)

    combined = tf.keras.layers.Concatenate()([x, speed_branch])
    combined = tf.keras.layers.Dense(128, activation="relu")(combined)
    combined = tf.keras.layers.Dropout(0.5)(combined)
    output = tf.keras.layers.Dense(len(CLASSES), activation="softmax")(combined)

    model = tf.keras.Model(inputs=[image_input, speed_input], outputs=output)
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def save_model_metadata(speed_min, speed_max):
    metadata = {
        "class_folder_names": CLASSES,
        "model_output_classes": MODEL_OUTPUT_CLASSES,
        "image_size": list(IMAGE_SIZE),
        "speed_min": float(speed_min),
        "speed_max": float(speed_max),
        "labels_filename": LABELS_FILENAME,
    }

    with open(MODEL_METADATA_FILENAME, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2, ensure_ascii=False)


def main():
    random.seed(42)
    np.random.seed(42)
    tf.random.set_seed(42)

    print("Cargando capturas y metadata de velocidad...")
    source_rows = load_capture_metadata(SOURCE_LABELS_PATH)

    print("Generando split train/test...")
    train_source_rows, test_source_rows = stratified_split(source_rows, TRAIN_RATIO)

    reset_split_directories()
    train_rows = save_split_rows(train_source_rows, TRAIN_DIR, TRAIN_LABELS_PATH)
    test_rows = save_split_rows(test_source_rows, TEST_DIR, TEST_LABELS_PATH)

    speed_values = [row["game_speed"] for row in train_rows]
    speed_min = min(speed_values)
    speed_max = max(speed_values)

    print("Construyendo datasets con imagen + velocidad...")
    x_train_images, x_train_speeds, y_train = build_dataset(train_rows, speed_min, speed_max)
    x_test_images, x_test_speeds, y_test = build_dataset(test_rows, speed_min, speed_max)

    print(f"Train: {len(train_rows)} muestras")
    print(f"Test:  {len(test_rows)} muestras")
    print(f"Rango de velocidad train: {speed_min} - {speed_max}")

    model = build_model()
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
        )
    ]

    model.fit(
        [x_train_images, x_train_speeds],
        y_train,
        validation_data=([x_test_images, x_test_speeds], y_test),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )

    model.save(MODEL_PATH)
    save_model_metadata(speed_min, speed_max)
    print(f"Modelo guardado en {MODEL_PATH}")
    print(f"Metadata del modelo guardada en {MODEL_METADATA_FILENAME}")


if __name__ == "__main__":
    main()
