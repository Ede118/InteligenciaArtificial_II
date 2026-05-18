import os
# Silenciar mensajes de TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import numpy as np
import matplotlib.pyplot as plt
from keras.datasets import mnist

# Importar herramientas de scikit-learn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ==========================================
# 1. CARGAR Y PREPARAR EL DATASET
# ==========================================
print("Cargando dataset MNIST...")
(X_train_raw, y_train), (X_test_raw, y_test) = mnist.load_data()

# Para que scikit-learn no tarde una eternidad, usamos una porción de los datos
# (Tomamos 10.000 imágenes para entrenar y 2.000 para testear)
X_train_raw = X_train_raw[:10000]
y_train = y_train[:10000]
X_test_raw = X_test_raw[:2000]
y_test = y_test[:2000]

# Aplanar las imágenes (de 28x28 a un vector de 784)
X_train_flat = X_train_raw.reshape(len(X_train_raw), -1)
X_test_flat = X_test_raw.reshape(len(X_test_raw), -1)

# NORMALIZACIÓN: Pasar los valores de píxel de [0, 255] a [0.0, 1.0]
X_train = X_train_flat / 255.0
X_test = X_test_flat / 255.0

print(f"Datos normalizados y listos.")
print(f"Forma del set de entrenamiento: {X_train.shape}")

# ==========================================
# 2. CREAR Y ENTRENAR EL MODELO (scikit-learn)
# ==========================================
print("\nEntrenando el modelo de Regresión Logística (esto puede tardar unos segundos)...")
# Usamos un max_iter alto para asegurar convergencia y un solver rápido
modelo = LogisticRegression(max_iter=1000, solver='saga', random_state=42)
modelo.fit(X_train, y_train)
print("¡Entrenamiento finalizado!")

# ==========================================
# 3. EVALUACIÓN DEL MODELO
# ==========================================
# Predecir sobre el set de testeo
y_pred = modelo.predict(X_test)

# Calcular la precisión (Accuracy)
precision = accuracy_score(y_test, y_pred)
print(True)
print(f"\n[RESULTADO] Precisión total del modelo (Accuracy): {precision * 100:.2f}%")

# Mostrar reporte detallado por cada dígito (0 al 9)
print("\nReporte de Clasificación detallado:")
print(classification_report(y_test, y_pred))

# ==========================================
# 4. VISUALIZAR PREDICCIONES
# ==========================================
# Mostramos 5 ejemplos del set de test con su predicción
r, c = 1, 5
fig = plt.figure(figsize=(2*c, 2*r))
for i in range(c):
    ix = np.random.randint(0, len(X_test_raw))
    img = X_test_raw[ix]
    
    plt.subplot(r, c, i + 1)
    plt.imshow(img, cmap='gray')
    plt.axis("off")
    
    # Si la predicción es correcta verde, si le erró rojo
    color = "green" if y_pred[ix] == y_test[ix] else "red"
    plt.title(f"Pred: {y_pred[ix]}\nReal: {y_test[ix]}", color=color)

plt.tight_layout()
print("\nAbriendo gráfico con ejemplos de predicciones...")
plt.show()