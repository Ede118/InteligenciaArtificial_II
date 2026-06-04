
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
        self.W = np.random.rand(self.n, self.q) * np.sqrt(2 / self.n)
        self.B = np.zeros((self.q, 1))
        
        self.AFunction = ActivationFunction
        
        

    def predict(self, *,
        InputVector: np.ndarray,
        ) -> np.ndarray:
        
        """Función de predicción del perceptrón."""
        [m, n] = InputVector.shape
        
        
        if n != self.n:
            raise ValueError(f"Dimensión de entrada incorrecta. \nSe esperaba una entrada de dim = {self.n}, pero se recibió una de dim = {n}.")
        
        OutputVector = np.zeros((m, self.q))
        
        WeightedVector = np.dot(InputVector, self.W) + self.B
        
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
        self.gW = np.zeros((Epochs, 1))
        self.gB = np.zeros((Epochs, 1))
        
        
        for epoch in range(Epochs):
            # 1. Forward Propagation
            Y = self.predict(InputVector=X)
                        
            # 2. Cálculo del error
            Error = T - Y
            
            # Guardar el costo (MSE) actual
            MSE_epoch = np.mean(Error ** 2)
            self.Loss[epoch] = MSE_epoch
            
            # 3. Cálculo de gradientes
            dW = -np.dot(X.T, Error) / m
            dB = -np.sum(Error, axis=0, keepdims=True) / m
            
            # Se calcula la norma para dW y dB
            
            self.gW[epoch] = np.linalg.norm(dW)
            self.gB[epoch] = np.linalg.norm(dB)
            if TestData is not None and TargetTest is not None:
                Y_test = self.predict(InputVector=TestData)
                mse_test = np.mean((TargetTest - Y_test) ** 2)
                self.Loss_test[epoch] = mse_test
            # ----------------------------------------------------
            
            # 4. Actualización de parámetros
            self.W -= LearningRate * dW
            self.B -= LearningRate * dB
            
    def graficarGradientes(self, 
        escala_logaritmica: bool = True, 
        saveFig: bool = False, 
        label: str = None):
        """
        Grafica la evolución temporal de la norma de los gradientes de W y B.
        """
        
        epocas = range(len(self.Loss))
        
        # Inicializar lienzo estilizado
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
        
        # Graficar la norma del gradiente de los pesos
        ax.plot(epocas, self.gW,
                color='#0072BD', linewidth=1.5, label=r'Norma del Gradiente $\nabla W$')
        
        # Graficar la norma del gradiente del sesgo
        ax.plot(epocas, self.gB, 
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
                nombre_archivo = f"E1 SISO {self.AFunction} Gradientes.png"
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
                nombre_archivo = f"E1 SISO {self.AFunction} Loss {self.q} Neurons.png"
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
        self.n = InputDim          
        self.p = HiddenDim         
        self.q = OutputDim         
        self.HFunction = ActivationHidden
        self.AFunction = AFunction
        
        # Inicialización adaptativa (raiz de la cantidad de neuronas en la capa anterior)
        
        self.W = []
        self.B = []
        
        for n_in, n_out in [(self.n, self.p), (self.p, self.q)]:
            W = np.random.randn(n_in, n_out) * np.sqrt(2.0 / n_in)
            B = np.zeros((1, n_out))
            self.W.append(W)
            self.B.append(B)
        
    def _get_params(self):
        return self.W[0], self.B[0], self.W[1], self.B[1]

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
        if n != self.n:
            raise ValueError(f"Dimensión de entrada incorrecta. Se esperaba {self.n}, se recibió {n}.")
            
        # 1. Capa Oculta
        Z1 = np.dot(InputVector, self.W[0]) + self.B[0]
        H = self._activate(Z1, self.HFunction)
        
        # 2. Capa de Salida 
        Z2 = np.dot(H, self.W[1]) + self.B[1]
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
        X = TrainingData.reshape(m, self.n)
        T = TargetData.reshape(m, self.q)
        
        if TestData is not None and TargetTest is not None:
            m_test = TestData.shape[0]
            X_test = TestData.reshape(m_test, self.n)
            T_test = TargetTest.reshape(m_test, self.q)
        
        # Estructuras para el registro del costo (MSE)
        self.Loss = np.zeros(Epochs)
        self.Loss_test =  np.zeros(Epochs) if TestData is not None and TargetTest is not None else None
        self.gW = np.zeros((Epochs, 2))
        self.gB = np.zeros((Epochs, 2))
        
        
        for epoch in range(Epochs):
            # 1. Forward Propagation
            Y, H = self.predict(InputVector=X)
            
            # 2. Cálculo del costo (MSE) de entrenamiento de la época actual
            Error = Y - T
            
            dW = [np.zeros_like(self.W[0]), np.zeros_like(self.W[1])]
            dB = [np.zeros_like(self.B[0]), np.zeros_like(self.B[1])]
                                                                
            # Validación cruzada ciega (se descarta H_test con _)
            if TestData is not None and TargetTest is not None:
                Y_test, _ = self.predict(InputVector=X_test)
                mse_test = np.mean((T_test - Y_test) ** 2)
                self.Loss_test[epoch] = mse_test
            
            # 3. Backpropagation (Cálculo de Gradientes)
            # Capa de Salida
            dY = (2.0 / m) * Error
            dW[1] = np.dot(H.T, dY)
            dB[1] = np.sum(dY, axis=0, keepdims=True)
            
            # Retropropagación hacia la Capa Oculta
            dH = np.dot(dY, self.W[1].T)
            dZ1 = dH * self._derived_activate(H, self.HFunction)
            dW[0] = np.dot(X.T, dZ1)
            dB[0] = np.sum(dZ1, axis=0, keepdims=True)
            
            # 4. Consolidación de gradientes en el ndarray unificado
            self.Loss[epoch] = np.mean(Error ** 2)
            self.gW[epoch, 0] = np.linalg.norm(dW[0])
            self.gW[epoch, 1] = np.linalg.norm(dW[1])
            self.gB[epoch, 0] = np.linalg.norm(dB[0])
            self.gB[epoch, 1] = np.linalg.norm(dB[1])
            
            
            # 5. Actualización de Parámetros
            self.W[1] -= LearningRate * dW[1]
            self.B[1] -= LearningRate * dB[1]
            self.W[0] -= LearningRate * dW[0]
            self.B[0] -= LearningRate * dB[0]
            
    def graficarGradientes(self, escala_logaritmica: bool = True, saveFig: bool = False):
        """
        Grafica la evolución temporal de la norma de los gradientes de W y B.
        """
        
        epocas = range(len(self.Loss))
        
        # Inicializar lienzo estilizado
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
        
        # Graficar la norma del gradiente de los pesos
        ax.plot(epocas, self.gW[:, 0],
                color='#0072BD', linewidth=1.5, label=r'$\nabla W_1$')
        
        ax.plot(epocas, self.gW[:, 1],
                color='#0072BD', linewidth=1.5, linestyle='--', label=r'$\nabla W_2$')
        
        
        # Graficar la norma del gradiente del sesgo
        ax.plot(epocas, self.gB[:, 0], 
                color='#D95319', linewidth=1.5, linestyle='--', label=r'$\nabla b_1$')
        
        ax.plot(epocas, self.gB[:, 1], 
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
            nombre_archivo = f"E1 MISO {self.AFunction} Gradientes {self.q} Neurons.png" 
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
                label = f"E1 SISO {self.AFunction} Loss {self.q} Neurons.png"
            else:
                nombre_archivo = label
            
            plt.savefig(f"./TP3/Imagen/{nombre_archivo}", dpi=300, bbox_inches='tight')
        plt.show()
        

class DeepMultiLayerPerceptron:
    def __init__(self, *,
                 InputDim: int,
                 HiddenLayers: tuple,
                 OutputDim: int,
                 ActivationFunction: str = "ReLU"):
        
        self.n = InputDim
        self.q = OutputDim
        self.AFunction = ActivationFunction
        
        # Capa 0 es la entrada, Capa L es la salida, el resto son ocultas
        self.topology = [self.n] + list(HiddenLayers) + [self.q]
        self.L = len(self.topology) - 1  # Cantidad de capas con procesamiento
        
        # Listas indexadas para almacenar pesos y sesgos de cada interfaz
        self.WeightMatrices = []
        self.Biases = []
        
        # Inicialización adaptativa (He/Xavier) para toda la jerarquía en serie
        for k in range(self.L):
            n_in = self.topology[k]
            n_out = self.topology[k + 1]
            
            # Inicialización de He para mitigar el problema de "Dying ReLU"
            W = np.random.randn(n_in, n_out) * np.sqrt(2.0 / n_in)
            B = np.zeros((1, n_out))
            
            self.WeightMatrices.append(W)
            self.Biases.append(B)

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
                raise ValueError(f"La función de activación '{func}' no es válida.")
            

    def predict(self, *, InputVector: np.ndarray) -> tuple:
        """
        Forward Propagation Generalizado.
        Retorna la predicción Y y las listas de estados activados (H) e inducidos (Z).
        """
        m, features = InputVector.shape
        if features != self.n:
            raise ValueError(f"Dimensión de entrada incorrecta. Se esperaba {self.n}.")
            
        # Listas para almacenar las activaciones y potenciales de cada nivel
        # La activación de la capa 0 es la entrada misma de la red
        H_layers = [InputVector]
        Z_layers = []
        
        current_activation = InputVector
        
        for k in range(self.L):
            # Combinación lineal afín utilizando broadcasting
            Z = np.dot(current_activation, self.WeightMatrices[k]) + self.Biases[k]
            Z_layers.append(Z)
            
            # La última capa (k = num_layers - 1) es de salida -> Activación Identidad fija
            if k == self.L - 1:
                current_activation = self._activate(Z, "Identity")
            else:
                current_activation = self._activate(Z, self.AFunction)
                
            H_layers.append(current_activation)
            
        return current_activation, H_layers, Z_layers
    
    def fit(self, *, 
            TrainingData: np.ndarray, 
            TargetData: np.ndarray,
            TestData: np.ndarray = None,
            TargetTest: np.ndarray = None, 
            LearningRate: float = 0.01, 
            Epochs: int = 1000):
        """
        Entrenamiento mediante Descenso por el Gradiente y Backpropagation generalizado.
        """
        m = TrainingData.shape[0]
        X = TrainingData.reshape(m, self.n)
        T = TargetData.reshape(m, self.q)
        
        if TestData is not None and TargetTest is not None:
            m_test = TestData.shape[0]
            X_test = TestData.reshape(m_test, self.n)
            T_test = TargetTest.reshape(m_test, self.q)
        
        # Estructuras para el registro del costo (MSE)
        self.Loss = np.zeros(Epochs)
        self.Loss_test = np.zeros(Epochs) if TestData is not None and TargetTest is not None else None
        
        # Inicialización de matrices para registrar las normas escalares de los gradientes
        # Filas = Épocas, Columnas = Capas (Interfaces de parámetros)
        self.gW = np.zeros((Epochs, self.L))
        self.gB = np.zeros((Epochs, self.L))
        
        for epoch in range(Epochs):
            # 1. Forward Propagation
            Y, H, Z = self.predict(InputVector=X)
            
            # 2. Cálculo del costo (MSE) y sensibilidad de salida
            Error = Y - T
            self.Loss[epoch] = np.mean(Error ** 2)
            
            # Derivada de la pérdida respecto a la última combinación lineal Z^L
            # Para regresión, la activación de salida es Identidad (derivada = 1)
            dY = (2.0 / m) * Error
            
            # Validación cruzada ciega
            if TestData is not None and TargetTest is not None:
                Y_test, _, _ = self.predict(InputVector=X_test)
                self.Loss_test[epoch] = np.mean((T_test - Y_test) ** 2)
            
            # Contenedores locales limpios para los gradientes de la época actual
            dW_epoch = []
            dB_epoch = []
            
            dZ = dY

            # 3. Backpropagation (Lazo regresivo generalizado)
            for k in reversed(range(self.L)):
                dW_k = np.dot(H[k].T, dZ)
                dB_k = np.sum(dZ, axis=0, keepdims=True)
                
                if k > 0:
                    dH = np.dot(dZ, self.WeightMatrices[k].T)
                    dZ = dH * self._derived_activate(H[k], self.AFunction)

                # Inserción al inicio para preservar el orden correcto (0 a num_layers-1)
                dW_epoch.insert(0, dW_k)
                dB_epoch.insert(0, dB_k)
            
            # 4. Consolidación de gradientes y almacenamiento de normas para diagnóstico
            for k in range(self.L):
                self.gW[epoch, k] = np.linalg.norm(dW_epoch[k])
                self.gB[epoch, k] = np.linalg.norm(dB_epoch[k])
            
            # 5. Actualización de Parámetros utilizando las listas de la época actual
            self.WeightMatrices = [W - LearningRate * dW for W, dW in zip(self.WeightMatrices, dW_epoch)]
            self.Biases = [B - LearningRate * dB for B, dB in zip(self.Biases, dB_epoch)]
            
    def graficarGradientes(self, escala_logaritmica: bool = True, saveFig: bool = False, label: str = None):
        """
        Grafica la evolución temporal de la norma de los gradientes de W y B.
        """
        
        epocas = range(len(self.Loss))
        
        # Inicializar lienzo estilizado
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
        
        # Graficar la norma global del gradiente de los pesos
        ax.plot(epocas, np.linalg.norm(self.gW, axis=1),
                color='#0072BD', linewidth=1.5, label=r'Norma Global $\nabla W$')
        
        # Graficar la norma global del gradiente de los sesgos
        ax.plot(epocas, np.linalg.norm(self.gB, axis=1), 
                color='#D95319', linewidth=1.5, linestyle='--', label=r'Norma Global $\nabla b$')
        
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
            nombre_archivo = f"E1 MISO {self.AFunction} Gradientes MLP.png" if label is None else label
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
        if self.Loss_test is not None:
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
                nombre_archivo = f"E1 SISO {self.AFunction} Loss MLP.png"
            else:
                nombre_archivo = label
            
            plt.savefig(f"./TP3/Imagen/{nombre_archivo}", dpi=300, bbox_inches='tight')
        plt.show()