from enum import Enum



BACKEND_SERVERS = [
    ("127.0.0.1", 8000),
    ("127.0.0.2", 8000),
    ("127.0.0.3", 8000),
    ("127.0.0.4", 8000),
]

BUFFER_SIZE = 4096

class LoadBalancingAlgorithms(Enum):
    RR = "RoundRobin"
    WRR = "WeightedRoundRobin"
    IPH = "IPHash"
    LCN = "LeastConnection"
    LRP = "LeastResponse"
    RB = "ResourceBased"