
class TrafficBalancer:
    def __init__(self, per_edge_base_wait, numedges):
        self.per_edge_base_wait = per_edge_base_wait
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
            r['percentage'] = r['count'] / totaltraffic
            r['time'] = r['percentage'] * self.intersection_total_wait
        return result
