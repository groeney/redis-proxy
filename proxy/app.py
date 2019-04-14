from os import environ
from threading import RLock
from flask import Flask, Response, g, request
from cachetools import cached, TTLCache
from redis_cache import RedisCache
from redis import Redis

application = Flask(__name__)
application.config.update(
    dict(
        redis_host=environ.get("REDIS_HOST", "redis"),
        redis_port=int(environ.get("REDIS_PORT", 6379)),
        maxsize=int(environ.get("CACHE_MAXSIZE", 1024)),
        ttl=int(environ.get("CACHE_TTL", 3600)),
    )
)


def create_cache():
    cache_config_keys = ["redis_host", "redis_port", "maxsize", "ttl"]
    return RedisCache(**{k: application.config[k] for k in cache_config_keys})


redis_cache = create_cache()
cache_lock = RLock()


@application.route("/get/<key>")
def get(key):
    with cache_lock:
        value = redis_cache[key]
    resp_val, resp_status = (
        (f"Key '{key}' not found!", 404) if value is None else (value, 200)
    )
    resp = Response(response=resp_val, status=resp_status)
    return resp


@application.route("/cache", methods=["GET", "DELETE"])
def delete_cache():
    resp_val = f"{redis_cache}"
    if request.method == "DELETE":
        with cache_lock:
            redis_cache.clear()
        resp_val = "Cache cleared!\n\n" + resp_val

    return Response(f"{resp_val}")
