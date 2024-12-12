import redis

CONNECTION_POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)


# Proxy config.
PROXY_SERVER_PORT = 8000
PROXY_SERVER_ADDRESS = "127.0.0.1"
PROXY_SERVER = (PROXY_SERVER_ADDRESS, PROXY_SERVER_PORT)
BUFFER_SIZE = 4096


BACKEND_SERVERS = [
    ("127.0.0.1", 8000),
    ("127.0.0.2", 8000),
    ("127.0.0.3", 8000),
    ("127.0.0.4", 8000),
]

SERVER_BACKLOG = 10