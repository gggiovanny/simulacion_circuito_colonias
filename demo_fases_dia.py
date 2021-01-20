from config import traci
import config
import models_db as m
import petri_nets as pn
import traffic_generator as tg
import subprocess

def run():
    # subprocess.call(['cd', config.sumo_data_path])
    # subprocess.call(['build.bat'])
    
    old_file = tg.setTrafficFile(config.sumo_data_path+'osm.sumocfg', 'osm_pt.rou.xml,osm.passenger.trips.xml', True)
    # conectando a la base de datos
    m.connect(True)
    # obteniendo los datos de la interseccion del cache 
    intersection = m.getIntersection("circuito_colonias")
    # obteniendo las redes de petri que controlan los semaforos
    nets = [
        pn.generateDemoTlsPetriNet(intersection.associated_traffic_light_name),
        pn.generateDualPetriNet(intersection.associated_traffic_light_name),
        pn.generateDualPetriNet(intersection.associated_traffic_light_name, "Dual alt net", states_set="alt")
    ]
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
            pn.setActiveNet(0, nets)
            nets[0].nextStep(t)
        elif t < 120*2:
            pn.setActiveNet(1, nets)
            nets[1].nextStep(t)
        else:
            pn.setActiveNet(2, nets)
            nets[2].nextStep(t)
        t+=1
        wait+=1
        estado_actual = traci.trafficlight.getRedYellowGreenState(intersection.associated_traffic_light_name)
        if estado_actual != estado_anterior:
            pn.stateChangeMsg(t, wait, estado_actual, estado_anterior, pn.getActiveNetName(nets))
            wait = 0
    traci.close()
    # restaurando archivo anterior
    tg.setTrafficFile(config.sumo_data_path+'osm.sumocfg', old_file, True)

# este es el punto de entrada al script
if __name__ == "__main__":
    # ejecutando la funcion que controla a la simulacion
    run()