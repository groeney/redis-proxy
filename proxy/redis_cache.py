from cachetools import TTLCache
from threading import RLock
from typing import Any, Hashable
from redis import Redis, ConnectionPool, Connection


class RedisCache(TTLCache):
    def __init__(self, redis_host: str, redis_port: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.redis = Redis(host=redis_host, port=redis_port)

    def __missing__(self, key: Hashable) -> Any:
        """ If key does not exist in cache get it and add to cache
        If key not in backing redis instance do nothing
        """
        value = self.redis.get(key)
        if value is None:
            return

        self[key] = value
        return value
