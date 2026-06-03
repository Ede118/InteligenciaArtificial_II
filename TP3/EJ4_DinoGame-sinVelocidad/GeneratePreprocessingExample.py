import json
from pathlib import Path

import numpy as np
from PIL import Image

IMAGE_SIZE = (80, 120)  # (alto, ancho)
SOURCE_IMAGE = Path("images/up/1090.png")
OUTPUT_IMAGE = Path("example_preprocessed_1090.png")
OUTPUT_VECTOR = Path("example_preprocessed_1090_vector.json")


def preprocess_pil_image(image, target_size=IMAGE_SIZE):
    target_height, target_width = target_size
    prepared_image = image.convert("L")
    prepared_image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

    canvas = Image.new("L", (target_width, target_height), color=255)
    offset_x = (target_width - prepared_image.width) // 2
    offset_y = (target_height - prepared_image.height) // 2
    canvas.paste(prepared_image, (offset_x, offset_y))
    return canvas


def main():
    with Image.open(SOURCE_IMAGE) as image:
        preprocessed_image = preprocess_pil_image(image, IMAGE_SIZE)

    tensor = np.asarray(preprocessed_image, dtype=np.float32)[..., np.newaxis] / 255.0
    flattened_vector = tensor.reshape(-1)

    preprocessed_image.save(OUTPUT_IMAGE)

    payload = {
        "source_image": str(SOURCE_IMAGE).replace("\\", "/"),
        "class_name": SOURCE_IMAGE.parent.name,
        "preprocessed_image": str(OUTPUT_IMAGE).replace("\\", "/"),
        "image_size": list(IMAGE_SIZE),
        "tensor_shape": list(tensor.shape),
        "flattened_vector_length": int(flattened_vector.size),
        "flattened_vector": [round(float(value), 6) for value in flattened_vector],
    }

    OUTPUT_VECTOR.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    print(f"Saved {OUTPUT_IMAGE}")
    print(f"Saved {OUTPUT_VECTOR}")


if __name__ == "__main__":
    main()
