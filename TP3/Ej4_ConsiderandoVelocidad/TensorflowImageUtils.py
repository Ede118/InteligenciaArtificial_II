from PIL import Image
from tensorflow.keras.preprocessing.image import img_to_array


IMAGE_SIZE = (80, 120)  # (alto, ancho)
CLASS_FOLDER_NAMES = ["up", "down", "right"]
MODEL_OUTPUT_CLASSES = ["JUMP", "DUCK", "RIGHT"]
LABELS_FILENAME = "labels.csv"
MODEL_METADATA_FILENAME = "tensorflow_nn_metadata.json"

CAPTURE_LEFT_OFFSET = 50
CAPTURE_TOP_OFFSET = 200
CAPTURE_RIGHT_OFFSET = 600
CAPTURE_BOTTOM_OFFSET = 550


def get_capture_bbox(window_left, window_top):
    return (
        window_left + CAPTURE_LEFT_OFFSET,
        window_top + CAPTURE_TOP_OFFSET,
        window_left + CAPTURE_RIGHT_OFFSET,
        window_top + CAPTURE_BOTTOM_OFFSET,
    )


def preprocess_pil_image(image, target_size=IMAGE_SIZE):
    target_height, target_width = target_size
    prepared_image = image.convert("L")
    prepared_image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

    canvas = Image.new("L", (target_width, target_height), color=255)
    offset_x = (target_width - prepared_image.width) // 2
    offset_y = (target_height - prepared_image.height) // 2
    canvas.paste(prepared_image, (offset_x, offset_y))
    return canvas


def preprocess_image_for_model(image, target_size=IMAGE_SIZE, normalize=False):
    prepared_image = preprocess_pil_image(image, target_size)

    image_array = img_to_array(prepared_image)
    if normalize:
        image_array = image_array / 255.0
    return image_array


def load_and_preprocess_image(file_path, target_size=IMAGE_SIZE, normalize=False):
    with Image.open(file_path) as image:
        return preprocess_image_for_model(image, target_size, normalize)


def normalize_speed(speed, speed_min, speed_max):
    if speed_max <= speed_min:
        return 0.0
    return (float(speed) - float(speed_min)) / (float(speed_max) - float(speed_min))
