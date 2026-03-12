"""
Busqueda Local con Temple Simulado para optimizar la secuencia de órdenes de un
montacargas en un almacén representado por una matriz de casillas. El objetivo 
es minimizar el costo total de las rutas del montacargas al seguir una secuencia 
de órdenes dada, utilizando el algoritmo A*.
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

    def _calcular_costo(self,
                        orden: np.ndarray,
                        agente: Montacargas
                        ) -> float:
        costo = 0
        for i in range(len(orden)-1):
            agente.iniciar = orden[i]
            agente.destino = orden[i+1]
            _, camino = agente.encontrar_camino()
            costo += camino
        return costo
    
    def busquedaLocal(self,
                      numero_orden: int,
                      Temperatura0: float,
                      coolingRate: float,
                      minTemperatura: float
                      ) -> tuple[np.ndarray, float]:
        iteracion = 0
        orden = self.ordenes[numero_orden]
        agente = Montacargas(self.matriz_casillas)
        
        costo = self._calcular_costo(orden, agente)
        TActual = Temperatura0
        
        while TActual > minTemperatura:
            new_orden = self._random_swap(orden.copy())
            new_costo = self._calcular_costo(new_orden, agente)
            if new_costo < costo:
                orden = new_orden
                costo = new_costo
            else:
                delta = new_costo - costo
                if np.exp(-delta/TActual) > np.random.rand():
                    orden = new_orden
            TActual *= coolingRate
        
        return orden, costo

if __name__ == "__main__":
    matriz_casilla = csv_to_array('TP1/casillas.csv')
    temple_simulado = TempleSimulado(matriz_casilla)
    temple_simulado._parser('TP1/ordenes.csv')