import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
EVALUATION_DIR = BASE_DIR / "evaluation_results"
OUTPUT_DIR = EVALUATION_DIR / "model_comparison"

EXPERIMENTS = [
    {
        "id": "lightweight_relu",
        "label": "Multiclase ReLU",
        "task": "Multiclase",
        "classes": "up/down/right",
        "hidden_activation": "relu",
        "output_activation": "softmax",
        "dataset": "3 clases, split original",
        "metrics_path": EVALUATION_DIR / "lightweight_relu" / "metrics.json",
        "summary_path": EVALUATION_DIR / "lightweight_relu" / "training_summary.json",
    },
    {
        "id": "lightweight_sigmoid",
        "label": "Multiclase Sigmoid",
        "task": "Multiclase",
        "classes": "up/down/right",
        "hidden_activation": "sigmoid",
        "output_activation": "softmax",
        "dataset": "3 clases, split original",
        "metrics_path": EVALUATION_DIR / "lightweight_sigmoid" / "metrics.json",
        "summary_path": EVALUATION_DIR / "lightweight_sigmoid" / "training_summary.json",
    },
    {
        "id": "binary_sigmoid_up_down",
        "label": "Binario Sigmoid/Sigmoid",
        "task": "Binario",
        "classes": "up/down",
        "hidden_activation": "sigmoid",
        "output_activation": "sigmoid",
        "dataset": "up/down balanceado",
        "metrics_path": EVALUATION_DIR / "binary_sigmoid_up_down" / "metrics.json",
        "summary_path": EVALUATION_DIR / "binary_sigmoid_up_down" / "training_summary.json",
    },
    {
        "id": "binary_relu_sigmoid_up_down",
        "label": "Binario ReLU/Sigmoid",
        "task": "Binario",
        "classes": "up/down",
        "hidden_activation": "relu",
        "output_activation": "sigmoid",
        "dataset": "up/down balanceado",
        "metrics_path": EVALUATION_DIR / "binary_relu_sigmoid_up_down" / "metrics.json",
        "summary_path": EVALUATION_DIR / "binary_relu_sigmoid_up_down" / "training_summary.json",
    },
]


def load_json(path):
    with Path(path).open("r", encoding="utf-8") as json_file:
        return json.load(json_file)


def format_float(value):
    if value is None:
        return ""
    return f"{float(value):.4f}"


def build_rows():
    rows = []
    for experiment in EXPERIMENTS:
        metrics = load_json(experiment["metrics_path"])
        summary = load_json(experiment["summary_path"])

        row = {
            "id": experiment["id"],
            "label": experiment["label"],
            "task": experiment["task"],
            "classes": experiment["classes"],
            "hidden_activation": experiment["hidden_activation"],
            "output_activation": experiment["output_activation"],
            "dataset": experiment["dataset"],
            "accuracy": metrics.get("accuracy"),
            "error_rate": metrics.get("error_rate"),
            "log_loss": metrics.get("log_loss"),
            "parameter_count": summary.get("parameter_count"),
            "training_seconds": summary.get("training_seconds"),
            "evaluation_seconds": summary.get("evaluation_seconds"),
            "best_val_accuracy": summary.get("best_val_accuracy"),
            "best_val_loss": summary.get("best_val_loss"),
            "macro_f1": metrics.get("macro_f1"),
            "weighted_f1": metrics.get("weighted_f1"),
            "f1_down": metrics.get("f1_down"),
            "precision_down": metrics.get("precision_down"),
            "recall_down": metrics.get("recall_down"),
        }
        rows.append(row)
    return rows


def save_json(rows):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "note": (
            "Las filas multiclase y binarias no son directamente comparables entre si, "
            "pero sirven para aislar el efecto de la activacion y del tipo de tarea."
        ),
        "rows": rows,
    }
    with (OUTPUT_DIR / "comparison.json").open("w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, indent=2, ensure_ascii=False)


def save_csv(rows):
    fieldnames = [
        "id",
        "label",
        "task",
        "classes",
        "hidden_activation",
        "output_activation",
        "dataset",
        "accuracy",
        "error_rate",
        "log_loss",
        "macro_f1",
        "weighted_f1",
        "f1_down",
        "precision_down",
        "recall_down",
        "parameter_count",
        "training_seconds",
        "evaluation_seconds",
        "best_val_accuracy",
        "best_val_loss",
    ]
    with (OUTPUT_DIR / "comparison.csv").open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_markdown(rows):
    lines = [
        "# Comparacion de Experimentos",
        "",
        "Nota: las pruebas multiclase y binarias no miden exactamente la misma dificultad.",
        "La comparacion mas justa es por pares:",
        "- `Multiclase ReLU` vs `Multiclase Sigmoid`",
        "- `Binario Sigmoid/Sigmoid` vs `Binario ReLU/Sigmoid`",
        "",
        "| Experimento | Tarea | Ocultas | Salida | Dataset | Accuracy | Error | Log loss | F1 macro | F1 down | Params | Train s |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in rows:
        lines.append(
            "| {label} | {task} | {hidden_activation} | {output_activation} | {dataset} | {accuracy} | {error_rate} | {log_loss} | {macro_f1} | {f1_down} | {parameter_count} | {training_seconds} |".format(
                label=row["label"],
                task=row["task"],
                hidden_activation=row["hidden_activation"],
                output_activation=row["output_activation"],
                dataset=row["dataset"],
                accuracy=format_float(row["accuracy"]),
                error_rate=format_float(row["error_rate"]),
                log_loss=format_float(row["log_loss"]),
                macro_f1=format_float(row["macro_f1"]),
                f1_down=format_float(row["f1_down"]),
                parameter_count=row["parameter_count"],
                training_seconds=format_float(row["training_seconds"]),
            )
        )

    lines.extend(
        [
            "",
            "## Lectura Rapida",
            "",
            "- En multiclase, `ReLU` supera ampliamente a `Sigmoid` con la misma arquitectura liviana.",
            "- En binario, `sigmoid` en la salida funciona bien solo cuando las capas ocultas usan `ReLU`.",
            "- `Sigmoid` en las capas ocultas tiende a saturarse y termina colapsando a una clase dominante o a soluciones cercanas al azar.",
        ]
    )
    return "\n".join(lines)


def save_markdown(rows):
    markdown = build_markdown(rows)
    with (OUTPUT_DIR / "comparison.md").open("w", encoding="utf-8") as markdown_file:
        markdown_file.write(markdown)


def print_summary(rows):
    print("\nComparacion de experimentos:")
    for row in rows:
        print(
            f"- {row['label']}: accuracy={format_float(row['accuracy'])}, "
            f"error={format_float(row['error_rate'])}, log_loss={format_float(row['log_loss'])}"
        )
    print(f"\nResultados guardados en: {OUTPUT_DIR.resolve()}")


def main():
    rows = build_rows()
    save_json(rows)
    save_csv(rows)
    save_markdown(rows)
    print_summary(rows)


if __name__ == "__main__":
    main()
