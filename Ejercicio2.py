import draw_new_entorno as Sim
import MultiAgente as MA


if __name__ == "__main__":

    entorno_estatico = [[0,0,0,0,0,0,0,0,0,0,0,0,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [2,0,0,0,0,0,0,0,0,0,0,0,2], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,0,0,0,0,0,0,0,0,0,0,0]]

    estante1 = int(input("Estante robot 1: "))
    estante2 = int(input("Estante robot 2: "))

    robot1 = MA.Montacargas(1,(5,0),entorno_estatico,estante1)
    robot2 = MA.Montacargas(2,(5,12),entorno_estatico,estante2)

    coord = MA.Coordinador(entorno_estatico,[robot1,robot2])

    camino1, camino2 = coord.planificar_rutas()

    sim = Sim.SimulacionMulti(entorno_estatico)

    sim.set_caminos(camino1,camino2)

    sim.run()