import socket


SERVER_BACKLOG = 10


class Server(socket.socket):
    def __init__(self, address, port):

        assert isinstance(address, str), f"address should be of type 'str', got {type(address)}"
        assert isinstance(port, int), f"port should be of type 'int', got {type(port)}"

        super().__init__(socket.AF_INET, socket.SOCK_STREAM)

        self._address = address
        self._port = port
        self._backlog = SERVER_BACKLOG

        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.bind((self._address, self._port))

    
    def start_server(self):

        self.listen(self._backlog)
        print("Info: Server listening at port: %s", self._port)
    

    def close_server(self):
        
        self.shutdown()
        print("Info: Closing server gracefully.")
    

    def forward(self, data):
        self.sendall(data)