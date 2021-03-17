from models_db import *
from pony.orm import db_session
from traffic_generator import secondsToTime


class TrafficStorage:
    def __init__(self, traci, intersection_name):
        # instancia de traci
        self.traci = traci
        # conectando a la base de datos
        connect(False)
        # de manera dinaminca, si no existe en la bd la interseccion de circuito colonias, crearla
        if not self.existsIntersection("circuito_colonias"):
            self.create_cinco_colonias_intersection()
        # inicializando los datos de la interseccion
        self.initIntersectionData(intersection_name)
        # creando cache del estado
        self.initStateCache()

    def save(self):
        pass

    def initStateCache(self):
        self.stateCache = {}
        # for attr in EdgeState._columns_without_pk_:
        #     self.stateCache[attr] = None

    def collect(self, *args, **kwargs):
        self.generateEdgesStateCache(*args, **kwargs)
        self.storeStates()

    def generateEdgesStateCache(self, simulation_time, state_label='', active_net_name=''):
        for edge_name in self.in_edges_name:
            self.stateCache[edge_name] = {
                'name': edge_name,
                'simulation_time': simulation_time,
                'state_label': state_label,
                'time_formated': secondsToTime(simulation_time),
                'active_net_name': active_net_name,
                'vehicle_number': self.traci.edge.getLastStepVehicleNumber(edge_name),
                'mean_speed': self.traci.edge.getLastStepMeanSpeed(edge_name),
                'waiting_time': self.traci.edge.getWaitingTime(edge_name),
                'occupancy': self.traci.edge.getLastStepOccupancy(edge_name),
                'travel_time': self.traci.edge.getTraveltime(edge_name),
                'co2_emission': self.traci.edge.getCO2Emission(edge_name),
                'fuel_consumption': self.traci.edge.getFuelConsumption(edge_name),
                'noise_emission': self.traci.edge.getNoiseEmission(edge_name),
                'halting_number': self.traci.edge.getLastStepHaltingNumber(edge_name)
            }

    @db_session
    def storeStates(self):
        for name, data in self.stateCache.items():
            EdgeState(**data)

    @db_session
    def initIntersectionData(self, name):
        self.intersection = Intersection.get(name=name)
        self.in_edges_name = []
        for edge in self.intersection.in_edges:
            self.in_edges_name.append(edge.name)

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
    def populateIntersectionUsingTraci(self):
        curr_intersection = Intersection.get(name=self.intersection.name)
        for edge in curr_intersection.edges:
            edge.num_lanes = self.traci.edge.getLaneNumber(edge.name)
            edge.street_name = self.traci.edge.getStreetName(edge.name)
