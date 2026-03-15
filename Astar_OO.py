import heapq

class Entorno:

    SUELO = 0
    ESTANTE = 1
    CARGA = 2

    def __init__(self, grid, estante_objetivo):
        self.grid = grid

        

        self.ROWS = len(grid)
        self.COLS = len(grid[0]) if self.ROWS > 0 else 0


        if not 1 <= estante_objetivo <= 48 :
            print("[WARNING]El estante objetivo debe estar entre 1 y 48.")
            if estante_objetivo < 1:
                estante_objetivo = 1
            if estante_objetivo > 48:
                estante_objetivo = 48

        
        #Numero de estante
        self.estante_objetivo = estante_objetivo 
        #Posicion del estante objetivo
        self.pos_estante = None
        #Contador de estantes para encontrar la posición del estante objetivo
        self.idx_estante = 0

        #cuando 
        for i in range(self.ROWS):
            for j in range(self.COLS):
                if self.grid[i][j] == self.ESTANTE:
                    self.idx_estante += 1
                    if self.idx_estante == self.estante_objetivo:
                        self.pos_estante = (i, j)
                        break
            if self.pos_estante is not None:
                break

        self.objetivo = None

        #Entorno debe saber que si seleccionamos una estanteria, solo se puede estar 
        #del lado derecho o del lado izquierdo, dependiendo de la posicion del estante_objetivo
        #Si a la derecha es estante, entonces asignamos la casilla izquierda
        if self.grid[self.pos_estante[0]][self.pos_estante[1] + 1] == self.ESTANTE:
            self.objetivo = (self.pos_estante[0], self.pos_estante[1] - 1)
        else:
            self.objetivo = (self.pos_estante[0], self.pos_estante[1] + 1)

    def vecinos(self, nodo):
        row, col = nodo
        posibles_vecinos = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
        vecinos_validos = []

        for vecino in posibles_vecinos:
            if 0 <= vecino[0] < self.ROWS and 0 <= vecino[1] < self.COLS:
                if self.grid[vecino[0]][vecino[1]] != self.ESTANTE:
                    vecinos_validos.append(vecino)

        return vecinos_validos


    


class Astar:
    def __init__(self, entorno):
        self.entorno = entorno
        self.objetivo = entorno.objetivo

      

    def heuristica(self, nodo):
        return abs(nodo[0] - self.objetivo[0]) + abs(nodo[1] - self.objetivo[1])
    
    def reconstruir_camino(self, nodo):
        camino = [nodo]

        while nodo in self.padres:
            nodo = self.padres[nodo]
            camino.append(nodo)

        camino.reverse()
        return camino
    
    def execute(self,inicio):
        self.inicio = inicio

        
        self.OPEN = []
        heapq.heappush(self.OPEN, (0, self.inicio))

        self.CLOSED = set()

        self.g = {self.inicio: 0}

        self.padres = {}
        
        while self.OPEN:

            _, nodo_actual = heapq.heappop(self.OPEN)

            if nodo_actual in self.CLOSED:
                continue


            if nodo_actual == self.objetivo:
                return self.reconstruir_camino(nodo_actual)

            self.CLOSED.add(nodo_actual)

            for vecino in self.entorno.vecinos(nodo_actual):

                if vecino in self.CLOSED:
                    continue

                nuevo_g = self.g[nodo_actual] + 1

                if vecino not in self.g or nuevo_g < self.g[vecino]:

                    self.padres[vecino] = nodo_actual
                    self.g[vecino] = nuevo_g

                    f = nuevo_g + self.heuristica(vecino)

                    heapq.heappush(self.OPEN, (f, vecino))

        return None