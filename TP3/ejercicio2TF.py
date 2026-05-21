import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.datasets import mnist # type: ignore
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import Dense, Flatten # type: ignore
#librerias para el desempenio
from sklearn.metrics import confusion_matrix, accuracy_score
import pandas as pd
import seaborn as sn

print("cargando dataset MNIST...")
(X_train_raw, y_train_raw), (X_test_raw, y_test_raw) = mnist.load_data()

CANTIDAD_ENTRENAMIENTO = 40000  
CANTIDAD_TESTEO = 1500         

X_train_cut = X_train_raw[:CANTIDAD_ENTRENAMIENTO]
y_train = y_train_raw[:CANTIDAD_ENTRENAMIENTO]
X_test_cut = X_test_raw[:CANTIDAD_TESTEO]
y_test = y_test_raw[:CANTIDAD_TESTEO]

#normalizacion de los datos
X_train = X_train_cut / 255.0
X_test = X_test_cut / 255.0

print(f"Datos normalizados listos.")
print(f" -> Entrenando con: {X_train.shape[0]} imágenes y {y_train.shape[0]} etiquetas.")
print(f" -> Testeando con: {X_test.shape[0]} imágenes y {y_test.shape[0]} etiquetas.")

#red neuronal
model = Sequential([
    Flatten(input_shape=(28, 28)),
    Dense(128, activation='relu'),
    Dense(10, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

#entrenamiento del modelo
print("\n>>> Iniciando entrenamiento de la Red Neuronal...")
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.1)
print("¡Entrenamiento de TensorFlow finalizado!")

#funcion de desenpenio
print("\nEvaluando rendimiento en el set de testeo...")


y_pred_probabilities = model.predict(X_test)
y_pred = np.argmax(y_pred_probabilities, axis=1)
acc = accuracy_score(y_test, y_pred)
print(f"\n[RESULTADO] Precisión total de TensorFlow: {acc * 100:.2f}%")

cm = confusion_matrix(y_test, y_pred)
df_cm = pd.DataFrame(cm, index = [i for i in range(0,10)], columns = [i for i in range(0,10)])

plt.figure(figsize = (10,7))
sn.heatmap(df_cm, annot=True, fmt='d', cmap='Purples')
plt.title(f'Matriz de Confusión - Red Neuronal (TensorFlow)\n(Precisión: {acc*100:.2f}%)', fontsize=14)
plt.xlabel('Predicho (Modelo TF)', fontsize=12)
plt.ylabel('Real (Dato Original)', fontsize=12)

print("\n>>> Abriendo gráfico de rendimiento...")
plt.show()