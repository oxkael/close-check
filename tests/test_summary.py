import unittest

from fastapi.testclient import TestClient

from closewatch.api import app


class SummaryApiTests(unittest.TestCase):
    def test_summary_includes_signal_fields(self):
        client = TestClient(app)

        response = client.get("/summary")
        self.assertEqual(response.status_code, 200)

        tickers = response.json()["tickers"]
        self.assertTrue(tickers)
        first = tickers[0]
        self.assertIn("gap_pct", first)
        self.assertIn("bucket", first)
        self.assertIn("accuracy_summary", first)


if __name__ == "__main__":
    unittest.main()
