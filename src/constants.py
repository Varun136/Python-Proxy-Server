from enum import Enum


class LoadBalancingAlgorithms(Enum):
    RR = "RoundRobin"
    WRR = "WeightedRoundRobin"
    IPH = "IPHash"
    LCN = "LeastConnection"
    LRP = "LeastResponse"
    RB = "ResourceBased"