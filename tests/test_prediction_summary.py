import unittest

from closewatch.database import Database


class PredictionSummaryTests(unittest.TestCase):
    def test_accuracy_summary_tracks_resolved_predictions(self):
        db = Database(":memory:")
        db.init_db()

        first_id = db.log_prediction(
            symbol="TSLAx",
            created_at="2026-09-12T10:00:00Z",
            status="pending",
            gap_pct=4.2,
        )
        second_id = db.log_prediction(
            symbol="TSLAx",
            created_at="2026-09-11T10:00:00Z",
            status="pending",
            gap_pct=2.1,
        )

        db.resolve_prediction(
            first_id, resolved_at="2026-09-13T10:00:00Z", result="converged")
        db.resolve_prediction(
            second_id, resolved_at="2026-09-13T11:00:00Z", result="failed")

        summary = db.get_accuracy_summary("TSLAx")
        self.assertEqual(summary["resolved_predictions"], 2)
        self.assertEqual(summary["converged"], 1)
        self.assertEqual(summary["accuracy_pct"], 50.0)


if __name__ == "__main__":
    unittest.main()
