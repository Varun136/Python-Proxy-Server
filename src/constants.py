from enum import Enum
import json


class LoadBalancingAlgorithms(Enum):
    RR = "RoundRobin"
    WRR = "WeightedRoundRobin"
    IPH = "IPHash"
    LCN = "LeastConnection"
    LRP = "LeastResponse"
    RB = "ResourceBased"


SERVER_UNAVAILBLE_MESSAGE = json.dumps({"status_code": 500, "message": "Server unavailble"})