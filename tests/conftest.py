from unittest.mock import patch, MagicMock
import pytest


@pytest.fixture
def mock_socket_instance():
    mock_socket_instance = MagicMock()
    mock_socket_instance.recv.return_value = b'Reponse'

    with patch("src.connection.socket.socket") as mock_socket:
        mock_socket.return_value = mock_socket_instance
        yield mock_socket_instance