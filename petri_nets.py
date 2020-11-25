import PetriPy as petri
from config import traci

def generateDemoTlsPetriNet(tls_name):
    # generando una lista de objetos Places() (Lugares) en una lista llamada 'places'
    places = petri.generatePlaces(range(4))
    # repitiendo el mismo proceso para generar los objetos tipo Transition() en la lista 'transition'
    transition = petri.generateTransitions(range(4))
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
    transition[0].action = lambda:traci.trafficlight.setRedYellowGreenState(tls_name, getStateLabel(label="demo state 1"))
    transition[1].action = lambda:traci.trafficlight.setRedYellowGreenState(tls_name, getStateLabel(label="demo state 2"))
    transition[2].action = lambda:traci.trafficlight.setRedYellowGreenState(tls_name, getStateLabel(label="demo state 3"))
    transition[3].action = lambda:traci.trafficlight.setRedYellowGreenState(tls_name, getStateLabel(label="demo state 4"))
    # el estado inicial de las marcas
    initial_state = [1,0,0,0]
    return petri.Network(places, transition, initial_state, name="Basic net")

def generateDualPetriNet(tls_name):
    NET_LENGTH = 5
    # generando una lista de objetos Places() (Lugares) en una lista llamada 'places'
    p = petri.generatePlaces(range(NET_LENGTH))
    # repitiendo el mismo proceso para generar los objetos tipo Transition() en la lista 'transition'
    t = petri.generateTransitions(range(NET_LENGTH))
    # estableciendo las relaciones entre Places y Transitions
    p[0].addNext(t[0]) 
    t[0].addNext(p[1])
    p[1].addNext(t[1])
    t[1].addNext(p[2])
    p[2].addNext(t[3])
    t[3].addNext(p[4])
    t[1].addNext(p[3])
    p[3].addNext(t[2])
    t[2].addNext(p[4])
    p[4].addNext(t[4])
    t[4].addNext(p[0])
    # estableciendo tiepos de espera para cada transicion
    t[0].wait_time = 35
    t[1].wait_time = 6
    t[2].wait_time = 15
    t[3].wait_time = 25
    t[4].wait_time = 3
    # agregando marks extra
    p[4].required_marks = 2
    # agregando callbacks en cada transición para que ejecuten un cambio de luces
    t[0].action = lambda:traci.trafficlight.setRedYellowGreenState(tls_name, getStateLabel(label="default yellow")) # yellow
    t[1].action = lambda:traci.trafficlight.setRedYellowGreenState(tls_name, getStateLabel(label="default red")) # red
    t[4].action = lambda:traci.trafficlight.setRedYellowGreenState(tls_name, getStateLabel(label="default green")) # green
    # el estado inicial de las marcas
    initial_state = [1,0,0,0,0]
    return petri.Network(p, t, initial_state, name="Dual net")

label_colors = {
    "demo state 1": "GGggGGGrrrr",
    "demo state 2": "yyyyyyyrrrr",
    "demo state 3": "rrrrrrrGGGG",
    "demo state 4": "rrrrrrryyyy",
    "default green": "GGggGGGrrrr",
    "default yellow": "yyyyyyyGGGG",
    "default red": "rrrrrrryyyy",
    "alt green": "rrGGGrrGGGG",
    "alt yellow": "rryyyrryyyy",
    "alt red": "GGrrrGGrrrr"
}


def getStateLabel(state="", label=""):
    if label:
        return label_colors[label]
    elif state:
        label_list = [label for label,color_state in label_colors.items() if color_state == state]
        if label_list:
            return label_list[0] 
        else:
            raise ValueError("No se encontro el state={}".format(state)) 
        