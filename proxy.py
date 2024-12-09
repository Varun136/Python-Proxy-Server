import socket
import signal
import threading
from typing import Tuple
import sys
from server import Server
from load_balancer import LoadBalancer
from constants import BUFFER_SIZE, BACKEND_SERVERS





class ProxyServer(Server):
    """Server that act as proxy between the client and the backend servers.
    
    Implemented: 
        1. Request and Response passing.

    To Do
        2. Domain blocking.
        3. Caching.
    
    Improvement
        1. Logging.
    """

    def __init__(self, port: int, address: str):
        """
        Initializes the instance - setting up the proxy server.
        """
        super().__init__(address, port)
        self._load_balancer = LoadBalancer(BACKEND_SERVERS)


    def start(self):
        signal.signal(signal.SIGINT, self.shutdown)
        self.start_server()
        
        while True:
            clientSocket, clientAddr = self.accept()

            # Get the server using load balancer and forward the request to the BE server.
            serverAddr = self._load_balancer.select_server(clientAddr)
            thread = threading.Thread(
                target=self.proxy_request_to_server,
                args=(clientSocket, serverAddr),
            )
            thread.daemon = True
            thread.start()


    def shutdown(self, signum, frame):
        """ Handle the exiting server. Clean all traces """

        main_thread = threading.currentThread() # Wait for all clients to exit
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()

        self.close_server()
        sys.exit(0)
    

    def proxy_request_to_server(self, clientSocket: socket.socket, serverAddr: Tuple[str, int]):
        """
        Get the domain name and port of the destination server and forward the 
        request data and receive the response to send it back to the 
        client socket.  
        """

        request = clientSocket.recv(BUFFER_SIZE)

        webserver, port = serverAddr
        destination_server = Server(webserver, port)
        destination_server.sendall(request)
        
        while True:
            try:
                data = destination_server.recv(BUFFER_SIZE)
                if data:
                    clientSocket.sendall(data)
                else:
                    break
            except Exception as e:
                print("Error: ", e)
                break


    def set_backlog(self, backlog: int):
        """Change the number of clients to be queued"""

        if not backlog:
            raise ValueError("Invalid backlog value")
        self._backlog = backlog



    