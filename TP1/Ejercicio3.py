"""
Busqueda Local con Temple Simulado para optimizar la secuencia de órdenes de un
montacargas en un almacén representado por una matriz de casillas. El objetivo 
es minimizar el costo total de las rutas del montacargas al seguir una secuencia 
de órdenes dada, utilizando el algoritmo A*.
"""

import sys
import numpy as np
import pandas as pd
import csv
import pathlib
import random
import os
import pygame
import Ejercicio1 as E1

class TempleSimulado:
    
    def __init__(self, 
                 grilla,
                 *,
                 ordenes: np.ndarray = None):
        self.ordenes = ordenes
        self.grilla = grilla

    def _parser(self, ruta: pathlib.Path):
        "Convierte el csv de ordenes a un array de numpy"
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

    def _calcular_costo(
        self, 
        orden: list[int]
        ) -> int:
        
        costo_total = 0
        posicion_actual = (5, 0) 

        for estante_id in orden:
            
            entorno = E1.Almacen(
                self.grilla, 
                estante_objetivo=estante_id,
                flag_almacen=False,
                lista_modificada0=None
            )
            
            agente = E1.Montacargas(
                grilla=entorno,
                casilla_inicial=posicion_actual
            )
            
            try:
                camino, costo_tramo = agente.execute()
                costo_total += costo_tramo
                posicion_actual = camino[-1]
            except ValueError:
                return 100 # Penalización alta si el camino es imposible
                
        return costo_total
    
    def busquedaLocal(self,
                      numero_orden: int,
                      Temperatura0: float,
                      coolingRate: float,
                      minTemperatura: float,
                      *,
                      orden_particular: np.ndarray = None
                      ) -> tuple[np.ndarray, float]:
        iteracion = 0
        TActual = Temperatura0
        costo = 100
        
        if orden_particular is not None:
            orden = orden_particular
            costo = self._calcular_costo(orden)
        else:
            orden = self.ordenes[numero_orden]
            costo = self._calcular_costo(orden)
        
        while TActual > minTemperatura:
            new_orden = self._random_swap(orden.copy())
            new_costo = self._calcular_costo(new_orden)
            if new_costo < costo:
                orden = new_orden
                costo = new_costo
            else:
                delta = new_costo - costo
                if np.exp(-delta/TActual) > np.random.rand():
                    orden = new_orden
                    costo = new_costo
            TActual *= coolingRate
        
        return orden, costo

class SimulacionInteractiva(E1.Simulacion):
    def __init__(self, grid):
        super().__init__(grid)
        self.tramos_acumulados = [] # Lista de (camino, color)
        self.indice_visible = 0      # Cuántos tramos mostramos actualmente
        self.palette = [
            (0, 255, 0, 180), (0, 0, 255, 180), (255, 165, 0, 180),
            (255, 0, 255, 180), (0, 255, 255, 180), (255, 255, 0, 180)
        ]

    def agregar_tramo(self, camino):
        if not camino: return
        color = self.palette[len(self.tramos_acumulados) % len(self.palette)]
        self.tramos_acumulados.append((camino, color))

    def draw_entorno(self, _):
        # Dibujamos el mapa base
        super().draw_entorno(None) 
        
        # Dibujamos solo hasta el índice visible actual
        for i in range(min(self.indice_visible, len(self.tramos_acumulados))):
            camino, color = self.tramos_acumulados[i]
            overlay = pygame.Surface((self.TAM_CELL, self.TAM_CELL), pygame.SRCALPHA)
            overlay.fill(color)
            for row, col in camino:
                self.pantalla.blit(overlay, (col * self.TAM_CELL, row * self.TAM_CELL))

    def run(self):
        print("\n[CONTROL] Presiona ESPACIO para mostrar el siguiente tramo.")
        print("[CONTROL] Presiona R para reiniciar o ESC para salir.")
        
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.indice_visible < len(self.tramos_acumulados):
                            self.indice_visible += 1
                            print(f"-> Mostrando tramo {self.indice_visible}/{len(self.tramos_acumulados)}")
                    
                    if event.key == pygame.K_r: # Reset por si quieres volver a ver la secuencia
                        self.indice_visible = 0
                    
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); return

            self.pantalla.fill((0, 0, 0))
            self.draw_entorno(None)
            pygame.display.flip()
            clock.tick(60)



if __name__ == "__main__":
    os.system('clear')
    entorno_estatico = E1.csv_to_array("TP1/utilities/casillas.csv")
    temple_simulado = TempleSimulado(grilla=entorno_estatico)
    temple_simulado._parser('TP1/utilities/ordenes.csv')

    # Obtener la secuencia optimizada (ejemplo para la primera orden)
    orden_optimo, costo = temple_simulado.busquedaLocal(
        numero_orden=random.randint(0,49), 
        Temperatura0=100,
        coolingRate=0.85,
        minTemperatura=0.001
    )
    print(f"Secuencia Optimizada: {orden_optimo} | Costo: {costo}")

    sim = SimulacionInteractiva(entorno_estatico)
    posicion_actual = (5, 0)
    
    # Pre-calculamos todos los tramos del camino óptimo
    for estante_id in orden_optimo:
        entorno_temp = E1.Almacen(
            entorno_estatico, 
            estante_objetivo=estante_id,
            flag_almacen=False,
            lista_modificada0=None
        )
        agente = E1.Montacargas(grilla=entorno_temp, casilla_inicial=posicion_actual)
        try:
            camino, _ = agente.execute()
            sim.agregar_tramo(camino)
            posicion_actual = camino[-1] 
        except ValueError:
            pass

    # Iniciamos el bucle interactivo
    sim.run()
    
#       Pruebas de código:
#
#    
#     temple_simulado = TempleSimulado(
#         grilla=entorno_estatico,
#         ordenes=[[1, 7, 19, 13], [25, 31, 37]]
#     )

#     # Si esta hecho correctamente, debería encontrar las soluciones
#     # particulares como [1, 7, 13, 19] y [25, 31, 37]
#     # Luego, probar con las ordenes del profesor

    # for i in range(20):
    #     orden_optimo, costo_optimo = temple_simulado.busquedaLocal(
    #         numero_orden=0,
    #         Temperatura0=100,
    #         coolingRate=0.85,
    #         minTemperatura=0.001
    #     )
    #     print("\n===================================\n")
    #     print(orden_optimo)
    #     print(costo_optimo)
    #     print("\n===================================\n")
    
#     # costo_de_todas_las_ordenes = 0
    
#     # for i in range(len(temple_simulado.ordenes)):
#     #     orden_optimo, costo_optimo = temple_simulado.busquedaLocal(
#     #         numero_orden=i,
#     #         Temperatura0=100,
#     #         coolingRate=0.85,
#     #         minTemperatura=0.001
#     #     )
        
#     #     costo_de_todas_las_ordenes += costo_optimo
        
#     #     print("\n════════════════════════════════════════════\n")
#     #     print(orden_optimo)
#     #     print(costo_optimo)
#     #     print("\n════════════════════════════════════════════\n")
    
#     # print(costo_de_todas_las_ordenes)