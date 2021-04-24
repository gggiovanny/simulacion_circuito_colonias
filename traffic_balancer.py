
class TrafficBalancer:
    def __init__(self, per_edge_base_wait: float,  numedges: int, min_wait: float = 1, max_wait: float = 999):
        self.per_edge_base_wait = per_edge_base_wait
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.numedges = numedges
        self.intersection_total_wait = per_edge_base_wait * numedges
        pass

    def balance(self, edgeState):
        totaltraffic = 0
        result = {}
        for e in edgeState.values():
            totaltraffic += e['vehicle_number']
            result[e['name']] = {'count': e['vehicle_number']}
        for r in result.values():
            # calculando el porcentaje de trafico de cada interseccion
            if totaltraffic == 0:
                # si no hay nada de tráfico, repartir el porcentaje de trafico equitativamente entre las calles
                r['percentage'] = 1 / self.numedges
            else:
                r['percentage'] = r['count'] / totaltraffic
            # calculando cuanto tiempo representa ese porcentaje
            r['time'] = r['percentage'] * self.intersection_total_wait
            if r['time'] < self.min_wait:
                r['time'] = self.min_wait
            if r['time'] > self.max_wait:
                r['time'] = self.max_wait
        return result
