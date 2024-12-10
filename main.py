from proxy import ProxyServer

PORT = 8000
ADDRESS = "127.0.0.1"
server_addr = (ADDRESS, PORT)
import socket

connection = socket.create_connection(server_addr)
print("hi") 
proxy_server = ProxyServer(server_addr)
proxy_server.start()