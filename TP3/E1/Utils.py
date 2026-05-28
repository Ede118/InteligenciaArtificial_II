
import matplotlib.pyplot as plt
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'serif'


def MostrarEstadisticos(*,
    variable: str,
    promedio: float,
    desviacion: float):
    console = Console()

    texto_estado = Text()
    texto_estado.append(f"Promedio: {promedio:.4f}", style="bold")
    texto_estado.append(f"\nDesviación estándar: {desviacion:.4f}", style="bold")

    console.print(Panel(
        texto_estado, 
        title=f"[blue]Variable: {variable}[/blue]", 
        border_style="green",
        padding=(1, 2) # Padding vertical=1, horizontal=2
    ))
    
def ExpandirCaracteristicasPolinomicas(X_original: np.ndarray, grado: int) -> np.ndarray:
    """
    Transforma una matriz de entrada (m x 1) en una matriz (m x grado)
    con las potencias sucesivas de x.
    """
    m = X_original.shape[0]
    X_poly = np.zeros((m, grado))
    
    for i in range(1, grado + 1):
        # Se eleva la columna original a la potencia i y se asigna a la columna i-1
        X_poly[:, i - 1] = (X_original ** i).flatten()
        
    return X_poly

def DividirEntrenamientoTest(
    X: np.ndarray, 
    T: np.ndarray, 
    test_size: float = 0.2, seed: int = 42):
    """
    Divide matrices de NumPy en conjuntos de entrenamiento y prueba de forma aleatoria.
    
    test_size: Proporción del dataset destinada a la prueba (ej: 0.2 = 20%)
    """
    np.random.seed(seed)
    m = X.shape[0]
    
    # 1. Generar un arreglo con los índices ordenados de 0 a m-1 y desordenarlos
    indices = np.arange(m)
    np.random.shuffle(indices)
    
    # 2. Determinar el punto de corte según el porcentaje requerido
    cantidad_test = int(m * test_size)
    
    indices_test = indices[:cantidad_test]
    indices_train = indices[cantidad_test:]
    
    # 3. Filtrar las matrices originales mediante indexación avanzada
    X_train, X_test = X[indices_train], X[indices_test]
    T_train, T_test = T[indices_train], T[indices_test]
    
    # Obtener los índices que ordenarían el conjunto de Train según su primera columna de características
    idx_sort_train = np.argsort(X_train[:, 0])
    X_train = X_train[idx_sort_train]
    T_train = T_train[idx_sort_train]
    
    # Obtener los índices que ordenarían el conjunto de Test según su primera columna de características
    idx_sort_test = np.argsort(X_test[:, 0])
    X_test = X_test[idx_sort_test]
    T_test = T_test[idx_sort_test]
    
    return X_train, X_test, T_train, T_test
    
    
def GraficarNormaGradientes(modelo, escala_logaritmica: bool = True):
    """
    Grafica la evolución temporal de la norma de los gradientes de W y B.
    """
    if not hasattr(modelo, 'history_norm_dW'):
        raise ValueError("El modelo no contiene el historial de gradientes. Verifique el método Fit.")
        
    epocas = range(len(modelo.history_norm_dW))
    
    # Inicializar lienzo estilizado
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
    
    # Graficar la norma del gradiente de los pesos
    ax.plot(epocas, modelo.history_norm_dW, 
            color='#0072BD', linewidth=1.5, label=r'Norma del Gradiente $\nabla W$')
    
    # Graficar la norma del gradiente del sesgo
    ax.plot(epocas, modelo.history_norm_dB, 
            color='#D95319', linewidth=1.5, linestyle='--', label=r'Norma del Gradiente $\nabla b$')
    
    # Configurar escala logarítmica para observar variaciones de órdenes de magnitud
    if escala_logaritmica:
        ax.set_yscale('log')
        ax.set_ylabel('Norma Euclídea (Escala Log)', fontsize=10)    
    else:
        ax.set_yscale('linear')
        ax.set_ylabel('Norma Euclídea (Escala Linear)', fontsize=10)
        
    
    # Formato y etiquetas técnicas
    ax.set_title('Evolución de la Magnitud del Gradiente (Salud del Aprendizaje)', fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel('Época de Entrenamiento', fontsize=10)
    
    ax.grid(True, which='both', linestyle=':', linewidth=0.5, color='#B0B0B0')
    ax.tick_params(direction='in', top=True, right=True, labelsize=9)
    ax.legend(loc='upper right', frameon=True, fontsize=9)
    
    plt.tight_layout()
    plt.show()
    


def GraficarCurvaPerdida(modelo):
    """
    Grafica la evolución de la función de pérdida (MSE) en función de las épocas.
    """
    if not hasattr(modelo, 'history_loss'):
        raise ValueError("El modelo no contiene el historial de pérdida. Ejecute Fit primero.")
        
    epocas = range(len(modelo.history_loss))
    
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
    
    # Curva de pérdida en entrenamiento
    ax.plot(epocas, modelo.history_loss, 
            color='#0072BD', linewidth=1.5, label='Loss Entrenamiento (Train)')
    
    # Curva de pérdida en prueba (si existe registro)
    if len(modelo.history_loss_test) > 0:
        ax.plot(epocas, modelo.history_loss_test, 
                color='#D95319', linewidth=1.5, linestyle='--', label='Loss Prueba (Test)')
    
    # Formato e instrumentación del gráfico
    ax.set_title('Evolución de la Función de Pérdida (Curva de Aprendizaje)', fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel('Época de Entrenamiento', fontsize=10)
    ax.set_ylabel('Error Cuadrático Medio (MSE)', fontsize=10)
    
    # En regresión, el error puede caer órdenes de magnitud, la escala logarítmica es opcional pero útil
    # ax.set_yscale('log') 
    
    ax.grid(True, which='both', linestyle=':', linewidth=0.5, color='#B0B0B0')
    ax.tick_params(direction='in', top=True, right=True, labelsize=9)
    ax.legend(loc='upper right', frameon=True, fontsize=9)
    
    plt.tight_layout()
    plt.show()