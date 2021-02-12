import lxml.etree as et
import re
from seaborn.utils import sig_stars
import config
import random
from datetime import datetime, timedelta
from scipy.stats import norm, uniform
import numpy as np
from operator import itemgetter

class TrafficGenerator:
    sumo_data_path = config.sumo_data_path
    sumocfg_filename = 'osm.sumocfg'
    
    def __init__(self, from_edge_name, to_edge_name, name="", replacefiles=False, to_edge_probabilities=[], from_edge_probabilities=[]):
        self.from_edge_name = from_edge_name
        self.to_edge_name = to_edge_name
        self.setupEdgesRouteProbs(from_edge_name, to_edge_name, to_edge_probabilities, from_edge_probabilities)
        if name:
            self.name = name
        elif type(to_edge_name) is str and type(from_edge_name) is str:
            self.name = "{}_{}".format(from_edge_name, to_edge_name)
        else:
            raise Exception('No se especificó un name para el generador.')
        self.traffic_filename = name + ".trips.xml"
        self.old_traffic_filename = addTrafficFile(self.sumo_data_path+self.sumocfg_filename, self.traffic_filename) if not replacefiles else setTrafficFile(self.sumo_data_path+self.sumocfg_filename, self.traffic_filename, True)
    
    def setupEdgesRouteProbs(self, from_edge_name, to_edge_name, to_edge_probabilities, from_edge_probabilities):
        # si to_edge_name es una lista...
        if type(to_edge_name) is list:
            # recibir las probabilidades si estan definidas
            if to_edge_probabilities:
                self.to_edge_probabilities = to_edge_probabilities
            # si no, generar probabilidades iguales para cada elemento
            else:
                nel = len(to_edge_name) # numero de elementos
                self.to_edge_probabilities = [1/nel for _ in range(nel)] # arreglo del tamaño de 'nel' donde cada elemento es 1/'nel'
        # si to_edge_name es una lista...
        if type(from_edge_name) is list:
            # recibir las probabilidades si estan definidas
            if from_edge_probabilities:
                self.from_edge_probabilities = from_edge_probabilities
            # si no, generar probabilidades iguales para cada elemento
            else:
                nel = len(from_edge_name) # numero de elementos
                self.from_edge_probabilities = [1/nel for _ in range(nel)] # arreglo del tamaño de 'nel' donde cada elemento es 1/'nel'
    
    # si to_edge_name es una lista, regresa uno de sus valores de acuerdo a las
    # probabilidades definidas
    def selectToEdge(self):
        # si to_edge_name es una lista, retornar uno de sus valores
        if type(self.to_edge_name) is list:
            return np.random.choice(self.to_edge_name, 1, p=self.to_edge_probabilities)[0]
        # si no, regresar su valor unico
        else:
            return self.to_edge_name
    
    # si from_edge_name es una lista, regresa uno de sus valores de acuerdo a las
    # probabilidades definidas
    def selectFromEdge(self):
        # si from_edge_name es una lista, retornar uno de sus valores
        if type(self.from_edge_name) is list:
            return np.random.choice(self.from_edge_name, 1, p=self.from_edge_probabilities)[0]
        # si no, regresar su valor unico
        else:
            return self.from_edge_name
    
    def generate(self, probability_list, vehicle_type = "", add_demo_vehicle=True):
        random.seed(42)  # Hace que la prueba sea reproducible
        with open(self.sumo_data_path+self.traffic_filename, "w") as routes:
            print("<routes>", file=routes)
            # si no se define tipo de vehiculo, definir uno por defecto y usarlo
            if not vehicle_type:
                if add_demo_vehicle:
                    print('    <vType id="coche_demo" length="5" color="1,1,0" maxSpeed="50" accel="2.6" decel="4.5" sigma="0.2" vClass="passenger"/>', file=routes)
                vehicle_type = 'coche_demo'
            coches_contador = 0
            for i, prob in enumerate(probability_list):
                if random.uniform(0, 1) < prob:
                    id = '{}_{}'.format(self.name, coches_contador)
                    # print('    <vehicle id="{3}_{0}" type="coche_normal" route="{1}" depart="{2}" color="1,1,0" />'.format(coches_contador, route_name, i, self.name), file=routes)
                    print('    <trip id="{}" type="{}" depart="{}" departLane="best" departSpeed="max" from="{}" to="{}"/>'.format(
                        id,
                        vehicle_type,
                        i,
                        self.selectFromEdge(),
                        self.selectToEdge()
                    ), file=routes)
                    coches_contador += 1
            print("</routes>", file=routes)
    
    def restoreOldTrafficFilename(self):
        setTrafficFile(self.sumo_data_path+self.sumocfg_filename, self.old_traffic_filename, True)

def setTrafficFile(sumocfg_filepath, trafic_filename, overwrite_all = False):
    # leyendo el archivo sumocfg especificado
    xmltree = et.parse(sumocfg_filepath)
    if not xmltree:
        raise Exception("No se encontró el archivo .sumocfg especificado")
    # buscando la ruta route-files
    routefiles = xmltree.xpath('//input/route-files');
    if len(routefiles) < 1:
        #TODO: aqui seria bueno agregar de manera inteligente el nodo route-files cuando no exista
        raise Exception("No se encontró el nodo route-files") 
    # obteniendo el valor que tiene actualmente
    prev_val = routefiles[0].get('value')
    if overwrite_all:
        new_val = trafic_filename
    else:
        # si existe valor previo, sustituir el que tenga la extensión .rou.xml por
        # el nuevo trafic_filename, si no, poner el nuevo trafic_filename tal cual
        if(prev_val):
            new_val = re.sub('[\w\.]*\.trips\.xml', trafic_filename, prev_val)
        else:
            new_val = trafic_filename
    
    # asignando el nuevo valor
    routefiles[0].set('value', new_val)
    # escribiendo el archivo xml
    xmltree.write(sumocfg_filepath, pretty_print=True, xml_declaration=True, encoding="utf-8")
    # retornando el valor previo por si se desea almacenarlo
    return prev_val

def addTrafficFile(sumocfg_filepath, trafic_filename):
    # leyendo el archivo sumocfg especificado
    xmltree = et.parse(sumocfg_filepath)
    if not xmltree:
        raise Exception("No se encontró el archivo .sumocfg especificado")
    # buscando la ruta route-files
    routefiles = xmltree.xpath('//input/route-files');
    if len(routefiles) < 1:
        #TODO: aqui seria bueno agregar de manera inteligente el nodo route-files cuando no exista
        raise Exception("No se encontró el nodo route-files") 
    # obteniendo el valor que tiene actualmente
    prev_val = routefiles[0].get('value')
    
    # si hay un valor previo...
    if prev_val:
        # si ya está puesto el valor que se quiere agregar, no cambiar nada
        if trafic_filename in prev_val:
            new_val = prev_val
        # si no está, agregarlo separado por una coma
        else:
            new_val = prev_val + ', ' + trafic_filename
    else:
        # si no hay valor previo, será igual al nombre del archivo a agregar
        new_val = trafic_filename
    
    # asignando el nuevo valor
    routefiles[0].set('value', new_val)
    # escribiendo el archivo xml
    xmltree.write(sumocfg_filepath, pretty_print=True, xml_declaration=True, encoding="utf-8")
    # retornando el valor previo por si se desea almacenarlo
    return prev_val


def intervalToSeconds(starttime, endtime, scale = 1, FORMAT='%H:%M'):
    """
    Convierte intervalos de tiempo en segundos

    Args:
        starttime (undefined): Hora de inicio
        endtime (undefined): Hora final
        scale=1 (undefined): para que no dure realmente la cantidad de segundos del dia, por motivos de desarrollo
        FORMAT='%H (%M'):

    """
    tdelta = datetime.strptime(endtime, FORMAT) - datetime.strptime(starttime, FORMAT)
    return (int)(tdelta.total_seconds()*scale)

def secondsToTime(seconds):
    return str(timedelta(seconds=seconds))

def dictToList(dict):
    return [(v) for k, v in dict.items()]

def sumDurationDict(intervals):
    sum = 0
    for duration in dictToList(intervals):
        sum += duration
    return sum

def printIntervals(intervals):
    for key, value in intervals.items():
        print('{}: {}'.format(key, value))

def genPeakProbs(duration, intensity, graphmode=False):
    size = duration # the number of random variates
    mean = 0.5 # mean of the distribution (loc)
    stddev = 0.8 # standard deviation (scale)
    input_numbers = np.linspace(0, 1, size) # genera numeros entre 0 y 1
    
    if intensity == 'high':
        stddev = 0.4
    elif intensity == 'low':
        stddev = 4
    elif intensity != 'medium':
        raise Exception('Invalid intensity value. Allowed values: "high", "medium" and "low"')
    probs = norm.pdf(x=input_numbers, loc=mean, scale=stddev)
    if(graphmode):
        return {
            'x': np.arange(duration),
            'y': probs
        }
    else: 
        return probs

def genUniformProbs(duration, intensity, graphmode=False):
    if intensity == 'high':
        return np.random.uniform(low=0, high=1, size=duration)
    elif intensity == 'low':
        return np.random.uniform(low=0, high=0.2, size=duration)
    elif intensity != 'medium':
        raise Exception('Invalid intensity value. Allowed values: "high", "medium" and "low"')
    probs = np.random.uniform(low=0, high=0.6, size=duration)
    if graphmode:
        return {
            'x': np.arange(duration),
            'y': probs
        }
    else:
        return probs
def genTrafficProbs(trafficconfigs, scale=1, getcumulativeintervals = False):
    intervalsdict = {} # dict de todas las probabilidades por día
    cumulativeintervals = {} # dict donde la key es el intervalo y el value la duracion en segundos
    cumulativeduration = 0
    for tc in trafficconfigs:
        # deconstruyendo valores del dict en variables
        start, end, gentype, intensity = itemgetter('start', 'end', 'gentype', 'intensity')(tc)
        duration = intervalToSeconds(start, end, scale=scale)
        cumulativeduration += duration
        intkeywsec = '{}-{} ({}s)'.format(start, end, duration) # interval key with seconds
        cumulativeintervals[end] = cumulativeduration
        if gentype == 'uniform':
            intervalsdict[intkeywsec] = genUniformProbs(duration, intensity)
        elif gentype == 'peak':
            intervalsdict[intkeywsec] = genPeakProbs(duration, intensity)
        else:
            raise Exception('Invalid type value.')
    allprobs = np.concatenate(dictToList(intervalsdict))
    if getcumulativeintervals:
        return allprobs, cumulativeintervals
    else:
        return allprobs

if __name__ == "__main__":
    from scipy.stats import norm
    import traffic_generator as tg

    # time section
    minute = 20
    day = minute * 60 * 24
    duration = day
    
    data_normal = norm.rvs(size=duration,loc=0,scale=0.2)

    gen1 = tg.TrafficGenerator("from_north_edge", "to_south_edge", name="test.trafns")
    gen1.generate(data_normal, vehicle_type="coche")
    
    # gen2 = tg.TrafficGenerator("from_east_edge", "to_west_edge", name="test.trafew")
    # gen2.generate(data_normal, vehicle_type="coche")
    
    # gen3 = tg.TrafficGenerator("from_west_edge", "to_east_edge", name="test.trafwe")
    # gen3.generate(data_normal, vehicle_type="coche")

    tg.config.testLaunch(duration)
    gen1.restoreOldTrafficFilename()
    # tg.config.traci.close()