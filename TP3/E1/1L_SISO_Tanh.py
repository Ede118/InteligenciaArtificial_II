
import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from Utils import DividirEntrenamientoTest, GraficarNormaGradientes, MostrarEstadisticos, GraficarCurvaPerdida
from RegresionClasses import Perceptron

plt.style.use('seaborn-v0_8-whitegrid')


def SL_SISO_Tanh():        
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
    
    X_train, X_test, T_train, T_test = DividirEntrenamientoTest(X, T, test_size=0.90)
        
    ModeloTanh = Perceptron(
        InputDim=1, 
        OutputDim=1, 
        Neurons=np.array([1]), 
        ActivationFunction="Tanh")
    
    Y_untrained = ModeloTanh.Predict(InputVector=X_test)
    W1_untrained = ModeloTanh.WeightMatrix[0, 0]
    b_untrained = ModeloTanh.Bias[0, 0]
    
    W1: float = []
    b: float = []
    

    ModeloTanh.Fit(
        TrainingData=X_train, 
        TargetData=T_train,
        TestData=X_test,
        TargetTest=T_test, 
        LearningRate=0.01, 
        Epochs=1000
    )
    
    W1 = ModeloTanh.WeightMatrix[0, 0]
    b = ModeloTanh.Bias[0, 0]
    
    MostrarEstadisticos(
        variable="W1",
        promedio=np.mean(W1),
        desviacion=np.std(W1)
    )
    
    MostrarEstadisticos(
        variable="b",
        promedio=np.mean(b),
        desviacion=np.std(b)
    )
    
    
    Y_trained = ModeloTanh.Predict(InputVector=X_test)
    
    
    # print("Grafico de evolución de W1 y b durante el entrenamiento...")
    

    
    # =============================================================================== #
    #               Gráficos de evolución de la norma de los gradientes     
    # =============================================================================== #
    
    GraficarNormaGradientes(ModeloTanh, False)

    # =============================================================================== #
    #               Gráficos de evolución de la norma de los gradientes     
    # =============================================================================== #

    GraficarCurvaPerdida(ModeloTanh)
    
    # =============================================================================== #
    #                       Graficos de ajuste final vs inicial     
    # =============================================================================== #
    
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=120)
    
    ax.scatter(X_test, T_test, 
            facecolors='none', 
            edgecolors='#0072BD', 
            linewidths=0.7, 
            label='Datos del dataset')
    
    ax.plot(X_test, Y_trained, 
            color='#D95319', 
            linewidth=1.5, 
            label=r"Ajuste Final: $y = g \left(" + f"{W1:.4f}x + {b:.4f}" + r"\right)$")
    
    ax.plot(X_test, Y_untrained, 
            color='#77AC30', 
            linewidth=1.5, 
            label=r"Ajuste Inicial: $y = g \left(" + f"{W1_untrained:.4f}x + {b_untrained:.4f}" + r"\right)$")
    
    
    ax.set_title('Función de activación: $g(z) = \\tanh(z)$ (Tanh)', fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel('Variable Independiente (x)', fontsize=10)
    ax.set_ylabel('Variable Dependiente (y)', fontsize=10)
    ax.tick_params(direction='in', top=True, right=True, labelsize=9)
    ax.legend(loc='upper left', frameon=True, fontsize=9)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    SL_SISO_Tanh()