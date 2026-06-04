import subprocess
import sys
try:
    import tensorflow as tf
except ImportError as err:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tensorflow'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])
    import tensorflow as tf

from tensorflow.keras.preprocessing.image import ImageDataGenerator, save_img
import os
import random
import shutil
from TensorflowImageUtils import CLASS_FOLDER_NAMES, IMAGE_SIZE, load_and_preprocess_image

# Rutas de las carpetas
source_dir = "images"

train_dir = source_dir + "/train/"
test_dir = source_dir + "/test/"

# El orden debe coincidir con Dinosaur.CLASSES: JUMP, DUCK, RIGHT.
classes = CLASS_FOLDER_NAMES

def reset_split_directories(): # Eliminar y recrear las carpetas de entrenamiento y prueba
    for split_dir in [train_dir, test_dir]:
        if os.path.isdir(split_dir):
            shutil.rmtree(split_dir)
        os.makedirs(split_dir, exist_ok=True)

        for class_name in classes:
            os.makedirs(os.path.join(split_dir, class_name), exist_ok=True)

reset_split_directories()

# Proporción de imágenes para entrenamiento y prueba
train_ratio = 0.8

# Parámetros para el modelo
batch_size = 32 # Tamaño del lote para el entrenamiento
image_size = IMAGE_SIZE # Tamaño al que se redimensionarán las imágenes (ancho, alto)
input_shape = image_size + (1,)  # Tamaño de la imagen con un solo canal para escala de grises

# Iterar sobre las subcarpetas
for class_name in classes:
    # Ruta de la subcarpeta de origen
    source_class_dir = os.path.join(source_dir, class_name)
    
    # Obtener la lista de imágenes en la subcarpeta de origen
    images = os.listdir(source_class_dir)
    
    # Mezclar aleatoriamente las imágenes
    random.shuffle(images)
    
    # Calcular el número de imágenes para entrenamiento
    num_train_images = int(len(images) * train_ratio)
    
    # Iterar sobre las imágenes para entrenamiento
    for img_name in images[:num_train_images]:
        # Ruta de la imagen de origen
        src_img_path = os.path.join(source_class_dir, img_name)
        # Ruta de destino para la imagen de entrenamiento
        dest_train_path = os.path.join(train_dir + class_name, f"{img_name}")
        # Mover la imagen a la carpeta de entrenamiento y renombrarla
        img_array = load_and_preprocess_image(src_img_path, image_size)
        save_img(dest_train_path, img_array)
    
    # Iterar sobre las imágenes para prueba
    for img_name in images[num_train_images:]:
        # Ruta de la imagen de origen
        src_img_path = os.path.join(source_class_dir, img_name)
        # Ruta de destino para la imagen de prueba
        dest_test_path = os.path.join(test_dir + class_name, f"{img_name}")
        # Mover la imagen a la carpeta de prueba y renombrarla
        img_array = load_and_preprocess_image(src_img_path, image_size)
        save_img(dest_test_path, img_array)

# Crear generadores de datos
train_datagen = ImageDataGenerator(rescale=1./255) # Normalizar las imágenes dividiendo por 255 para que los valores estén entre 0 y 1
train_generator = train_datagen.flow_from_directory(
    train_dir,
    classes=classes,
    target_size=image_size,
    batch_size=batch_size,
    class_mode='categorical',
    color_mode='grayscale')  # Se especifica el modo de color escala de grises

validation_datagen = ImageDataGenerator(rescale=1./255)
validation_generator = validation_datagen.flow_from_directory(
    test_dir,
    classes=classes,
    target_size=image_size,
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=False,
    color_mode='grayscale')  # Se especifica el modo de color escala de grises

# ========================== Construir el modelo ==========================================
model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(len(classes), activation='softmax')
])
# ==========================================================================================

# Compilar el modelo
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Entrenar el modelo
model.fit(train_generator, epochs=10, validation_data=validation_generator)

# Guardar el modelo
model.save('tensorflow_nn.h5')
