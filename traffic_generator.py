import lxml.etree as et
import re
import config

# es importante que el
def setTrafficFileInXML(sumocfg_filepath, trafic_filename):
    # leyendo el archivo sumocfg especificado
    xmltree = et.parse(sumocfg_filepath)
    if not xmltree:
        raise Exception("No se encontró el archivo .sumocfg especificado")
    # buscando la ruta route-files
    routefiles = xmltree.xpath('//input/route-files');
    if len(routefiles) < 1:
        raise Exception("No se encontró el nodo route-files")
    # obteniendo el valor que tiene actualmente
    prev_val = routefiles[0].get('value')
    
    # si existe valor previo, sustituir el que tenga la extensión .rou.xml por
    # el nuevo trafic_filename, si no, poner el nuevo trafic_filename tal cual
    if(prev_val):
        new_val = re.sub('[a-z]*\.rou\.xml', trafic_filename, prev_val)
    else:
        new_val = trafic_filename
    
    # asignando el nuevo valor
    routefiles[0].set('value', new_val)
    # escribiendo el archivo xml
    xmltree.write(sumocfg_filepath, pretty_print=True, xml_declaration=True, encoding="utf-8")
    # retornando el valor previo por si se desea almacenarlo
    return prev_val


def generar_archivo_vehiculos():
    random.seed(42)  # Hace que la prueba sea reproducible
    N = 3600  # numero de time steps (segundos de la simulacion)
    # demanda por segundo desde las diferentes direcciones
    probabilidad_coche_desde_izquierda = 1. / 10
    probabilidad_ambulancia_desde_izquierda =  1. / 100
    probabilidad_coche_desde_abajo = 1. / 50
    probabilidad_ambulancia_desde_abajo = 0
    with open(sumo_data_path+"vehiculos.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="coche_normal" length="5" color="1,1,0" maxSpeed="50" accel="2.6" decel="4.5" sigma="0.2" vClass="passenger"/>
    <vType id="emergencia" length="5" color="1,0,0" maxSpeed="50" accel="2.6" decel="4.5" sigma="0.2" vClass="emergency"/>
    <route id="de_izquierda_a_derecha" edges="izquierda_a_derecha_inicio izquierda_a_derecha_fin" />
    <route id="de_abajo_a_arriba" edges="abajo_a_arriba_inicio abajo_a_arriba_fin" />
    """, file=routes)
        coches_contador = 0
        for i in range(N):
            if random.uniform(0, 1) < probabilidad_coche_desde_izquierda:
                print('    <vehicle id="izq_%i" type="coche_normal" route="de_izquierda_a_derecha" depart="%i" color="1,1,0" />' % (
                    coches_contador, i), file=routes)
                coches_contador += 1
            if random.uniform(0, 1) < probabilidad_ambulancia_desde_izquierda:
                print('    <vehicle id="izq_ambulancia_%i" type="emergencia" route="de_izquierda_a_derecha" depart="%i" color="1,0,0" />' % (
                    coches_contador, i), file=routes)
                coches_contador += 1
            if random.uniform(0, 1) < probabilidad_coche_desde_abajo:
                print('    <vehicle id="abajo_%i" type="coche_normal" route="de_abajo_a_arriba" depart="%i" color="1,1,0" />' % (
                    coches_contador, i), file=routes)
                coches_contador += 1
            if random.uniform(0, 1) < probabilidad_ambulancia_desde_abajo:
                print('    <vehicle id="abajo_ambulancia_%i" type="emergencia" route="de_abajo_a_arriba" depart="%i" color="1,0,0" />' % (
                    coches_contador, i), file=routes)
                coches_contador += 1
            
        print("</routes>", file=routes)
        
        
if __name__ == "__main__":
    # ejecutando la funcion que controla a la simulacion
    sumocfg_filepath = config.sumo_data_path + 'osm.sumocfg'
    trafic_filename = 'prueba_vehiculos.rou.xml'
    setTrafficFileInXML(sumocfg_filepath, trafic_filename)