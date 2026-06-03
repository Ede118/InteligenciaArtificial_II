

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid')


if __name__ == "__main__":
    
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

    # Figura para graficar todos los ajustes en un único gráfico
    fig_curvas, ax_curvas = plt.subplots(figsize=(8, 5.5), dpi=120)
    dataset_graficado = False
    
    ax_curvas.scatter(X, T, 
                    facecolors='none', 
                    edgecolors='#0072BD', 
                    linewidths=0.7, 
                    label='Data')
    
        
    ax_curvas.set_title('Grafico del Dataset', fontsize=11, fontweight='bold', pad=10)
    ax_curvas.set_xlabel('Variable Independiente (x)', fontsize=10)
    ax_curvas.set_ylabel('Variable Dependiente (y)', fontsize=10)
    ax_curvas.tick_params(direction='in', top=True, right=True, labelsize=9)
    ax_curvas.legend(loc='upper left', frameon=True, fontsize=9)
    ax_curvas.grid(True)
    ax_curvas.set_xlim([min(X) - 1, max(X) + 1])
    ax_curvas.set_ylim([min(T) - 1, max(T) + 1])
    
    fig_curvas.tight_layout()
    fig_curvas.savefig(f"./TP3/Imagen/E1 Dataset.png", dpi=300, bbox_inches='tight')
    fig_curvas.show()
    
