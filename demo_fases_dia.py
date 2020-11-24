from config import traci
import config
import models_db as m
import petri_nets as nets

def run():
    # obteniendo los datos de la interseccion del cache 
    intersection = m.getIntersection("circuito_colonias")
    # obteniendo las redes de petri que controlan los semaforos
    net1 = nets.generateDualPetriNet(intersection.associated_traffic_light_name)
    net2 = nets.generateDemoTlsPetriNet(intersection.associated_traffic_light_name)
    
    # iniciando la simulacion
    traci.start(['sumo-gui', "-c", config.sumo_data_path+'osm.sumocfg'])
    
    # # obteniendo alguanas propiedades desde la simulacion
    m.populateIntersectionUsingTraci(intersection, traci)
    
    t = 0
    wait = 0
    # Ejecuta el bucle de control de TraCI
    while traci.simulation.getMinExpectedNumber() > 0:
        estado_anterior = traci.trafficlight.getRedYellowGreenState(intersection.associated_traffic_light_name)
        # recorriendo todas las calles y generando el estado de cada una
        m.autoGenerateState(intersection, traci, t, "demo_fases_dia")
        # avanzando la simulacion
        traci.simulationStep()
        if t < 120:
            net1.active = True
            net2.active = False
            net1.nextStep(t)
        elif t < 120*2:
            net2.active = True
            net1.active = False
            net2.nextStep(t)
        # else:
        t+=1
        wait+=1
        estado_actual = traci.trafficlight.getRedYellowGreenState(intersection.associated_traffic_light_name)
        if estado_actual != estado_anterior:
            stateChangeMsg(t, wait, estado_actual, estado_anterior, net1.name if net1.active else net2.name)
            wait = 0
    traci.close()

def stateChangeMsg(t, wait, estado_actual, estado_anterior, active_net_name):
    print("\t[!]Estado cambiado: {}->{} [t={}, w={}] ({} duró {}s, lo  efectuó {})".format(
        nets.getStateLabel(state=estado_anterior), 
        nets.getStateLabel(state=estado_actual), 
        t, 
        wait, 
        nets.getStateLabel(state=estado_anterior), 
        wait,
        active_net_name
    ))

# este es el punto de entrada al script
if __name__ == "__main__":
    # ejecutando la funcion que controla a la simulacion
    run()