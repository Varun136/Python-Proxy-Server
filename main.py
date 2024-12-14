"""
A proxy server requires :-
  :PROXY_SERVER - a server address to bind its socket connectionn.
  :BACKEND_SERVERS - list of backend servers for load balancing.
"""

from src.proxy import ProxyServer
from src.config import BACKEND_SERVERS, PROXY_SERVER

proxy_server = ProxyServer(PROXY_SERVER, BACKEND_SERVERS)
proxy_server.start()
