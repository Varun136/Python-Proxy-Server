"""
Script purpose:
    Mock backend servers which gives reponse regardless of the request.
    Can also be used to check the health checking property of the load balancers.
"""

import json
import sys
from src.config import BACKEND_SERVERS, BUFFER_SIZE
from src.connection import Connection
import signal

# Choose a server to be heathy.
temp_server = BACKEND_SERVERS[0]
connection = Connection(temp_server)
connection.start()

# Close the connection on stoping the terminal.
def shutdown(signum, frame):
    connection.close()
    print("Gracefully closing server.")
    sys.exit(0)
signal.signal(signal.SIGINT, shutdown)

temp_response = json.dumps({"status code": 200})
# Receive request and provide response like a backend server.
while True:
    proxy_conn, proxy_addr = connection.accept()
    if proxy_conn:
        request = proxy_conn.recv(BUFFER_SIZE)
        print("--------------------------")
        print("request: ", request.decode("ascii"))
        print("--------------------------")
        proxy_conn.sendall(temp_response.encode())
    


