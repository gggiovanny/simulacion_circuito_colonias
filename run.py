from config import traci
import config
import PetriPy

class Edge:
    def __init__(self, is_traffic_input = False, associated_detector_name = "", num_lanes = 1, aprox_length = 0, aprox_total_width = 0, from_direction = "", to_direction = ""):
        self.is_traffic_input = is_traffic_input
        self.associated_detector_name = associated_detector_name
        self.num_lanes = num_lanes
        self.aprox_length = aprox_length
        self.aprox_total_width = aprox_total_width # ancho de la calle completa que incluye a todos los carriles
        self.aprox_area = aprox_length * aprox_total_width # area calculada
        self.from_direction = from_direction # desde que direccion viene el la calle TODO: implementar enum/dict
        self.to_direction = to_direction # a que direccion va la calle TODO: implementar enum/dict

class Conection:
    def __init__(self, from_edge, to_edge, validate = False):
        self.from_edge = from_edge
        self.to_edge = to_edge
        if validate:
            self.validate()
        self.from_edge.is_traffic_input = True
        self.to_edge.is_traffic_input = False
    
    def validate(self):
        if not isinstance(self.from_edge, Edge):
            raise ValueError(self.typeErrorText("from_edge", self.from_edge))
        if not isinstance(self.to_edge, Edge):
            raise ValueError(self.typeErrorText("to_edge", self.to_edge))
        if not self.from_edge.is_traffic_input:
            raise Exception("from_edge DEBE ser entrada de trafico")
        if self.to_edge.is_traffic_input:
            raise Exception("to_edge NO DEBE ser entrada de trafico")
    
    def typeErrorText(self, kind_of_edge, received_object):
        return 'Error de tipo de datos!', "Se esperaba que {} sea de clase {}, pero se es de tipo {}".format(kind_of_edge, received_object.__class__.__name__, Edge.__name__) 

class Intersection:
    def __init__(self, associated_traffic_light_name, edges_list=[], conections_list=[], ):
        self.edges_list = edges_list
        self.conections_list = conections_list
        self.associated_traffic_light_name = associated_traffic_light_name

# class EventObserver:
#     def __init__(self):

#     def observe(self):

def run():
    t = 0
    # Ejecuta el bucle de control de TraCI
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        t+=1
        print(t)
    traci.close()

# este es el punto de entrada al script
if __name__ == "__main__":
    # este es el modo normal de usar traci. sumo es iniciado como un subproceso y entonces el script de python se conecta y ejecuta
    traci.start(['sumo-gui', "-c", config.sumo_data_path+'osm.sumocfg'])
    # ejecutando la funcion que controla a la simulacion
    run()