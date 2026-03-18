import numpy as np
import matplotlib.pyplot as plt
from Ejercicio1 import csv_to_array
from Ejercicio3 import TempleSimulado
from utilities.Graficador import Layout, Graficador, LectorFrecuenciasPedidos


class AlgoritmoGenetico:

    def __init__(self):
        self.grilla = csv_to_array("TP1/utilities/casillas.csv")
        self.N_poblacion = 200
        self.long_individuo = 48
        self.generaciones = 200
        self.n_elite = 6

        # Cargamos todas las órdenes del CSV
        self.simulacion = TempleSimulado(self.grilla)
        self.simulacion.cargar_ordenes("TP1/utilities/ordenes.csv")

    # Inicializar población
    def inicializar_poblacion(self) -> np.ndarray:
        return np.array([
            np.random.permutation(self.long_individuo) + 1
            for _ in range(self.N_poblacion)
        ])

    def evaluar_individuo(self, individuo: np.ndarray) -> float:
        """
        El costo del individuo es la suma de recorrer TODOS los pedidos del CSV,
        usando la disposición representada por el individuo.
        """
        return self.simulacion.calcular_costo_total_todos_los_pedidos(individuo)

    def evaluar_poblacion(self, poblacion: np.ndarray) -> np.ndarray:
        return np.array([self.evaluar_individuo(individuo) for individuo in poblacion], dtype=float)

    def calcular_fitness(self, puntajes: np.ndarray) -> np.ndarray:
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

    def obtener_elite(self, poblacion: np.ndarray, puntajes: np.ndarray) -> np.ndarray:
        indices_ordenados = np.argsort(puntajes)   # menor puntaje = mejor
        elite = [poblacion[i].copy() for i in indices_ordenados[:self.n_elite]]
        return np.array(elite)

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

    def mutacion_swap(self, individuo: np.ndarray, prob_mutacion: float = 0.1) -> np.ndarray:
        nuevo = individuo.copy()

        if np.random.rand() < prob_mutacion:
            i, j = np.random.choice(len(nuevo), size=2, replace=False)
            nuevo[i], nuevo[j] = nuevo[j], nuevo[i]

        return nuevo

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

    def algoritmo(
        self,
        max_generaciones: int = 100,
        prob_cruce: float = 0.5,
        prob_mutacion: float = 0.05
    ):

        poblacion = self.inicializar_poblacion()
        print("Población inicializada")
        print(f"Ejemplo de individuo inicial: {poblacion[0]}")

        historial_puntaje_min = []
        historial_puntaje_prom = []
        historial_mejor_global = []

        mejor_individuo = None
        mejor_puntaje = np.inf

        for gen in range(max_generaciones):
            puntajes = self.evaluar_poblacion(poblacion)
            fitness = self.calcular_fitness(puntajes)
            probabilidades = self.calcular_probabilidades(fitness)

            idx_mejor = np.argmin(puntajes)

            print(f"Generación {gen}: mejor = {puntajes[idx_mejor]}, promedio = {np.mean(puntajes)}")

            if puntajes[idx_mejor] < mejor_puntaje:
                mejor_puntaje = puntajes[idx_mejor]
                mejor_individuo = poblacion[idx_mejor].copy()

            historial_puntaje_min.append(float(np.min(puntajes)))
            historial_puntaje_prom.append(float(np.mean(puntajes)))
            historial_mejor_global.append(float(mejor_puntaje))

            elite = self.obtener_elite(poblacion, puntajes)

            cantidad_hijos = self.N_poblacion - self.n_elite
            cantidad_parejas = int(np.ceil(cantidad_hijos / 2))

            parejas = self.seleccionar_parejas_ruleta(
                poblacion,
                probabilidades,
                cantidad_parejas
            )

            hijos = self.generar_hijos(
                parejas,
                cantidad_hijos=cantidad_hijos,
                prob_cruce=prob_cruce,
                prob_mutacion=prob_mutacion
            )

            poblacion = np.vstack((elite, hijos))

        return {
            "poblacion_final": poblacion,
            "mejor_individuo": mejor_individuo,
            "mejor_puntaje": mejor_puntaje,
            "historial_puntaje_min": historial_puntaje_min,
            "historial_puntaje_prom": historial_puntaje_prom,
            "historial_mejor_global": historial_mejor_global
        }


if __name__ == "__main__":
    np.random.seed(42)

    ag = AlgoritmoGenetico()

    resultados = ag.algoritmo(
        max_generaciones=200,
        prob_cruce=0.8,
        prob_mutacion=0.05
    )

    print("\nMejor individuo:")
    print(resultados["mejor_individuo"])

    print("\nMejor puntaje:")
    print(resultados["mejor_puntaje"])

    plt.plot(resultados["historial_puntaje_min"], label="Mejor de la generación")
    plt.plot(resultados["historial_puntaje_prom"], label="Promedio")
    plt.plot(resultados["historial_mejor_global"], label="Mejor global")
    plt.xlabel("Generación")
    plt.ylabel("Costo total")
    plt.title("Evolución del algoritmo genético")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    layout = Layout()
    graf = Graficador(layout)
    lector = LectorFrecuenciasPedidos("TP1/utilities/ordenes.csv")
    frecuencias = lector.calcular_frecuencias()
        
    graf.graficar(resultados["mejor_individuo"], frecuencias)