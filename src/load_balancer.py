from typing import List
import threading
import time
import socket
import hashlib
import redis
from src.constants import LoadBalancingAlgorithms
from src.config import CONNECTION_POOL
from typing import Tuple


HEALTH_CHECK_TIME_PERIOD = 1

class LoadBalancer:
    """Load balancer

    Features:
        1. Load balancing.
        2. Periodic health checking.
        3. Caching for reduced latency.
    """

    def __init__(self, servers :List):
        """Initialize load balancer.
        Args:
            servers: List of backend servers to be used.
        
        """
        self._servers = {server: True for server in servers}
        self._current_server_index = 0
        self._lock = threading.Lock()

        self._algorithm = LoadBalancingAlgorithms.RR
        self.__index = 0
        self._check_health = False
        self._health_check_thread = None
        self.start_health_check()
        
    
    def add_server(self, server_address):
        """Add new server to load balancer."""

        if self._servers.get(server_address, None):
            raise Exception("Server already added.")

        try:
            connection = socket.create_connection(server_address)
            connection.close()
            self._servers[server_address] = True
        except Exception as e:
            self._servers[server_address] = False
            raise Exception("Provided server is found unhealthy")
    

    def remove_server(self, server_address):
        """Remove server from the list of server"""

        if not self._servers.get(server_address, None):
            print("Warning: Server unavailable to delete")
        
        with self._lock:
            del self._servers[server_address]
        return


    def set_algorithm(self, algorithm):
        """Update the load balancing algorithm."""

        if algorithm not in LoadBalancingAlgorithms:
            raise NotImplementedError(f"Warning: Either {algorithm} is not supported yet, or not valid.")
        with self._lock:
            self._algorithm = algorithm

    
    def suspend_health_check(self):
        """Stop periodic health check."""
        if not self._check_health:
            return
        with self._lock:
            self._check_health = False
        return


    def start_health_check(self):
        """Start periodic health checking of servers."""
        self._check_health = True
        
        health_check_thread = threading.Thread(
            target=self._check_server_health,
            args=(HEALTH_CHECK_TIME_PERIOD, )
        )
        health_check_thread.daemon = True
        health_check_thread.start()

    
    def _check_server_health(self, interval: int = HEALTH_CHECK_TIME_PERIOD):
        """Check the health status of servers every 10 minutes
        
        interval: time interval between health checks, default: 10 mins
        """

        updated_server_status = {}
        while self._check_health:
            for server in self._servers:
                try:
                    connection = socket.create_connection(server)
                    connection.close()
                    updated_server_status[server] = True
                except Exception as e:
                    updated_server_status[server] = False
            
            with self._lock:
                self._servers = updated_server_status
            
            time.sleep(interval)
        
        print("Stoping health checking.")
        return


    def select_server(self, client_addr: Tuple[str, int]):
        """Choose a server from the list of servers based on the algorithm"""

        server_addr = None
        cliet_host, client_ip = client_addr

        # check in cache if it is a cache hit check if the server is healthy.
        client_key = f'{cliet_host}:{client_ip}'
        redis_client = redis.Redis(connection_pool=CONNECTION_POOL)
        cached_server_key = redis_client.get(client_key)
        if cached_server_key:
            address, port = cached_server_key.decode("utf-8").split(":")
            cached_server = (address, int(port))
            if self._servers[cached_server]: return cached_server
            else: redis_client.delete(cached_server_key)

        # Get all the health servers and choose using the lb algorithm.
        healthy_servers = [server for server, health_status in self._servers.items() if health_status]
        if not healthy_servers:
            return None
        
        if self._algorithm == LoadBalancingAlgorithms.RR:
            server_addr =  self.__round_robin(healthy_servers)
        
        elif self._algorithm == LoadBalancingAlgorithms.IPH:
            server_addr =  self.__ip_hash(healthy_servers, client_key)
        
        elif self._algorithm == LoadBalancingAlgorithms.WRR:
            raise NotImplementedError(f"{LoadBalancingAlgorithms.WRR} not yet supported.")
            
        elif self._algorithm == LoadBalancingAlgorithms.LCN:
            raise NotImplementedError(f"{LoadBalancingAlgorithms.LCN} not yet supported.")

        elif self._algorithm == LoadBalancingAlgorithms.LRP:
            raise NotImplementedError(f"{LoadBalancingAlgorithms.LRP} not yet supported.")

        elif self._algorithm == LoadBalancingAlgorithms.RB:
            raise NotImplementedError(f"{LoadBalancingAlgorithms.RB} not yet supported.")
        
        server_host, server_ip = server_addr
        server_key = f"{server_host}:{server_ip}" 
        redis_client.set(client_key, server_key)

        return server_addr


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


        


