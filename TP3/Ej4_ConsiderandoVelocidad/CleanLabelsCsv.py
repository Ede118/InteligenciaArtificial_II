import csv
import os

from TensorflowImageUtils import LABELS_FILENAME


SOURCE_DIR = "images"
LABELS_PATH = os.path.join(SOURCE_DIR, LABELS_FILENAME)


def main():
    if not os.path.isfile(LABELS_PATH):
        raise FileNotFoundError(f"No se encontro el archivo de labels: {LABELS_PATH}")

    with open(LABELS_PATH, "r", newline="", encoding="utf-8") as labels_file:
        reader = csv.DictReader(labels_file)
        fieldnames = reader.fieldnames

        if not fieldnames:
            raise ValueError("El archivo de labels no tiene encabezados.")

        valid_rows = []
        removed_rows = 0

        for row in reader:
            relative_path = row["relative_path"].replace("/", os.sep).replace("\\", os.sep)
            image_path = os.path.join(SOURCE_DIR, relative_path)

            if os.path.isfile(image_path):
                valid_rows.append(row)
            else:
                removed_rows += 1

    with open(LABELS_PATH, "w", newline="", encoding="utf-8") as labels_file:
        writer = csv.DictWriter(labels_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(valid_rows)

    print(f"Filas conservadas: {len(valid_rows)}")
    print(f"Filas eliminadas:  {removed_rows}")
    print(f"Archivo actualizado: {os.path.abspath(LABELS_PATH)}")


if __name__ == "__main__":
    main()
