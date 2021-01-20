import lxml.etree as et
import re
from seaborn.utils import sig_stars
import config
import random

class TrafficGenerator:
    sumo_data_path = config.sumo_data_path
    sumocfg_filename = 'osm.sumocfg'
    
    def __init__(self, from_edge_name, to_edge_name, name="generated_traffic", replacefiles=False):
        self.name = name
        self.traffic_filename = name + ".trips.xml"
        self.from_edge_name = from_edge_name
        self.to_edge_name = to_edge_name
        self.old_traffic_filename = addTrafficFile(self.sumo_data_path+self.sumocfg_filename, self.traffic_filename) if not replacefiles else setTrafficFile(self.sumo_data_path+self.sumocfg_filename, self.traffic_filename, True)
    
    def generate(self, probability_list, vehicle_type = "", add_demo_vehicle=True):
        random.seed(42)  # Hace que la prueba sea reproducible
        route_name = self.from_edge_name + self.to_edge_name
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
                        self.from_edge_name,
                        self.to_edge_name
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