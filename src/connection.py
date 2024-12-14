import socket
import threading
from typing import Tuple
from src.config import SERVER_BACKLOG


class Connection(socket.socket):
    """Socket instance"""

    def __init__(self, server_addr: Tuple[str, int]):
        """
        Args:
            server_addr: (server_host, server_port)
        """

        try:
            super().__init__(socket.AF_INET, socket.SOCK_STREAM)
            self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self.bind(server_addr)
            
        except socket.gaierror or OSError :
            raise ValueError("Unhealthy or Invalid server address.")

        self._ip, self._port = server_addr
        self._addr = server_addr
        self._backlog = SERVER_BACKLOG
        self._lock = threading.Lock()
        self.is_alive = False

    def start(self):
        """Start listening on the server."""

        self.listen(self._backlog)
        self.is_alive = True
        print(f"Info: Starting server at {self._ip}:{self._port}")
    

    def close_server(self, signum, frame):
        """Close connection"""
        
        self.close()
        self.is_alive = False
        print(f"Info: Closing server ({self._ip}:{self._port}) gracefully.")