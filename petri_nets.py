import PetriPy as petri
from config import traci
from datetime import timedelta


def generateDemoTlsPetriNet(tls_name, name="Basic net"):
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
    transition[0].action = lambda: traci.trafficlight.setRedYellowGreenState(
        tls_name, getStateLabel(label="N_r-EW_g"))
    transition[1].action = lambda: traci.trafficlight.setRedYellowGreenState(
        tls_name, getStateLabel(label="N_r-EW_y"))
    transition[2].action = lambda: traci.trafficlight.setRedYellowGreenState(
        tls_name, getStateLabel(label="N_g-EW_r"))
    transition[3].action = lambda: traci.trafficlight.setRedYellowGreenState(
        tls_name, getStateLabel(label="N_y-EW_r"))
    # el estado inicial de las marcas
    initial_state = [1, 0, 0, 0]
    return petri.Network(places, transition, initial_state, name=name)


def generateDualPetriNet(tls_name, name="Dual net", states_set="default"):
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
    if states_set == "default":
        t[0].action = lambda: traci.trafficlight.setRedYellowGreenState(
            tls_name, getStateLabel(label="default yellow"))  # yellow
        t[1].action = lambda: traci.trafficlight.setRedYellowGreenState(
            tls_name, getStateLabel(label="default red"))  # red
        t[4].action = lambda: traci.trafficlight.setRedYellowGreenState(
            tls_name, getStateLabel(label="default green"))  # green
    elif states_set == "alt":
        t[0].action = lambda: traci.trafficlight.setRedYellowGreenState(
            tls_name, getStateLabel(label="alt yellow"))  # yellow
        t[1].action = lambda: traci.trafficlight.setRedYellowGreenState(
            tls_name, getStateLabel(label="alt red"))  # red
        t[4].action = lambda: traci.trafficlight.setRedYellowGreenState(
            tls_name, getStateLabel(label="alt green"))  # green
    else:
        raise Exception("Unknow state_set:{}".format(states_set))
    # el estado inicial de las marcas
    initial_state = [1, 0, 0, 0, 0]
    return petri.Network(p, t, initial_state, name=name)


def generateDinamycNet(tls_name: str,  duraciones: list, yellow_time: int = 6, name: str = "Dinamyc Net"):
    """
    Genera una red de petri de una estructura circular de tamaño fijo (para 4
    transiciones) a la que se le puede configurar el estado al que se cambia con
    cada transición y la duración del mismo.
    """
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
    transition[1].wait_time = duraciones[0] # controla la duracion del tiempo de green en las calles que vienen del este y oeste
    transition[2].wait_time = yellow_time
    transition[3].wait_time = duraciones[1] # controla la duracion del tiempo de green en las calles que vienes del norte
    transition[0].wait_time = yellow_time
    # agregando callbacks en cada transición para que ejecuten un cambio de luces
    transition[0].action = lambda: traci.trafficlight.setRedYellowGreenState(
        tls_name, getStateLabel(label="N_r-EW_g"))
    transition[1].action = lambda: traci.trafficlight.setRedYellowGreenState(
        tls_name, getStateLabel(label="N_r-EW_y"))
    transition[2].action = lambda: traci.trafficlight.setRedYellowGreenState(
        tls_name, getStateLabel(label="N_g-EW_r"))
    transition[3].action = lambda: traci.trafficlight.setRedYellowGreenState(
        tls_name, getStateLabel(label="N_y-EW_r"))
    return petri.Network(places, transition, initial_state_list=[1, 0, 0, 0], name=name)


label_colors = {
    # inicio set por defecto
    "N_r-EW_g": "GGgggGGrrrr", # nort red, east and west green
    "N_r-EW_y": "yyyyyyyrrrr", # north red, east and west yellow
    "N_g-EW_r": "rrrrrrrGGGG", # north green, east and west red
    "N_y-EW_r": "rrrrrrryyyy", # north yellow, east and west red
    # fin set por defecto
    "default green": "GGggGGGrrrr",
    "default yellow": "yyyyyyyGGGG",
    "default red": "rrrrrrryyyy",
    "alt green": "rrGGGrrGGGG",
    "alt yellow": "rryyyrryyyy",
    "alt red": "GGrrrGGrrrr",
    "Sin inicializar": ""
}

colors_that_starts_cycle = [
    'N_g-EW_r',
    'default green',
    'alt red',
]


def isStartOfCycle(state=None, label=None):
    if label == None and state != None:
        label = getStateLabel(state=state)
    if label == None:
        raise Exception('No se definió label o state.')
    return label in colors_that_starts_cycle


def getStateLabel(state="", label=""):
    if label:
        return label_colors[label]
    elif state != None:
        label_list = [label for label,
                      color_state in label_colors.items() if color_state == state]
        if label_list:
            return label_list[0]
        else:
            raise ValueError("No se encontro el state={}".format(state))


def stateChangeMsg(t, wait, estado_actual, estado_anterior, active_net_name):
    print("\t[!]Estado cambiado: {}->{} [t={}({}), w={}] ({} duró {}s, lo  efectuó {})".format(
        getStateLabel(state=estado_anterior),
        getStateLabel(state=estado_actual),
        t,
        str(timedelta(seconds=t)),
        wait,
        getStateLabel(state=estado_anterior),
        wait,
        active_net_name
    ))


def setActiveNet(net_index, nets):
    # dinamicamente recorrer nets para que funcione si es list o dict
    for i, net in nets.items() if type(nets) is dict else enumerate(nets, start=0):
        if i == net_index:
            net.active = True
        else:
            net.active = False


def getActiveNetName(nets):
    # dinamicamente recorrer nets para que funcione si es list o dict
    for net in nets.values() if type(nets) is dict else nets:
        if net.active:
            return net.name
    # si no retorno nada, no hay net activa
    return "Sin red de petri activa."
