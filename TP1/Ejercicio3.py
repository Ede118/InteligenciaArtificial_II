"""

"""

import numpy as np
import pandas as pd
import csv
import pathlib
from Ejercicio1 import Montacargas, csv_to_array

class TempleSimulado:
    
    def __init__(self, 
                 matriz_casillas: np.ndarray,
                 *,
                 ordenes: np.ndarray = None):
        self.matriz_casillas = matriz_casillas
        self.ordenes = ordenes

    def _parser(self, ruta: pathlib.Path):
        vectores = []
        with open(ruta, 'r') as f:
            lector = csv.reader(f)
            for fila in lector:
                vector = np.array([int(dato) for dato in fila])
                vectores.append(vector)
        self.ordenes = vectores
    
    def _random_swap(self, secuencia: np.ndarray) -> np.ndarray:
        idx1, idx2 = np.random.choice(len(secuencia), size=2, replace=False)
        secuencia[idx1], secuencia[idx2] = secuencia[idx2], secuencia[idx1]
        return secuencia

    def busquedaLocal(self,
                      numero_orden: int,
                      Temperatura0: float,
                      pendiente: float
                      ) -> np.ndarray:
        iteracion = 0
        orden = self.ordenes[numero_orden]
        agente = Montacargas(self.matriz_casillas)
        
        
        
        TActual = Temperatura0 - pendiente*iteracion
        
        # Implementar el algoritmo A* para encontrar el camino más corto
        pass
    
    
if __name__ == "__main__":
    matriz_casilla = csv_to_array('TP1/casillas.csv')
    temple_simulado = TempleSimulado(matriz_casilla)
    temple_simulado._parser('TP1/ordenes.csv')