
import os
import sys
from unittest import case

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from Utils import DividirEntrenamientoTest, MostrarEstadisticos
from RegresionClasses import Perceptron

plt.style.use('seaborn-v0_8-whitegrid')


def SL_SISO(*,
    X_train: np.ndarray,
    T_train: np.ndarray,
    X_test: np.ndarray,
    T_test: np.ndarray,
    AFunction: str = "Identity",
    graficar: bool = False
    ):        
    
        
    Model = Perceptron(
        InputDim=1, 
        OutputDim=1, 
        ActivationFunction=AFunction)
    
    W_untrained = Model.WeightMatrix[0,0]
    b_untrained = Model.Bias[0,0]
    
    Y_untrained = Model.predict(InputVector=X_test)
    e_untrained = T_test - Y_untrained
    

    Model.fit(
        TrainingData=X_train, 
        TargetData=T_train,
        TestData=X_test,
        TargetTest=T_test, 
        LearningRate=0.01, 
        Epochs=1000
    )
    
    W_trained = Model.WeightMatrix[0,0]
    b_trained = Model.Bias[0,0]
    
    Y_trained = Model.predict(InputVector=X_test)
    e_trained = T_test - Y_trained
    

    
    if graficar:
    
        console = Console()

        texto_estado = Text()
        texto_estado.append(f"Promedio: {np.mean(e_untrained):.4f}", style="bold")
        texto_estado.append(f"\nDesviación estándar: {np.std(e_untrained):.4f}", style="bold")

        console.print(Panel(
            texto_estado, 
            title=f"[blue]Error Sin Entrenamiento: {AFunction}[/blue]", 
            border_style="green",
            padding=(1, 2) # Padding vertical=1, horizontal=2
        ))
        
        texto_estado = Text()
        texto_estado.append(f"Promedio: {np.mean(e_trained):.4f}", style="bold")
        texto_estado.append(f"\nDesviación estándar: {np.std(e_trained):.4f}", style="bold")

        console.print(Panel(
            texto_estado, 
            title=f"[blue]Error Tras Entrenamiento: {AFunction}[/blue]", 
            border_style="green",
            padding=(1, 2) # Padding vertical=1, horizontal=2
        ))
        
        # =============================================================================== #
        #               Gráficos de evolución de la norma de los gradientes     
        # =============================================================================== #
    
        Model.graficarGradientes(escala_logaritmica=False, saveFig=True)

        # =============================================================================== #
        #               Gráficos de evolución de la norma de los gradientes     
        # =============================================================================== #

        Model.graficarLoss(saveFig=True)
    
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
                label=r"Ajuste Final: $y = g \left(" + f"{W_trained:.4f}x + {b_trained:.4f}" + r"\right)$")
        
        ax.plot(X_test, Y_untrained, 
                color='#77AC30', 
                linewidth=1.5, 
                label=r"Ajuste Inicial: $y = g \left(" + f"{W_untrained :.4f}x + {b_untrained:.4f}" + r"\right)$")
        
        match AFunction:
            case "Identity": label_activation = "Función de activación: $g(z) = z$ (Identidad)"
            case "ReLU": label_activation = "Función de activación: $g(z) = max(0, z)$ (ReLU)"
            case "Sigmoid": label_activation = "Función de activación: $g(z) = \\frac{1}{1 + e^{-z}}$ (Sigmoide)"
            case "Tanh": label_activation = "Función de activación: $g(z) = \\frac{e^z - e^{-z}}{e^z + e^{-z}}$ (Tangente Hiperbólica)"
            case _: label_activation = f"Función de activación: {AFunction}"
                
        ax.set_title(label_activation, fontsize=11, fontweight='bold', pad=10)
        ax.set_xlabel('Variable Independiente (x)', fontsize=10)
        ax.set_ylabel('Variable Dependiente (y)', fontsize=10)
        ax.tick_params(direction='in', top=True, right=True, labelsize=9)
        ax.legend(loc='upper left', frameon=True, fontsize=9)
        
        plt.tight_layout()
        nombre_archivo = f"E1 SISO {AFunction} Grafico.pdf" 
        plt.savefig(f"./TP3/Imagen/{nombre_archivo}", dpi=300, bbox_inches='tight')
        plt.show()
        

if __name__ == "__main__":
    
    os.system("cls" if os.name == "nt" else "clear")
    
    datos = pd.read_csv("./TP3/E1/datos.csv", header=None)
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
    
    functions = ["Identity", "ReLU", "Sigmoid", "Tanh"]
    
    for AFunction in functions:
        SL_SISO(
            X_train=X_train,
            T_train=T_train,
            X_test=X_test,
            T_test=T_test,
            AFunction=AFunction,
            graficar=True
        )
        input("")