import draw_entorno as Draw


if __name__ == "__main__":
    entorno_estatico = [[0,0,0,0,0,0,0,0,0,0,0,0,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [2,0,0,0,0,0,0,0,0,0,0,0,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,1,1,0,0,1,1,0,0,1,1,0], 
                        [0,0,0,0,0,0,0,0,0,0,0,0,0]]
    
    estante = int(input("Ingrese el número del estante objetivo (1-48): "))

    simulacion = Draw.Simulacion(entorno_estatico)
    simulacion.calcular_camino(estante)
    simulacion.run()

