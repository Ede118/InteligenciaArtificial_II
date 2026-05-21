import numpy as np
import matplotlib.pyplot as plt
from keras.datasets import mnist
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, accuracy_score
import pandas as pd
import seaborn as sn

print("Cargando dataset MNIST...")
(X_train_raw, y_train), (X_test_raw, y_test) = mnist.load_data()

X_train_raw, y_train = X_train_raw[:40000], y_train[:40000]
X_test_raw, y_test = X_test_raw[:1500], y_test[:1500]

#normalizado y aplanado
X_train = X_train_raw.reshape(len(X_train_raw), -1) / 255.0
X_test = X_test_raw.reshape(len(X_test_raw), -1) / 255.0

print("Datos listos. Entrenando los 3 modelos...")

#modelos ya entrenados
modelos = {
    'Regresión Logística': LogisticRegression(max_iter=300, solver='saga', random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    'K-Vecinos (KNN)': KNeighborsClassifier(n_neighbors=5, n_jobs=-1)
}

#entrenamiento de los modelos
for nombre, modelo in modelos.items():
    print(f" -> Entrenando {nombre}...")
    modelo.fit(X_train, y_train)

print("\n¡Entrenamiento finalizado! Generando funciones de desempeño...\n")

#evaluacion de desempenio
for nombre, modelo in modelos.items():
    
    y_pred = modelo.predict(X_test) 
    acc = accuracy_score(y_test, y_pred)
    print(f"Preparando ventana para: {nombre}...")

    cm = confusion_matrix(y_test, y_pred)
    df_cm = pd.DataFrame(cm, index = [i for i in range(0,10)], columns = [i for i in range(0,10)])
    
    plt.figure(nombre, figsize = (9, 6))
    sn.heatmap(df_cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'Matriz de Confusión - {nombre}\n(Precisión: {acc*100:.2f}%)', fontsize=12)
    plt.xlabel('Predicho (Modelo)', fontsize=10)
    plt.ylabel('Real (Dato Original)', fontsize=10)
    plt.tight_layout()


print("\n>>> Abriendo las 3 ventanas al mismo tiempo...")
plt.show() 
print("Proceso terminado de forma exitosa.")