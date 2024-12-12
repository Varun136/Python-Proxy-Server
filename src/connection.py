import socket
import threading
from typing import Tuple
from src.config import SERVER_BACKLOG


class Connection(socket.socket):
    """Socket instance"""

    def __init__(self, server_addr: Tuple[str, int]):
        """
            :server_addr - Tuple(server_ip: str, port: int)
        """

        try: # check the health status of the server before connecting.
            test_connection = socket.create_connection(server_addr)
            test_connection.close()
        except:
            raise ValueError("Server address invalid or unhealthy.")
        
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.bind(server_addr)

        self._ip, self._port = server_addr
        self._backlog = SERVER_BACKLOG
        self._lock = threading.Lock()

    def start(self):
        """Start listening on the server."""

        self.listen(self._backlog)
        print(f"Info: Starting server at {self._ip}:{self._port}")
    

    def close_server(self, signum, frame):
        """Close connection"""
        
        self.shutdown(signum, frame)
        print(f"Info: Closing server ({self._ip}:{self._port}) gracefully.")