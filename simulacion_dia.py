from config import traci
import config
import models_db as m
import petri_nets as pn
import traffic_generator as tg
import numpy as np

def generateTraffic():
    # generando duraciones de cada intervalo
    # cada intante de simulacion se corresponde a un segundo
    s = 0.2 # para que no dure realmente la cantidad de segundos del dia, por motivos de desarrollo
    dur = {}
    dur['0_5']   = tg.intervalToSeconds('0:00', '5:30', scale=s)
    dur['5_8']   = tg.intervalToSeconds('5:30', '8:30', scale=s)
    dur['8_12']  = tg.intervalToSeconds('8:30', '12:30', scale=s)
    dur['12_15'] = tg.intervalToSeconds('12:30', '15:30', scale=s)
    dur['15_18'] = tg.intervalToSeconds('15:30', '18:30', scale=s)
    dur['18_21'] = tg.intervalToSeconds('18:30', '21:30', scale=s)
    dur['21_23'] = tg.intervalToSeconds('21:30', '23:00', scale=s)
    dur['23_24'] = tg.intervalToSeconds('23:00', '23:59', scale=s)
    tg.printIntervals(dur)
    # generando trafico de north to south en las diferentes fases del dia
    trafns = {}
    trafns['0_5']   = tg.genUniformProbs(dur['0_5'],   'low')
    trafns['5_8']   = tg.genPeakProbs   (dur['5_8'],   'medium')
    trafns['8_12']  = tg.genUniformProbs(dur['8_12'],  'low')
    trafns['12_15'] = tg.genPeakProbs   (dur['12_15'], 'medium')
    trafns['15_18'] = tg.genUniformProbs(dur['15_18'], 'medium')
    trafns['18_21'] = tg.genPeakProbs   (dur['18_21'], 'medium')
    trafns['21_23'] = tg.genUniformProbs(dur['21_23'], 'medium')
    trafns['23_24'] = tg.genUniformProbs(dur['23_24'], 'low')
    # uniendo las probabilidades de trafico en un solo arreglo
    trafns_allday = np.concatenate(tg.dictToList(trafns))
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