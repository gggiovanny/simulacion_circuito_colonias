from models_db import *
from pony.orm import db_session


class TrafficStorage:
    def __init__(self):
        # conectando a la base de datos
        connect(False)
        # de manera dinaminca, si no existe en la bd la interseccion de circuito colonias, crearla
        if not self.existsIntersection("circuito_colonias"):
            self.create_cinco_colonias_intersection()
        pass

    def store(self):
        pass

    def hold(self):
        pass

    @db_session
    def generateEdgeStateWithTraci(self, traci, edge_name, simulation_time, state_label='', time_formated='', active_net_name=''):
        return EdgeState(
            name=edge_name,
            simulation_time=simulation_time,
            vehicle_number=traci.edge.getLastStepVehicleNumber(edge_name),
            mean_speed=traci.edge.getLastStepMeanSpeed(edge_name),
            waiting_time=traci.edge.getWaitingTime(edge_name),
            occupancy=traci.edge.getLastStepOccupancy(edge_name),
            state_label=state_label,
            travel_time=traci.edge.getTraveltime(edge_name),
            co2_emission=traci.edge.getCO2Emission(edge_name),
            fuel_consumption=traci.edge.getFuelConsumption(edge_name),
            noise_emission=traci.edge.getNoiseEmission(edge_name),
            halting_number=traci.edge.getLastStepHaltingNumber(edge_name),
            time_formated=time_formated,
            active_net_name=active_net_name
        )

    @db_session
    def autoGenerateState(self, intersection, traci, simulation_time, state_label='', time_formated='', active_net_name=''):
        intersection_refreshed = self.getIntersection(intersection.name)
        for edge in intersection_refreshed.in_edges:
            self.generateEdgeStateWithTraci(traci,
                                            edge_name=edge.name,
                                            simulation_time=simulation_time,
                                            state_label=state_label,
                                            time_formated=time_formated,
                                            active_net_name=active_net_name
                                            )

    @db_session
    def getIntersection(self, name):
        return Intersection.get(name=name)

    @db_session
    def create_cinco_colonias_intersection(self):
        edges = {
            "from_north": Edge(name='from_north'),
            "to_south": Edge(name='to_south'),
            "from_east": Edge(name='from_east'),
            "to_west": Edge(name='to_west'),
            "from_west": Edge(name='from_west'),
            "to_east": Edge(name='to_east'),
        }
        conections = []
        conections.append(
            Conection(from_edge=edges["from_north"], to_edge=edges["to_south"]))
        conections.append(
            Conection(from_edge=edges["from_east"], to_edge=edges["to_west"]))
        conections.append(
            Conection(from_edge=edges["from_west"], to_edge=edges["to_east"]))
        cinco_col = Intersection(
            name="circuito_colonias",
            associated_traffic_light_name="semaforo_circuito_colonias",
            conections=conections
        )

    @db_session
    def existsIntersection(self, name):
        return Intersection.exists(name=name)

    @db_session
    def populateIntersectionUsingTraci(self, intersection, traci):
        intersection_refreshed = self.getIntersection(intersection.name)
        for edge in intersection_refreshed.edges:
            edge.num_lanes = traci.edge.getLaneNumber(edge.name)
            edge.street_name = traci.edge.getStreetName(edge.name)
