
import os

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neural_network import MLPRegressor

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


from Utils import DividirEntrenamientoTest, MostrarEstadisticos
from RegresionClasses import HiddenLayerPerceptron  

plt.style.use('seaborn-v0_8-whitegrid')



def Sklearn_Model(*,
    Train_Input: np.ndarray,
    Train_Output: np.ndarray,
    Test_Input: np.ndarray,
    Test_Output: np.ndarray,
    HFunction: str = "Identity",
    h: tuple = (10,),
    ):
    
    m_train = Train_Input.shape[0]
    m_test = Test_Input.shape[0]

       
    Train_Input = Train_Input.reshape(m_train, 1)
    # Scikit-learn requiere target unidimensional (1D array)
    Train_Output = Train_Output.reshape(m_train, 1).ravel()  

    Test_Input = Test_Input.reshape(m_test, 1)
    # Scikit-learn requiere target unidimensional (1D array)
    Test_Output = Test_Output.reshape(m_test, 1).ravel()


    # 2. Inicialización del modelo Scikit-Learn parametrizado de forma equivalente
    activation_clean = HFunction.lower()
    
    modelo_sklearn = MLPRegressor(
        hidden_layer_sizes=h,                   # Tupla de capas ocultas
        activation=activation_clean,            # Activación ReLU en capa oculta
        solver='lbfgs',                         # Algoritmo cuasi-Newton (ideal para pocos datos)
        alpha=0.0,                              # Sin regularización L2
        max_iter=3000,                          # Equivalente a Epochs
        random_state=42                         # Fijación de semilla estocástica para reproducibilidad
    )

    # 3. Fase de Entrenamiento
    modelo_sklearn.fit(Train_Input, Train_Output)

    return modelo_sklearn

def DL_SISO(*,
    Train_Input: np.ndarray,
    Train_Output: np.ndarray,
    Test_Input: np.ndarray,
    Test_Output: np.ndarray,
    AFunction: str = "ReLU",
    HFunction: str = "ReLU",
    h_dim: int = 10,
    graficar: bool = False
    ):        
        
    Modelo = HiddenLayerPerceptron(
        InputDim=1, 
        HiddenDim=h_dim,
        OutputDim=1,
        ActivationHidden=HFunction,
        AFunction=AFunction
    )
        
        
    Untrained_Prediction, H = Modelo.predict(InputVector=Test_Input)
    

    Modelo.fit(
        TrainingData=Train_Input, 
        TargetData=Train_Output,
        TestData=Test_Input,
        TargetTest=Test_Output, 
        LearningRate=0.01, 
        Epochs=1000
    )
        
    Trained_Prediction, H = Modelo.predict(InputVector=Test_Input)
    
    
    if graficar:
        
        # =============================================================================== #
        #               Gráficos de evolución de la norma de los gradientes     
        # =============================================================================== #
        
        Modelo.graficarGradientes(escala_logaritmica=False)

        # =============================================================================== #
        #               Gráficos de evolución de la norma de los gradientes     
        # =============================================================================== #

        Modelo.graficarLoss()
        
        # =============================================================================== #
        #                       Graficos de ajuste final vs inicial     
        # =============================================================================== #
        
        fig, ax = plt.subplots(figsize=(8, 5.5), dpi=120)
        
        ax.scatter(Test_Input, Test_Output, 
                facecolors='none', 
                edgecolors='#0072BD', 
                linewidths=0.7, 
                label='Datos del dataset')
        
        ax.plot(Test_Input, Trained_Prediction, 
                color='#D95319', 
                linewidth=1.5, 
                label=r"Ajuste Final")
        
        ax.plot(Test_Input, Untrained_Prediction, 
                color='#77AC30', 
                linewidth=1.5, 
                label=r"Ajuste Inicial")
        
        
        match HFunction:
            case "Identity": label_activation = "Función capa oculta: $g(z) = z$ (Identidad)"
            case "ReLU": label_activation = "Función capa oculta: $g(z) = max(0, z)$ (ReLU)"
            case "Sigmoid": label_activation = "Función capa oculta: $g(z) = \\frac{1}{1 + e^{-z}}$ (Sigmoide)"
            case "Tanh": label_activation = "Función capa oculta: $g(z) = \\frac{e^z - e^{-z}}{e^z + e^{-z}}$ (Tangente Hiperbólica)"
            case _: label_activation = f"Función capa oculta: {HFunction}"
                
        ax.set_title(label_activation, fontsize=11, fontweight='bold', pad=10)
        ax.set_xlabel('Variable Independiente (x)', fontsize=10)
        ax.set_ylabel('Variable Dependiente (y)', fontsize=10)
        ax.tick_params(direction='in', top=True, right=True, labelsize=9)
        ax.legend(loc='upper left', frameon=True, fontsize=9)
        
        plt.tight_layout()
        plt.show()
        
    return Modelo

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
    
    p_test = 0.75
    h = 24
    ht = (4,4)
    
    Train_Input, Test_Input, Train_Output, Test_Output = DividirEntrenamientoTest(X, T, test_size=p_test)
    
    
    modeloPropio = DL_SISO(
        Train_Input=Train_Input,
        Train_Output=Train_Output,
        Test_Input=Test_Input,
        Test_Output=Test_Output,
        AFunction="ReLU",
        HFunction="ReLU",
        h_dim=h,
        graficar=False
    )
    
    modeloSKL = Sklearn_Model(
        Train_Input=Train_Input,
        Train_Output=Train_Output,
        Test_Input=Test_Input,
        Test_Output=Test_Output,
        HFunction="relu",
        h=ht
    )
    
    Trained_Prediction, _ = modeloPropio.predict(InputVector=Test_Input)
    SKLearn_Prediction = modeloSKL.predict(Test_Input)
    
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=120)
    
    ax.scatter(Test_Input, Test_Output, 
            facecolors='none', 
            edgecolors="#0019BD", 
            linewidths=0.7, 
            label='Datos del dataset')
    
    ax.plot(Test_Input, Trained_Prediction, 
            color="#E64709", 
            linewidth=1.5, 
            label=r"MLP Casero (1 Wide Layer)")
    
    ax.plot(Test_Input, SKLearn_Prediction, 
            color="#169B3A", 
            linewidth=1.5, 
            label=r"SKL MLPRegressor (Multiple Narrow Layers)")
    
    
    label_activation = f"Comparacion: Wide Layer vs Multiple Narrow Layers"
            
    ax.set_title(label_activation, fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel('Variable Independiente (x)', fontsize=10)
    ax.set_ylabel('Variable Dependiente (y)', fontsize=10)
    ax.tick_params(direction='in', top=True, right=True, labelsize=9)
    ax.legend(loc='upper left', frameon=True, fontsize=9)
    
    plt.tight_layout()
    nombre_archivo = f"E1 SISO 1 Wide Layer vs Multiple Narrow Layers.png" 
    plt.savefig(f"./TP3/Imagen/{nombre_archivo}", dpi=300, bbox_inches='tight')
    plt.show()
    
    error_prop = np.ndarray([2, 1])
    error_prop[0, 0] = np.mean((Test_Output - Trained_Prediction) ** 2)
    error_prop[1, 0] = np.std((Test_Output - Trained_Prediction) ** 2)
    
    
    cantidad_coef_p = modeloPropio._W1.size + modeloPropio._B1.size + modeloPropio._W2.size + modeloPropio._B2.size
    
    
    
    error_SKL = np.ndarray([2, 1])
    error_SKL[0, 0] = np.mean((Test_Output - SKLearn_Prediction.reshape(-1, 1)) ** 2)
    error_SKL[1, 0] = np.std((Test_Output - SKLearn_Prediction.reshape(-1, 1)) ** 2)
    cantidad_coef_skl = sum(modeloSKL.coefs_[i].size + modeloSKL.intercepts_[i].size for i in range(len(modeloSKL.coefs_)))
    
    texto1 = Text()
    texto1.append(f"Error Promedio: {error_prop[0,0]:.4f}", style="bold")
    texto1.append(f"\nDesviación Estándar: {error_prop[1,0]:.4f}", style="bold")
    texto1.append(f"\nCantidad de Coeficientes: {cantidad_coef_p}", style="bold")
    console = Console()
    console.print(Panel(
        texto1, 
        title=f"[blue]Estadísticos de MLP Casero[/blue]", 
        border_style="green",
        padding=(1, 2) # Padding vertical=1, horizontal=2
    ))
    
    texto2 = Text()
    texto2.append(f"Error Promedio: {error_SKL[0,0]:.4f}", style="bold")
    texto2.append(f"\nDesviación Estándar: {error_SKL[1,0]:.4f}", style="bold")
    texto2.append(f"\nCantidad de Coeficientes: {cantidad_coef_skl}", style="bold")
    
    console = Console()
    console.print(Panel(
        texto2, 
        title=f"[blue]Estadísticos de SKLearn MLPRegressor[/blue]", 
        border_style="green",
        padding=(1, 2) # Padding vertical=1, horizontal=2
    ))

    # minNuerons = 2
    # maxNuerons = 50
    # stepNuerons = 2
    # pMin = 10
    # pMax = 90
    # pStep = 5
    
    # for j in range(pMin, pMax+1, pStep):
        
    #     e_trained = []
    #     e_untrained = []
        
    #     for i in range(minNuerons, maxNuerons+1, stepNuerons):
            
    #         # print(f"Cantidad de Neuronas ocultas: {i}")
    #         _, _, et, eu = DL_SISO(
    #             AFunction="ReLU",
    #             HFunction="ReLU",
    #             h_dim=i,
    #             graficar = False,
    #             p_test=j/100.0
    #         )
        
    #         e_trained.append(et)
    #         e_untrained.append(eu)
            
    #     e_trained = np.array(e_trained).reshape(-1, 2)
    #     e_untrained = np.array(e_untrained).reshape(-1, 2)
        
    #     plt.figure(figsize=(8, 5.5), dpi=120)
    #     plt.errorbar(x=np.arange(minNuerons, maxNuerons+1, stepNuerons), y=e_untrained[:, 0], yerr=e_untrained[:, 1], fmt='-o', ecolor='red', capsize=5)
    #     plt.title('Error Promedio vs Cantidad de Neuronas Ocultas', fontsize=11, fontweight='bold', pad=10)
    #     plt.xlabel('Cantidad de Neuronas Ocultas', fontsize=10)
    #     plt.ylabel('Error Promedio', fontsize=10)
    #     plt.xticks(np.arange(0, maxNuerons+1, stepNuerons*3))
    #     plt.grid(True)
    #     plt.tight_layout()
    #     plt.show() 
        
    #     texto_estado = Text()
    #     texto_estado.append(f"Error Promedio Mínimo: {np.min(e_untrained[:, 0]):.4f}", style="bold")
    #     texto_estado.append(f"\nDesviación estándar Mínima: {np.std(e_untrained[:, 0]):.4f}", style="bold")

    #     console = Console()
    #     console.print(Panel(
    #         texto_estado, 
    #         title=f"[blue]Porcentaje de datos de prueba: {j/100.0:.2f}[/blue]", 
    #         border_style="green",
    #         padding=(1, 2) # Padding vertical=1, horizontal=2
    #     ))
    
    