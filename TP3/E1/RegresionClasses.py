
import numpy as np

def Expand(
    VectorDatos: np.ndarray, 
    GradoExpansion: int) -> np.ndarray:
    """
    Transforma una matriz de entrada (m x 1) en una matriz (m x grado)
    con las potencias sucesivas de x.
    """
    m = VectorDatos.shape[0]
    MatrizAumentada = np.zeros((m, GradoExpansion))
    
    for i in range(1, GradoExpansion + 1):
        # Se eleva la columna original a la potencia i y se asigna a la columna i-1
        MatrizAumentada[:, i - 1] = (VectorDatos ** i).flatten()
        
    return MatrizAumentada

class Perceptron:
    def __init__(self,
        *,
        InputDim: int,                         # Input Dimension
        OutputDim: int,                         # Output Dimension
        Neurons: np.ndarray,
        ActivationFunction: str = ["Identity", "Sigmoid", "Tanh", "ReLU"]):
        
        self.n = InputDim
        self.q = OutputDim
        self.Neurons = Neurons
        
        self.WeightMatrix = np.ones((self.n, self.q)) * np.random.rand(self.n, self.q) * 0.5
        self.Bias = np.zeros((self.q, 1)) * 0.5
        
        self.ActivationFunction = ActivationFunction

    def Predict(self, *,
        InputVector: np.ndarray,
        ) -> np.ndarray:
        
        """Función de predicción del perceptrón."""
        [m, n] = InputVector.shape
        
        
        if n != self.n:
            raise ValueError(f"Dimensión de entrada incorrecta. \nSe esperaba una entrada de dim = {self.n}, pero se recibió una de dim = {n}.")
        
        OutputVector = np.zeros((m, self.q))
        
        WeightedVector = np.dot(InputVector, self.WeightMatrix) + self.Bias
        
        OutputVector = self.Activate(WeightedVector)
        
        return OutputVector

    def Activate(self, WeightedVector: np.ndarray) -> np.ndarray:
        """Asignación de la función de activación."""
        switcher = {
            "Identity": self._f_identity,
            "Sigmoid": self._f_sigmoid,
            "Tanh": self._f_tanh,
            "ReLU": self._f_relu
        }
        func = switcher.get(self.ActivationFunction, None)
        if func is None:
            raise ValueError(f"La función de activación '{self.ActivationFunction}' no es válida.")
        return func(WeightedVector)
    
    # Funciones de activación vectorizadas (soportan matrices de NumPy directamente)
    def _f_identity(self, x: np.ndarray) -> np.ndarray:
        return x

    def _f_tanh(self, x: np.ndarray) -> np.ndarray:
        return np.tanh(x)

    def _f_sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-x))

    def _f_relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)
    
    def Fit(self, *, 
            TrainingData: np.ndarray, 
            TargetData: np.ndarray, 
            TestData: np.ndarray = None,
            TargetTest: np.ndarray = None,
            LearningRate: float = 0.01, 
            Epochs: int = 100):
        """Entrenamiento mediante Descenso por el Gradiente (Regla LMS para lineal)."""
        
        m = TrainingData.shape[0]
        T = TargetData.reshape(m, self.q)       # Aseguramos que T tenga la forma (m, q)
        X = TrainingData.reshape(m, self.n)     # Aseguramos que X tenga la forma (m, n)
        
        self.history_loss = []
        self.history_norm_dW = []
        self.history_norm_dB = []
        self.history_loss_test = []
        
        
        for epoch in range(Epochs):
            # 1. Forward Propagation
            Y = self.Predict(InputVector=X)
                        
            # 2. Cálculo del error
            Error = T - Y
            
            # Guardar el costo (MSE) actual
            mse_actual = np.mean(Error ** 2)
            self.history_loss.append(mse_actual)
            
            # 3. Cálculo de gradientes
            dW = -np.dot(X.T, Error) / m
            dB = -np.sum(Error, axis=0, keepdims=True) / m
            
            # Se calcula la norma para dW y dB
            norma_dW = np.linalg.norm(dW)
            norma_dB = np.linalg.norm(dB)
            
            self.history_norm_dW.append(norma_dW)
            self.history_norm_dB.append(norma_dB)
            if TestData is not None and TargetTest is not None:
                Y_test = self.Predict(InputVector=TestData)
                mse_test = np.mean((TargetTest - Y_test) ** 2)
                self.history_loss_test.append(mse_test)
            # ----------------------------------------------------
            
            # 4. Actualización de parámetros
            self.WeightMatrix -= LearningRate * dW
            self.Bias -= LearningRate * dB
    



    