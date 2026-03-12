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

import numpy as np

class Montacargas:
    def __init__(self, 
                 matriz_casillas: np.ndarray):
        self.matriz_casillas = matriz_casillas

    def encontrar_camino(self) -> np.ndarray:
        # Implementar el algoritmo A* para encontrar el camino más corto
        pass
