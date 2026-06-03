
import numpy as np
import matplotlib.pyplot as plt


def expand(
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
        ActivationFunction: str = ["Identity", "Sigmoid", "Tanh", "ReLU"]
        ):
        
        self.n = InputDim
        self.q = OutputDim
        
        # Inicialización adaptativa (según Xavier/He)
        self.WeightMatrix = np.random.rand(self.n, self.q) * np.sqrt(2 / self.n)
        self.Bias = np.zeros((self.q, 1))
        
        self.AFunction = ActivationFunction
        
        

    def predict(self, *,
        InputVector: np.ndarray,
        ) -> np.ndarray:
        
        """Función de predicción del perceptrón."""
        [m, n] = InputVector.shape
        
        
        if n != self.n:
            raise ValueError(f"Dimensión de entrada incorrecta. \nSe esperaba una entrada de dim = {self.n}, pero se recibió una de dim = {n}.")
        
        OutputVector = np.zeros((m, self.q))
        
        WeightedVector = np.dot(InputVector, self.WeightMatrix) + self.Bias
        
        OutputVector = self._activate(WeightedVector)
        
        return OutputVector

    def _activate(self, WeightedVector: np.ndarray) -> np.ndarray:
        """Asignación de la función de activación."""
        match self.AFunction:
            case "Identity": 
                return WeightedVector
            case "Sigmoid": 
                return 1 / (1 + np.exp(-WeightedVector))
            case "Tanh": 
                return np.tanh(WeightedVector)
            case "ReLU": 
                return np.maximum(0, WeightedVector)
            case _: 
                # Si no coincide con ninguno, lanzamos el error inmediatamente
                raise ValueError(f"La función de activación '{self.AFunction}' no es válida.")
            
    def fit(self, *, 
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
        
        self.Loss = np.zeros(Epochs)
        self.Loss_test =  np.zeros(Epochs) if TestData is not None and TargetTest is not None else None
        self.W_gradient = np.zeros((Epochs, 1))
        self.B_gradient = np.zeros((Epochs, 1))
        
        
        for epoch in range(Epochs):
            # 1. Forward Propagation
            Y = self.predict(InputVector=X)
                        
            # 2. Cálculo del error
            Error = T - Y
            
            # Guardar el costo (MSE) actual
            mse_actual = np.mean(Error ** 2)
            self.Loss[epoch] = mse_actual
            
            # 3. Cálculo de gradientes
            dW = -np.dot(X.T, Error) / m
            dB = -np.sum(Error, axis=0, keepdims=True) / m
            
            # Se calcula la norma para dW y dB
            
            self.W_gradient[epoch] = np.linalg.norm(dW)
            self.B_gradient[epoch] = np.linalg.norm(dB)
            if TestData is not None and TargetTest is not None:
                Y_test = self.predict(InputVector=TestData)
                mse_test = np.mean((TargetTest - Y_test) ** 2)
                self.Loss_test[epoch] = mse_test
            # ----------------------------------------------------
            
            # 4. Actualización de parámetros
            self.WeightMatrix -= LearningRate * dW
            self.Bias -= LearningRate * dB
            
    def graficarGradientes(self, 
        escala_logaritmica: bool = True, 
        saveFig: bool = False, 
        label: str = "gradientes.png"):
        """
        Grafica la evolución temporal de la norma de los gradientes de W y B.
        """
        
        epocas = range(len(self.Loss))
        
        # Inicializar lienzo estilizado
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
        
        # Graficar la norma del gradiente de los pesos
        ax.plot(epocas, self.W_gradient,
                color='#0072BD', linewidth=1.5, label=r'Norma del Gradiente $\nabla W$')
        
        # Graficar la norma del gradiente del sesgo
        ax.plot(epocas, self.B_gradient, 
                color='#D95319', linewidth=1.5, linestyle='--', label=r'Norma del Gradiente $\nabla b$')
        
        # Configurar escala logarítmica para observar variaciones de órdenes de magnitud
        if escala_logaritmica:
            ax.set_yscale('log')
            ax.set_ylabel('Norma Euclídea (Escala Log)', fontsize=10)    
        else:
            ax.set_yscale('linear')
            ax.set_ylabel('Norma Euclídea (Escala Linear)', fontsize=10)
            
        
        # Formato y etiquetas técnicas
        ax.set_title('Evolución de la Magnitud del Gradiente', fontsize=11, fontweight='bold', pad=10)
        ax.set_xlabel('Época de Entrenamiento', fontsize=10)
        
        ax.grid(True, which='both', linestyle=':', linewidth=0.5, color='#B0B0B0')
        ax.tick_params(direction='in', top=True, right=True, labelsize=9)
        ax.legend(loc='upper right', frameon=True, fontsize=9)
        
        plt.tight_layout()
        
        if saveFig:
            if label is None:
                label = f"E1 SISO {self.AFunction} Gradientes.pdf"
            else:
                nombre_archivo = label
            
            plt.savefig(f"./TP3/Imagen/{nombre_archivo}", dpi=300, bbox_inches='tight')
            
        plt.show()
        
    def graficarLoss(self, 
                     saveFig: bool = False,
                     label: str = None):
        """
        Grafica la evolución de la función de pérdida (MSE) en función de las épocas.
        """
        if not hasattr(self, 'Loss'):
            raise ValueError("El modelo no contiene el historial de pérdida. Ejecute Fit primero.")
            
        epocas = range(len(self.Loss))
        
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
        
        # Curva de pérdida en entrenamiento
        ax.plot(epocas, self.Loss, 
                color='#0072BD', linewidth=1.5, label='Loss Entrenamiento (Train)')
        
        # Curva de pérdida en prueba (si existe registro)
        if len(self.Loss_test) > 0:
            ax.plot(epocas, self.Loss_test, 
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
        if saveFig:
            if label is None:
                label = f"E1 SISO {self.AFunction} Loss {self._q} Neurons.pdf"
            else:
                nombre_archivo = label
            
            plt.savefig(f"./TP3/Imagen/{nombre_archivo}", dpi=300, bbox_inches='tight')
        plt.show()


class HiddenLayerPerceptron:
    def __init__(self, *,
                 InputDim: int = 1,
                 HiddenDim: int,
                 OutputDim: int = 1,
                 ActivationHidden: str = "ReLU",
                 AFunction: str = "ReLU"):
        """
        Inicialización del MLP SISO con una única capa oculta.
        """
        self._n = InputDim          
        self._p = HiddenDim         
        self._q = OutputDim         
        self.HFunction = ActivationHidden
        self.AFunction = AFunction
        
        # Inicialización adaptativa (raiz de la cantidad de neuronas en la capa anterior)
        self._W1 = np.random.randn(self._n, self._p) * np.sqrt(2/self._n)
        self._B1 = np.zeros((1, self._p))
        
        self._W2 = np.random.randn(self._p, self._q) * np.sqrt(2/self._p)
        self._B2 = np.zeros((1, self._q))
        
    def _get_params(self):
        return self._W1, self._B1, self._W2, self._B2

    def _activate(self, WeightedVector: np.ndarray, function: str) -> np.ndarray:
        """Asignación de la función de activación."""
        match function:
            case "Identity": 
                return WeightedVector
            case "Sigmoid": 
                return 1 / (1 + np.exp(-WeightedVector))
            case "Tanh": 
                return np.tanh(WeightedVector)
            case "ReLU": 
                return np.maximum(0, WeightedVector)
            case "LeakyReLU":
                return np.where(WeightedVector > 0, WeightedVector, 0.001 * WeightedVector)
            case _: 
                # Si no coincide con ninguno, lanzamos el error inmediatamente
                raise ValueError(f"La función de activación '{self.AFunction}' no es válida.")
            

    def _derived_activate(self, activated_h: np.ndarray, func: str) -> np.ndarray:
        """
        Derivadas de las funciones de activación expresadas 
        en términos de la salida ya activada.
        """
        match func:
            case "Identity": 
                return np.ones_like(activated_h)
            case "Sigmoid": 
                return activated_h * (1 - activated_h)
            case "Tanh": 
                return 1 - activated_h ** 2
            case "ReLU": 
                return np.where(activated_h > 0, 1.0, 0.0)
            case "LeakyReLU":
                return np.where(activated_h > 0, 1.0, 0.001)
            case _: 
                # Si no coincide con ninguno, lanzamos el error inmediatamente
                raise ValueError(f"La función de activación '{self.HFunction}' no es válida.")
            

    def predict(self, *, InputVector: np.ndarray) -> tuple:
        """
        Forward Propagation. 
        Devuelve la salida final y los estados intermedios necesarios para Backpropagation.
        """
        m, n = InputVector.shape
        if n != self._n:
            raise ValueError(f"Dimensión de entrada incorrecta. Se esperaba {self._n}, se recibió {n}.")
            
        # 1. Capa Oculta
        Z1 = np.dot(InputVector, self._W1) + self._B1
        H = self._activate(Z1, self.HFunction)
        
        # 2. Capa de Salida 
        Z2 = np.dot(H, self._W2) + self._B2
        Y = self._activate(Z2, self.AFunction)
        
        return Y, H

    def fit(self, *, 
            TrainingData: np.ndarray, 
            TargetData: np.ndarray,
            TestData: np.ndarray = None,
            TargetTest: np.ndarray = None, 
            LearningRate: float = 0.01, 
            Epochs: int = 1000):
        """
        Entrenamiento mediante Descenso por el Gradiente y Backpropagation optimizado.
        """
        m = TrainingData.shape[0]
        X = TrainingData.reshape(m, self._n)
        T = TargetData.reshape(m, self._q)
        
        if TestData is not None and TargetTest is not None:
            m_test = TestData.shape[0]
            X_test = TestData.reshape(m_test, self._n)
            T_test = TargetTest.reshape(m_test, self._q)
        
        # Estructuras para el registro del costo (MSE)
        self.Loss = np.zeros(Epochs)
        self.Loss_test =  np.zeros(Epochs) if TestData is not None and TargetTest is not None else None
        self.W_gradients = np.zeros((Epochs, 2))
        self.B_gradients = np.zeros((Epochs, 2))
        
        
        for epoch in range(Epochs):
            # 1. Forward Propagation
            Y, H = self.predict(InputVector=X)
            
            # 2. Cálculo del costo (MSE) de entrenamiento de la época actual
            Error = Y - T
            
            
            # Validación cruzada ciega (se descarta H_test con _)
            if TestData is not None and TargetTest is not None:
                Y_test, _ = self.predict(InputVector=X_test)
                mse_test = np.mean((T_test - Y_test) ** 2)
                self.Loss_test[epoch] = mse_test
            
            # 3. Backpropagation (Cálculo de Gradientes)
            # Capa de Salida
            dY = (2.0 / m) * Error
            dW2 = np.dot(H.T, dY)
            dB2 = np.sum(dY, axis=0, keepdims=True)
            
            # Retropropagación hacia la Capa Oculta
            dH = np.dot(dY, self._W2.T)
            dZ1 = dH * self._derived_activate(H, self.HFunction)
            dW1 = np.dot(X.T, dZ1)
            dB1 = np.sum(dZ1, axis=0, keepdims=True)
            
            # 4. Consolidación de gradientes en el ndarray unificado
            self.Loss[epoch] = np.mean(Error ** 2)
            self.W_gradients[epoch, 0] = np.linalg.norm(dW1)
            self.W_gradients[epoch, 1] = np.linalg.norm(dW2)
            self.B_gradients[epoch, 0] = np.linalg.norm(dB1)
            self.B_gradients[epoch, 1] = np.linalg.norm(dB2)
            
            
            # 5. Actualización de Parámetros
            self._W2 -= LearningRate * dW2
            self._B2 -= LearningRate * dB2
            self._W1 -= LearningRate * dW1
            self._B1 -= LearningRate * dB1
            
    def graficarGradientes(self, escala_logaritmica: bool = True, saveFig: bool = False):
        """
        Grafica la evolución temporal de la norma de los gradientes de W y B.
        """
        
        epocas = range(len(self.Loss))
        
        # Inicializar lienzo estilizado
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
        
        # Graficar la norma del gradiente de los pesos
        ax.plot(epocas, self.W_gradients[:, 0],
                color='#0072BD', linewidth=1.5, label=r'$\nabla W_1$')
        
        ax.plot(epocas, self.W_gradients[:, 1],
                color='#0072BD', linewidth=1.5, linestyle='--', label=r'$\nabla W_2$')
        
        
        # Graficar la norma del gradiente del sesgo
        ax.plot(epocas, self.B_gradients[:, 0], 
                color='#D95319', linewidth=1.5, linestyle='--', label=r'$\nabla b_1$')
        
        ax.plot(epocas, self.B_gradients[:, 1], 
                color='#D95319', linewidth=1.5, label=r'$\nabla b_2$')
        
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
        if saveFig:
            nombre_archivo = f"E1 MISO {self.AFunction} Gradientes {self._q} Neurons.pdf" 
            plt.savefig(f"./TP3/Imagen/{nombre_archivo}", dpi=300, bbox_inches='tight')
        plt.show()
        
    def graficarLoss(self, 
                     saveFig: bool = False,
                     label: str = None):
        """
        Grafica la evolución de la función de pérdida (MSE) en función de las épocas.
        """
        if not hasattr(self, 'Loss'):
            raise ValueError("El modelo no contiene el historial de pérdida. Ejecute Fit primero.")
            
        epocas = range(len(self.Loss))
        
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
        
        # Curva de pérdida en entrenamiento
        ax.plot(epocas, self.Loss, 
                color='#0072BD', linewidth=1.5, label='Loss Entrenamiento (Train)')
        
        # Curva de pérdida en prueba (si existe registro)
        if len(self.Loss_test) > 0:
            ax.plot(epocas, self.Loss_test, 
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
        if saveFig:
            if label is None:
                label = f"E1 SISO {self.AFunction} Loss {self._q} Neurons.pdf"
            else:
                nombre_archivo = label
            
            plt.savefig(f"./TP3/Imagen/{nombre_archivo}", dpi=300, bbox_inches='tight')
        plt.show()