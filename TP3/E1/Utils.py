
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
    var_matrix: np.ndarray, 
    dep_matrix: np.ndarray, 
    test_size: float = 0.2, seed: int = 42):
    """
    Divide matrices de NumPy en conjuntos de entrenamiento y prueba de forma aleatoria.
    
    test_size: Proporción del dataset destinada a la prueba (ej: 0.2 = 20%)
    """
    np.random.seed(seed)
    m = var_matrix.shape[0]
    
    # 1. Generar un arreglo con los índices ordenados de 0 a m-1 y desordenarlos
    indices = np.arange(m)
    np.random.shuffle(indices)
    
    # 2. Determinar el punto de corte según el porcentaje requerido
    cantidad_test = int(m * test_size)
    
    indices_test = indices[:cantidad_test]
    indices_train = indices[cantidad_test:]
    
    # 3. Filtrar las matrices originales mediante indexación avanzada
    X_train, X_test = var_matrix[indices_train], var_matrix[indices_test]
    T_train, T_test = dep_matrix[indices_train], dep_matrix[indices_test]
    
    # Obtener los índices que ordenarían el conjunto de Train según su primera columna de características
    idx_sort_train = np.argsort(X_train[:, 0])
    X_train = X_train[idx_sort_train]
    T_train = T_train[idx_sort_train]
    
    # Obtener los índices que ordenarían el conjunto de Test según su primera columna de características
    idx_sort_test = np.argsort(X_test[:, 0])
    X_test = X_test[idx_sort_test]
    T_test = T_test[idx_sort_test]
    
    return X_train, X_test, T_train, T_test
    
    

