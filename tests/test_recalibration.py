import unittest

from closewatch.database import Database


class RecalibrationTests(unittest.TestCase):
    def test_recompute_calibration_buckets_persists_stats(self):
        db = Database(":memory:")
        db.init_db()

        db.log_prediction(
            symbol="TSLAx",
            created_at="2026-09-12T10:00:00Z",
            status="resolved",
            gap_pct=4.0,
            resolved_at="2026-09-13T11:00:00Z",
            result="converged",
        )
        db.log_prediction(
            symbol="TSLAx",
            created_at="2026-09-11T10:00:00Z",
            status="resolved",
            gap_pct=5.0,
            resolved_at="2026-09-12T09:00:00Z",
            result="failed",
        )

        buckets = db.recompute_calibration_buckets(symbol="TSLAx", width=2.0)

        self.assertTrue(buckets)
        self.assertEqual(buckets[0]["sample_size"], 2)
        self.assertGreaterEqual(buckets[0]["convergence_rate"], 0.0)
        row = db.get_calibration_buckets(symbol="TSLAx")
        self.assertTrue(row)


if __name__ == "__main__":
    unittest.main()
