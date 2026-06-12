import json
import random
import time
from pathlib import Path

import numpy as np
import tensorflow as tf

from BuildTensorflowModelVariants import (
    OUTPUT_ROOT_DIR,
    SOURCE_LABELS_PATH,
    TEST_DIR,
    TEST_LABELS_PATH,
    TRAIN_DIR,
    TRAIN_LABELS_PATH,
    TRAIN_RATIO,
    balance_rows,
    build_dataset,
    load_capture_metadata,
    reset_split_directories,
    save_split_rows,
    train_variant,
)


BALANCED_SIGMOID_VARIANT = {
    "name": "lightweight_sigmoid_balanced",
    "filters": [16, 32, 64],
    "activation": "sigmoid",
    "model_path": Path(__file__).resolve().parent / "tensorflow_nn_lightweight_sigmoid_balanced.h5",
    "metadata_path": Path(__file__).resolve().parent / "tensorflow_nn_lightweight_sigmoid_balanced_metadata.json",
    "output_dir": OUTPUT_ROOT_DIR / "lightweight_sigmoid_balanced",
    "dataset_strategy": "balanced_undersample",
}


def save_dataset_summary(output_dir, original_counts, balanced_total_per_class, train_rows, test_rows):
    train_counts = {}
    test_counts = {}
    for row in train_rows:
        train_counts[row["class_name"]] = train_counts.get(row["class_name"], 0) + 1
    for row in test_rows:
        test_counts[row["class_name"]] = test_counts.get(row["class_name"], 0) + 1

    payload = {
        "original_counts": original_counts,
        "balanced_total_per_class": balanced_total_per_class,
        "train_counts": train_counts,
        "test_counts": test_counts,
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "dataset_summary.json").open("w", encoding="utf-8") as summary_file:
        json.dump(payload, summary_file, indent=2, ensure_ascii=False)


def main():
    random.seed(42)
    np.random.seed(42)
    tf.random.set_seed(42)

    print("Cargando capturas y metadata de velocidad...")
    source_rows = load_capture_metadata(SOURCE_LABELS_PATH)

    print("Balanceando dataset por submuestreo a la clase minoritaria...")
    balanced_source_rows, min_count, original_counts = balance_rows(source_rows)
    print(f"Cantidad original por clase: {original_counts}")
    print(f"Se usaran {min_count} muestras por clase.")

    train_source_rows = []
    test_source_rows = []
    rows_by_class = {}
    for row in balanced_source_rows:
        rows_by_class.setdefault(row["class_name"], []).append(row)

    for class_rows in rows_by_class.values():
        random.shuffle(class_rows)
        split_index = int(len(class_rows) * TRAIN_RATIO)
        if split_index <= 0 and len(class_rows) > 1:
            split_index = 1
        if split_index >= len(class_rows) and len(class_rows) > 1:
            split_index = len(class_rows) - 1

        train_source_rows.extend(class_rows[:split_index])
        test_source_rows.extend(class_rows[split_index:])

    reset_split_directories()
    train_rows = save_split_rows(train_source_rows, TRAIN_DIR, TRAIN_LABELS_PATH)
    test_rows = save_split_rows(test_source_rows, TEST_DIR, TEST_LABELS_PATH)

    speed_values = [row["game_speed"] for row in train_rows]
    speed_min = min(speed_values)
    speed_max = max(speed_values)

    print("Construyendo datasets balanceados con imagen + velocidad...")
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

    BALANCED_SIGMOID_VARIANT["class_target_count"] = min_count

    print(f"Train balanceado: {len(train_rows)} muestras")
    print(f"Test balanceado:  {len(test_rows)} muestras")
    print(f"Rango de velocidad train: {speed_min} - {speed_max}")

    run_start = time.perf_counter()
    train_variant(
        BALANCED_SIGMOID_VARIANT,
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
    print(f"Tiempo total de la corrida balanceada: {time.perf_counter() - run_start:.2f}s")

    save_dataset_summary(
        BALANCED_SIGMOID_VARIANT["output_dir"],
        original_counts,
        min_count,
        train_rows,
        test_rows,
    )


if __name__ == "__main__":
    main()
