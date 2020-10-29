from config import traci
import config
import PetriPy

class Edge: # o calle/arista
    def __init__(self, is_traffic_input = False, associated_detector_name = "", num_lanes = 1, aprox_length = 0, aprox_total_width = 0, name = ""):
        # propiedades
        self.is_traffic_input = is_traffic_input # indica si el trafico entra por esta calle
        self.associated_detector_name = associated_detector_name # nombre del detector de trafico asociado a esta calle
        self.num_lanes = num_lanes # numero de carriles
        self.aprox_length = aprox_length # largo aproximado de la calle
        self.aprox_total_width = aprox_total_width # ancho aproximado de la calle completa que incluye a todos los carriles
        self.aprox_area = aprox_length * aprox_total_width # area calculada
        self.name = name # nombre o apodo para la calle
        # estado
    
    def __str__(self):
        return self.name

class Conection:
    def __init__(self, from_edge, to_edge, validate = False):
        # propiedades
        self.from_edge = from_edge # desde que calle viene el trafico
        self.to_edge = to_edge # hacia que calle viene el trafico
        if validate: # si se deben validar que los parametros recibidos representen una conexión válida. Por defecto es False, para evitar realizar esta operación cuando no sea necesario para ahorrar procesamiento
            self.validate()
        self.from_edge.is_traffic_input = True 
        self.to_edge.is_traffic_input = False
        # estado
    
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
    
    def __str__(self):
        return "{} -> {}".format(self.from_edge.name, self.to_edge.name)

class Intersection:
    def __init__(self, associated_traffic_light_name, edges_list=[], conections_list=[] ):
        # propiedades
        self.edges_list = edges_list # lista de todas las calles en la intersección. Útil si se quiere recorrer todas una por una
        self.conections_list = conections_list # lista de todas las conexiones entre calles
        self.associated_traffic_light_name = associated_traffic_light_name # el nombre del semáforo asociado a la interseccion
        # estado
    
    def __str__(self):
        edges_str = ', '.join(map(str, self.edges_list))
        conections_str = ', '.join(map(str, self.conections_list))
        return "[{}] controls:\n\tedges: [{}]\n\tconections: [{}]".format(self.associated_traffic_light_name, edges_str, conections_str)

# class EventObserver:
#     def __init__(self):

#     def observe(self):
def setup():
    edges = {
        "from_north": Edge(num_lanes=2, name='from_north'),
        "to_south": Edge(num_lanes=2, name='to_south'),
        "from_east": Edge(num_lanes=2, name='from_east'),
        "to_west": Edge(num_lanes=2, name='to_west'),
        "from_west": Edge(num_lanes=2, name='from_west'),
        "to_east": Edge(num_lanes=2, name='to_east'),
    }
    conections = {
        "north_to_south": Conection(edges["from_north"], edges["to_south"]),
        "east_to_west": Conection(edges["from_east"], edges["to_west"]),
        "west_to_east": Conection(edges["from_west"], edges["to_east"]),
    }
    intersection = Intersection(
        "semaforo_circuito_colonias", 
        edges_list=edges.values(), 
        conections_list=conections.values()
    )
    print(intersection)



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