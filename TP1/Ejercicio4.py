import numpy as np
import matplotlib.pyplot as plt
from Ejercicio3 import TempleSimulado
from Ejercicio1 import csv_to_array


class AlgoritmoGenetico:

    def __init__(self):
        self.grilla = csv_to_array("TP1/utilities/casillas.csv")
        self.N_poblacion = 100
        self.long_individuo = 48
        self.generaciones = 10
        self.n_elite = 4

        # Parámetros de evaluación con temple
        self.temperatura0 = 800
        self.cooling_rate = 0.95
        self.min_temperatura = 1

        # Para reducir ruido en la evaluación
        self.repeticiones_evaluacion = 1

        # Semilla base para reproducibilidad parcial
        self.seed_base = 1234

    # =========================
    # Inicialización
    # =========================
    def inicializar_poblacion(self) -> np.ndarray:
        return np.array([
            np.random.permutation(self.long_individuo) + 1
            for _ in range(self.N_poblacion)
        ])

    # =========================
    # Evaluación
    # =========================
    def evaluar_individuo(self, individuo: np.ndarray, seed: int | None = None) -> float:
        """
        Evalúa un individuo una sola vez.
        Si TempleSimulado usa aleatoriedad basada en numpy, fijar seed ayuda a estabilizar resultados.
        """
        if seed is not None:
            np.random.seed(seed)

        simulacion = TempleSimulado(self.grilla)
        costo_total = simulacion.busquedaLocal(
            numero_orden=0,
            Temperatura0=self.temperatura0,
            coolingRate=self.cooling_rate,
            minTemperatura=self.min_temperatura,
            orden_particular=individuo
        )
        return float(costo_total[1])

    def evaluar_individuo_promedio(self, individuo: np.ndarray, repeticiones: int = 1, base_seed: int = 0) -> float:
        """
        Evalúa un individuo varias veces y devuelve el promedio.
        Esto ayuda si la evaluación tiene ruido/azar.
        """
        puntajes = []
        for k in range(repeticiones):
            seed = self.seed_base + base_seed + k
            puntaje = self.evaluar_individuo(individuo, seed=seed)
            puntajes.append(puntaje)
        return float(np.mean(puntajes))

    def evaluar_poblacion(self, poblacion: np.ndarray, generacion: int = 0) -> np.ndarray:
        """
        Evalúa toda la población.
        Usa semillas reproducibles por generación e individuo para reducir variabilidad.
        """
        puntajes = []
        for i, individuo in enumerate(poblacion):
            base_seed = generacion * 100000 + i * 100
            puntaje = self.evaluar_individuo_promedio(
                individuo,
                repeticiones=self.repeticiones_evaluacion,
                base_seed=base_seed
            )
            puntajes.append(puntaje)

        return np.array(puntajes, dtype=float)

    # =========================
    # Fitness y selección
    # =========================
    def calcular_fitness(self, puntajes: np.ndarray) -> np.ndarray:
        """
        Menor puntaje = mejor.
        Se transforma a fitness positivo mayor = mejor.
        """
        return 1.0 / (puntajes + 1e-12)

    def calcular_probabilidades(self, fitness: np.ndarray) -> np.ndarray:
        suma = np.sum(fitness)
        if suma <= 0:
            return np.ones_like(fitness) / len(fitness)
        return fitness / suma

    def seleccionar_parejas_ruleta(
        self,
        poblacion: np.ndarray,
        probabilidades: np.ndarray,
        cantidad_parejas: int
    ) -> list[tuple[np.ndarray, np.ndarray]]:

        parejas = []
        indices = np.arange(len(poblacion))

        for _ in range(cantidad_parejas):
            idx1 = np.random.choice(indices, p=probabilidades)
            padre1 = poblacion[idx1].copy()

            mascara = indices != idx1
            indices_restantes = indices[mascara]
            probabilidades_restantes = probabilidades[mascara]

            suma_restante = np.sum(probabilidades_restantes)
            if suma_restante <= 0:
                probabilidades_restantes = np.ones_like(probabilidades_restantes) / len(probabilidades_restantes)
            else:
                probabilidades_restantes = probabilidades_restantes / suma_restante

            idx2 = np.random.choice(indices_restantes, p=probabilidades_restantes)
            padre2 = poblacion[idx2].copy()

            parejas.append((padre1, padre2))

        return parejas

    def obtener_elite(self, poblacion: np.ndarray, puntajes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Devuelve los n_elite mejores individuos y sus puntajes correspondientes.
        """
        indices_ordenados = np.argsort(puntajes)  # menor puntaje = mejor
        indices_elite = indices_ordenados[:self.n_elite]

        elite = np.array([poblacion[i].copy() for i in indices_elite])
        puntajes_elite = np.array([puntajes[i] for i in indices_elite], dtype=float)

        return elite, puntajes_elite

    # =========================
    # Cruce
    # =========================
    def cruce_ciclos(self, padre1: np.ndarray, padre2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        n = len(padre1)
        hijo1 = np.full(n, -1, dtype=int)
        hijo2 = np.full(n, -1, dtype=int)

        visitado = np.zeros(n, dtype=bool)
        pos_en_padre1 = {valor: i for i, valor in enumerate(padre1)}

        ciclo = 0
        while not np.all(visitado):
            inicio = np.where(~visitado)[0][0]
            idx = inicio
            indices_ciclo = []

            while not visitado[idx]:
                indices_ciclo.append(idx)
                visitado[idx] = True
                valor = padre2[idx]
                idx = pos_en_padre1[valor]

            if ciclo % 2 == 0:
                for i in indices_ciclo:
                    hijo1[i] = padre1[i]
                    hijo2[i] = padre2[i]
            else:
                for i in indices_ciclo:
                    hijo1[i] = padre2[i]
                    hijo2[i] = padre1[i]

            ciclo += 1

        return hijo1, hijo2

    # =========================
    # Mutación
    # =========================
    def mutacion_swap(self, individuo: np.ndarray, prob_mutacion: float = 0.1) -> np.ndarray:
        nuevo = individuo.copy()

        if np.random.rand() < prob_mutacion:
            i, j = np.random.choice(len(nuevo), size=2, replace=False)
            nuevo[i], nuevo[j] = nuevo[j], nuevo[i]

        return nuevo

    def mutacion_insercion(self, individuo: np.ndarray, prob_mutacion: float = 0.1) -> np.ndarray:
        nuevo = individuo.copy()

        if np.random.rand() < prob_mutacion:
            i, j = np.random.choice(len(nuevo), size=2, replace=False)

            valor = nuevo[i]
            nuevo = np.delete(nuevo, i)
            nuevo = np.insert(nuevo, j, valor)

        return nuevo

    # =========================
    # Generación de hijos
    # =========================
    def generar_hijos(
        self,
        parejas: list[tuple[np.ndarray, np.ndarray]],
        cantidad_hijos: int,
        prob_cruce: float = 0.5,
        prob_mutacion: float = 0.05
    ) -> np.ndarray:

        hijos = []

        for padre1, padre2 in parejas:
            if len(hijos) >= cantidad_hijos:
                break

            if np.random.rand() < prob_cruce:
                hijo1, hijo2 = self.cruce_ciclos(padre1, padre2)
            else:
                hijo1, hijo2 = padre1.copy(), padre2.copy()

            hijo1 = self.mutacion_swap(hijo1, prob_mutacion)
            hijo2 = self.mutacion_swap(hijo2, prob_mutacion)

            hijos.append(hijo1)

            if len(hijos) < cantidad_hijos:
                hijos.append(hijo2)

        return np.array(hijos, dtype=int)

    # =========================
    # Algoritmo principal
    # =========================
    def algoritmo(
        self,
        max_generaciones: int = 100,
        prob_cruce: float = 0.5,
        prob_mutacion: float = 0.05
    ):

        poblacion = self.inicializar_poblacion()
        print("Población inicializada")
        print(f"Ejemplo de individuo inicial: {poblacion[0]}")

        historial_fitness_max = []
        historial_fitness_prom = []
        historial_puntaje_min = []
        historial_puntaje_prom = []
        historial_mejor_global = []

        historial_mejor_individuo_generacion = []
        historial_mejor_puntaje_generacion = []

        mejor_individuo = None
        mejor_puntaje = np.inf

        for gen in range(max_generaciones):
            # Evaluar población actual
            puntajes = self.evaluar_poblacion(poblacion, generacion=gen)
            fitness = self.calcular_fitness(puntajes)
            probabilidades = self.calcular_probabilidades(fitness)

            # Mejor individuo de la generación
            idx_mejor = np.argmin(puntajes)
            mejor_individuo_generacion = poblacion[idx_mejor].copy()
            mejor_puntaje_generacion = float(puntajes[idx_mejor])

            print(f"\nGeneración {gen}")
            print(f"Mejor puntaje generación = {mejor_puntaje_generacion}")
            print(f"Mejor individuo generación = {mejor_individuo_generacion}")

            historial_mejor_individuo_generacion.append(mejor_individuo_generacion.copy())
            historial_mejor_puntaje_generacion.append(mejor_puntaje_generacion)

            # Actualizar mejor global
            if mejor_puntaje_generacion < mejor_puntaje:
                mejor_puntaje = mejor_puntaje_generacion
                mejor_individuo = mejor_individuo_generacion.copy()

            # Guardar evolución
            historial_fitness_max.append(float(np.max(fitness)))
            historial_fitness_prom.append(float(np.mean(fitness)))
            historial_puntaje_min.append(float(np.min(puntajes)))
            historial_puntaje_prom.append(float(np.mean(puntajes)))
            historial_mejor_global.append(float(mejor_puntaje))

            # =========================
            # ELITISMO
            # =========================
            elite, puntajes_elite = self.obtener_elite(poblacion, puntajes)

            print("Puntajes elite actuales:", puntajes_elite)

            # Cantidad de hijos necesarios para completar la nueva población
            cantidad_hijos = self.N_poblacion - self.n_elite
            cantidad_parejas = int(np.ceil(cantidad_hijos / 2))

            # Seleccionar parejas
            parejas = self.seleccionar_parejas_ruleta(
                poblacion,
                probabilidades,
                cantidad_parejas=cantidad_parejas
            )

            # Generar hijos
            hijos = self.generar_hijos(
                parejas,
                cantidad_hijos=cantidad_hijos,
                prob_cruce=prob_cruce,
                prob_mutacion=prob_mutacion
            )

            # Nueva población = élite + hijos
            poblacion = np.vstack((elite, hijos))

            # Verificación estructural del elitismo: los primeros n_elite deben ser exactamente la élite
            coincide_elite = np.array_equal(poblacion[:self.n_elite], elite)
            #print("¿Elite copiada intacta a la nueva población?:", coincide_elite)

        return {
            "poblacion_final": poblacion,
            "mejor_individuo": mejor_individuo,
            "mejor_puntaje": mejor_puntaje,
            "historial_fitness_max": historial_fitness_max,
            "historial_fitness_prom": historial_fitness_prom,
            "historial_puntaje_min": historial_puntaje_min,
            "historial_puntaje_prom": historial_puntaje_prom,
            "historial_mejor_global": historial_mejor_global,
            "historial_mejor_individuo_generacion": historial_mejor_individuo_generacion,
            "historial_mejor_puntaje_generacion": historial_mejor_puntaje_generacion
        }


if __name__ == "__main__":

    ag = AlgoritmoGenetico()

    # Si la evaluación con temple tiene mucho ruido, prueba con 3
    ag.repeticiones_evaluacion = 1

    resultados = ag.algoritmo(
        max_generaciones=10,
        prob_cruce=0.8,
        prob_mutacion=0.04
    )

    print("\n=========================")
    print("Mejor individuo global:")
    print(resultados["mejor_individuo"])

    print("\nMejor puntaje global:")
    print(resultados["mejor_puntaje"])

    # Gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(resultados["historial_puntaje_min"], label="Mejor de la generación")
    plt.plot(resultados["historial_puntaje_prom"], label="Puntaje promedio")
    plt.plot(resultados["historial_mejor_global"], label="Mejor global histórico")
    plt.xlabel("Generación")
    plt.ylabel("Puntaje")
    plt.title("Evolución del puntaje")
    plt.legend()
    plt.grid(True)
    plt.show()