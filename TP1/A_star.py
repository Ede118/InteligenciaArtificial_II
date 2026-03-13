import heapq

SUELO = 0
ESTANTE = 1
CARGA = 2

entorno_estatico = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [2,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,1,1,0,0,1,1,0,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0]
]

filas = len(entorno_estatico)
cols = len(entorno_estatico[0])


# -------------------------
# heurística Manhattan
# -------------------------

def heuristica(nodo, objetivo):
    f, c = nodo
    fo, co = objetivo
    return abs(f-fo) + abs(c-co)

# -------------------------
# vecinos válidos
# -------------------------

def vecinos(nodo):
    f, c = nodo
    
    movimientos = [(-1,0),(1,0),(0,-1),(0,1)]
    
    resultado = []
    
    for df, dc in movimientos:
        
        nf = f + df
        nc = c + dc
        
        if 0 <= nf < filas and 0 <= nc < cols:
            if entorno_estatico[nf][nc] != ESTANTE:
                resultado.append((nf,nc))
    
    return resultado

# -------------------------
# algoritmo A*
# -------------------------

def a_estrella(inicio, objetivo):
     
    OPEN = []
    
    
    heapq.heappush(OPEN, (0, inicio))

    CLOSED = set()

    g = {inicio: 0}

    padres = {}

    while OPEN:

        _, nodo_actual = heapq.heappop(OPEN)

        if nodo_actual == objetivo:
            return reconstruir_camino(padres, nodo_actual)

        CLOSED.add(nodo_actual)

        for vecino in vecinos(nodo_actual):

            if vecino in CLOSED:
                continue

            nuevo_g = g[nodo_actual] + 1

            if vecino not in g or nuevo_g < g[vecino]:

                padres[vecino] = nodo_actual
                g[vecino] = nuevo_g

                f = nuevo_g + heuristica(vecino, objetivo)

                heapq.heappush(OPEN, (f, vecino))

    return None

# -------------------------
# reconstruir camino
# -------------------------

def reconstruir_camino(padres, nodo):

    camino = [nodo]

    while nodo in padres:
        nodo = padres[nodo]
        camino.append(nodo)

    camino.reverse()
    return camino




