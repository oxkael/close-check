import unittest

from fastapi.testclient import TestClient

from closewatch.api import app


class CalibrationApiTests(unittest.TestCase):
    def test_calibration_and_accuracy_endpoints_expose_bucket_stats(self):
        client = TestClient(app)

        calibration_response = client.get("/ticker/TSLAx/calibration")
        self.assertEqual(calibration_response.status_code, 200)
        payload = calibration_response.json()
        self.assertIn("symbol", payload)
        self.assertIn("buckets", payload)

        accuracy_response = client.get("/accuracy/summary")
        self.assertEqual(accuracy_response.status_code, 200)
        summary = accuracy_response.json()
        self.assertIn("resolved_predictions", summary)
        self.assertIn("accuracy_pct", summary)


if __name__ == "__main__":
    unittest.main()
