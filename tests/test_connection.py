import pytest
from src.connection import Connection

class TestConnection:
    
    def setup_method(self, method):
        self.ip = '0.0.0.0'
        self.port = 8000
        self.addr = (self.ip, self.port)
    
    def test_connection_success(self, mock_socket_instance):
        connection = Connection(self.addr)

        assert connection._ip == self.ip
        assert connection._port == self.port
        assert connection._addr == self.addr
        assert connection._backlog > 0
        assert connection.is_alive
    
    def test_connection_failure(self):
        invalid_addr = ('0.1.2.3', 1234)
        with pytest.raises(ValueError):
            connection = Connection(invalid_addr)
