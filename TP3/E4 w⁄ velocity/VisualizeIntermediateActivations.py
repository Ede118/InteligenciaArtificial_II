import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image

from TensorflowImageUtils import load_and_preprocess_image, normalize_speed


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LABELS_PATH = BASE_DIR / "images" / "labels.csv"
DEFAULT_OUTPUT_DIR = BASE_DIR / "evaluation_results" / "intermediate_activations"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Visualiza activaciones intermedias de capas Conv2D para un modelo imagen+velocidad."
    )
    parser.add_argument("--model", required=True, help="Ruta al modelo .h5")
    parser.add_argument("--metadata", required=True, help="Ruta al json de metadata del modelo")
    parser.add_argument("--image", help="Ruta a la imagen original a analizar")
    parser.add_argument("--speed", type=float, help="Velocidad del juego asociada a la imagen")
    parser.add_argument(
        "--labels-csv",
        default=str(DEFAULT_LABELS_PATH),
        help=f"CSV para inferir imagen y velocidad si no se pasan manualmente. Por defecto: {DEFAULT_LABELS_PATH}",
    )
    parser.add_argument(
        "--sample-index",
        type=int,
        default=0,
        help="Indice de fila dentro del CSV si no se pasa --image. Por defecto: 0",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Directorio de salida. Por defecto: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--max-channels",
        type=int,
        default=16,
        help="Cantidad maxima de mapas por capa a guardar. Por defecto: 16",
    )
    return parser.parse_args()


def load_metadata(path):
    with Path(path).open("r", encoding="utf-8") as metadata_file:
        return json.load(metadata_file)


def resolve_sample(args, metadata):
    if args.image and args.speed is not None:
        return Path(args.image), float(args.speed)

    labels_path = Path(args.labels_csv)
    with labels_path.open("r", newline="", encoding="utf-8") as labels_file:
        rows = list(csv.DictReader(labels_file))

    if not rows:
        raise ValueError("El CSV de labels esta vacio.")
    if args.sample_index < 0 or args.sample_index >= len(rows):
        raise IndexError("sample-index fuera de rango para el CSV indicado.")

    row = rows[args.sample_index]
    relative_path = row["relative_path"].replace("/", "\\")
    image_path = labels_path.parent / relative_path
    speed = float(row["game_speed"])
    return image_path, speed


def build_activation_model(model):
    conv_layers = [layer for layer in model.layers if isinstance(layer, tf.keras.layers.Conv2D)]
    if not conv_layers:
        raise ValueError("El modelo no tiene capas Conv2D para visualizar.")
    activation_model = tf.keras.Model(inputs=model.inputs, outputs=[layer.output for layer in conv_layers])
    return conv_layers, activation_model


def save_input_preview(image_path, image_array, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(image_path) as original_image:
        fig, axes = plt.subplots(1, 2, figsize=(8, 4))
        axes[0].imshow(original_image)
        axes[0].set_title("Imagen original")
        axes[0].axis("off")

        axes[1].imshow(image_array[:, :, 0], cmap="gray")
        axes[1].set_title("Imagen preprocesada")
        axes[1].axis("off")

        fig.tight_layout()
        fig.savefig(output_dir / "input_preview.png", dpi=200, bbox_inches="tight")
        plt.close(fig)


def save_activation_grid(activation, layer_name, output_dir, max_channels):
    feature_maps = activation[0]
    num_channels = min(feature_maps.shape[-1], max_channels)
    columns = 4
    rows = math.ceil(num_channels / columns)

    fig, axes = plt.subplots(rows, columns, figsize=(12, 3 * rows))
    axes = np.atleast_1d(axes).reshape(rows, columns)

    for axis in axes.ravel():
        axis.axis("off")

    for channel_index in range(num_channels):
        axis = axes[channel_index // columns, channel_index % columns]
        axis.imshow(feature_maps[:, :, channel_index], cmap="viridis")
        axis.set_title(f"Canal {channel_index}", fontsize=9)
        axis.axis("off")

    fig.suptitle(layer_name, fontsize=14)
    fig.tight_layout()
    fig.savefig(output_dir / f"{layer_name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def save_activation_summary(layer_summaries, prediction_summary, output_dir):
    payload = {
        "prediction_summary": prediction_summary,
        "layers": layer_summaries,
    }
    with (output_dir / "activation_summary.json").open("w", encoding="utf-8") as summary_file:
        json.dump(payload, summary_file, indent=2, ensure_ascii=False)


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata = load_metadata(args.metadata)
    image_path, game_speed = resolve_sample(args, metadata)

    image_size = tuple(metadata["image_size"])
    speed_min = float(metadata["speed_min"])
    speed_max = float(metadata["speed_max"])
    normalized_speed = normalize_speed(game_speed, speed_min, speed_max)

    image_array = load_and_preprocess_image(str(image_path), image_size, normalize=True)
    x_image = np.expand_dims(image_array, axis=0)
    x_speed = np.asarray([[normalized_speed]], dtype=np.float32)

    model = tf.keras.models.load_model(args.model)
    conv_layers, activation_model = build_activation_model(model)
    activations = activation_model.predict([x_image, x_speed], verbose=0)
    predictions = model.predict([x_image, x_speed], verbose=0)

    save_input_preview(image_path, image_array, output_dir)

    layer_summaries = []
    for layer, activation in zip(conv_layers, activations):
        layer_name = layer.name.replace("/", "_")
        save_activation_grid(activation, layer_name, output_dir, args.max_channels)
        layer_summaries.append(
            {
                "layer_name": layer.name,
                "shape": list(activation.shape),
                "mean_activation": float(np.mean(activation)),
                "max_activation": float(np.max(activation)),
                "min_activation": float(np.min(activation)),
                "std_activation": float(np.std(activation)),
            }
        )

    prediction_summary = {
        "image_path": str(Path(image_path).resolve()),
        "game_speed": float(game_speed),
        "normalized_speed": float(normalized_speed),
        "prediction_shape": list(predictions.shape),
        "prediction_values": predictions[0].tolist(),
    }
    if "class_folder_names" in metadata:
        prediction_summary["class_names"] = metadata["class_folder_names"]
    if "classes" in metadata:
        prediction_summary["class_names"] = metadata["classes"]

    save_activation_summary(layer_summaries, prediction_summary, output_dir)

    print(f"Imagen analizada: {Path(image_path).resolve()}")
    print(f"Velocidad usada: {game_speed} (normalizada={normalized_speed:.4f})")
    print(f"Capas convolucionales visualizadas: {len(conv_layers)}")
    print(f"Resultados guardados en: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
