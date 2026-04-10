"""
Init:
    @param grilla:      [class Almacen]: matriz de almacen [0s, 1s y 2].
    @param ordenes:     [list[np.ndarray]] lista de órdenes de pedidos.

Args `busquedaLocal`:
    @param numero_orden:        [list[np.ndarray]] Array de ordenes particulares que se desea manejar
    @param Temperatura0:        [float] Temperatura inicial del Templado Simulado
    @param coolingRate:         [float] Número 0<float<1 con el que disminuye la temperatura
    @param minTemperatura:      [float] Temperatura mínima (restringe número de iteraciones)
    @param orden_particular:    [np.ndarray] Lista de ordenes particulares 
    @param seed:                [int] 
    @param max_iter:            [int]

Return:
    @param camino_optimo:       [np.ndarray] Lista de ordenes de manera "ordenada" con el costo optimo en mente
    @param costo_optimo:        [int] Costo optimo (medido en distancia manhattan)


Búsqueda Local con Temple Simulado para optimizar la secuencia de órdenes de un
montacargas en un almacén representado por una matriz de casillas.

Además, incluye utilidades para evaluar una disposición global de productos
(individuo del AG) usando TODOS los pedidos del CSV.
"""

import sys
import csv
import pathlib
import random
import os
import numpy as np
import pygame
import Ejercicio1 as E1

class TempleSimulado:
    def __init__(self, grilla, *, ordenes: list[np.ndarray] | None = None): #Permite pasar las órdenes directamente al constructor, o cargarlas con cargar_ordenes()
        self.ordenes = ordenes if ordenes is not None else []
        self.grilla = grilla

    def cargar_ordenes(self, ruta: str | pathlib.Path) -> None:
        """Convierte el csv de órdenes a una lista de arrays de numpy."""
        ruta = pathlib.Path(ruta)
        vectores = []

        with open(ruta, "r", newline="") as f:
            lector = csv.reader(f)
            for fila in lector:
                if not fila:
                    continue
                vector = np.array([int(dato) for dato in fila], dtype=int)
                vectores.append(vector)

        self.ordenes = vectores

    def _random_swap(self, secuencia: np.ndarray) -> np.ndarray:
        """
        Devuelve una nueva secuencia con dos posiciones intercambiadas.
        """
        nueva = secuencia.copy()
        idx1, idx2 = np.random.choice(len(nueva), size=2, replace=False)
        nueva[idx1], nueva[idx2] = nueva[idx2], nueva[idx1]
        return nueva

    def _calcular_costo(self, orden: list[int] | np.ndarray) -> int:
        """
        Calcula el costo total de un pedido expresado como secuencia de
        posiciones físicas (estantes), incluyendo:

        C -> e1 -> e2 -> ... -> en -> C
        """
        costo_total = 0
        posicion_carga = (5, 0)
        posicion_actual = posicion_carga

        # Ir desde C al primer estante y luego entre estantes
        for estante_id in orden:
            entorno = E1.Almacen(
                self.grilla,
                estante_objetivo=int(estante_id),
                posicion_final=None,
                flag_almacen=False,
                lista_modificada=None
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
                return 10_000

        # Volver a la estación de carga al terminar el pedido
        if posicion_actual != posicion_carga:
            entorno_regreso = E1.Almacen(
                self.grilla,
                estante_objetivo=None,
                posicion_final=posicion_carga,
                flag_almacen=False,
                lista_modificada=None
            )

            agente_regreso = E1.Montacargas(
                grilla=entorno_regreso,
                casilla_inicial=posicion_actual
            )

            try:
                camino_regreso, costo_regreso = agente_regreso.execute()
                costo_total += costo_regreso
            except ValueError:
                return 10_000

        return int(costo_total)

    def convertir_pedido_a_posiciones(
        self,
        pedido: np.ndarray,
        layout_individuo: np.ndarray
    ) -> np.ndarray:
        """
        Convierte un pedido expresado en IDs de productos a posiciones físicas,
        según la disposición dada por el individuo.

        layout_individuo[i] = producto ubicado en la posición física i+1
        """
        pos_producto = {producto: i + 1 for i, producto in enumerate(layout_individuo)}
        return np.array([pos_producto[int(producto)] for producto in pedido], dtype=int)

    def _calcular_costo_secuencia_posiciones(self, secuencia_posiciones: np.ndarray) -> int:
        return self._calcular_costo(secuencia_posiciones)

    def calcular_costo_total_todos_los_pedidos(self, layout_individuo: np.ndarray) -> float:
        """
        Evalúa una disposición global de productos (individuo del AG)
        sumando el costo de atender todos los pedidos del CSV.
        """
        if not self.ordenes:
            raise ValueError("No hay órdenes cargadas. Usa cargar_ordenes() primero.")

        costo_total = 0

        for pedido in self.ordenes:
            secuencia_posiciones = self.convertir_pedido_a_posiciones(
                pedido=pedido,
                layout_individuo=layout_individuo
            )
            costo_total += self._calcular_costo(secuencia_posiciones)

        return float(costo_total)

    def busquedaLocal(
        self,
        numero_orden: int,
        Temperatura0: float,
        coolingRate: float,
        minTemperatura: float,
        *,
        orden_particular: np.ndarray = None,
        seed: int | None = None,
        max_iter: int | None = None
    ) -> tuple[np.ndarray, float]:
        """
        Temple simulado sobre una secuencia de POSICIONES FÍSICAS.

        - Si se pasa orden_particular → se asume que ya son posiciones físicas
        - Si NO se pasa → usa orden del CSV 
        """

        if seed is not None:
            np.random.seed(seed)

        if not (0 < coolingRate < 1):
            raise ValueError("coolingRate debe estar entre 0 y 1.")

        if Temperatura0 <= 0:
            raise ValueError("Temperatura0 debe ser mayor que 0.")

        if minTemperatura <= 0:
            raise ValueError("minTemperatura debe ser mayor que 0.")

        # orden pasada directamente 
        if orden_particular is not None:
            orden = np.array(orden_particular, dtype=int).copy()

        # Si no se pasa usamos el número de orden para obtener la orden del CSV
        else:
            if not self.ordenes:
                raise ValueError("No hay órdenes cargadas.")

            if not (0 <= numero_orden < len(self.ordenes)):
                raise IndexError("numero_orden fuera de rango.")

            orden = np.array(self.ordenes[numero_orden], dtype=int).copy()

        # Inicialización
        TActual = float(Temperatura0)
        costo = self._calcular_costo(orden)

        iteracion = 0

        # Loop de temple
        while TActual > minTemperatura:

            if max_iter is not None and iteracion >= max_iter:
                break

            new_orden = self._random_swap(orden)
            new_costo = self._calcular_costo(new_orden)

            if new_costo < costo:
                orden = new_orden
                costo = new_costo
            else:
                delta = new_costo - costo
                prob_aceptacion = np.exp(-delta / TActual)

                if prob_aceptacion > np.random.rand():
                    orden = new_orden
                    costo = new_costo

            TActual *= coolingRate
            iteracion += 1

        return orden, float(costo)


class SimulacionInteractiva(E1.Simulacion):
    def __init__(self, grid):
        super().__init__(grid)
        self.tramos_acumulados = []
        self.indice_visible = 0
        self.palette = [
            (0, 255, 0, 180),
            (0, 0, 255, 180),
            (255, 165, 0, 180),
            (255, 0, 255, 180),
            (0, 255, 255, 180),
            (255, 255, 0, 180)
        ]

    def agregar_tramo(self, camino):
        if not camino:
            return
        color = self.palette[len(self.tramos_acumulados) % len(self.palette)]
        self.tramos_acumulados.append((camino, color))

    def draw_entorno(self, _):
        super().draw_entorno(None)

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
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.indice_visible < len(self.tramos_acumulados):
                            self.indice_visible += 1
                            print(f"-> Mostrando tramo {self.indice_visible}/{len(self.tramos_acumulados)}")

                    if event.key == pygame.K_r:
                        self.indice_visible = 0

                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

            self.pantalla.fill((0, 0, 0))
            self.draw_entorno(None)
            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")

    entorno_estatico = E1.csv_to_array("TP1/utilities/casillas.csv")

    temple_simulado = TempleSimulado(grilla=entorno_estatico)
    temple_simulado.cargar_ordenes("TP1/utilities/ordenes.csv")

    numero_orden = random.randint(0, len(temple_simulado.ordenes) - 1)
    numero_orden = 36
    orden_original = temple_simulado.ordenes[numero_orden]

    orden_optimo, costo = temple_simulado.busquedaLocal(
        numero_orden=numero_orden,
        Temperatura0=100,
        coolingRate=0.85,
        minTemperatura=0.001,
        seed=42,
        max_iter=None
    )

    char = input("¿Mostrar original? [y/n]:")
    if char is 'y':
        show_original = True
    else:
        show_original = False
    
    print(f"Orden N°: {numero_orden}")
    print(f"Orden original: {temple_simulado.ordenes[numero_orden]}")
    print("\n\n")
    
    print(f"Secuencia optimizada: {orden_optimo}")
    print(f"Costo: {costo}")
    print("\n\n")
    
    sim = SimulacionInteractiva(entorno_estatico) # O el nombre de tu clase de simulación
    posicion_actual = (5, 0) 


    for estante_id in orden_optimo:
        entorno_temp = E1.Almacen(entorno_estatico, estante_objetivo=estante_id)
        agente = E1.Montacargas(grilla=entorno_temp, casilla_inicial=posicion_actual)
        
        try:
            camino, _ = agente.execute()
            sim.agregar_tramo(camino)
            posicion_actual = camino[-1] # El fin de este tramo es el inicio del siguiente
        except ValueError:
            print(f"Error: Estante {estante_id} inalcanzable.")

    punto_carga = (5, 0)
    # Creamos un entorno genérico para el regreso
    entorno_retorno = E1.Almacen(entorno_estatico, estante_objetivo=1) 

    # Forzamos el objetivo a la zona de carga
    # La clase Almacen calcula casilla_objetivo en el __init__ basándose en estantes,
    # pero el Montacargas usa el atributo casilla_objetivo para su búsqueda.
    entorno_retorno.casilla_objetivo = punto_carga 

    agente_retorno = E1.Montacargas(grilla=entorno_retorno, casilla_inicial=posicion_actual)

    try:
        camino_vuelta, _ = agente_retorno.execute()
        sim.agregar_tramo(camino_vuelta)
        print("-> Trayecto de retorno al origen calculado.")
    except ValueError:
        print("Error: No se encontró camino de regreso al punto de carga.")

    sim.run()
    
    # ====================================================================================
    #   SIMULACIÓN DEL ORDEN ORIGINAL
    # ====================================================================================
    if show_original:
        sim = SimulacionInteractiva(entorno_estatico) # O el nombre de tu clase de simulación
        posicion_actual = (5, 0) 


        for estante_id in orden_original:
            entorno_temp = E1.Almacen(entorno_estatico, estante_objetivo=estante_id)
            agente = E1.Montacargas(grilla=entorno_temp, casilla_inicial=posicion_actual)
            
            try:
                camino, _ = agente.execute()
                sim.agregar_tramo(camino)
                posicion_actual = camino[-1] # El fin de este tramo es el inicio del siguiente
            except ValueError:
                print(f"Error: Estante {estante_id} inalcanzable.")

        punto_carga = (5, 0)
        # Creamos un entorno genérico para el regreso
        entorno_retorno = E1.Almacen(entorno_estatico, estante_objetivo=1) 

        # Forzamos el objetivo a la zona de carga
        # La clase Almacen calcula casilla_objetivo en el __init__ basándose en estantes,
        # pero el Montacargas usa el atributo casilla_objetivo para su búsqueda.
        entorno_retorno.casilla_objetivo = punto_carga 

        agente_retorno = E1.Montacargas(grilla=entorno_retorno, casilla_inicial=posicion_actual)

        try:
            camino_vuelta, _ = agente_retorno.execute()
            sim.agregar_tramo(camino_vuelta)
            print("-> Trayecto de retorno al origen calculado.")
        except ValueError:
            print("Error: No se encontró camino de regreso al punto de carga.")

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