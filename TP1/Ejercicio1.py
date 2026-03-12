"""
# Montacargas.
El algoritmo de montacargas debe ser diseñado con el paradigma de programación orientada a objetos.
Se le deben dar 2 parámetros:
@param Casilla de inicio
@param Casilla de destino

El algoritmo debe retornar una lista de casillas que representan el camino a seguir para llegar al destino.
Se debe utilizar el algoritmo de búsqueda A* para encontrar el camino más corto entre las casillas de inicio y destino,
teniendo en cuenta las restricciones del montacargas.

Se deben desarrollar las restricciones y objetivos.
"""

from unittest import case

import numpy as np

def csv_to_array(ruta: str) -> np.ndarray:
    with open(ruta, 'r') as f:
        lines = f.readlines()
    array = np.array([[int(dato) for dato in line.strip().split(',')] for line in lines])
    return array

def casilla_a_coordenadas(
    casilla:int
    ) -> tuple:
    
    pass

class Montacargas:
    def __init__(self, 
                 matriz_casillas: np.ndarray):
        self.matriz_casillas = matriz_casillas

    def encontrar_camino(self) -> np.ndarray:
        # Implementar el algoritmo A* para encontrar el camino más corto
        # Devuelve "array de casillas" que representan el camino a seguir para llegar al destino
        pass

if __name__ == "__main__":
    array = csv_to_array('TP1/casillas.csv')
    print(array)