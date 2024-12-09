from typing import List
import threading
import time
import socket
import hashlib
import redis
from constants import LoadBalancingAlgorithms
from cache import connection_pool


class LoadBalancer:

    def __init__(self, servers :List):
        self._servers = {server: True for server in servers}
        self._current_server_index = 0
        self._lock = threading.Lock()

        self._algorithm = LoadBalancingAlgorithms.RR
        self.__index = 0
    

    def _check_server_health(self, interval: int = 10):
        """Check the health status of servers every 10 minutes
        
        interval: time interval between health checks, default: 10mins
        """
        while True:
            with self._lock:
                for server in self._servers:
                    try:
                        connection = socket.create_connection(server, timeout=2)
                        connection.close()
                        self._servers[server] = True
                    except Exception as e:
                        print(f"Server {server} found unhealthy")
                        self._servers[server] = False
            time.sleep(interval*60)
        
    
    def add_server(self, server_address):
        """Add new server to load balancer."""

        if self._servers.get(server_address, None):
            raise Exception("Warning: Server already added.")

        try:
            connection = socket.create_connection(server_address, timeout=2)
            connection.close()
            self._servers[server_address] = True
        except Exception as e:
            self._servers[server_address] = False
            raise Exception("Warning: Provided server is found unhealthy")
    

    def remove_server(self, server_address):
        """Remove server from the list of server"""

        if not self._servers.get(server_address, None):
            print("Warning: Server unavailable to delete")
        
        with self._lock:
            del self._servers(server_address)
        return

    def set_algorithm(self, algorithm):
        """Update the load balancing algorithm."""

        if algorithm not in LoadBalancingAlgorithms:
            raise ValueError(f"Warning: Either {algorithm} is not supported yet, or not valid.")
        with self._lock:
            self._algorithm = algorithm


    def select_server(self, client_ip: str):
        """Choose a server from the list of servers based on the algorithm"""
        
        # check in cache if it is a cache hit check if the server is healthy.
        redis_client = redis.Redis(connection_pool=connection_pool)
        cached_server_key = redis_client.get(client_ip)
        if cached_server_key:
            address, port = cached_server_key.decode("utf-8").split(":")
            cached_server = (address, int(port))
            if self._servers[cached_server]: return cached_server
            else: redis_client.delete(cached_server_key)

        # Get all the health servers and choose using the lb algorithm.
        healthy_servers = [server for server, health_status in self._servers.items() if health_status]
        if not healthy_servers:
            raise SystemError("No healthy servers, please retry after sometime.")
        
        if self._algorithm == LoadBalancingAlgorithms.RR:
            server =  self.__round_robin(healthy_servers)
        
        elif self._algorithm == LoadBalancingAlgorithms.IPH:
            server =  self.__ip_hash(healthy_servers, client_ip)
        
        elif self._algorithm == LoadBalancingAlgorithms.WRR:
            raise NotImplementedError(f"{LoadBalancingAlgorithms.WRR} not yet supported.")
            
        elif self._algorithm == LoadBalancingAlgorithms.LCN:
            raise NotImplementedError(f"{LoadBalancingAlgorithms.LCN} not yet supported.")

        elif self._algorithm == LoadBalancingAlgorithms.LRP:
            raise NotImplementedError(f"{LoadBalancingAlgorithms.LRP} not yet supported.")

        elif self._algorithm == LoadBalancingAlgorithms.RB:
            raise NotImplementedError(f"{LoadBalancingAlgorithms.RB} not yet supported.")
        
        server_key = f"{server[0]}:{server[1]}" 
        redis_client.set(client_ip, server_key)

        return server


    def __round_robin(self, servers):
        """Distributed evenly and cyclically among a set of healthy Servers or resources"""

        server = servers[self.__index]
        with self._lock:
            self.__index == (self.__index + 1) % len(servers)
        return server


    def __ip_hash(self, servers, client_ip):
        """Distributed by getting the hashvalue from the client ip"""

        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        server = servers[hash_value % len(servers)]
        return server


        


