
class TrafficBalancer:
    def __init__(self):
        pass

    def balance(self, edgeState):
        numedges = len(edgeState)
        totaltraffic = 0
        result = {}
        for e in edgeState.values():
            totaltraffic += e['vehicle_number']
            result[e['name']] = {'count': e['vehicle_number']}
        for r in result.values():
            r['percentage'] = r['count'] / totaltraffic
        return result
