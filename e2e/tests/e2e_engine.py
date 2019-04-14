from os import environ
from redis import Redis
from typing import Any
import requests
from requests import Response

REDIS_CONFIG = {
    "host": environ.get("REDIS_HOST", "redis"),
    "port": int(environ.get("REDIS_PORT", 6379)),
}

PROXY_CONFIG = {
    "host": environ.get("PROXY_HOST", "proxy"),
    "port": int(environ.get("PROXY_PORT", 5000)),
}


class E2eEngine:
    def __init__(self, protocol: str = "http://"):
        self.protocol = protocol
        self._redis = self._create_redis()
        self._proxy_url = self._create_proxy_url()

    @property
    def redis(self) -> "Redis":
        if not hasattr(self, "_redis"):
            self._redis = _create_redis()
        return self._redis

    @property
    def proxy_url(self) -> str:
        if not hasattr(self, "_proxy_url"):
            self._proxy_url = create_proxy_url()
        return self._proxy_url

    def delete(self, key: str) -> None:
        self.redis.delete(key)

    def get(self, key: str) -> Any:
        return requests.get(f"{self.proxy_url}/get/{key}")

    def get_cache(self) -> Response:
        return requests.get(f"{self.proxy_url}/cache")

    def set(self, key: str, value: str) -> None:
        self.redis.set(key, value)

    def set_batch(self, keys: list, values: list) -> None:
        assert len(keys) == len(values)
        for key, value in zip(keys, values):
            self.set(key, value)

    def clear(self) -> None:
        self.clear_cache()
        self.flush_redis()

    def clear_cache(self) -> None:
        requests.delete(f"{self.proxy_url}/cache")

    def flush_redis(self) -> None:
        self.redis.flushdb()

    def _create_proxy_url(self) -> str:
        return f"{self.protocol}{PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}"

    def _create_redis(self) -> "Redis":
        redis = Redis(**REDIS_CONFIG)
        return redis
