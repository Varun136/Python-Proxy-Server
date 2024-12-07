import socket
import signal
import threading
from typing import Tuple
import sys


BUFFER_SIZE = 4096

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

    def __init__(self, port: int, address: str):
        """
        Initializes the instance - setting up the proxy server.
        """
        self._port = port
        self._address = address
        self.__server: socket.socket = None
        self._backlog = 10
        self.__clients = {}

    def start(self):
        signal.signal(signal.SIGINT, self.shutdown)
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Reuse the address and port imediatly without waiting for the TIME_WAIT state by OS.
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.__server.bind((self._address, self._port))
        self.__server.listen(self._backlog)

        print(f"Starting proxy server at port: {self._port}")
        
        while True:
            clientSocket, clientAddr = self.__server.accept()

            # Spin up a new thread for each socket connection.
            thread = threading.Thread(
                target=self.proxy_request_to_server,
                args=(clientSocket,),
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
            self.__server.close()
        
        print("Shutting server down gracefully.")
        sys.exit(0)
    

    def proxy_request_to_server(self, clientSocket: socket.socket):
        """Forward the request to the destination server

        Get the domain name and port of the destination server and forward the 
        request data and receive the response to send it back to the 
        client socket.  
        """

        request = clientSocket.recv(BUFFER_SIZE)
        url = self.__get_url_from_request(request)
        port, webserver = self.__get_port_and_server(url)
        if not (port or webserver):
            print("Unable to resolve the port and server, Aborting the request.")
            return
        
        destination_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # destination_server.settimeout(10)
        destination_server.connect((webserver, port))
        destination_server.sendall(request)
        while True:
            try:
                data = destination_server.recv(BUFFER_SIZE)
                if data:
                    print("response: ", data)
                    clientSocket.send(data)
                else:
                    break
            except Exception as e:
                print("Error: ", e)
                break

    
    def __get_url_from_request(self, request):
        """Get the url from the decoded request"""

        request_str = request.decode("utf-8")
        url_pos = request_str.find("Host:")
        return request_str[url_pos+5:].split("\n")[0]
    

    def __get_port_and_server(self, url: str) -> Tuple[int, str]:
        """Retrieve the port number and the webserver name from the url"""

        port = None
        webserver = None
        temp_url = url

        port_pos = temp_url.find(":")
        webserver_pos = temp_url.find("/")

        if webserver_pos == -1:
            webserver_pos = len(temp_url)
        
        if (port_pos == -1) or (webserver_pos < port_pos):
            port = 80
            webserver = temp_url[:webserver_pos]
        else:
            port = temp_url[port_pos+1: webserver_pos]
            webserver = temp_url[:port_pos]
        
        return int(port), webserver.strip()


    def set_backlog(self, backlog: int):
        """Change the number of clients to be queued"""

        if not backlog:
            raise ValueError("Invalid backlog value")
        self._backlog = backlog



    