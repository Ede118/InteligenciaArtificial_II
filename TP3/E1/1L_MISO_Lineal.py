
import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from Utils import DividirEntrenamientoTest, GraficarNormaGradientes, MostrarEstadisticos, GraficarCurvaPerdida, ExpandirCaracteristicasPolinomicas
from RegresionClasses import Perceptron

plt.style.use('seaborn-v0_8-whitegrid')


if __name__ == "__main__":
        
    os.system("cls" if os.name == "nt" else "clear")
    
    url = "https://drive.google.com/uc?export=download&id=1g8KNOJsaE3jzXob-ZsTE_PqYwuxJ05pg"

    # Cargar sin encabezado
    datos = pd.read_csv(url, header=None)
    # Renombrar columnas
    datos.columns = ["x", "y"]
    # Limpiar paréntesis y espacios
    datos["x"] = datos["x"].astype(str).str.replace("(", "", regex=False).str.strip()
    datos["y"] = datos["y"].astype(str).str.replace(")", "", regex=False).str.strip()
    # Convertir a float
    datos["x"] = datos["x"].astype(float)
    datos["y"] = datos["y"].astype(float)
    
    datos = datos.sort_values(by="x").reset_index(drop=True)
    
        
    X = datos[["x"]].values
    T = datos[["y"]].values
    
    G = 10
    
    X_expanded = ExpandirCaracteristicasPolinomicas(X_original=X, grado=G)
    
    if G > 3:       
        media = np.mean(X_expanded, axis=0)
        desviacion = np.std(X_expanded, axis=0)

        # 3. Se aplica la transformación Z-score (se añade un pequeño épsilon para evitar división por cero)
        X_expanded = (X_expanded - media) / (desviacion + 1e-8)
            
    X_train, X_test, T_train, T_test = DividirEntrenamientoTest(X_expanded, T, test_size=0.90)
    
    
    ModeloLineal = Perceptron(
        InputDim=X_expanded.shape[1], 
        OutputDim=1, 
        Neurons=np.array([1]), 
        ActivationFunction="Identity")
    
    Y_untrained = ModeloLineal.Predict(InputVector=X_test)
    W1_untrained = ModeloLineal.WeightMatrix[0, 0]
    b_untrained = ModeloLineal.Bias[0, 0]
    
    
    ModeloLineal.Fit(
        TrainingData=X_train, 
        TargetData=T_train,
        TestData=X_test,
        TargetTest=T_test, 
        LearningRate=0.01, 
        Epochs=1000
    )
    W = np.array(ModeloLineal.WeightMatrix).reshape(-1, 1)
    b = np.array(ModeloLineal.Bias).reshape(-1, 1)
    
    
    for i in range(W.shape[1]):
        MostrarEstadisticos(
            variable=f"W{i+1}",
            promedio=np.mean(W[:,i]),
            desviacion=np.std(W[:,i])
        )
    
    for i in range(b.shape[1]):
         MostrarEstadisticos(
            variable=f"b",
            promedio=np.mean(b),
            desviacion=np.std(b)
        )
    
    Y_trained = ModeloLineal.Predict(InputVector=X_test)
    
    
    # print("Grafico de evolución de W1 y b durante el entrenamiento...")
    

    
    # =============================================================================== #
    #               Gráficos de evolución de la norma de los gradientes     
    # =============================================================================== #
    
    GraficarNormaGradientes(ModeloLineal, False)

    # =============================================================================== #
    #               Gráficos de evolución de la norma de los gradientes     
    # =============================================================================== #

    GraficarCurvaPerdida(ModeloLineal)
    
    # =============================================================================== #
    #                       Graficos de ajuste final vs inicial     
    # =============================================================================== #
    
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=120)
    
    ax.scatter(X_test[:, 0], T_test, 
            facecolors='none', 
            edgecolors='#0072BD', 
            linewidths=0.7, 
            label='Datos del dataset')
    
    ax.plot(X_test[:, 0], Y_trained, 
            color='#D95319', 
            linewidth=1.5, 
            label=r"Ajuste Final: $y = g \left( \sum_{i=1}^{" + str(G) + r"} w_{k,trained} A_{k,trained} + b_{trained} \right)$")
    
    ax.plot(X_test[:, 0], Y_untrained, 
            color='#77AC30', 
            linewidth=1.5, 
            label=r"Ajuste Inicial: $y = g \left( \sum_{i=1}^{" + str(G) + r"} w_{k,untrained} A_{k,untrained} + b_{untrained} \right)$")
    
    
    ax.set_title('Función de activación: $g(z) = z$ (Identidad)', fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel('Variable Independiente (x)', fontsize=10)
    ax.set_ylabel('Variable Dependiente (y)', fontsize=10)
    ax.tick_params(direction='in', top=True, right=True, labelsize=9)
    ax.legend(loc='upper left', frameon=True, fontsize=9)
    
    plt.tight_layout()
    plt.show()