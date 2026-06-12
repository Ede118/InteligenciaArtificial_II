import json
import random
import time
from pathlib import Path

import numpy as np
import tensorflow as tf

from BuildTensorflowModelVariants import (
    SOURCE_LABELS_PATH,
    load_capture_metadata,
)
from TensorflowImageUtils import IMAGE_SIZE, load_and_preprocess_image, normalize_speed


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "evaluation_results" / "binary_relu_sigmoid_up_down"
MODEL_PATH = BASE_DIR / "tensorflow_nn_binary_relu_sigmoid_up_down.h5"
METADATA_PATH = BASE_DIR / "tensorflow_nn_binary_relu_sigmoid_up_down_metadata.json"

TARGET_CLASSES = ["up", "down"]
TRAIN_RATIO = 0.8
BATCH_SIZE = 32
EPOCHS = 15
INPUT_SHAPE = IMAGE_SIZE + (1,)


def filter_and_balance_rows(rows):
    filtered = [row for row in rows if row["class_name"] in TARGET_CLASSES]
    rows_by_class = {}
    for class_name in TARGET_CLASSES:
        class_rows = [row for row in filtered if row["class_name"] == class_name]
        random.shuffle(class_rows)
        rows_by_class[class_name] = class_rows

    min_count = min(len(class_rows) for class_rows in rows_by_class.values())
    balanced_rows = []
    original_counts = {class_name: len(rows_by_class[class_name]) for class_name in TARGET_CLASSES}

    for class_name in TARGET_CLASSES:
        balanced_rows.extend(rows_by_class[class_name][:min_count])

    random.shuffle(balanced_rows)
    return balanced_rows, min_count, original_counts


def split_rows(rows):
    train_rows = []
    test_rows = []
    for class_name in TARGET_CLASSES:
        class_rows = [row for row in rows if row["class_name"] == class_name]
        random.shuffle(class_rows)
        split_index = int(len(class_rows) * TRAIN_RATIO)
        if split_index <= 0 and len(class_rows) > 1:
            split_index = 1
        if split_index >= len(class_rows) and len(class_rows) > 1:
            split_index = len(class_rows) - 1
        train_rows.extend(class_rows[:split_index])
        test_rows.extend(class_rows[split_index:])
    random.shuffle(train_rows)
    random.shuffle(test_rows)
    return train_rows, test_rows


def build_dataset(rows, speed_min, speed_max):
    images = []
    speeds = []
    labels = []
    for row in rows:
        images.append(load_and_preprocess_image(row["source_image_path"], IMAGE_SIZE, normalize=True))
        speeds.append([normalize_speed(row["game_speed"], speed_min, speed_max)])
        labels.append(1.0 if row["class_name"] == "down" else 0.0)

    x_images = np.asarray(images, dtype=np.float32)
    x_speeds = np.asarray(speeds, dtype=np.float32)
    y = np.asarray(labels, dtype=np.float32)
    return x_images, x_speeds, y


def build_model():
    image_input = tf.keras.Input(shape=INPUT_SHAPE, name="image")
    x = tf.keras.layers.Conv2D(16, (3, 3), activation="relu")(image_input)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(32, (3, 3), activation="relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(64, (3, 3), activation="relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Flatten()(x)

    speed_input = tf.keras.Input(shape=(1,), name="speed")
    speed_branch = tf.keras.layers.Dense(16, activation="relu")(speed_input)

    combined = tf.keras.layers.Concatenate()([x, speed_branch])
    combined = tf.keras.layers.Dense(128, activation="relu")(combined)
    combined = tf.keras.layers.Dropout(0.5)(combined)
    output = tf.keras.layers.Dense(1, activation="sigmoid")(combined)

    model = tf.keras.Model(inputs=[image_input, speed_input], outputs=output)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def safe_divide(numerator, denominator):
    return float(numerator) / float(denominator) if denominator else 0.0


def compute_metrics(y_true, probabilities):
    y_pred = (probabilities >= 0.5).astype(np.int32)
    y_true = y_true.astype(np.int32)

    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    accuracy = safe_divide(tp + tn, len(y_true))
    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    f1 = safe_divide(2 * precision * recall, precision + recall)
    error_rate = 1.0 - accuracy
    log_loss = float(tf.keras.losses.binary_crossentropy(y_true.astype(np.float32), probabilities).numpy().mean())

    return {
        "accuracy": accuracy,
        "error_rate": error_rate,
        "precision_down": precision,
        "recall_down": recall,
        "f1_down": f1,
        "log_loss": log_loss,
        "confusion_matrix": [[tn, fp], [fn, tp]],
        "predicted_down_rate": float(np.mean(y_pred)),
    }


def save_outputs(metrics, history, model, train_seconds, eval_seconds, original_counts, min_count, train_rows, test_rows):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with (OUTPUT_DIR / "metrics.json").open("w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, indent=2, ensure_ascii=False)

    history_payload = {
        key: [float(value) for value in values]
        for key, values in history.history.items()
    }
    with (OUTPUT_DIR / "training_history.json").open("w", encoding="utf-8") as history_file:
        json.dump(history_payload, history_file, indent=2, ensure_ascii=False)

    summary = {
        "variant_name": "binary_relu_sigmoid_up_down",
        "classes": TARGET_CLASSES,
        "hidden_activation": "relu",
        "output_activation": "sigmoid",
        "filters": [16, 32, 64],
        "parameter_count": int(model.count_params()),
        "epochs_ran": len(history_payload.get("loss", [])),
        "training_seconds": float(train_seconds),
        "evaluation_seconds": float(eval_seconds),
        "balanced_total_per_class": int(min_count),
        "original_counts": original_counts,
        "train_counts": {class_name: sum(1 for row in train_rows if row["class_name"] == class_name) for class_name in TARGET_CLASSES},
        "test_counts": {class_name: sum(1 for row in test_rows if row["class_name"] == class_name) for class_name in TARGET_CLASSES},
        "best_val_accuracy": max(history_payload.get("val_accuracy", [])) if history_payload.get("val_accuracy") else None,
        "best_val_loss": min(history_payload.get("val_loss", [])) if history_payload.get("val_loss") else None,
    }
    with (OUTPUT_DIR / "training_summary.json").open("w", encoding="utf-8") as summary_file:
        json.dump(summary, summary_file, indent=2, ensure_ascii=False)

    report_lines = [
        "Experimento binario up vs down con ocultas ReLU y salida sigmoid",
        f"Accuracy:           {metrics['accuracy']:.4f}",
        f"Error de test:      {metrics['error_rate']:.4f}",
        f"Precision down:     {metrics['precision_down']:.4f}",
        f"Recall down:        {metrics['recall_down']:.4f}",
        f"F1 down:            {metrics['f1_down']:.4f}",
        f"Log loss:           {metrics['log_loss']:.4f}",
        f"Tasa predicha down: {metrics['predicted_down_rate']:.4f}",
        f"Matriz confusion:   {metrics['confusion_matrix']}",
    ]
    with (OUTPUT_DIR / "metrics.txt").open("w", encoding="utf-8") as report_file:
        report_file.write("\n".join(report_lines))


def main():
    random.seed(42)
    np.random.seed(42)
    tf.random.set_seed(42)

    print("Cargando capturas y metadata de velocidad...")
    source_rows = load_capture_metadata(SOURCE_LABELS_PATH)

    print("Filtrando up/down y balanceando dataset...")
    balanced_rows, min_count, original_counts = filter_and_balance_rows(source_rows)
    train_rows, test_rows = split_rows(balanced_rows)

    speed_values = [row["game_speed"] for row in train_rows]
    speed_min = min(speed_values)
    speed_max = max(speed_values)

    x_train_images, x_train_speeds, y_train = build_dataset(train_rows, speed_min, speed_max)
    x_test_images, x_test_speeds, y_test = build_dataset(test_rows, speed_min, speed_max)

    print(f"Cantidad original: {original_counts}")
    print(f"Usando {min_count} muestras por clase.")
    print(f"Train binario: {len(train_rows)} muestras")
    print(f"Test binario:  {len(test_rows)} muestras")

    model = build_model()
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
        )
    ]

    train_start = time.perf_counter()
    history = model.fit(
        [x_train_images, x_train_speeds],
        y_train,
        validation_data=([x_test_images, x_test_speeds], y_test),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )
    train_seconds = time.perf_counter() - train_start

    model.save(MODEL_PATH)
    metadata = {
        "classes": TARGET_CLASSES,
        "image_size": list(IMAGE_SIZE),
        "speed_min": float(speed_min),
        "speed_max": float(speed_max),
        "output_activation": "sigmoid",
        "hidden_activation": "relu",
        "task": "binary_up_down",
    }
    with METADATA_PATH.open("w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2, ensure_ascii=False)

    eval_start = time.perf_counter()
    probabilities = model.predict([x_test_images, x_test_speeds], verbose=0).reshape(-1)
    eval_seconds = time.perf_counter() - eval_start
    metrics = compute_metrics(y_test, probabilities)
    save_outputs(metrics, history, model, train_seconds, eval_seconds, original_counts, min_count, train_rows, test_rows)

    print("\n=== Evaluacion binaria ===")
    print(f"Accuracy:           {metrics['accuracy']:.4f}")
    print(f"Error de test:      {metrics['error_rate']:.4f}")
    print(f"Precision down:     {metrics['precision_down']:.4f}")
    print(f"Recall down:        {metrics['recall_down']:.4f}")
    print(f"F1 down:            {metrics['f1_down']:.4f}")
    print(f"Log loss:           {metrics['log_loss']:.4f}")
    print(f"Tasa predicha down: {metrics['predicted_down_rate']:.4f}")
    print(f"Resultados guardados en: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
