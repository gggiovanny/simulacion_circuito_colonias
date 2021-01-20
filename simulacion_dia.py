from config import traci
import config
import models_db as m
import petri_nets as pn
import traffic_generator as tg
from scipy.stats import norm

def generateTraffic():
    # time section
    minute = 20
    day = minute * 60 * 24
    duration = day
    data_normal = norm.rvs(size=duration,loc=0,scale=0.2)
    gen1 = tg.TrafficGenerator("from_north_edge", "to_south_edge", name="test.trafns")
    gen1.generate(data_normal, vehicle_type="coche")
    gen2 = tg.TrafficGenerator("from_east_edge", "to_west_edge", name="test.trafew")
    gen2.generate(data_normal, vehicle_type="coche")
    gen3 = tg.TrafficGenerator("from_west_edge", "to_east_edge", name="test.trafwe")
    gen3.generate(data_normal, vehicle_type="coche")

def run():
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

# este es el punto de entrada al script
if __name__ == "__main__":
    generateTraffic()
    # ejecutando la funcion que controla a la simulacion
    run()