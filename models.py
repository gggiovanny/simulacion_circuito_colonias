class Edge: # o calle/arista
    def __init__(self, is_traffic_input = False, associated_detector_name = "", num_lanes = 1, lane_names_list = [], aprox_length = 0, aprox_total_width = 0, max_speed = 0, name = "", ):
        # propiedades
        self.is_traffic_input = is_traffic_input # indica si el trafico entra por esta calle
        self.associated_detector_name = associated_detector_name # nombre del detector de trafico asociado a esta calle
        self.num_lanes = num_lanes # numero de carriles
        self.lane_names_list = lane_names_list # nombres de los carriles para obtener datos extra de ellos, como lenght y width
        self.name = name # nombre o apodo para la calle
        # propiedades obtenidas de la simulacion
        self.setSize(aprox_length, aprox_total_width)
        self.max_speed = max_speed
        # estado
    
    def setSize(self, aprox_length, aprox_total_width):
        self.aprox_length = aprox_length # largo aproximado de la calle
        self.aprox_total_width = aprox_total_width # ancho aproximado de la calle completa que incluye a todos los carriles
        self.aprox_area = aprox_length * aprox_total_width # area calculada
    
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

class EdgeState:
    def __init__(self, name, timestamp, vehicle_number = 0, mean_speed = 0, vehicle_ids = 0, waiting_time = 0, occupancy = 0):
        self.name = name
        self.timestamp = timestamp
        self.vehicle_number = vehicle_number # The number of vehicles on this lane within the last time step.
        self.mean_speed = mean_speed # the mean speed of vehicles that were on this lane within the last simulation step [m/s]
        self.vehicle_ids = vehicle_ids #list of ids of vehicles that were on the named edge in the last simulation step
        self.waiting_time = waiting_time #  the sum of the waiting times for all vehicles on the edge
        self.occupancy = occupancy # the percentage of time the edge was occupied by a vehicle (%)
