""" Gunicorn WSGI server config """
from os import environ
import multiprocessing as mp


def max_threads():
    return 2 * mp.cpu_count()


reload = True
bind = "0.0.0.0:" + environ.get("PROXY_PORT", "5000")
threads = min(max_threads(), int(environ.get("MAX_PARALLEL", 1)))
backlog = int(environ.get("MAX_CONNECTIONS", 2048))
worker_class = "gthread"
