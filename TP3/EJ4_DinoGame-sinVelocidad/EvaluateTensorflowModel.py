import argparse
import json
import math
import os
import subprocess
import sys
from PIL import Image

try:
    import matplotlib
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    import numpy as np
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy as np

try:
    import tensorflow as tf
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflow"])
    import tensorflow as tf

from TensorflowImageUtils import CLASS_FOLDER_NAMES, load_and_preprocess_image, preprocess_pil_image


DEFAULT_MODEL_PATH = "tensorflow_nn.h5"
DEFAULT_TEST_DIR = os.path.join("images", "test")
DEFAULT_OUTPUT_DIR = "evaluation_results"
DEFAULT_CLASS_NAMES = CLASS_FOLDER_NAMES


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evalua el modelo de TensorFlow sobre las imagenes de images/test."
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_PATH,
        help=f"Ruta al archivo .h5 del modelo. Por defecto: {DEFAULT_MODEL_PATH}",
    )
    parser.add_argument(
        "--test-dir",
        default=DEFAULT_TEST_DIR,
        help=f"Directorio con subcarpetas por clase. Por defecto: {DEFAULT_TEST_DIR}",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directorio donde se guardan metricas y graficos. Por defecto: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Muestra los graficos ademas de guardarlos en disco.",
    )
    return parser.parse_args()


def infer_input_config(model):
    _, height, width, channels = model.input_shape
    if channels not in (1, 3):
        raise ValueError(
            f"Cantidad de canales no soportada por el script: {channels}. "
            "Solo se soportan modelos grayscale o RGB."
        )
    color_mode = "grayscale" if channels == 1 else "rgb"
    return (height, width), channels, color_mode


def discover_class_names(test_dir):
    missing_classes = [
        class_name
        for class_name in DEFAULT_CLASS_NAMES
        if not os.path.isdir(os.path.join(test_dir, class_name))
    ]
    if missing_classes:
        raise FileNotFoundError(
            "Faltan subcarpetas de clases dentro del directorio de test: "
            + ", ".join(missing_classes)
        )
    return DEFAULT_CLASS_NAMES


def load_test_dataset(test_dir, class_names, image_size, color_mode):
    images = []
    labels = []
    file_paths = []

    for class_index, class_name in enumerate(class_names):
        class_dir = os.path.join(test_dir, class_name)
        if not os.path.isdir(class_dir):
            continue

        for file_name in sorted(os.listdir(class_dir)):
            file_path = os.path.join(class_dir, file_name)
            if not os.path.isfile(file_path):
                continue

            image_array = load_and_preprocess_image(
                file_path,
                image_size,
                normalize=True,
            )

            images.append(image_array)
            labels.append(class_index)
            file_paths.append(file_path)

    if not images:
        raise FileNotFoundError(
            f"No se encontraron imagenes para evaluar dentro de {test_dir}."
        )

    x_test = np.asarray(images, dtype=np.float32)
    y_test = np.asarray(labels, dtype=np.int32)
    return x_test, y_test, file_paths


def build_confusion_matrix(y_true, y_pred, num_classes):
    confusion = np.zeros((num_classes, num_classes), dtype=np.int32)
    for true_label, pred_label in zip(y_true, y_pred):
        confusion[true_label, pred_label] += 1
    return confusion


def safe_divide(numerator, denominator):
    return float(numerator) / float(denominator) if denominator else 0.0


def compute_metrics(y_true, y_pred, probabilities, class_names):
    num_classes = len(class_names)
    confusion = build_confusion_matrix(y_true, y_pred, num_classes)

    accuracy = safe_divide(np.trace(confusion), np.sum(confusion))
    error_rate = 1.0 - accuracy

    true_one_hot = tf.keras.utils.to_categorical(y_true, num_classes=num_classes)
    log_loss = float(tf.keras.losses.categorical_crossentropy(true_one_hot, probabilities).numpy().mean())

    per_class = []
    recalls = []
    weighted_f1_sum = 0.0
    total_support = int(np.sum(confusion))

    for index, class_name in enumerate(class_names):
        tp = int(confusion[index, index])
        fp = int(np.sum(confusion[:, index]) - tp)
        fn = int(np.sum(confusion[index, :]) - tp)
        support = int(np.sum(confusion[index, :]))

        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        f1 = safe_divide(2 * precision * recall, precision + recall)
        class_error = 1.0 - recall if support else 0.0

        recalls.append(recall)
        weighted_f1_sum += f1 * support

        per_class.append(
            {
                "class_name": class_name,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "support": support,
                "error_rate": class_error,
            }
        )

    macro_precision = float(np.mean([item["precision"] for item in per_class]))
    macro_recall = float(np.mean(recalls))
    macro_f1 = float(np.mean([item["f1_score"] for item in per_class]))
    weighted_f1 = safe_divide(weighted_f1_sum, total_support)

    return {
        "accuracy": accuracy,
        "error_rate": error_rate,
        "balanced_accuracy": macro_recall,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "log_loss": log_loss,
        "confusion_matrix": confusion,
        "per_class": per_class,
    }


def save_metrics_report(metrics, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    serializable_metrics = {
        "accuracy": metrics["accuracy"],
        "error_rate": metrics["error_rate"],
        "balanced_accuracy": metrics["balanced_accuracy"],
        "macro_precision": metrics["macro_precision"],
        "macro_recall": metrics["macro_recall"],
        "macro_f1": metrics["macro_f1"],
        "weighted_f1": metrics["weighted_f1"],
        "log_loss": metrics["log_loss"],
        "confusion_matrix": metrics["confusion_matrix"].tolist(),
        "per_class": metrics["per_class"],
    }

    json_path = os.path.join(output_dir, "metrics.json")
    with open(json_path, "w", encoding="utf-8") as metrics_file:
        json.dump(serializable_metrics, metrics_file, indent=2, ensure_ascii=False)

    report_lines = [
        "Resumen de evaluacion del modelo",
        f"Accuracy:           {metrics['accuracy']:.4f}",
        f"Error de test:      {metrics['error_rate']:.4f}",
        f"Balanced accuracy:  {metrics['balanced_accuracy']:.4f}",
        f"Macro precision:    {metrics['macro_precision']:.4f}",
        f"Macro recall:       {metrics['macro_recall']:.4f}",
        f"Macro F1:           {metrics['macro_f1']:.4f}",
        f"Weighted F1:        {metrics['weighted_f1']:.4f}",
        f"Log loss:           {metrics['log_loss']:.4f}",
        "",
        "Metricas por clase:",
    ]

    for item in metrics["per_class"]:
        report_lines.append(
            (
                f"- {item['class_name']}: precision={item['precision']:.4f}, "
                f"recall={item['recall']:.4f}, f1={item['f1_score']:.4f}, "
                f"error={item['error_rate']:.4f}, support={item['support']}"
            )
        )

    txt_path = os.path.join(output_dir, "metrics.txt")
    with open(txt_path, "w", encoding="utf-8") as report_file:
        report_file.write("\n".join(report_lines))


def plot_confusion_matrix(confusion, class_names, output_dir, show_plots):
    row_sums = confusion.sum(axis=1, keepdims=True)
    normalized = np.divide(
        confusion,
        row_sums,
        out=np.zeros_like(confusion, dtype=np.float64),
        where=row_sums != 0,
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    image = ax.imshow(normalized, cmap="Blues", vmin=0.0, vmax=1.0)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    ax.set_title("Matriz de confusion normalizada")
    ax.set_xlabel("Prediccion")
    ax.set_ylabel("Valor real")
    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names)
    ax.set_yticklabels(class_names)

    for row in range(confusion.shape[0]):
        for col in range(confusion.shape[1]):
            text = f"{confusion[row, col]}\n{normalized[row, col] * 100:.1f}%"
            color = "white" if normalized[row, col] > 0.5 else "black"
            ax.text(col, row, text, ha="center", va="center", color=color, fontsize=10)

    fig.tight_layout()
    output_path = os.path.join(output_dir, "confusion_matrix.png")
    fig.savefig(output_path, dpi=200, bbox_inches="tight")

    if show_plots:
        plt.show()
    plt.close(fig)


def plot_test_error(metrics, output_dir, show_plots):
    class_names = [item["class_name"] for item in metrics["per_class"]]
    class_errors = [item["error_rate"] for item in metrics["per_class"]]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    global_names = ["Accuracy", "Error", "Balanced Acc."]
    global_values = [
        metrics["accuracy"],
        metrics["error_rate"],
        metrics["balanced_accuracy"],
    ]
    global_colors = ["#2E8B57", "#B22222", "#1F77B4"]
    axes[0].bar(global_names, global_values, color=global_colors)
    axes[0].set_ylim(0, 1)
    axes[0].set_title("Resumen global de test")
    axes[0].set_ylabel("Valor")

    for index, value in enumerate(global_values):
        axes[0].text(index, min(value + 0.03, 0.98), f"{value:.3f}", ha="center")

    axes[1].bar(class_names, class_errors, color="#FF8C00")
    axes[1].set_ylim(0, 1)
    axes[1].set_title("Error por clase")
    axes[1].set_ylabel("Error")
    axes[1].tick_params(axis="x", rotation=20)

    for index, value in enumerate(class_errors):
        axes[1].text(index, min(value + 0.03, 0.98), f"{value:.3f}", ha="center")

    fig.tight_layout()
    output_path = os.path.join(output_dir, "test_error.png")
    fig.savefig(output_path, dpi=200, bbox_inches="tight")

    if show_plots:
        plt.show()
    plt.close(fig)


def plot_class_metrics(metrics, output_dir, show_plots):
    class_names = [item["class_name"] for item in metrics["per_class"]]
    precision_values = [item["precision"] for item in metrics["per_class"]]
    recall_values = [item["recall"] for item in metrics["per_class"]]
    f1_values = [item["f1_score"] for item in metrics["per_class"]]

    x_positions = np.arange(len(class_names))
    width = 0.24

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x_positions - width, precision_values, width=width, label="Precision")
    ax.bar(x_positions, recall_values, width=width, label="Recall")
    ax.bar(x_positions + width, f1_values, width=width, label="F1-score")

    ax.set_title("Metricas por clase")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(class_names)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Valor")
    ax.legend()

    fig.tight_layout()
    output_path = os.path.join(output_dir, "class_metrics.png")
    fig.savefig(output_path, dpi=200, bbox_inches="tight")

    if show_plots:
        plt.show()
    plt.close(fig)


def plot_misclassified_examples(
    file_paths, y_true, y_pred, class_names, image_size, color_mode, output_dir, show_plots
):
    mistakes = [
        (file_path, true_label, pred_label)
        for file_path, true_label, pred_label in zip(file_paths, y_true, y_pred)
        if true_label != pred_label
    ]

    if not mistakes:
        return

    max_examples = min(12, len(mistakes))
    columns = 3
    rows = math.ceil(max_examples / columns)
    fig, axes = plt.subplots(rows, columns, figsize=(12, 3.5 * rows))
    axes = np.atleast_1d(axes).reshape(rows, columns)

    for axis in axes.ravel():
        axis.axis("off")

    for index, (file_path, true_label, pred_label) in enumerate(mistakes[:max_examples]):
        axis = axes[index // columns, index % columns]
        with Image.open(file_path) as image:
            prepared_image = preprocess_pil_image(image, image_size)
        axis.imshow(prepared_image, cmap="gray")
        axis.set_title(
            f"Real: {class_names[true_label]}\nPred: {class_names[pred_label]}",
            fontsize=10,
        )
        axis.axis("off")

    fig.suptitle("Ejemplos mal clasificados", fontsize=14)
    fig.tight_layout()
    output_path = os.path.join(output_dir, "misclassified_examples.png")
    fig.savefig(output_path, dpi=200, bbox_inches="tight")

    if show_plots:
        plt.show()
    plt.close(fig)


def print_summary(metrics, class_names):
    print("\n=== Evaluacion del modelo ===")
    print(f"Accuracy:           {metrics['accuracy']:.4f}")
    print(f"Error de test:      {metrics['error_rate']:.4f}")
    print(f"Balanced accuracy:  {metrics['balanced_accuracy']:.4f}")
    print(f"Macro precision:    {metrics['macro_precision']:.4f}")
    print(f"Macro recall:       {metrics['macro_recall']:.4f}")
    print(f"Macro F1:           {metrics['macro_f1']:.4f}")
    print(f"Weighted F1:        {metrics['weighted_f1']:.4f}")
    print(f"Log loss:           {metrics['log_loss']:.4f}")
    print("\nMetricas por clase:")

    for item in metrics["per_class"]:
        print(
            f"- {item['class_name']}: precision={item['precision']:.4f}, "
            f"recall={item['recall']:.4f}, f1={item['f1_score']:.4f}, "
            f"error={item['error_rate']:.4f}, support={item['support']}"
        )

    print("\nOrden de clases usado por la evaluacion:")
    print(", ".join(class_names))


def main():
    args = parse_args()

    if not os.path.isfile(args.model):
        raise FileNotFoundError(
            f"No se encontro el archivo del modelo: {args.model}"
        )
    if not os.path.isdir(args.test_dir):
        raise FileNotFoundError(
            f"No se encontro el directorio de test: {args.test_dir}"
        )

    os.makedirs(args.output_dir, exist_ok=True)

    model = tf.keras.models.load_model(args.model)
    image_size, _, color_mode = infer_input_config(model)
    class_names = discover_class_names(args.test_dir)

    if model.output_shape[-1] != len(class_names):
        raise ValueError(
            "La cantidad de clases del modelo no coincide con las subcarpetas de test. "
            f"Salida del modelo: {model.output_shape[-1]}, clases detectadas: {len(class_names)}."
        )

    x_test, y_true, file_paths = load_test_dataset(
        args.test_dir, class_names, image_size, color_mode
    )
    probabilities = model.predict(x_test, verbose=0)
    y_pred = np.argmax(probabilities, axis=1)

    metrics = compute_metrics(y_true, y_pred, probabilities, class_names)
    save_metrics_report(metrics, args.output_dir)
    plot_confusion_matrix(metrics["confusion_matrix"], class_names, args.output_dir, args.show)
    plot_test_error(metrics, args.output_dir, args.show)
    plot_class_metrics(metrics, args.output_dir, args.show)
    plot_misclassified_examples(
        file_paths, y_true, y_pred, class_names, image_size, color_mode, args.output_dir, args.show
    )
    print_summary(metrics, class_names)
    print(f"\nResultados guardados en: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()
