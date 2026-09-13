import unittest

from closewatch.database import Database


class DatabaseTests(unittest.TestCase):
    def test_database_creates_schema_and_stores_prices(self):
        db = Database(":memory:")
        db.init_db()
        db.insert_real_close("TSLA", "2026-09-12", 232.15)

        latest = db.get_latest_real_close("TSLA")
        self.assertEqual(latest, 232.15)

    def test_database_tracks_token_price_rows(self):
        db = Database(":memory:")
        db.init_db()
        db.insert_token_price("TSLAx", "2026-09-12T12:00:00Z", 236.5)

        row = db.get_latest_token_price("TSLAx")
        self.assertEqual(row["price"], 236.5)


if __name__ == "__main__":
    unittest.main()
