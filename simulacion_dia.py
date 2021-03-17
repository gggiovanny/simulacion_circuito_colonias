from config import traci
import config
import petri_nets as pn
import traffic_generator as tg
import numpy as np
from traffic_storage import TrafficStorage

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
    gen1 = tg.TrafficGenerator('from_north_edge', ['to_south_edge', 'to_west_edge', 'to_east_edge'], name="test.traffromnorth")
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
    tg.TrafficGenerator('from_east_edge', ['to_west_edge', 'to_south_edge'], name="test.traffromeast").generate(trafew_allday, vehicle_type="coche_rojo")
    
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
    tg.TrafficGenerator('from_west_edge', ['to_east_edge', 'to_south_edge'], name="test.trafromwest").generate(trafwe_allday, vehicle_type="coche_verde")
    
    return gen1, intervals

def run(intervals, nets, ts, intersection):
    # iniciando la simulacion
    traci.start(['sumo-gui', "-c", config.sumo_data_path+'osm.sumocfg'])
    t = 0
    wait = 0
    estado_anterior = ''
    estado_actual = ''
    # Ejecuta el bucle de control de TraCI
    while traci.simulation.getMinExpectedNumber() > 0:
        estado_anterior = traci.trafficlight.getRedYellowGreenState(intersection.associated_traffic_light_name)
        # recorriendo todas las calles y generando el estado de cada una
        ts.collect(intersection,
            simulation_time=t,
            state_label=pn.getStateLabel(state=estado_actual),
            active_net_name=pn.getActiveNetName(nets)
        )
        # avanzando la simulacion
        traci.simulationStep()
        #? entre las 5:30 y las 8:30,  y entre las 18:30 y las 21:30, poner la
        #? red pensada para más volumen de tráfico.
        if intervals['5:30'] < t < intervals['8:30']:
            pn.setActiveNet("in", nets)
            nets["in"].nextStep(t)
        elif intervals['18:30'] < t < intervals['21:30']:
            pn.setActiveNet("out", nets)
            nets["out"].nextStep(t)
        #? entre las 12:30 y las 15:30, poner la  red pensada para trafico medio
        elif intervals['12:30'] < t < intervals['15:30']:
            pn.setActiveNet("inout", nets)
            nets["inout"].nextStep(t)
        #? en los otros intervalos, poner la red por defecto
        else:
            pn.setActiveNet("default", nets)
            nets["default"].nextStep(t)
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
    # creando instancia de la clase TrafficStorage para operaciones de lectura y escritura de datos
    ts = TrafficStorage(traci)
    # obteniendo los datos de la interseccion del cache 
    intersection = ts.getIntersection("circuito_colonias")
    # obteniendo las redes de petri que controlan los semaforos
    nets = {
        "out": pn.generateDemoTlsPetriNet(intersection.associated_traffic_light_name, name="Hight out traffic net"),
        "in": pn.generateDualPetriNet(intersection.associated_traffic_light_name, name="High in traffic net"),
        "inout": pn.generateDualPetriNet(intersection.associated_traffic_light_name, name="In and out traffic net", states_set="alt"),
        "default": pn.generateDualPetriNet(intersection.associated_traffic_light_name, name="Default traffic net", states_set="alt"),
    }
    # ejecutando la funcion que controla a la simulacion
    try:
        run(intervals, nets, ts, intersection)
    except traci.exceptions.FatalTraCIError:
        print('Conexión con traci cerrada por SUMO. Problemente la simulación se detuvo antes de finalizar.')
    finally:
        gen.restoreOldTrafficFilename()