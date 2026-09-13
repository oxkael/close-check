import unittest

from closewatch.database import Database


class PredictionLogTests(unittest.TestCase):
    def test_prediction_can_be_logged_and_resolved(self):
        db = Database(":memory:")
        db.init_db()

        prediction_id = db.log_prediction(
            symbol="TSLAx",
            created_at="2026-09-12T10:00:00Z",
            status="pending",
            gap_pct=4.2,
        )

        db.resolve_prediction(
            prediction_id,
            resolved_at="2026-09-13T10:00:00Z",
            result="converged",
        )

        row = db.get_prediction(prediction_id)
        self.assertEqual(row["status"], "resolved")
        self.assertEqual(row["result"], "converged")


if __name__ == "__main__":
    unittest.main()
