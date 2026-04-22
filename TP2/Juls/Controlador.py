import numpy as np
import matplotlib.pyplot as plt

class FuzzyController:
    def __init__(self):
        # Etiquetas lingüísticas
        self.labels = ["NG", "NM", "NP", "Z", "PP", "PM", "PG"]

        # Rangos de trabajo
        self.theta_range = (-179.0, 180.0)        # deg
        self.theta_dot_range = (-300.0, 300.0)    # deg/s
        self.force_range = (-300.0, 300.0)      # N

        # Funciones de pertenencia
        self.theta_mf = self.define_theta_mf()
        self.theta_dot_mf = self.define_theta_dot_mf()
        self.force_mf = self.define_force_mf()

        # Base de reglas como matriz 7x7:
        # filas = theta_p, columnas = theta
        # columnas:          NG    NM    NP    Z     PP    PM    PG
        self.rule_matrix = [
            ["PM", "NP", "NP", "NG", "PP", "PP", "NM"],  # theta_p = NG
            ["PG", "NM", "NM", "NM", "PM", "PM", "NG"],  # theta_p = NM
            ["PG", "NG", "NM", "NP", "PM", "PG", "NG"],  # theta_p = NP
            ["PG", "NM", "NP", "Z",  "PP", "PM", "NG"],  # theta_p = Z
            ["PG", "NG", "NM", "PP", "PM", "PG", "NG"],  # theta_p = PP
            ["PG", "NM", "NM", "PM", "PM", "PM", "NG"],  # theta_p = PM
            ["PM", "NP", "NP", "PG", "PP", "PP", "NM"]   # theta_p = PG
        ]

        # Centros para defuzzificación simplificada 
        self.output_centers = {
            "NG": -245.0,
            "NM": -145.0,
            "NP": -60.0,
            "Z":   0.0,
            "PP":  60.0,
            "PM":  145.0,
            "PG":  245.0
        }

    # --------------------------------------------------
    # FUNCIONES DE PERTENENCIA
    # --------------------------------------------------
    def define_theta_mf(self):
        return {
            "NG": (-180.0, -130.0, -80.0),
            "NM": (-100.0, -70.0,  -40.0),
            "NP": (-60.0,  -30.0,   0.0),
            "Z":  ( -5.0,   0.0,   5.0),
            "PP": (  0.0,   30.0,  60.0),
            "PM": (  40.0,   70.0, 100.0),
            "PG": (  80.0,  130.0, 180.0),
        }

    def define_theta_dot_mf(self):
        return {
            "NG": (-300.0, -240.0, -180.0),
            "NM": (-200.0, -145.0, -90.0),
            "NP": (-110.0,  -55.0,  -10.0),
            "Z":  ( -30.0,    0.0,   30.0),
            "PP": (  10.0,   55.0,  110.0),
            "PM": (  90.0,  145.0,  200.0),
            "PG": ( 180.0,  240.0,  300.0),
        }

    def define_force_mf(self):
        return {
            "NG": (-300.0, -245.0, -190.0),
            "NM": ( -210.0, -145.0, -90.0),
            "NP": ( -110.0, -60.0,  -10.0),
            "Z":  ( -15.0,   0.0,  15.0),
            "PP": (   10.0,  60.0,  110.0),
            "PM": ( 90.0,  145.0,  200.0),
            "PG": (  190.0,  245.0,  300.0),
        }

    def graficar_funciones_pertenencia(self):
        conjuntos = [
            ("Angulo theta", "theta [deg]", self.theta_mf, (-180.0, 180.0)),
            ("Velocidad angular theta_p", "theta_p [deg/s]", self.theta_dot_mf, (-400.0, 400.0)),
            ("Fuerza de control", "F [N]", self.force_mf, self.force_range),
        ]

        fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharey=True)
        fig.suptitle("Funciones de pertenencia del controlador fuzzy")

        for ax, (titulo, etiqueta_x, funciones, rango) in zip(axes, conjuntos):
            x = np.linspace(rango[0], rango[1], 600)

            for etiqueta in self.labels:
                a, b, c = funciones[etiqueta]
                y = [self.triangular(valor, a, b, c) for valor in x]
                ax.plot(x, y, label=etiqueta)

            ax.set_title(titulo)
            ax.set_xlabel(etiqueta_x)
            ax.set_ylabel("Pertenencia")
            ax.set_xlim(rango)
            ax.set_ylim(-0.05, 1.05)
            ax.grid(True, alpha=0.25, linestyle="--")
            ax.legend(loc="upper right", ncols=7, fontsize=8)

        fig.tight_layout(rect=[0, 0, 1, 0.96])
        return fig, axes

    def calcular_mapa_decisiones(self, cantidad_theta=90, cantidad_theta_dot=90):
        theta_valores = np.linspace(self.theta_range[0], self.theta_range[1], cantidad_theta)
        theta_dot_valores = np.linspace(self.theta_dot_range[0], self.theta_dot_range[1], cantidad_theta_dot)
        fuerzas = np.zeros((cantidad_theta_dot, cantidad_theta))

        for i, theta_dot in enumerate(theta_dot_valores):
            for j, theta in enumerate(theta_valores):
                fuerzas[i, j] = self.compute_control(theta, theta_dot)

        return theta_valores, theta_dot_valores, fuerzas

    def graficar_mapa_decisiones(self, cantidad_theta=90, cantidad_theta_dot=90):
        theta_valores, theta_dot_valores, fuerzas = self.calcular_mapa_decisiones(
            cantidad_theta=cantidad_theta,
            cantidad_theta_dot=cantidad_theta_dot,
        )

        fig, ax = plt.subplots(figsize=(8.5, 7))
        im = ax.imshow(
            fuerzas,
            cmap="coolwarm",
            vmin=self.force_range[0],
            vmax=self.force_range[1],
            origin="lower",
            aspect="auto",
            extent=[
                theta_valores[0],
                theta_valores[-1],
                theta_dot_valores[0],
                theta_dot_valores[-1],
            ],
        )

        ax.set_title("Mapa de calor de salida del controlador fuzzy")
        ax.set_xlabel("Posicion angular theta [deg]")
        ax.set_ylabel("Velocidad angular theta_p [deg/s]")
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label("Fuerza calculada [N]")
        fig.tight_layout()
        return fig, ax, theta_valores, theta_dot_valores, fuerzas

    # --------------------------------------------------
    # PERTENENCI TRIANGULAR
    # --------------------------------------------------
    def triangular(self, x, a, b, c): #Función de Pertenencia triangular, recibe un valor x y los parámetros a, b, c que definen la forma del triángulo
        if a == b and x <= b:
            return 1.0
        if b == c and x >= b:
            return 1.0
        if x <= a or x >= c:
            return 0.0
        elif a < x < b:
            return (x - a) / (b - a)
        elif b <= x < c:
            return (c - x) / (c - b)
        return 0.0

    # --------------------------------------------------
    # FUZZIFICACIÓN
    # --------------------------------------------------
    def fuzzify(self, x, mf_dict): 
    # Recibe un valor y un diccionario de funciones de pertenencia, devuelve un diccionario con los grados de pertenencia para cada etiqueta
        memberships = {} #Diccionario para almacenar los grados de pertenencia de cada etiqueta
        for label, (a, b, c) in mf_dict.items(): #Itera sobre cada etiqueta y su función de pertenencia definida por los parámetros a, b, c
            memberships[label] = self.triangular(x, a, b, c) #Calcula el grado de pertenencia para el valor x usando la función triangular y lo almacena en el diccionario
        return memberships

    # --------------------------------------------------
    # INFERENCIA
    # --------------------------------------------------
    #Recibe los grados de pertenencia para theta y theta_dot, devuelve una lista de reglas activadas con sus respectivos grados de activación
    def inference(self, theta_membership, theta_dot_membership): 
        activated_rules = []

        for i, theta_dot_label in enumerate(self.labels): #Itera sobre cada fila de theta_dot
            for j, theta_label in enumerate(self.labels): #Itera sobre cada columna de theta
                alpha = min(   #Minimo entre las pertenencias
                    theta_membership[theta_label], #Grado de pertenencia de theta para la etiqueta actual
                    theta_dot_membership[theta_dot_label] #Grado de pertenencia de theta_dot para la etiqueta actual
                )

                if alpha > 0.0:  #Si el grado de activación es mayor que cero, se considera que la regla está activada
                    output_label = self.rule_matrix[i][j]
                    activated_rules.append((alpha, output_label))

        return activated_rules

    # --------------------------------------------------
    # DEFUZZIFICACIÓN
    # --------------------------------------------------
    #Recibe una lista de reglas activadas con sus grados de activación, devuelve el valor de control calculado usando el método del centroide
    def defuzzify(self, activated_rules): 
        numerator = 0.0
        denominator = 0.0

        for alpha, output_label in activated_rules:  #Itera sobre cada regla activada, donde alpha es el grado de activación y output_label es la etiqueta de salida correspondiente a esa regla
            center = self.output_centers[output_label] #Obtiene el valor central asociado a la etiqueta de salida usando un diccionario predefinido
            numerator += alpha * center #Suma al numerador el producto del grado de activación por el valor central de la etiqueta de salida
            denominator += alpha #Suma al denominador el grado de activación

        if denominator == 0.0:
            return 0.0

        return numerator / denominator

    # --------------------------------------------------
    # CÁLCULO FINAL DEL CONTROL
    # --------------------------------------------------
    #Recibe el ángulo en grados y la velocidad angular en grados/s, devuelve la fuerza de control calculada por el controlador fuzzy
    def compute_control(self, theta, theta_dot): 
        # Saturación de entradas
        theta = np.clip(theta, *self.theta_range)  #Limita el valor de theta al rango definido para evitar valores extremos que puedan afectar la estabilidad del controlador
        theta_dot = np.clip(theta_dot, *self.theta_dot_range) #Limita el valor de theta_dot al rango definido para evitar valores extremos que puedan afectar la estabilidad del controlador

        # Paso 1: fuzzificación
        theta_membership = self.fuzzify(theta, self.theta_mf) #Calcula los grados de pertenencia para el ángulo theta 
        theta_dot_membership = self.fuzzify(theta_dot, self.theta_dot_mf) #Calcula los grados de pertenencia para la velocidad angular theta_dot

        # Paso 2: inferencia
        activated_rules = self.inference(theta_membership, theta_dot_membership) #Determina qué reglas de la base de reglas están activadas y con qué grado de activación, basándose en los grados de pertenencia calculados para theta y theta_dot

        # Paso 3: defuzzificación
        force = self.defuzzify(activated_rules) #Calcula el valor de control (fuerza) a aplicar al sistema utilizando el método del centroide
        # Saturación de salida
        force = np.clip(force, *self.force_range)

        return force
