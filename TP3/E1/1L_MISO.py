
import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from Utils import DividirEntrenamientoTest, MostrarEstadisticos, ExpandirCaracteristicasPolinomicas
from RegresionClasses import Perceptron

plt.style.use('seaborn-v0_8-whitegrid')


def SL_MISO(*,
    AFunction: str = "Identity",
    G: int = 2,
    graficar: bool = False
    ):        
    os.system("cls" if os.name == "nt" else "clear")
    
    # Cargar sin encabezado
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
    
    X_expanded = ExpandirCaracteristicasPolinomicas(X_original=X, grado=G)
    
    x_mean, x_std = 0.0, 1.0
    if G > 3:       
        media = np.mean(X_expanded, axis=0)
        desviacion = np.std(X_expanded, axis=0)

        # 3. Se aplica la transformación Z-score (se añade un pequeño épsilon para evitar división por cero)
        X_expanded = (X_expanded - media) / (desviacion + 1e-8)
        x_mean = media[0]
        x_std = desviacion[0]
            
    X_train, X_test, T_train, T_test = DividirEntrenamientoTest(X_expanded, T, test_size=0.85)
    
    
    ModeloLineal = Perceptron(
        InputDim=X_expanded.shape[1], 
        OutputDim=1, 
        ActivationFunction="Identity")
    
    Y_untrained = ModeloLineal.predict(InputVector=X_test)
    e_untrained = T_test - Y_untrained
    
    
    ModeloLineal.fit(
        TrainingData=X_train, 
        TargetData=T_train,
        TestData=X_test,
        TargetTest=T_test, 
        LearningRate=0.01, 
        Epochs=1000
    )
    
    Y_trained = ModeloLineal.predict(InputVector=X_test)
    e_trained = T_test - Y_trained
    
    
    if graficar:    
        MostrarEstadisticos(
            variable="Loss",
            promedio=np.mean(ModeloLineal.Loss),
            desviacion=np.std(ModeloLineal.Loss)
        )
        
        MostrarEstadisticos(
            variable="Error Sin Entrenar",
            promedio=np.mean(e_untrained),
            desviacion=np.std(e_untrained)
        )
        
        MostrarEstadisticos(
            variable="Error Entrenado",
            promedio=np.mean(e_trained),
            desviacion=np.std(e_trained)
        )
    
        # =============================================================================== #
        #               Gráficos de evolución de la norma de los gradientes     
        # =============================================================================== #
        
        ModeloLineal.graficarGradientes(
            escala_logaritmica=False, 
            saveFig=True,
            label = f"E1 MISO {AFunction} Gradientes - Expancion Poly {G}.pdf"
            )

        # =============================================================================== #
        #               Gráficos de evolución de la norma de los gradientes     
        # =============================================================================== #

        ModeloLineal.graficarLoss(
            saveFig=True,
            label = f"E1 MISO {AFunction} Loss - Expancion Poly {G}.pdf"
        )
        
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
        nombre_archivo = f"E1 MISO {AFunction} Expansion Poly {G} Grafico.pdf" 
        plt.savefig(f"./TP3/Imagen/{nombre_archivo}", dpi=300, bbox_inches='tight')
        
        plt.show()
    
    x_test_original = X_test[:, 0] * x_std + x_mean
    return np.mean(e_trained), np.std(e_trained), x_test_original, T_test, Y_trained
    
if __name__ == "__main__":
    
    grados_a_probar = [2, 3, 4, 5, 10, 20, 50, 100, 200]
    
    e_prom = np.zeros((len(grados_a_probar), 1))
    e_std = np.zeros((len(grados_a_probar), 1))
    
    indice = 0

    # Figura para graficar todos los ajustes en un único gráfico
    fig_curvas, ax_curvas = plt.subplots(figsize=(8, 5.5), dpi=120)
    dataset_graficado = False
    
    for i in grados_a_probar:
        prom, std, x_test, t_test, y_trained = SL_MISO(
            AFunction="Identity",
            G=i,
            graficar=False
        )
        e_prom[indice] = prom
        e_std[indice] = std
        
        if not dataset_graficado:
            ax_curvas.scatter(x_test, t_test, 
                    facecolors='none', 
                    edgecolors='#0072BD', 
                    linewidths=0.7, 
                    label='Datos del dataset')
            dataset_graficado = True
        
        if i <= 5: # Para evitar saturar el gráfico con curvas de alto grado, solo graficamos hasta grado 5
            ax_curvas.plot(x_test, y_trained, linewidth=1.5, label=f"Ajuste G={i}")
        
        indice += 1
        
    ax_curvas.set_title('Ajustes con Expansión Polinómica vs Datos Reales', fontsize=11, fontweight='bold', pad=10)
    ax_curvas.set_xlabel('Variable Independiente (x)', fontsize=10)
    ax_curvas.set_ylabel('Variable Dependiente (y)', fontsize=10)
    ax_curvas.tick_params(direction='in', top=True, right=True, labelsize=9)
    ax_curvas.legend(loc='upper left', frameon=True, fontsize=9)
    ax_curvas.grid(True)
    # ax_curvas.set_xlim(-5, 5)
    ax_curvas.set_ylim([min(t_test) - 1, max(t_test) + 1])
    
    fig_curvas.tight_layout()
    fig_curvas.savefig(f"./TP3/Imagen/E1 MISO Ajustes Polinomicos De Bajo Grado.pdf", dpi=300, bbox_inches='tight')
    
    print("Error Promedio por Grado del Polinomio:")
    for i in range(len(e_prom)):
        print(f"Grado {grados_a_probar[i]}: {e_prom[i][0]:.4f} ± {e_std[i][0]:.4f}")
        
    plt.figure(figsize=(8, 5.5), dpi=120)
    plt.errorbar(x=grados_a_probar, y=e_prom[:, 0], yerr=e_std[:, 0], fmt='-o', ecolor='red', capsize=5)
    plt.title('Error Promedio vs Grado del Polinomio', fontsize=11, fontweight='bold', pad=10)
    plt.xlabel('Grado del Polinomio (G)', fontsize=10)
    plt.ylabel('Error Promedio', fontsize=10)
    plt.xscale('log') # Escala logarítmica recomendada por la dispersión (de 2 a 200)
    plt.xticks(grados_a_probar, labels=[str(g) for g in grados_a_probar])
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"./TP3/Imagen/E1 MISO Error Promedio vs Grado Aumentado.pdf", dpi=300, bbox_inches='tight')
    plt.show() 