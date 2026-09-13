import unittest

from fastapi.testclient import TestClient

from closewatch.api import app


class ApiTests(unittest.TestCase):
    def test_health_and_signal_endpoints(self):
        client = TestClient(app)

        health = client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")

        signal = client.get("/ticker/TSLAx/signal")
        self.assertEqual(signal.status_code, 200)
        self.assertEqual(signal.json()["symbol"], "TSLAx")
        self.assertIn("gap_pct", signal.json())


if __name__ == "__main__":
    unittest.main()
