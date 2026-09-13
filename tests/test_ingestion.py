import unittest

from closewatch.database import Database
from closewatch.ingestion import ingest_recent_real_closes


class FakeRow(dict):
    pass


class FakeHistory:
    def __init__(self, rows):
        self._rows = rows

    def iterrows(self):
        return iter(self._rows)


class FakeTicker:
    def __init__(self, symbol):
        self.symbol = symbol

    def history(self, period, interval):
        return FakeHistory([
            ("2026-09-01", FakeRow({"Close": 100.0})),
            ("2026-09-02", FakeRow({"Close": 101.5})),
        ])


class IngestionTests(unittest.TestCase):
    def test_ingest_recent_real_closes_persists_history(self):
        db = Database(":memory:")
        db.init_db()

        summary = ingest_recent_real_closes(
            db=db,
            symbols=["TSLAx"],
            fetcher=lambda symbol: FakeTicker(symbol),
        )

        self.assertEqual(summary["TSLAx"], 2)
        self.assertEqual(db.get_latest_real_close("TSLA"), 101.5)


if __name__ == "__main__":
    unittest.main()
