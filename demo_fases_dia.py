from config import traci
import config
import models_db as m
import petri_nets as pn

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
            setActiveNet(0, nets)
            nets[0].nextStep(t)
        elif t < 120*2:
            setActiveNet(1, nets)
            nets[1].nextStep(t)
        else:
            setActiveNet(2, nets)
            nets[2].nextStep(t)
        t+=1
        wait+=1
        estado_actual = traci.trafficlight.getRedYellowGreenState(intersection.associated_traffic_light_name)
        if estado_actual != estado_anterior:
            stateChangeMsg(t, wait, estado_actual, estado_anterior, getActiveNetName(nets))
            wait = 0
    traci.close()

def stateChangeMsg(t, wait, estado_actual, estado_anterior, active_net_name):
    print("\t[!]Estado cambiado: {}->{} [t={}, w={}] ({} duró {}s, lo  efectuó {})".format(
        pn.getStateLabel(state=estado_anterior), 
        pn.getStateLabel(state=estado_actual), 
        t, 
        wait, 
        pn.getStateLabel(state=estado_anterior), 
        wait,
        active_net_name
    ))
    
def setActiveNet(net_index, nets):
    for i, net in enumerate(nets, start=0):
        if i==net_index:
            net.active = True
        else:
            net.active = False

def getActiveNetName(nets):
    for net in nets:
        if net.active:
            return net.name
    # si no retorno nada, no hay net activa
    return "Warning: Sin red activa."

# este es el punto de entrada al script
if __name__ == "__main__":
    # ejecutando la funcion que controla a la simulacion
    run()