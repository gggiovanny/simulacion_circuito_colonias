from config import traci
import config
import PetriPy as p
import models as m
from models import EdgeState

def get_cinco_colonias_intersection():
    edges = {
        "from_north": m.Edge(name='from_north'),
        "to_south": m.Edge(name='to_south'),
        "from_east": m.Edge(name='from_east'),
        "to_west": m.Edge(name='to_west'),
        "from_west": m.Edge(name='from_west'),
        "to_east": m.Edge(name='to_east'),
    }
    conections = {
        "north_to_south": m.Conection(edges["from_north"], edges["to_south"]),
        "east_to_west": m.Conection(edges["from_east"], edges["to_west"]),
        "west_to_east": m.Conection(edges["from_west"], edges["to_east"]),
    }
    return m.Intersection(
        "semaforo_circuito_colonias", 
        edges_list=list(edges.values()), 
        conections_list=list(conections.values())
    )
    
def generateTlsPetriNet(tls_name):
    # generando una lista de objetos Places() (Lugares) en una lista llamada 'places'
    places = p.generatePlaces(range(4))
    # repitiendo el mismo proceso para generar los objetos tipo Transition() en la lista 'transition'
    transition = p.generateTransitions(range(4))
    # estableciendo las relaciones entre Places y Transitions
    places[0].addNext(transition[0]) 
    transition[0].addNext(places[1])
    places[1].addNext(transition[1])
    transition[1].addNext(places[2])
    places[2].addNext(transition[2])
    transition[2].addNext(places[3])
    places[3].addNext(transition[3])
    transition[3].addNext(places[0])
    # estableciendo tiepos de espera para cada transicion
    transition[1].wait_time = 30
    transition[2].wait_time = 6
    transition[3].wait_time = 30
    transition[0].wait_time = 6
    # agregando callbacks en cada transición para que ejecuten un cambio de luces
    transition[0].action = lambda:traci.trafficlight.setRedYellowGreenState(tls_name, "GGggGGGrrrr")
    transition[1].action = lambda:traci.trafficlight.setRedYellowGreenState(tls_name, "yyyyyyyrrrr")
    transition[2].action = lambda:traci.trafficlight.setRedYellowGreenState(tls_name, "rrrrrrrGGGG")
    transition[3].action = lambda:traci.trafficlight.setRedYellowGreenState(tls_name, "rrrrrrryyyy")
    # el estado inicial de las marcas
    initial_state = [1,0,0,0]
    return p.Network(places, transition, initial_state, 6)

def run():
    # obteniendo la clase de la interseccion
    intersection = get_cinco_colonias_intersection()
    # obteniendo la red de petri que controla los semaforos
    net = generateTlsPetriNet(intersection.associated_traffic_light_name)
    
    # iniciando la simulacion
    traci.start(['sumo-gui', "-c", config.sumo_data_path+'osm.sumocfg'])
    
    # obteniendo alguanas propiedades desde la simulacion
    for edge in intersection.edges_list:
        edge.num_lanes = traci.edge.getLaneNumber(edge.name)
        edge.street_name = traci.edge.getStreetName(edge.name)
    
    t = 0
    # Ejecuta el bucle de control de TraCI
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        net.nextStep()
        # TODO: volver esto un foreach recorriendo todas las calles
        edge_state = m.generateEdgeStateWithTraci(traci, "from_north", t, "normal traffic static rule 25x5")
        
        
        
        t+=1
    traci.close()

# este es el punto de entrada al script
if __name__ == "__main__":
    # ejecutando la funcion que controla a la simulacion
    run()