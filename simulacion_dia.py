from config import traci
import config
import models_db as m
import petri_nets as pn
import traffic_generator as tg
from scipy.stats import norm
from scipy.stats import uniform
import numpy as np

def generateTraffic():
    # time section
    minute = 10
    hour = minute * 60
    day = hour * 24
    duration = day
    
    # generando trafico de north to south en las diferentes fases del dia
    u_loc_medio = 0
    u_scale_medio = 0.3
    u_loc_bajo = 0
    u_scale_bajo = 0.1
    duracion1 = (int)((hour*5.5)-0)
    print(duracion1)
    trafns_0_5 = uniform.rvs(size=duracion1, loc = u_loc_bajo, scale=u_scale_bajo)
    trafns_5_8 = norm.rvs(size=(int)((hour*8.5)-(hour*5.5)),loc=0,scale=3)
    trafns_8_12 = uniform.rvs(size=(int)((hour*12.5)-(hour*8.5)), loc = u_loc_bajo, scale=u_loc_medio)
    trafns_12_15 = norm.rvs(size=(int)((hour*15.5)-(hour*12.5)),loc=0,scale=3)
    trafns_15_18 = uniform.rvs(size=(int)((hour*18.5)-(hour*15.5)), loc = u_loc_medio, scale=u_scale_medio)
    trafns_18_21 = norm.rvs(size=(int)((hour*21.5)-(hour*18.5)),loc=0,scale=3)
    trafns_21_23 = uniform.rvs(size=(int)((hour*23)-(hour*21.5)), loc = u_loc_medio, scale=u_scale_medio)
    trafns_23_24 = uniform.rvs(size=(int)((hour*24)-(hour*23)), loc = u_loc_bajo, scale=u_scale_bajo)
    # uniendolo en un solo arreglo
    trafns_allday = np.concatenate(( trafns_0_5, trafns_5_8, trafns_8_12, trafns_12_15, trafns_15_18, trafns_18_21, trafns_21_23, trafns_23_24 ))
    # usandolo para generar tráfico
    gen1 = tg.TrafficGenerator("from_north_edge", "to_south_edge", name="test.trafns")
    gen1.generate(trafns_allday, vehicle_type="coche")
    
    
    
    # gen2 = tg.TrafficGenerator("from_east_edge", "to_west_edge", name="test.trafew")
    # gen2.generate(data_normal, vehicle_type="coche")
    # gen3 = tg.TrafficGenerator("from_west_edge", "to_east_edge", name="test.trafwe")
    # gen3.generate(data_normal, vehicle_type="coche")

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