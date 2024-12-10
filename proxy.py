import socket
import signal
import threading
from typing import Tuple
import sys
from server import Connection
from load_balancer import LoadBalancer
from constants import BUFFER_SIZE, BACKEND_SERVERS


class ProxyServer:
    """Server that act as proxy between the client and the backend servers.
    
    Implemented: 
        1. Request and Response passing.

    To Do
        2. Domain blocking.
        3. Caching.
    
    Improvement
        1. Logging.
    """

    def __init__(self, server_addr: Tuple[str, int]):
        """
        Initializes the instance - setting up the proxy server.
        """
        self._proxy_server = Connection(server_addr)
        self._load_balancer = LoadBalancer(BACKEND_SERVERS)


    def start(self):
        signal.signal(signal.SIGINT, self.shutdown)
        self._proxy_server.start()
        
        while True:
            client_socket, client_addr = self._proxy_server.accept()

            # Get the server using load balancer and forward the request to the BE server.
            try:
                backend_server_addr = self._load_balancer.select_server(client_addr)
                thread = threading.Thread(
                    target=self.proxy_request_to_server,
                    args=(client_socket, backend_server_addr),
                )
                thread.daemon = True
                thread.start()
            
            except Exception as e:
                print("Unable to continue with the request at the moment, error: ", e)


    def shutdown(self, signum, frame):
        """ Handle the exiting server. Clean all traces """

        main_thread = threading.currentThread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()
            self.shutdown(signum, frame)
        sys.exit(0)
    

    def proxy_request_to_server(self, client_socket: socket.socket, backend_server_addr: Tuple[str, int]):
        """
        Get the domain name and port of the destination server and forward the 
        request data and receive the response to send it back to the 
        client socket.  
        """

        request = client_socket.recv(BUFFER_SIZE)

        server_socket = Connection(backend_server_addr)
        server_socket.sendall(request)
        
        while True:
            response = server_socket.recv(BUFFER_SIZE)
            if not response: break

            client_socket.sendall(response)

            # unlesss 'keep-alive' is received from the header of the request.
            client_socket.close()
            server_socket.close()



    def set_backlog(self, backlog: int):
        """Change the number of clients to be queued"""

        if not backlog:
            raise ValueError("Invalid backlog value")
        self._backlog = backlog



    