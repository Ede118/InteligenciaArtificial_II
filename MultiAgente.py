import copy
import Astar_OO as Astar


class Montacargas:

    def __init__(self, id_robot, inicio, grid, estante):

        self.id = id_robot
        self.inicio = inicio
        self.grid = grid
        self.estante = estante

        self.camino = None


    def planificar(self):

        entorno = Astar.Entorno(self.grid, self.estante)

        astar = Astar.Astar(entorno)


        self.camino = astar.execute(self.inicio)

        return self.camino


    def replanificar(self, celdas_bloqueadas):

        grid_temp = copy.deepcopy(self.grid)

        for row, col in celdas_bloqueadas:
            grid_temp[row][col] = Astar.Entorno.ESTANTE

        entorno = Astar.Entorno(grid_temp, self.estante)

        astar = Astar.Astar(entorno)


        self.camino = astar.execute(self.inicio)

        return self.camino



class Coordinador:

    def __init__(self, grid, robots):

        self.grid = grid
        self.robots = robots


    def detectar_conflicto(self, camino1, camino2):

        tiempo = min(len(camino1), len(camino2))

        for t in range(tiempo):

            if camino1[t] == camino2[t]:
                return True
            if t>0:
                 if camino1[t] == camino2[t-1] and camino1[t-1] == camino2[t]:
                  return True

        return False


    def planificar_rutas(self):

        robot_prioridad = self.robots[0]
        robot_secundario = self.robots[1]

        camino1 = robot_prioridad.planificar()

        camino2 = robot_secundario.planificar()

        if self.detectar_conflicto(camino1, camino2):

            print("Conflicto detectado → Replanificando robot 2")

            camino2 = robot_secundario.replanificar(camino1)

        return camino1, camino2