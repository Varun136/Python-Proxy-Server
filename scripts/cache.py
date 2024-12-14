"""
Script purpose:
    Check the cache values from redis to validate if load balancer
    is using the cached value and for future cache testing.
"""

import redis
from src.config import CACHE_HOST, CACHE_PORT

redis_client = redis.Redis(host=CACHE_HOST, port=CACHE_PORT, db=0)


test_host = "127.0.0.1"
test_port = 47952
redis_key = f"{test_host}:{test_port}"
redis_result = redis_client.get(redis_key)

print(redis_result)