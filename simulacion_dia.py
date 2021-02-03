from config import traci
import config
import models_db as m
import petri_nets as pn
import traffic_generator as tg
import numpy as np

def generateTrafficSimDay(scale=1):
    """
    Description of generateTrafficSimDay

    Args:
        scale=1 (undefined): Si es igual a 1, cada instante de simulacion se
        corresponde a un segundo. Si se quiere que se generen intervalos mas
        cortos, mandar valores entre 0 y 1.
        
    Returns: TrafficGenerator
    """
    # probabilidades de trafico de north to south en las diferentes fases del dia
    trafns_allday, intervals = tg.genTrafficProbs([
            { 'start': '0:00',  'end': '5:30',  'gentype': 'uniform', 'intensity': 'low' },
            { 'start': '5:30',  'end': '8:30',  'gentype': 'peak', 'intensity': 'medium' },
            { 'start': '8:30',  'end': '12:30', 'gentype': 'uniform', 'intensity': 'low' },
            { 'start': '12:30', 'end': '15:30', 'gentype': 'peak', 'intensity': 'low' },
            { 'start': '15:30', 'end': '18:30', 'gentype': 'uniform', 'intensity': 'low' },
            { 'start': '18:30', 'end': '21:30', 'gentype': 'uniform', 'intensity': 'medium' },
            { 'start': '21:30', 'end': '23:00', 'gentype': 'uniform', 'intensity': 'medium' },
            { 'start': '23:00', 'end': '23:59', 'gentype': 'uniform', 'intensity': 'low' },
        ], scale=scale, getcumulativeintervals=True
    )
    # usandolo para generar tráfico
    gen1 = tg.TrafficGenerator("from_north_edge", "to_south_edge", name="test.trafns")
    gen1.generate(trafns_allday, vehicle_type="coche_azul")
    
    # trafico de east to west en las diferentes fases del dia
    trafew_allday = tg.genTrafficProbs([
            { 'start': '0:00',  'end': '5:30',  'gentype': 'uniform', 'intensity': 'low' },
            { 'start': '5:30',  'end': '8:30',  'gentype': 'uniform', 'intensity': 'medium' },
            { 'start': '8:30',  'end': '12:30', 'gentype': 'uniform', 'intensity': 'low' },
            { 'start': '12:30', 'end': '15:30', 'gentype': 'peak', 'intensity': 'low' },
            { 'start': '15:30', 'end': '18:30', 'gentype': 'uniform', 'intensity': 'low' },
            { 'start': '18:30', 'end': '21:30', 'gentype': 'peak', 'intensity': 'medium' },
            { 'start': '21:30', 'end': '23:00', 'gentype': 'uniform', 'intensity': 'medium' },
            { 'start': '23:00', 'end': '23:59', 'gentype': 'uniform', 'intensity': 'low' },
        ], scale=scale
    )
    tg.TrafficGenerator("from_east_edge", "to_west_edge", name="test.trafew").generate(trafew_allday, vehicle_type="coche_rojo")
    
    # trafico de east to west en las diferentes fases del dia
    trafwe_allday = tg.genTrafficProbs([
            { 'start': '0:00',  'end': '5:30',  'gentype': 'uniform', 'intensity': 'low' },
            { 'start': '5:30',  'end': '8:30',  'gentype': 'peak', 'intensity': 'medium' },
            { 'start': '8:30',  'end': '12:30', 'gentype': 'uniform', 'intensity': 'low' },
            { 'start': '12:30', 'end': '15:30', 'gentype': 'peak', 'intensity': 'low' },
            { 'start': '15:30', 'end': '18:30', 'gentype': 'uniform', 'intensity': 'low' },
            { 'start': '18:30', 'end': '21:30', 'gentype': 'uniform', 'intensity': 'medium' },
            { 'start': '21:30', 'end': '23:00', 'gentype': 'uniform', 'intensity': 'medium' },
            { 'start': '23:00', 'end': '23:59', 'gentype': 'uniform', 'intensity': 'low' },
        ], scale=scale
    )
    tg.TrafficGenerator("from_west_edge", "to_east_edge", name="test.trafwe").generate(trafwe_allday, vehicle_type="coche_verde")
    
    return gen1, intervals

def run(intervals):
    # iniciando la simulacion
    traci.start(['sumo-gui', "-c", config.sumo_data_path+'osm.sumocfg'])
    t = 0
    wait = 0
    # Ejecuta el bucle de control de TraCI
    while traci.simulation.getMinExpectedNumber() > 0:
        estado_anterior = traci.trafficlight.getRedYellowGreenState(intersection.associated_traffic_light_name)
        # recorriendo todas las calles y generando el estado de cada una
        m.autoGenerateState(intersection, traci, t, "demo_fases_dia")
        # avanzando la simulacion
        traci.simulationStep()
        #? entre las 5:30 y las 8:30,  y entre las 18:30 y las 21:30, poner la
        #? red pensada para más volumen de tráfico.
        if intervals['5:30'] < t < intervals['8:30']:
            pn.setActiveNet(2, nets)
            nets[2].nextStep(t)
        elif intervals['18:30'] < t < intervals['21:30']:
            pn.setActiveNet(2, nets)
            nets[2].nextStep(t)
        #? entre las 12:30 y las 15:30, poner la  red pensada para trafico medio
        elif intervals['12:30'] < t < intervals['15:30']:
            pn.setActiveNet(1, nets)
            nets[1].nextStep(t)
        #? en los otros intervalos, poner la red por defecto
        else:
            pn.setActiveNet(0, nets)
            nets[0].nextStep(t)
        t+=1
        wait+=1
        estado_actual = traci.trafficlight.getRedYellowGreenState(intersection.associated_traffic_light_name)
        if estado_actual != estado_anterior:
            pn.stateChangeMsg(t, wait, estado_actual, estado_anterior, pn.getActiveNetName(nets))
            wait = 0
    traci.close()

# este es el punto de entrada al script
if __name__ == "__main__":
    # generando el tráfico para la simulación
    gen, intervals = generateTrafficSimDay(scale=0.1)
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
    # ejecutando la funcion que controla a la simulacion
    try:
        run(intervals)
    except:
        print('La simulación se detuvo antes de finalizar.')
    finally:
        gen.restoreOldTrafficFilename()