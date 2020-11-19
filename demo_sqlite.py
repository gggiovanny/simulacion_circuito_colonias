from config import traci
import config
import models_db as m
import petri_nets as nets

def run():
    # obteniendo los datos de la interseccion del cache 
    intersection = m.getIntersection("circuito_colonias")
    # obteniendo la red de petri que controla los semaforos
    net = nets.generateDemoTlsPetriNet(intersection.associated_traffic_light_name)
    
    # iniciando la simulacion
    traci.start(['sumo-gui', "-c", config.sumo_data_path+'osm.sumocfg'])
    
    # # obteniendo alguanas propiedades desde la simulacion
    m.populateIntersectionUsingTraci(intersection, traci)
    
    t = 0
    # Ejecuta el bucle de control de TraCI
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        net.nextStep()
        
        # recorriendo todas las calles y generando el estado de cada una
        m.autoGenerateState(intersection, traci, t, "normal traffic static rule 25x5")
        
        t+=1
    traci.close()

# este es el punto de entrada al script
if __name__ == "__main__":
    # ejecutando la funcion que controla a la simulacion
    run()