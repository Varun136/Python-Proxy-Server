from src.load_balancer import LoadBalancer
from src.constants import LoadBalancingAlgorithms
import pytest
from unittest.mock import patch, Mock, MagicMock
import time

@pytest.fixture
def load_balancer():
    servers = [("127.0.0.1", 8001), ("127.0.0.1", 8002)]
    llb = LoadBalancer(servers)
    return llb


def test_load_balancer_init():
    servers = [("127.0.0.1", 8001), ("127.0.0.1", 8002)]
    llb = LoadBalancer(servers)
    
    assert len(llb._servers) == len(servers)
    assert llb._algorithm == LoadBalancingAlgorithms.RR


@patch("socket.create_connection")
def test_add_server(mock_socket):
    mock_socket.return_value = MagicMock()

    llb = LoadBalancer([])
    test_server = ("127.0.0.1", 8002)
    llb.add_server(test_server)

    assert llb._servers[test_server]
    assert test_server in llb._servers


def test_remove_server():
    test_server = ("127.0.0.1", 8002)
    llb = LoadBalancer([])

    assert not llb.add_server(test_server)
    assert test_server not in llb._servers


def test_remove_server():
    servers = [("127.0.0.1", 8001), ("127.0.0.1", 8002)]
    test_server = ("127.0.0.1", 8001)
    llb = LoadBalancer(servers)

    assert llb.remove_server(test_server)
    assert test_server not in llb._servers


def test_remove_server_failure():
    servers = [("127.0.0.1", 8001), ("127.0.0.1", 8002)]
    test_server = ("127.0.0.1", 8003)
    llb = LoadBalancer(servers)

    assert not llb.remove_server(test_server)


def test_set_algorithm(load_balancer):
    assert load_balancer._algorithm == LoadBalancingAlgorithms.RR

    load_balancer.set_algorithm(LoadBalancingAlgorithms.IPH)
    assert load_balancer._algorithm == LoadBalancingAlgorithms.IPH


@patch('socket.create_connection', side_effect=[None, Exception])
def test_health_check(mock_socket, load_balancer):
    lb = load_balancer

    assert lb._servers[("127.0.0.1", 8001)] == True
    assert lb._servers[("127.0.0.1", 8002)] == True

def test_suspend_health_check():
    servers = [("127.0.0.1", 8000), ("127.0.0.2", 8000)]
    lb = LoadBalancer(servers)

    lb.suspend_health_check()
    assert not lb._check_health

