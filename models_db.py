from pony.orm import *
from traci import connection
# creando el objeto de la base de datos
db = Database()

# definiendo modelos de objetos ...

class Edge(db.Entity): # o calle/arista
    # propiedades
    conection_uses_from = Optional(lambda:Conection, reverse='from_edge') # relaciona el Edge con una Conection
    conection_uses_to = Optional(lambda:Conection, reverse='to_edge') # relaciona el Edge con una Conection
    name = Required(str) # nombre o apodo para la calle
    num_lanes = Optional(int) # numero de carriles
    is_traffic_input = Optional(bool) # indica si el trafico entra por esta calle
    associated_detector_name = Optional(str) # nombre del detector de trafico asociado a esta calle
    street_name = Optional(str) # nombre real de la calle
    aprox_length = Optional(float) # largo aproximado de la calle
    # propiedades obtenidas de la simulacion
    aprox_total_width = Optional(float) # ancho aproximado de la calle completa que incluye a todos los carriles
    max_speed = Optional(float)
    
    @property
    def aprox_area(self):
        return self.aprox_length * self.aprox_total_width # area calculada
    
    def getRepresentation(self):
        return "{} -> {}".format(self.from_edge.name, self.to_edge.name)
class Conection(db.Entity):
    # propiedades
    intersection = Optional(lambda:Intersection) #  relaciona que una Intersection puede tener varias Conections
    from_edge = Required(Edge, reverse='conection_uses_from') # desde que calle viene el trafico
    to_edge = Required(Edge, reverse='conection_uses_to') # hacia que calle viene el trafico
    
    def autoSetTraficInputs(self):
        self.from_edge.is_traffic_input = True 
        self.to_edge.is_traffic_input = False
class Intersection(db.Entity):
    # propiedades
    name = Required(str)
    associated_traffic_light_name = Required(str) # el nombre del semáforo asociado a la interseccion
    conections = Set(Conection) # lista de todas las conexiones entre calles
    
    @property
    def edges(self):
        return self.getEdges()
    
    def getEdges(self):
        edges_list = []
        for con in self.conections:
            edges_list.append(con.from_edge)
            edges_list.append(con.to_edge)
        return edges_list
    
    def getRepresentation(self):
        edges_str = ', '.join(map(str, self.edges_list))
        conections_str = ', '.join(map(str, self.conections_list))
        return "[{}] controls:\n\tedges: [{}]\n\tconections: [{}]".format(self.associated_traffic_light_name, edges_str, conections_str)
class EdgeState(db.Entity):
    name = Required(str)
    timestamp = Required(int)
    vehicle_number = Optional(int) # The number of vehicles on this lane within the last time step.
    mean_speed = Optional(float) # the mean speed of vehicles that were on this lane within the last simulation step [m/s]
    waiting_time = Optional(float) #  the sum of the waiting times for all vehicles on the edge
    occupancy = Optional(float) # the percentage of time the edge was occupied by a vehicle (%)
    state_label = Optional(str) # identifica la condicion dada del estado (ej. mucho trafico, politica fija, etc.)


def connect(in_memory_database = True):
    # conectando a la base de datos
    if in_memory_database:
        db.bind(provider='sqlite', filename=':memory:') # in memory database
    else:
        db.bind(provider='sqlite', filename='cache.sqlite', create_db=True) # file database
    # mapeando modelos a la base de datos
    db.generate_mapping(create_tables=True)
    # de manera dinaminca, si no existe la interseccion de circuito colonias, crearla
    if not existsIntersection("circuito_colonias"):
        create_cinco_colonias_intersection()


# haciando funciones de insersion y consulta
@db_session
def create_cinco_colonias_intersection():
    edges = {
        "from_north": Edge(name='from_north'),
        "to_south": Edge(name='to_south'),
        "from_east": Edge(name='from_east'),
        "to_west": Edge(name='to_west'),
        "from_west": Edge(name='from_west'),
        "to_east": Edge(name='to_east'),
    }
    conections = []
    conections.append(Conection(from_edge=edges["from_north"], to_edge=edges["to_south"]))
    conections.append(Conection(from_edge=edges["from_east"], to_edge=edges["to_west"]))
    conections.append(Conection(from_edge=edges["from_west"], to_edge=edges["to_east"]))
    cinco_col = Intersection(
        name="circuito_colonias",
        associated_traffic_light_name="semaforo_circuito_colonias", 
        conections=conections
    )

@db_session
def generateEdgeStateWithTraci(traci, edge_name, timestamp, state_label):
    return EdgeState(
        name=edge_name,
        timestamp=timestamp,
        vehicle_number=traci.edge.getLastStepVehicleNumber(edge_name),
        mean_speed=traci.edge.getLastStepMeanSpeed(edge_name),
        waiting_time=traci.edge.getWaitingTime(edge_name),
        occupancy=traci.edge.getLastStepOccupancy(edge_name),
        state_label=state_label
)
    
@db_session
def getIntersection(name):
    return Intersection.get(name=name)

@db_session
def existsIntersection(name):
    return Intersection.exists(name=name)

@db_session
def populateIntersectionUsingTraci(intersection, traci):
    intersection_refreshed = getIntersection(intersection.name)
    for edge in intersection_refreshed.edges:
        edge.num_lanes = traci.edge.getLaneNumber(edge.name)
        edge.street_name = traci.edge.getStreetName(edge.name)

@db_session
def autoGenerateState(intersection, traci, timestamp, label):
    intersection_refreshed = getIntersection(intersection.name)
    for edge in intersection_refreshed.edges:
        generateEdgeStateWithTraci(traci, edge.name, timestamp, label)
        
