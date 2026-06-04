
import os

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neural_network import MLPRegressor

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


from Utils import DividirEntrenamientoTest, MostrarEstadisticos
from RegresionClasses import HiddenLayerPerceptron, DeepMultiLayerPerceptron  

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
        
    HLModel = HiddenLayerPerceptron(
        InputDim=1, 
        HiddenDim=h_dim,
        OutputDim=1,
        ActivationHidden=HFunction,
        AFunction=AFunction
    )
        
        
    Untrained_Prediction, H = HLModel.predict(InputVector=Test_Input)
    

    HLModel.fit(
        TrainingData=Train_Input, 
        TargetData=Train_Output,
        TestData=Test_Input,
        TargetTest=Test_Output, 
        LearningRate=0.01, 
        Epochs=1000
    )
        
    Trained_Prediction, H = HLModel.predict(InputVector=Test_Input)
    
    
    if graficar:
        
        # =============================================================================== #
        #               Gráficos de evolución de la norma de los gradientes     
        # =============================================================================== #
        
        HLModel.graficarGradientes(escala_logaritmica=False)

        # =============================================================================== #
        #               Gráficos de evolución de la norma de los gradientes     
        # =============================================================================== #

        HLModel.graficarLoss()
        
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
        
    return HLModel

def ML_SISO(*,
    Train_Input: np.ndarray,
    Train_Output: np.ndarray,
    Test_Input: np.ndarray,
    Test_Output: np.ndarray,
    AFunction: str = "ReLU",
    HFunction: str = "ReLU",
    h_dim: tuple = (10,),
    graficar: bool = False
    ):        
        
    MLPModel = DeepMultiLayerPerceptron(
        InputDim=1,
        HiddenLayers=h_dim,
        OutputDim=1,
        ActivationFunction=AFunction
    )
    
    Untrained_Prediction, _, _ = MLPModel.predict(InputVector=Test_Input)
    

    MLPModel.fit(
        TrainingData=Train_Input, 
        TargetData=Train_Output,
        TestData=Test_Input,
        TargetTest=Test_Output, 
        LearningRate=0.01, 
        Epochs=1000
    )
        
    Trained_Prediction, _, _ = MLPModel.predict(InputVector=Test_Input)
    
    
    if graficar:
        
        # =============================================================================== #
        #               Gráficos de evolución de la norma de los gradientes     
        # =============================================================================== #
        
        MLPModel.graficarGradientes(escala_logaritmica=False)

        # =============================================================================== #
        #               Gráficos de evolución de la norma de los gradientes     
        # =============================================================================== #

        MLPModel.graficarLoss()
        
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
        
    return MLPModel
    
    
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
    h = 20
    ht = (4,4)
    
    Train_Input, Test_Input, Train_Output, Test_Output = DividirEntrenamientoTest(X, T, test_size=p_test)
    
    
    HLPCasero = DL_SISO(
        Train_Input=Train_Input,
        Train_Output=Train_Output,
        Test_Input=Test_Input,
        Test_Output=Test_Output,
        AFunction="ReLU",
        HFunction="ReLU",
        h_dim=h,
        graficar=False
    )
    
    modeloSKL1 = Sklearn_Model(
        Train_Input=Train_Input,
        Train_Output=Train_Output,
        Test_Input=Test_Input,
        Test_Output=Test_Output,
        HFunction="relu",
        h=(h,)
    )
    
    MLPCasero = ML_SISO(
        Train_Input=Train_Input,
        Train_Output=Train_Output,
        Test_Input=Test_Input,
        Test_Output=Test_Output,
        AFunction="ReLU",
        HFunction="ReLU",
        h_dim=ht,
        graficar=False
    )
    
    
    modeloSKL2 = Sklearn_Model(
        Train_Input=Train_Input,
        Train_Output=Train_Output,
        Test_Input=Test_Input,
        Test_Output=Test_Output,
        HFunction="relu",
        h=ht
    )
    
    # 1 Hidden Layer
    Trained_Prediction1, _ = HLPCasero.predict(InputVector=Test_Input)
    SKLearn_Prediction1 = modeloSKL1.predict(Test_Input)
    
    # Multiple Hidden Layers
    Trained_Prediction2, _, _ = MLPCasero.predict(InputVector=Test_Input)
    SKLearn_Prediction2 = modeloSKL2.predict(Test_Input)
    
    
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=120)
    
    ax.scatter(Test_Input, Test_Output, 
            facecolors='none', 
            edgecolors="#0019BD", 
            linewidths=0.7, 
            label='Datos del dataset')
    
    ax.plot(Test_Input, Trained_Prediction1, 
            color="#E64709",
            linestyle='--',
            linewidth=1.5, 
            label=f"1 Hidden Layer - {h} Neurons"
    )
    
    ax.plot(Test_Input, SKLearn_Prediction1, 
            color="#169B3A",
            linestyle='--', 
            linewidth=1.5, 
            label=f"SKL 1 Hidden Layer - {h} Neurons")
    
    ax.plot(Test_Input, Trained_Prediction2, 
            color="#E64709", 
            linewidth=1.5, 
            label=f"Multiple Layer - {ht} Neurons"
    )
    
    ax.plot(Test_Input, SKLearn_Prediction2, 
            color="#169B3A", 
            linewidth=1.5, 
            label=f"SKL Multiple Layers - {ht} Neurons")
    
    label_activation = "Comparacion: Casero vs SKLearn"
            
    ax.set_title(label_activation, fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel('Variable Independiente (x)', fontsize=10)
    ax.set_ylabel('Variable Dependiente (y)', fontsize=10)
    ax.tick_params(direction='in', top=True, right=True, labelsize=9)
    ax.legend(loc='upper left', frameon=True, fontsize=9)
    
    plt.tight_layout()
    nombre_archivo = f"E1 SISO Casero vs SKL.png" 
    plt.savefig(f"./TP3/Imagen/{nombre_archivo}", dpi=300, bbox_inches='tight')
    plt.show()
    
    # === Estadísticas y Coeficientes ===
    # 1. HLPCasero (1 Capa Oculta)
    err_1HL_prop_mean = np.mean((Test_Output - Trained_Prediction1) ** 2)
    err_1HL_prop_std = np.std((Test_Output - Trained_Prediction1) ** 2)
    coef_1HL_prop = sum(W.size + B.size for W, B in zip(HLPCasero.W, HLPCasero.B))
    
    # 2. SKLearn (1 Capa Oculta)
    err_1HL_SKL_mean = np.mean((Test_Output - SKLearn_Prediction1.reshape(-1, 1)) ** 2)
    err_1HL_SKL_std = np.std((Test_Output - SKLearn_Prediction1.reshape(-1, 1)) ** 2)
    coef_1HL_SKL = sum(modeloSKL1.coefs_[i].size + modeloSKL1.intercepts_[i].size for i in range(len(modeloSKL1.coefs_)))
    
    # 3. MLPCasero (Múltiples Capas Ocultas)
    err_ML_prop_mean = np.mean((Test_Output - Trained_Prediction2) ** 2)
    err_ML_prop_std = np.std((Test_Output - Trained_Prediction2) ** 2)
    coef_ML_prop = sum(W.size + B.size for W, B in zip(MLPCasero.WeightMatrices, MLPCasero.Biases))
    
    # 4. SKLearn (Múltiples Capas Ocultas)
    err_ML_SKL_mean = np.mean((Test_Output - SKLearn_Prediction2.reshape(-1, 1)) ** 2)
    err_ML_SKL_std = np.std((Test_Output - SKLearn_Prediction2.reshape(-1, 1)) ** 2)
    coef_ML_SKL = sum(modeloSKL2.coefs_[i].size + modeloSKL2.intercepts_[i].size for i in range(len(modeloSKL2.coefs_)))
    
    # === Paneles de Consola ===
    resultados = [
        (f"MLP Casero (1 Capa de {h})", err_1HL_prop_mean, err_1HL_prop_std, coef_1HL_prop),
        (f"SKLearn MLPRegressor (1 Capa de {h})", err_1HL_SKL_mean, err_1HL_SKL_std, coef_1HL_SKL),
        (f"Deep MLP Casero (Capas de {ht})", err_ML_prop_mean, err_ML_prop_std, coef_ML_prop),
        (f"SKLearn MLPRegressor (Capas de {ht})", err_ML_SKL_mean, err_ML_SKL_std, coef_ML_SKL)
    ]
    
    console = Console()
    for titulo, err_mean, err_std, coefs in resultados:
        texto = Text()
        texto.append(f"Error Promedio: {err_mean:.4f}", style="bold")
        texto.append(f"\nDesviación Estándar: {err_std:.4f}", style="bold")
        texto.append(f"\nCantidad de Coeficientes: {coefs}", style="bold")
        
        console.print(Panel(
            texto, 
            title=f"[blue]{titulo}[/blue]", 
            border_style="green",
            padding=(1, 2)
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
    
    