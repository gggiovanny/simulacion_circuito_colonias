import os
import sys
import random
# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
from sumolib import checkBinary  # noqa
import traci


base_path = os.path.dirname(os.path.realpath(__file__)) + os.sep
sumo_data_path = os.path.join(base_path, 'data', 'sumo-net') + os.sep
logs_path = os.path.join(base_path, "logs") + os.sep
semaforo = 'semaforo_circuito_colonias'

def testLaunch(end_time = 50):
    # iniciando la simulacion
    traci.start(['sumo-gui', "-c", sumo_data_path+'osm.sumocfg'])
    t = 0
    # Ejecuta el bucle de control de TraCI
    while traci.simulation.getMinExpectedNumber() > 0 and t <= end_time:
        traci.simulationStep()
        # recorriendo todas las calles y generando el estado de cada una
        t+=1
    traci.close()