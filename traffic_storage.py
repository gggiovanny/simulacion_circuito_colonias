from models_db import *
from pony.orm import db_session
from traffic_generator import secondsToTime
import time


class TrafficStorage:
    def __init__(self, traci, intersection_name):
        # instancia de traci
        self.traci = traci
        # generando nombre de instancia
        self.instance_name = self.__generateInstanceName()
        # conectando a la base de datos
        connect(self.instance_name)
        # de manera dinaminca, si no existe en la bd la interseccion de circuito colonias, crearla
        if not self.__existsIntersection("circuito_colonias"):
            self.__create_cinco_colonias_intersection()
        # inicializando los datos de la interseccion
        self.__initIntersectionData(intersection_name)
        # creando cache del estado
        self.__initStateCache()
        # callback que se ejecuta al guardar el estado
        self.onSave = None

    def collect(self, *args, **kwargs):
        self.__generateEdgesStateCache(*args, **kwargs)

    def save(self, simulation_time):
        # TODO: crear un modelo de EdgeStateRange que indique en cada campo si es acumulado, promedio y que los rangos se tiempo sean campos separados: ej. start_time, end_time
        for edge_name in self.in_edges_name:
            prev = self.stateCache[edge_name]
            # poner rangos de tiempo
            self.stateCache[edge_name]['simulation_time'] = '{}-{}'.format(
                prev['simulation_time'], simulation_time)
            self.stateCache[edge_name]['time_formated'] = '{}-{}'.format(
                prev['time_formated'], secondsToTime(simulation_time))
            # promediando los campos pertinentes
            campos_a_promediar = ('mean_speed', 'occupancy', 'noise_emission')
            for key in campos_a_promediar:
                self.stateCache[edge_name][key] = prev[key] / self.cache_count
            # calculando el waiting_time total
            self.stateCache[edge_name]['waiting_time'] = prev['waiting_time'] + \
                sum(prev['waiting_time_peak_values'])
        if self.onSave:
            self.onSave(self.stateCache)
        self.__storeStates()
        self.__initStateCache()

    @db_session
    def getPerformanceData(self):
        return select(e.waiting_time for e in EdgeState).sum()

    def __initStateCache(self):
        self.stateCache = {}
        self.cache_count = 0

    def __generateInstanceName(self):
        return time.strftime("%Y%m%d_%H%M%S")

    def __generateEdgesStateCache(self, simulation_time, state_label='', active_net_name=''):
        self.cache_count += 1
        for edge_name in self.in_edges_name:
            current_waiting_time = self.traci.edge.getWaitingTime(edge_name)
            if edge_name in self.stateCache:
                prev = self.stateCache[edge_name]

                accumulated_waiting_time, waiting_time_peak_values = self.__accumulatePeakValue(
                    accumulator=prev['waiting_time'],
                    prevValue=prev['waiting_time_prev_value'],
                    currentValue=current_waiting_time,
                    peakValues=prev['waiting_time_peak_values'],
                    edge_name=edge_name
                )

                self.stateCache[edge_name] = {
                    'name': prev['name'],  # mantener primero agregado
                    # mantener primero agregado
                    'simulation_time': prev['simulation_time'],
                    'state_label': self.__concatIfchanges(prev['state_label'], state_label),
                    # mantener primero agregado
                    'time_formated': prev['time_formated'],
                    'active_net_name': self.__concatIfchanges(prev['active_net_name'], active_net_name),
                    # suma
                    'vehicle_number': prev['vehicle_number'] + self.traci.edge.getLastStepVehicleNumber(edge_name),
                    # promedio
                    'mean_speed': prev['mean_speed'] + self.traci.edge.getLastStepMeanSpeed(edge_name),
                    # acumular el valor pico
                    'waiting_time': accumulated_waiting_time,
                    # valor temporal para 'waiting_time'
                    'waiting_time_prev_value': current_waiting_time,
                    # valor temporal para 'waiting_time'
                    'waiting_time_peak_values': waiting_time_peak_values,
                    # promedio
                    'occupancy': prev['occupancy'] + self.traci.edge.getLastStepOccupancy(edge_name),
                    # suma
                    'travel_time': prev['travel_time'] + self.traci.edge.getTraveltime(edge_name),
                    # suma
                    'co2_emission': prev['co2_emission'] + self.traci.edge.getCO2Emission(edge_name),
                    # suma
                    'fuel_consumption': prev['fuel_consumption'] + self.traci.edge.getFuelConsumption(edge_name),
                    # promedio
                    'noise_emission': prev['noise_emission'] + self.traci.edge.getNoiseEmission(edge_name),
                    # suma
                    'halting_number': prev['halting_number'] + self.traci.edge.getLastStepHaltingNumber(edge_name)
                }
            else:
                self.stateCache[edge_name] = {
                    'name': edge_name,
                    'simulation_time': simulation_time,
                    'state_label': state_label,
                    'time_formated': secondsToTime(simulation_time),
                    'active_net_name': active_net_name,
                    'vehicle_number': self.traci.edge.getLastStepVehicleNumber(edge_name),
                    'mean_speed': self.traci.edge.getLastStepMeanSpeed(edge_name),
                    'waiting_time': current_waiting_time,
                    'waiting_time_prev_value': current_waiting_time,
                    'waiting_time_peak_values': [],
                    'occupancy': self.traci.edge.getLastStepOccupancy(edge_name),
                    'travel_time': self.traci.edge.getTraveltime(edge_name),
                    'co2_emission': self.traci.edge.getCO2Emission(edge_name),
                    'fuel_consumption': self.traci.edge.getFuelConsumption(edge_name),
                    'noise_emission': self.traci.edge.getNoiseEmission(edge_name),
                    'halting_number': self.traci.edge.getLastStepHaltingNumber(edge_name)
                }

    def __concatIfchanges(self, oldvalue, newvalue):
        return oldvalue if newvalue in oldvalue else '{}|{}'.format(oldvalue, newvalue)

    # reducer function, always return the new value of the accumulator
    def __accumulatePeakValue(self, *, accumulator, prevValue, currentValue, peakValues, edge_name):
        returnAccumulator = accumulator
        returnPeakValues = peakValues

        # cuando currentValue era 0 y empieza a aumentar
        if currentValue > 0 and prevValue == 0 and accumulator > 0:
            returnPeakValues.append(accumulator)
            returnAccumulator = max(prevValue, currentValue)
        else:
            returnAccumulator = max(accumulator, currentValue)

        return returnAccumulator, returnPeakValues

    def removeTempValues(self, d):
        r = dict(d)
        del r['waiting_time_prev_value']
        del r['waiting_time_peak_values']
        return r

    @db_session
    def __storeStates(self):
        for name, data in self.stateCache.items():
            EdgeState(**self.removeTempValues(data))

    @db_session
    def __initIntersectionData(self, name):
        self.intersection = Intersection.get(name=name)
        self.in_edges_name = []
        for edge in self.intersection.in_edges:
            self.in_edges_name.append(edge.name)

    @db_session
    def __create_cinco_colonias_intersection(self):
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
    def __existsIntersection(self, name):
        return Intersection.exists(name=name)

    @db_session
    def __populateIntersectionUsingTraci(self):
        curr_intersection = Intersection.get(name=self.intersection.name)
        for edge in curr_intersection.edges:
            edge.num_lanes = self.traci.edge.getLaneNumber(edge.name)
            edge.street_name = self.traci.edge.getStreetName(edge.name)
