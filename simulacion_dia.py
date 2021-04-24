from config import traci
import config
import petri_nets as pn
import traffic_generator as tg
import numpy as np
from traffic_storage import TrafficStorage
from traffic_balancer import TrafficBalancer 

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

def run(ts: TrafficStorage, tb: TrafficBalancer, tls_name: str):
    # iniciando la simulacion
    traci.start(['sumo-gui', "-c", config.sumo_data_path+'osm.sumocfg'])
    t = 0
    wait = 0
    estado_anterior = ''
    estado_actual = ''
    activenet = pn.generateDinamycNet(tls_name, [15, 25])
    def onSaveCallback(data):
        nonlocal activenet # declarando que esta variable se va a usar del scope de afuera de esta funcion interna (es un closure)
        result = tb.balance(data)
        # cambiando los tiempos de la red activa dinamicamente
        time_we = result['from_west']['time'] + result['from_east']['time'] # [0] controla la duracion del tiempo de green en las calles que vienen del este y oeste
        time_n = result['from_north']['time'] # [1] controla la duracion del tiempo de green en las calles que vienes del norte
        time_we = int(round(time_we)) # redondeando, porque los tiempos deben ser enteros, si no la red de Petri se buguea 
        time_n = int(round(time_n)) # redondeando, porque los tiempos deben ser enteros, si no la red de Petri se buguea
        activenet = pn.generateDinamycNet(tls_name, [time_we, time_n])
    ts.onSave = onSaveCallback
    # Ejecuta el bucle de control de TraCI
    while traci.simulation.getMinExpectedNumber() > 0:
        estado_anterior = traci.trafficlight.getRedYellowGreenState(tls_name)
        # recorriendo todas las calles y generando el estado de cada una
        ts.collect(
            simulation_time=t,
            state_label=pn.getStateLabel(state=estado_actual),
            active_net_name=activenet.name
        )
        # avanzando la simulacion
        traci.simulationStep()
        activenet.nextStep(t)
        t+=1
        wait+=1
        estado_actual = traci.trafficlight.getRedYellowGreenState(tls_name)
        if estado_actual != estado_anterior:
            # guardar en la bd en cada inicio de ciclo del semaforo, de tal manera que los datos sean por ciclo
            if pn.isStartOfCycle(state=estado_actual):
                ts.save(t)
            pn.stateChangeMsg(t, wait, estado_actual, estado_anterior, activenet.name)
            wait = 0
    traci.close()

# este es el punto de entrada al script
if __name__ == "__main__":
    # generando el tráfico para la simulación
    gen, intervals = generateTrafficSimDay(scale=0.1)
    # instanciando balanceador de trafico
    tb = TrafficBalancer(per_edge_base_wait = 30, numedges=3, min_wait=5)
    # creando instancia de la clase TrafficStorage para operaciones de lectura y escritura de datos
    ts = TrafficStorage(traci, 'circuito_colonias')
    tls_name = ts.intersection.associated_traffic_light_name
    # ejecutando la funcion que controla a la simulacion
    try:
        run(ts, tb, tls_name)
    except traci.exceptions.FatalTraCIError:
        print('Conexión con traci cerrada por SUMO. Problemente la simulación se detuvo antes de finalizar.')
    finally:
        gen.restoreOldTrafficFilename()