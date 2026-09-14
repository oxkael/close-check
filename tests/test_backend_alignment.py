import unittest
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from closewatch.api import create_app
from closewatch.market_calendar import is_market_closed


class BackendAlignmentTests(unittest.TestCase):
    def test_market_closed_uses_exchange_local_time(self):
        # 2026-09-14 is a Monday; 9:30 ET is open, 13:30 UTC is 9:30 ET.
        open_time = datetime(2026, 9, 14, 13, 30, tzinfo=timezone.utc)
        self.assertFalse(is_market_closed("NASDAQ", open_time))

        # 16:00 ET is close boundary; 20:00 UTC is 16:00 ET.
        close_time = datetime(2026, 9, 14, 20, 0, tzinfo=timezone.utc)
        self.assertTrue(is_market_closed("NASDAQ", close_time))

    def test_r_token_alias_is_accepted(self):
        client = TestClient(create_app())

        response = client.get("/ticker/rTSLA/signal")
        self.assertEqual(response.status_code, 200)
        self.assertIn("symbol", response.json())


if __name__ == "__main__":
    unittest.main()
