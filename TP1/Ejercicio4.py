import numpy as np
import matplotlib.pyplot as plt
from Ejercicio3 import TempleSimulado
from Ejercicio1 import csv_to_array

class AlgoritmoGenetico:

    def __init__(self):
        grilla = csv_to_array("TP1/utilities/casillas.csv")
        self.N_poblacion = 100
        self.long_individuo = 48
        self.generaciones = 2000

    # Inicializar población
    def inicializar_poblacion(self):
        return np.array([np.random.permutation(self.long_individuo) + 1 for _ in range(self.N_poblacion)])

        
    def evaluar_individuo(self, individuo: np.ndarray) -> float:
        simulacion = TempleSimulado(self.grilla)
        costo_total = simulacion.busquedaLocal(numero_orden=0, Temperatura0=1000, coolingRate=0.95, minTemperatura=1, orden_particular=individuo)
        return costo_total[1]  # Retorna el costo total de la simulación
    
    def evaluar_poblacion(self, poblacion: np.ndarray, plantilla: np.ndarray):
    
        puntajes = []
        for individuo in poblacion:
            puntaje = self.evaluar_individuo(individuo)
            puntajes.append(puntaje)
        
        return np.array(puntajes)
    
    def calcular_fitness(self, puntajes: np.ndarray) -> np.ndarray:
    
        total = np.sum(puntajes)
        fitness = (total - puntajes) / total
        return fitness
    
    def calcular_probabilidades(self, fitness: np.ndarray) -> np.ndarray:
        return fitness / np.sum(fitness)
    
    def seleccionar_parejas_ruleta(self,
                                poblacion: np.ndarray,
                                probabilidades: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
        
        parejas = []
        indices = np.arange(len(poblacion))

        for _ in range(self.N_poblacion // 2):
            # seleccionar primer padre
            idx1 = np.random.choice(indices, p=probabilidades)
            padre1 = poblacion[idx1]

            # quitar temporalmente ese índice
            mascara = indices != idx1
            indices_restantes = indices[mascara]
            probabilidades_restantes = probabilidades[mascara]
            probabilidades_restantes = probabilidades_restantes / np.sum(probabilidades_restantes)

            # seleccionar segundo padre
            idx2 = np.random.choice(indices_restantes, p=probabilidades_restantes)
            padre2 = poblacion[idx2]

            parejas.append((padre1, padre2))

        return parejas
        
    def cruce_ciclos(self, padre1: np.ndarray, padre2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        n = len(padre1)

        hijo1 = np.full(n, -1, dtype=int) # inicializa con -1 para identificar posiciones no asignadas
        hijo2 = np.full(n, -1, dtype=int)

        visitado = np.zeros(n, dtype=bool) # para marcar índices ya visitados en el ciclo
        ciclo = 0

        while not np.all(visitado):
            # buscar primer índice no visitado
            inicio = np.where(~visitado)[0][0]  
            idx = inicio  # índice actual en el ciclo
            indices_ciclo = []  # para almacenar los índices del ciclo actual

            # construir ciclo
            while not visitado[idx]:  # mientras no se haya visitado este índice
                indices_ciclo.append(idx)  # agregar índice al ciclo
                visitado[idx] = True

                valor = padre2[idx]  # valor correspondiente en el otro padre
                idx = np.where(padre1 == valor)[0][0] # encontrar índice del valor en el padre1 para continuar el ciclo

            # ciclos pares: hijo1 hereda de padre1, hijo2 de padre2
            # ciclos impares: al revés
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

    #Aca defino dos tipos de mutaciones para luego decidir cual usar

    def mutacion_swap(self, individuo: np.ndarray, prob_mutacion: float = 0.1) -> np.ndarray:
        nuevo = individuo.copy()

        if np.random.rand() < prob_mutacion:  # con cierta probabilidad, realizar la mutación
            i, j = np.random.choice(len(nuevo), size=2, replace=False) # seleccionar dos índices aleatorios para intercambiar
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

    def generar_hijos(self,
                        parejas: list[tuple[np.ndarray, np.ndarray]],
                        prob_cruce: float = 0.5,
                        prob_mutacion: float = 0.05) -> np.ndarray:
        
        hijos = []

        for padre1, padre2 in parejas:
            if np.random.rand() < prob_cruce: 
                hijo1, hijo2 = self.cruce_ciclos(padre1, padre2)
            else:
                hijo1, hijo2 = padre1.copy(), padre2.copy()

            hijo1 = self.mutacion_swap(hijo1, prob_mutacion)
            hijo2 = self.mutacion_swap(hijo2, prob_mutacion)

            hijos.append(hijo1)
            hijos.append(hijo2)

        return np.array(hijos)

    def algoritmo(self,
                grilla: np.ndarray,
                ordenes: np.ndarray,
                max_generaciones: int = 2000,
                prob_cruce: float = 0.5,
                prob_mutacion: float = 0.05):
        
        poblacion = self.inicializar_poblacion()

        historial_fitness_max = []
        historial_fitness_prom = []
        historial_puntaje_min = []
        historial_puntaje_prom = []

        mejor_individuo = None
        mejor_puntaje = np.inf

        for gen in range(max_generaciones):
            # Evaluar población
            puntajes = self.evaluar_poblacion(poblacion, grilla)
            fitness = self.calcular_fitness(puntajes)
            probabilidades = fitness / np.sum(fitness)

            # Guardar evolución
            historial_fitness_max.append(np.max(fitness))
            historial_fitness_prom.append(np.mean(fitness))
            historial_puntaje_min.append(np.min(puntajes))
            historial_puntaje_prom.append(np.mean(puntajes))

            # Guardar mejor individuo global
            idx_mejor = np.argmin(puntajes)
            if puntajes[idx_mejor] < mejor_puntaje:
                mejor_puntaje = puntajes[idx_mejor]
                mejor_individuo = poblacion[idx_mejor].copy()

            # Selección y reproducción
            parejas = self.seleccionar_parejas_ruleta(poblacion, probabilidades)
            poblacion = self.generar_hijos(
                parejas,
                prob_cruce=prob_cruce,
                prob_mutacion=prob_mutacion
            )

        return {
            "poblacion_final": poblacion,
            "mejor_individuo": mejor_individuo,
            "mejor_puntaje": mejor_puntaje,
            "historial_fitness_max": historial_fitness_max,
            "historial_fitness_prom": historial_fitness_prom,
            "historial_puntaje_min": historial_puntaje_min,
            "historial_puntaje_prom": historial_puntaje_prom
        }
    
if __name__ == "__main__":
    ag = AlgoritmoGenetico()

    resultados = ag.algoritmo(
        grilla=csv_to_array("TP1/utilities/casillas.csv"),
        max_generaciones=2000,
        prob_cruce=0.5,
        prob_mutacion=0.05
    )

    print("Mejor individuo:")
    print(resultados["mejor_individuo"])

    print("\nMejor puntaje:")
    print(resultados["mejor_puntaje"])

    plt.plot(resultados["historial_puntaje_min"], label="Puntaje mínimo")
    plt.plot(resultados["historial_puntaje_prom"], label="Puntaje promedio")
    plt.xlabel("Generación")
    plt.ylabel("Puntaje")
    plt.title("Evolución del puntaje")
    plt.legend()
    plt.grid(True)
    plt.show()