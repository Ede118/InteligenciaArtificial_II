import random

import numpy as np
import tensorflow as tf

from BuildTensorflowModelVariants import (
    OUTPUT_ROOT_DIR,
    SOURCE_LABELS_PATH,
    SOURCE_DIR,
    TEST_LABELS_PATH,
    TEST_DIR,
    TRAIN_LABELS_PATH,
    TRAIN_DIR,
    TRAIN_RATIO,
    build_dataset,
    load_capture_metadata,
    reset_split_directories,
    save_split_rows,
    stratified_split,
    train_variant,
)


TWO_LAYER_RELU_VARIANT = {
    "name": "two_layer_relu",
    "filters": [16, 32],
    "activation": "relu",
    "model_path": SOURCE_DIR.parent / "tensorflow_nn_two_layer_relu.h5",
    "metadata_path": SOURCE_DIR.parent / "tensorflow_nn_two_layer_relu_metadata.json",
    "output_dir": OUTPUT_ROOT_DIR / "two_layer_relu",
}


def main():
    random.seed(42)
    np.random.seed(42)
    tf.random.set_seed(42)

    print("Cargando capturas y metadata de velocidad...")
    source_rows = load_capture_metadata(SOURCE_LABELS_PATH)

    print("Generando split train/test para el modelo de dos capas...")
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

    train_variant(
        TWO_LAYER_RELU_VARIANT,
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
