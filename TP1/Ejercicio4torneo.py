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
        self.n_elite = 8 

        self.simulacion = TempleSimulado(self.grilla)
        self.simulacion.cargar_ordenes("TP1/utilities/ordenes.csv")

    def inicializar_poblacion(self) -> np.ndarray:
        return np.array([
            np.random.permutation(self.long_individuo) + 1
            for _ in range(self.N_poblacion)
        ])

    def evaluar_poblacion(self, poblacion: np.ndarray) -> np.ndarray:
        return np.array([self.simulacion.calcular_costo_total_todos_los_pedidos(ind) for ind in poblacion], dtype=float)

    def seleccionar_torneo(self, poblacion: np.ndarray, puntajes: np.ndarray, k: int = 4):
        parejas = []
        cantidad_hijos = self.N_poblacion - self.n_elite
        n_parejas = int(np.ceil(cantidad_hijos / 2))
        
        for _ in range(n_parejas):
            padres = []
            for _ in range(2):
                indices_aspirantes = np.random.choice(len(poblacion), k, replace=False)
                ganador_idx = indices_aspirantes[np.argmin(puntajes[indices_aspirantes])]
                padres.append(poblacion[ganador_idx].copy())
            parejas.append(tuple(padres))
        return parejas

    def cruce_ciclos(self, padre1, padre2):
        n = len(padre1)
        h1, h2 = np.full(n, -1, dtype=int), np.full(n, -1, dtype=int)
        visitado = np.zeros(n, dtype=bool)
        pos_p1 = {val: i for i, val in enumerate(padre1)}

        ciclo = 0
        while not np.all(visitado):
            inicio = np.where(~visitado)[0][0]
            idx = inicio
            indices_ciclo = []
            while not visitado[idx]:
                indices_ciclo.append(idx)
                visitado[idx] = True
                idx = pos_p1[padre2[idx]]

            if ciclo % 2 == 0:
                h1[indices_ciclo], h2[indices_ciclo] = padre1[indices_ciclo], padre2[indices_ciclo]
            else:
                h1[indices_ciclo], h2[indices_ciclo] = padre2[indices_ciclo], padre1[indices_ciclo]
            ciclo += 1
        return h1, h2

    def mutacion_scramble(self, individuo: np.ndarray, prob: float) -> np.ndarray:
        nuevo = individuo.copy()
        if np.random.rand() < prob:
            idx1, idx2 = sorted(np.random.choice(len(nuevo), size=2, replace=False))
            segmento = nuevo[idx1:idx2]
            np.random.shuffle(segmento)
            nuevo[idx1:idx2] = segmento
        return nuevo

    def algoritmo(self, max_generaciones=200, prob_cruce=0.8, prob_mut=0.1):
        poblacion = self.inicializar_poblacion()
        mejor_global_ind = None
        mejor_global_score = np.inf
        
        historial_min = []
        historial_avg = []
        historial_best = []

        for gen in range(max_generaciones):
            puntajes = self.evaluar_poblacion(poblacion)
            
            idx_mejor_gen = np.argmin(puntajes)
            if puntajes[idx_mejor_gen] < mejor_global_score:
                mejor_global_score = puntajes[idx_mejor_gen]
                mejor_global_ind = poblacion[idx_mejor_gen].copy()

            historial_min.append(float(puntajes[idx_mejor_gen]))
            historial_avg.append(float(np.mean(puntajes)))
            historial_best.append(float(mejor_global_score))

            print(f"Gen {gen} | Mejor Gen: {puntajes[idx_mejor_gen]} | Mejor Global: {mejor_global_score}")

            # 1. Elitismo
            indices_ordenados = np.argsort(puntajes)
            elite = poblacion[indices_ordenados[:self.n_elite]]

            # 2. Selección
            parejas = self.seleccionar_torneo(poblacion, puntajes)

            # 3. Reproducción
            hijos = []
            for p1, p2 in parejas:
                if np.random.rand() < prob_cruce:
                    h1, h2 = self.cruce_ciclos(p1, p2)
                else:
                    h1, h2 = p1.copy(), p2.copy()
                
                hijos.append(self.mutacion_scramble(h1, prob_mut))
                hijos.append(self.mutacion_scramble(h2, prob_mut))

            hijos = hijos[:(self.N_poblacion - self.n_elite)]
            poblacion = np.vstack((elite, np.array(hijos)))

        return {
            "mejor_individuo": mejor_global_ind,
            "mejor_puntaje": mejor_global_score,
            "historial_puntaje_min": historial_min,
            "historial_puntaje_prom": historial_avg,
            "historial_mejor_global": historial_best
        }

if __name__ == "__main__":
    np.random.seed(42)
    ag = AlgoritmoGenetico()

    resultados = ag.algoritmo(max_generaciones=200)

    print("\n--- RESULTADOS FINALES ---")
    print(f"Mejor Puntaje: {resultados['mejor_puntaje']}")
    print(f"Mejor Individuo: {resultados['mejor_individuo']}")

    plt.figure(figsize=(10, 6))
    plt.plot(resultados["historial_puntaje_min"], label="Mejor de la generación")
    plt.plot(resultados["historial_puntaje_prom"], label="Promedio")
    plt.plot(resultados["historial_mejor_global"], label="Mejor global", linestyle='--')
    plt.xlabel("Generación")
    plt.ylabel("Costo total")
    plt.title("Evolución con Torneo y Scramble Mutation")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    try:
        layout = Layout()
        graf = Graficador(layout)
        lector = LectorFrecuenciasPedidos("TP1/utilities/ordenes.csv")
        frecuencias = lector.calcular_frecuencias()
        graf.graficar(resultados["mejor_individuo"], frecuencias)
    except Exception as e:
        print(f"No se pudo graficar el resultado final: {e}")