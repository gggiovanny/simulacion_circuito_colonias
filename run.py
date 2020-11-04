from config import traci
import config
import PetriPy
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

def run():
    intersection = get_cinco_colonias_intersection()
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
        # TODO: volver esto un foreach recorriendo todas las calles
        edge_state = m.generateEdgeStateWithTraci(traci, "from_north", t)
        
        
        
        t+=1
    traci.close()

# este es el punto de entrada al script
if __name__ == "__main__":
    # ejecutando la funcion que controla a la simulacion
    run()