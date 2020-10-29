from config import traci
import config
import PetriPy
import models as m

def get_cinco_colonias_intersection():
    edges = {
        "from_north": m.Edge(num_lanes=2, name='from_north'),
        "to_south": m.Edge(num_lanes=2, name='to_south'),
        "from_east": m.Edge(num_lanes=2, name='from_east'),
        "to_west": m.Edge(num_lanes=2, name='to_west'),
        "from_west": m.Edge(num_lanes=2, name='from_west'),
        "to_east": m.Edge(num_lanes=2, name='to_east'),
    }
    conections = {
        "north_to_south": m.Conection(edges["from_north"], edges["to_south"]),
        "east_to_west": m.Conection(edges["from_east"], edges["to_west"]),
        "west_to_east": m.Conection(edges["from_west"], edges["to_east"]),
    }
    return m.Intersection(
        "semaforo_circuito_colonias", 
        edges_list=edges.values(), 
        conections_list=conections.values()
    )

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