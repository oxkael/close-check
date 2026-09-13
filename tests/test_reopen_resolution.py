import unittest

from closewatch.database import Database


class ReopenResolutionTests(unittest.TestCase):
    def test_pending_predictions_resolve_when_reopen_narrows_gap(self):
        db = Database(":memory:")
        db.init_db()

        prediction_id = db.log_prediction(
            symbol="TSLAx",
            created_at="2026-09-12T10:00:00Z",
            status="pending",
            gap_pct=4.0,
        )

        db.resolve_pending_predictions(
            symbol="TSLAx",
            last_real_close=100.0,
            reopen_price=102.0,
            resolved_at="2026-09-13T10:00:00Z",
        )

        row = db.get_prediction(prediction_id)
        self.assertEqual(row["status"], "resolved")
        self.assertEqual(row["result"], "converged")


if __name__ == "__main__":
    unittest.main()
