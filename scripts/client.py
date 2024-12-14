"""
Script purpose:
    Mocks a browser client that connect to the proxy socket
    and send requests.
"""

import socket
from scripts.data import GET_REQUEST
from src.config import PROXY_SERVER, BUFFER_SIZE

# Temp ip and port for the client.
client_host = "127.0.0.1"
client_ip = 47951
client_addr = (client_host, client_ip)

client_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_conn.bind(client_addr)
client_conn.connect(PROXY_SERVER)
client_conn.send(GET_REQUEST.encode())
response = client_conn.recv(BUFFER_SIZE)
print(response.decode("ascii"))
client_conn.close()
