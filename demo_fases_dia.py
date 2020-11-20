from config import traci
import config
import models_db as m
import petri_nets as nets

def run():
    # obteniendo los datos de la interseccion del cache 
    intersection = m.getIntersection("circuito_colonias")
    # obteniendo las redes de petri que controlan los semaforos
    net1 = nets.generateDualPetriNet(intersection.associated_traffic_light_name)
    
    
    # iniciando la simulacion
    traci.start(['sumo-gui', "-c", config.sumo_data_path+'osm.sumocfg'])
    
    # # obteniendo alguanas propiedades desde la simulacion
    m.populateIntersectionUsingTraci(intersection, traci)
    
    t = 0
    wait_between_changes = 0
    # Ejecuta el bucle de control de TraCI
    while traci.simulation.getMinExpectedNumber() > 0:
        estado_anterior = traci.trafficlight.getRedYellowGreenState(intersection.associated_traffic_light_name)
        # recorriendo todas las calles y generando el estado de cada una
        m.autoGenerateState(intersection, traci, t, "demo_fases_dia")
        # avanzando la simulacion
        traci.simulationStep()
        # if t < 1200:
        net1.nextStep(t)
        # elif t < 2400:
        # else:
        t+=1
        wait_between_changes+=1
        estado_actual = traci.trafficlight.getRedYellowGreenState(intersection.associated_traffic_light_name)
        if estado_actual != estado_anterior:
            print("\t[!]Estado cambiado: {}->{} [t={}, w={}] ({} duró {}s)".format(nets.getStateLabel(state=estado_anterior), nets.getStateLabel(state=estado_actual), t, wait_between_changes, nets.getStateLabel(state=estado_anterior), wait_between_changes))
            wait_between_changes = 0
    traci.close()

# este es el punto de entrada al script
if __name__ == "__main__":
    # ejecutando la funcion que controla a la simulacion
    run()