from proxy import ProxyServer

PORT = 8000
ADDRESS = "127.0.0.1"

proxy_server = ProxyServer(PORT, ADDRESS)
proxy_server.start()