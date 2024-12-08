from typing import List
from enum import StrEnum


class LoadBalancingAlgorithms(StrEnum):
    RR = "RoundRobin"
    WRR = "WeightedRoundRobin"
    IPH = "IPHash"
    LCN = "LeastConnection"
    LRP = "LeastResponse"
    RB = "ResourceBased"

class LoadBalancer:

    def __init__(self, servers :List, algorithm = LoadBalancingAlgorithms.RR):
        self._servers = servers
        self._algorithm = algorithm
