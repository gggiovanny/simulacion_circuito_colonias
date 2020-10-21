from config import traci
import config
import PetriPy

def run():
    t = 0
    # Ejecuta el bucle de control de TraCI
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        t+=1
        print(t)
    traci.close()

# este es el punto de entrada al script
if __name__ == "__main__":
    # este es el modo normal de usar traci. sumo es iniciado como un subproceso y entonces el script de python se conecta y ejecuta
    traci.start(['sumo-gui', "-c", config.sumo_data_path+'osm.sumocfg'])
    # ejecutando la funcion que controla a la simulacion
    run()