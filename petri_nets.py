import PetriPy as p
from config import traci

def generateDemoTlsPetriNet(tls_name):
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