from unittest import TestCase
from e2e_engine import E2eEngine


class WebServiceTestCase(TestCase):
    def setUp(self):
        self.e2e_engine = E2eEngine()
        self.e2e_engine.set("foo", "bar")

    def test_existing_key(self):
        resp = self.e2e_engine.get("foo")
        self.assertEqual(resp.text, "bar")
        self.assertEqual(resp.status_code, 200)

    def test_non_existing_key(self):
        resp = self.e2e_engine.get("bar")
        self.assertEqual(resp.status_code, 404)
