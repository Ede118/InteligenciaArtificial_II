
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
    


class HiddenLayerPerceptron:
    def __init__(self, *,
                 InputDim: int = 1,
                 HiddenDim: int,
                 OutputDim: int = 1,
                 ActivationHidden: str = "ReLU"):
        """
        Inicialización del MLP SISO con una única capa oculta.
        """
        self.n = InputDim          
        self.p = HiddenDim         
        self.q = OutputDim         
        self.ActivationHidden = ActivationHidden
        
        # Inicialización adaptativa (raiz de la cantidad de neuronas en la capa anterior)
        self.W1 = np.random.randn(self.n, self.p) / np.sqrt(self.n)
        self.B1 = np.zeros((1, self.p))
        
        self.W2 = np.random.randn(self.p, self.q) / np.sqrt(self.p)
        self.B2 = np.zeros((1, self.q))
        
    def _get_params(self):
        return self.W1, self.B1, self.W2, self.B2

    def _activate(self, x: np.ndarray, name: str) -> np.ndarray:
        """Asignación de la función de activación."""
        if name == "Identity":
            return x
        elif name == "Sigmoid":
            return 1 / (1 + np.exp(-x))
        elif name == "Tanh":
            return np.tanh(x)
        elif name == "ReLU":
            return np.maximum(0, x)
        else:
            raise ValueError(f"Función de activación '{name}' no válida.")

    def _derived_activate(self, activated_h: np.ndarray, name: str) -> np.ndarray:
        """
        Derivadas de las funciones de activación expresadas 
        en términos de la salida ya activada.
        """
        if name == "Identity":
            return np.ones_like(activated_h)
        elif name == "Sigmoid":
            return activated_h * (1 - activated_h)
        elif name == "Tanh":
            return 1 - activated_h ** 2
        elif name == "ReLU":
            return np.where(activated_h > 0, 1.0, 0.0)
        else:
            raise ValueError(f"Derivada no definida para '{name}'.")

    def Predict(self, *, InputVector: np.ndarray) -> tuple:
        """
        Forward Propagation. 
        Devuelve la salida final y los estados intermedios necesarios para Backpropagation.
        """
        m, n = InputVector.shape
        if n != self.n:
            raise ValueError(f"Dimensión de entrada incorrecta. Se esperaba {self.n}, se recibió {n}.")
            
        # 1. Capa Oculta
        Z1 = np.dot(InputVector, self.W1) + self.B1
        H = self._activate(Z1, self.ActivationHidden)
        
        # 2. Capa de Salida 
        Z2 = np.dot(H, self.W2) + self.B2
        Y = self._activate(Z2, "Identity")
        
        return Y, H

    def Fit(self, *, 
            TrainingData: np.ndarray, 
            TargetData: np.ndarray,
            TestData: np.ndarray = None,
            TargetTest: np.ndarray = None, 
            LearningRate: float = 0.01, 
            Epochs: int = 1000):
        """
        Entrenamiento mediante Descenso por el Gradiente y Backpropagation.
        """
        m = TrainingData.shape[0]
        X = TrainingData.reshape(m, self.n)
        T = TargetData.reshape(m, self.q)
        
        self.history_loss = []
        self.history_norm_dW1 = []
        self.history_norm_dW2 = []
        self.history_norm_dB1 = []
        self.history_norm_dB2 = []
        self.history_loss_test = []
        
        for epoch in range(Epochs):
            # 1. Forward Propagation
            Y, H = self.Predict(InputVector=X)
            
            
            # 3. Backpropagation (Cálculo de Gradientes)
            # Capa de Salida (Derivada de Identidad es 1)
            dY = (2.0 / m) * Error
            dW2 = np.dot(H.T, dY)
            dB2 = np.sum(dY, axis=0, keepdims=True)
            
            # Retropropagación hacia la Capa Oculta
            dH = np.dot(dY, self.W2.T)
            dZ1 = dH * self._derived_activate(H, self.ActivationHidden)
            
            dW1 = np.dot(X.T, dZ1)
            dB1 = np.sum(dZ1, axis=0, keepdims=True)
            
            # 2. Cálculo del Error Cuadrático Medio
            Error = Y - T
            mse = np.mean(Error ** 2)
            self.history_loss.append(mse)
            
            
            norma_dW1 = np.linalg.norm(dW1)
            norma_dB1 = np.linalg.norm(dB1)
            norma_dW2 = np.linalg.norm(dW2)
            norma_dB2 = np.linalg.norm(dB2)
            
            self.history_norm_dW1.append(norma_dW1)
            self.history_norm_dB1.append(norma_dB1)
            
            self.history_norm_dW2.append(norma_dW2)
            self.history_norm_dB2.append(norma_dB2)
            
            if TestData is not None and TargetTest is not None:
                Y_test = self.Predict(InputVector=TestData)
                mse_test = np.mean((TargetTest - Y_test) ** 2)
                self.history_loss_test.append(mse_test)
            # -----------------------------------------
            
            # 4. Actualización de Parámetros
            self.W2 -= LearningRate * dW2
            self.B2 -= LearningRate * dB2
            self.W1 -= LearningRate * dW1
            self.B1 -= LearningRate * dB1