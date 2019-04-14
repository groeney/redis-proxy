from os import environ
from unittest import TestCase
from e2e_engine import E2eEngine
from time import monotonic, sleep
import logging

TTL = int(environ.get("CACHE_TTL", 3600))
MAXSIZE = int(environ.get("CACHE_MAXSIZE", 1024))
LOGGER = logging.getLogger(__name__)


class CacheTestCase(TestCase):
    def setUp(self):
        self.e2e_engine = E2eEngine()
        self.e2e_engine.set("foo", "bar")
        for i in range(MAXSIZE):
            self.e2e_engine.set(str(i), i)

    def test_ttl_recache(self):
        key = value = "1"
        self.e2e_engine.get(key)  # Put in cache
        last_set = monotonic()

        while last_set + TTL > monotonic():
            LOGGER.warning(
                f"Waiting for cache to expire -- TTL: {TTL}s. Consider setting it lower for testing!"
            )
            sleep(1)

        resp = self.e2e_engine.get(key)
        self.assertEqual(resp.text, value)
        self.assertEqual(resp.status_code, 200)

    def test_ttl_delete(self):
        key = value = "0"
        resp = self.e2e_engine.get(key)  # Put in cache
        self.assertEqual(resp.text, value)
        self.assertEqual(resp.status_code, 200)

        self.e2e_engine.delete(key)
        last_set = monotonic()

        while last_set + TTL > monotonic():
            LOGGER.warning(
                f"Waiting for cache to expire -- TTL: {TTL}s. Consider setting it lower for testing!"
            )
            resp = self.e2e_engine.get(key)
            self.assertEqual(resp.text, value)
            self.assertEqual(resp.status_code, 200)
            sleep(1)

        resp = self.e2e_engine.get(key)
        self.assertEqual(resp.status_code, 404)

    def test_lru_evict(self):
        key = "0"
        for i in range(MAXSIZE):  # Fill cache
            self.e2e_engine.get(str(i))

        # Delete key from redis
        self.e2e_engine.delete(key)

        # Evict key from cache
        self.e2e_engine.set(str(MAXSIZE), MAXSIZE)
        self.e2e_engine.get(str(MAXSIZE))

        resp = self.e2e_engine.get(key)
        self.assertEqual(resp.status_code, 404)

    def test_use_cache(self):
        self.e2e_engine.get("foo")  # Inserts "foo" into cache
        self.e2e_engine.delete("foo")  # Deletes "foo" from backing instance

        resp = self.e2e_engine.get("foo")
        self.assertEqual(resp.text, "bar")
        self.assertEqual(resp.status_code, 200)
