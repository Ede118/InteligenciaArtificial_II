import csv
import json
import os
import random
import shutil
import subprocess
import sys
import time

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

from EvaluateTensorflowModel import (
    compute_metrics,
    plot_class_metrics,
    plot_confusion_matrix,
    plot_misclassified_examples,
    plot_test_error,
    print_summary,
    save_metrics_report,
)
from TensorflowImageUtils import (
    CLASS_FOLDER_NAMES,
    IMAGE_SIZE,
    LABELS_FILENAME,
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
OUTPUT_ROOT_DIR = "evaluation_results"

CLASSES = CLASS_FOLDER_NAMES
TRAIN_RATIO = 0.8
BATCH_SIZE = 32
EPOCHS = 15
INPUT_SHAPE = IMAGE_SIZE + (1,)
SHOW_PLOTS = False

MODEL_VARIANTS = [
    {
        "name": "lightweight_relu",
        "filters": [16, 32, 64],
        "activation": "relu",
        "model_path": "tensorflow_nn_lightweight_relu.h5",
        "metadata_path": "tensorflow_nn_lightweight_relu_metadata.json",
        "output_dir": os.path.join(OUTPUT_ROOT_DIR, "lightweight_relu"),
    },
    {
        "name": "lightweight_sigmoid",
        "filters": [16, 32, 64],
        "activation": "sigmoid",
        "model_path": "tensorflow_nn_lightweight_sigmoid.h5",
        "metadata_path": "tensorflow_nn_lightweight_sigmoid_metadata.json",
        "output_dir": os.path.join(OUTPUT_ROOT_DIR, "lightweight_sigmoid"),
    },
]


def balance_rows(rows):
    rows_by_class = {}
    for class_name in CLASSES:
        class_rows = [row for row in rows if row["class_name"] == class_name]
        random.shuffle(class_rows)
        rows_by_class[class_name] = class_rows

    min_count = min(len(class_rows) for class_rows in rows_by_class.values())
    balanced_rows = []
    original_counts = {}

    for class_name in CLASSES:
        original_counts[class_name] = len(rows_by_class[class_name])
        balanced_rows.extend(rows_by_class[class_name][:min_count])

    random.shuffle(balanced_rows)
    return balanced_rows, min_count, original_counts


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
    file_paths = []

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
        file_paths.append(row["image_path"])

    x_images = np.asarray(images, dtype=np.float32)
    x_speeds = np.asarray(speeds, dtype=np.float32)
    y_indices = np.asarray(labels, dtype=np.int32)
    y_labels = tf.keras.utils.to_categorical(y_indices, num_classes=len(CLASSES))
    return x_images, x_speeds, y_indices, y_labels, file_paths


def build_model(filters, activation):
    image_input = tf.keras.Input(shape=INPUT_SHAPE, name="image")
    x = image_input
    for filter_count in filters:
        x = tf.keras.layers.Conv2D(filter_count, (3, 3), activation=activation)(x)
        x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Flatten()(x)

    speed_input = tf.keras.Input(shape=(1,), name="speed")
    speed_branch = tf.keras.layers.Dense(16, activation=activation)(speed_input)

    combined = tf.keras.layers.Concatenate()([x, speed_branch])
    combined = tf.keras.layers.Dense(128, activation=activation)(combined)
    combined = tf.keras.layers.Dropout(0.5)(combined)
    output = tf.keras.layers.Dense(len(CLASSES), activation="softmax")(combined)

    model = tf.keras.Model(inputs=[image_input, speed_input], outputs=output)
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def save_model_metadata(metadata_path, speed_min, speed_max, variant):
    metadata = {
        "class_folder_names": CLASSES,
        "model_output_classes": MODEL_OUTPUT_CLASSES,
        "image_size": list(IMAGE_SIZE),
        "speed_min": float(speed_min),
        "speed_max": float(speed_max),
        "labels_filename": LABELS_FILENAME,
        "model_variant": variant["name"],
        "filters": variant["filters"],
        "hidden_activation": variant["activation"],
    }
    if "dataset_strategy" in variant:
        metadata["dataset_strategy"] = variant["dataset_strategy"]
    if "class_target_count" in variant:
        metadata["class_target_count"] = int(variant["class_target_count"])

    with open(metadata_path, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2, ensure_ascii=False)


def serialize_history(history):
    serialized = {}
    for key, values in history.history.items():
        serialized[key] = [float(value) for value in values]
    return serialized


def save_training_summary(output_dir, variant, model, history, training_seconds, evaluation_seconds, test_loss, test_accuracy):
    os.makedirs(output_dir, exist_ok=True)
    history_data = serialize_history(history)
    history_path = os.path.join(output_dir, "training_history.json")
    with open(history_path, "w", encoding="utf-8") as history_file:
        json.dump(history_data, history_file, indent=2, ensure_ascii=False)

    val_accuracy_history = history_data.get("val_accuracy", [])
    val_loss_history = history_data.get("val_loss", [])

    summary = {
        "variant_name": variant["name"],
        "filters": variant["filters"],
        "hidden_activation": variant["activation"],
        "parameter_count": int(model.count_params()),
        "epochs_ran": len(history_data.get("loss", [])),
        "training_seconds": float(training_seconds),
        "evaluation_seconds": float(evaluation_seconds),
        "keras_test_loss": float(test_loss),
        "keras_test_accuracy": float(test_accuracy),
        "best_val_accuracy": max(val_accuracy_history) if val_accuracy_history else None,
        "best_val_loss": min(val_loss_history) if val_loss_history else None,
    }
    if "dataset_strategy" in variant:
        summary["dataset_strategy"] = variant["dataset_strategy"]
    if "class_target_count" in variant:
        summary["class_target_count"] = int(variant["class_target_count"])

    summary_path = os.path.join(output_dir, "training_summary.json")
    with open(summary_path, "w", encoding="utf-8") as summary_file:
        json.dump(summary, summary_file, indent=2, ensure_ascii=False)


def evaluate_and_save_results(
    model,
    x_test_images,
    x_test_speeds,
    y_test_indices,
    test_file_paths,
    output_dir,
):
    os.makedirs(output_dir, exist_ok=True)

    evaluation_start = time.perf_counter()
    test_loss, test_accuracy = model.evaluate(
        [x_test_images, x_test_speeds],
        tf.keras.utils.to_categorical(y_test_indices, num_classes=len(CLASSES)),
        verbose=0,
    )
    probabilities = model.predict([x_test_images, x_test_speeds], verbose=0)
    y_pred = np.argmax(probabilities, axis=1)
    metrics = compute_metrics(y_test_indices, y_pred, probabilities, CLASSES)
    evaluation_seconds = time.perf_counter() - evaluation_start

    save_metrics_report(metrics, output_dir)
    plot_confusion_matrix(metrics["confusion_matrix"], CLASSES, output_dir, SHOW_PLOTS)
    plot_test_error(metrics, output_dir, SHOW_PLOTS)
    plot_class_metrics(metrics, output_dir, SHOW_PLOTS)
    plot_misclassified_examples(
        test_file_paths,
        y_test_indices,
        y_pred,
        CLASSES,
        IMAGE_SIZE,
        output_dir,
        SHOW_PLOTS,
    )
    print_summary(metrics, CLASSES)

    return metrics, float(test_loss), float(test_accuracy), float(evaluation_seconds)


def train_variant(
    variant,
    x_train_images,
    x_train_speeds,
    y_train,
    x_test_images,
    x_test_speeds,
    y_test_indices,
    test_file_paths,
    speed_min,
    speed_max,
):
    print(
        "\nEntrenando variante "
        f"{variant['name']} con filtros {variant['filters']} y activacion {variant['activation']}..."
    )
    model = build_model(variant["filters"], variant["activation"])
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
        )
    ]

    training_start = time.perf_counter()
    history = model.fit(
        [x_train_images, x_train_speeds],
        y_train,
        validation_data=(
            [x_test_images, x_test_speeds],
            tf.keras.utils.to_categorical(y_test_indices, num_classes=len(CLASSES)),
        ),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )
    training_seconds = time.perf_counter() - training_start

    model.save(variant["model_path"])
    save_model_metadata(variant["metadata_path"], speed_min, speed_max, variant)

    _, test_loss, test_accuracy, evaluation_seconds = evaluate_and_save_results(
        model,
        x_test_images,
        x_test_speeds,
        y_test_indices,
        test_file_paths,
        variant["output_dir"],
    )
    save_training_summary(
        variant["output_dir"],
        variant,
        model,
        history,
        training_seconds,
        evaluation_seconds,
        test_loss,
        test_accuracy,
    )

    print(f"Modelo guardado en {variant['model_path']}")
    print(f"Metadata guardada en {variant['metadata_path']}")
    print(f"Resultados guardados en {os.path.abspath(variant['output_dir'])}")


def main():
    random.seed(42)
    np.random.seed(42)
    tf.random.set_seed(42)

    print("Cargando capturas y metadata de velocidad...")
    source_rows = load_capture_metadata(SOURCE_LABELS_PATH)

    print("Generando split train/test compartido para todas las variantes...")
    train_source_rows, test_source_rows = stratified_split(source_rows, TRAIN_RATIO)

    reset_split_directories()
    train_rows = save_split_rows(train_source_rows, TRAIN_DIR, TRAIN_LABELS_PATH)
    test_rows = save_split_rows(test_source_rows, TEST_DIR, TEST_LABELS_PATH)

    speed_values = [row["game_speed"] for row in train_rows]
    speed_min = min(speed_values)
    speed_max = max(speed_values)

    print("Construyendo datasets con imagen + velocidad...")
    x_train_images, x_train_speeds, _, y_train, _ = build_dataset(
        train_rows,
        speed_min,
        speed_max,
    )
    x_test_images, x_test_speeds, y_test_indices, _, test_file_paths = build_dataset(
        test_rows,
        speed_min,
        speed_max,
    )

    print(f"Train: {len(train_rows)} muestras")
    print(f"Test:  {len(test_rows)} muestras")
    print(f"Rango de velocidad train: {speed_min} - {speed_max}")

    for variant in MODEL_VARIANTS:
        train_variant(
            variant,
            x_train_images,
            x_train_speeds,
            y_train,
            x_test_images,
            x_test_speeds,
            y_test_indices,
            test_file_paths,
            speed_min,
            speed_max,
        )


if __name__ == "__main__":
    main()
