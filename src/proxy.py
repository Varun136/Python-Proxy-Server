import socket
import signal
import threading
import time
from typing import Tuple, List
import sys
from src.connection import Connection
from src.load_balancer import LoadBalancer
from src.config import BUFFER_SIZE, CONNECTION_TIMEOUT
from src.constants import SERVER_UNAVAILBLE_MESSAGE


class ProxyServer:
    """
    Server that act as proxy between the client and the backend servers.

    Features:
        1. Request re-routing.
        2. Inbuilt load balancer.
    """

    def __init__(self, server_addr: Tuple[str, int], backend_servers: List[Tuple[str, int]]):
        """
        Initializes the instance - setting up the proxy server.

        Args:
            server_addr: hostname and ip for the proxy server
            backend_servers: list of server addresses to be used as backend servers.
        """
        self.proxy_server = Connection(server_addr)
        self.load_balancer = LoadBalancer(backend_servers)
        self._buffer_size = BUFFER_SIZE


    def start(self):
        """Initiate the socket instance and start listsning for requests."""

        signal.signal(signal.SIGINT, self.shutdown)
        self.proxy_server.start()
        while True:
            client_socket, client_addr = self.proxy_server.accept()
            client_socket.settimeout(CONNECTION_TIMEOUT)
            print(f"Request received from client: {client_addr}")

            # Get the server addr using load balancer and forward the request to the BE server.
            try:
                backend_server_addr = self.load_balancer.select_server(client_addr)
                if not backend_server_addr: 
                    raise Exception("No healthy server available.")
                else:
                    print(f"Request forwarding to server: {backend_server_addr}")
                    thread = threading.Thread(
                        target=self._proxy_request_to_server,
                        args=(client_socket, backend_server_addr, client_addr),
                    )
                    thread.daemon = True
                    thread.start()
            except Exception as e:
                print("Unable to continue with the request at the moment, error: ", e)
                client_socket.sendall(SERVER_UNAVAILBLE_MESSAGE.encode())
                client_socket.close()


    def shutdown(self, signum, frame):
        """ Handle the exiting server. Clean all traces """
        
        self.load_balancer.suspend_health_check()
        main_thread = threading.currentThread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()

        self.proxy_server.close_server(signum, frame)
        sys.exit(0)


    def _proxy_request_to_server(self, 
            client_socket: socket.socket, 
            backend_server_addr: Tuple[str, int],
            client_addr: Tuple[str, int]
        ):
        """
        Get the domain name and port of the destination server and forward the 
        request data and receive the response to send it back to the 
        client socket.  
        """

        request = client_socket.recv(self._buffer_size)
        try:
            server_socket = socket.create_connection(backend_server_addr)
            server_socket.settimeout(CONNECTION_TIMEOUT)
        except Exception as e:
            new_server = self.load_balancer.select_server(client_addr)
            print(new_server)
            if not new_server:
                print("No healthy servers available.")
                client_socket.send(SERVER_UNAVAILBLE_MESSAGE.encode())
                client_socket.close()
                return
            server_socket = socket.create_connection(new_server)
            server_socket.settimeout(CONNECTION_TIMEOUT)
        
        try:
            server_socket.sendall(request)
            response = server_socket.recv(self._buffer_size)
            client_socket.sendall(response)
            client_socket.close()
        except Exception as e:
            print(f"Error: {e}")
            client_socket.sendall(SERVER_UNAVAILBLE_MESSAGE.encode())
            client_socket.close()

        return
            

    def set_backlog(self, backlog: int):
        """Change the number of clients to be queued"""

        if not backlog:
            raise ValueError("Invalid backlog value")
        self._backlog = backlog
    

    def set_buffer_size(self, buffer_size: int):
        """Update the buffer size of the proxy connection"""

        if buffer_size % 1024 != 0:
            raise ValueError("Inavlid buffer size")
        self._buffer_size = buffer_size




    