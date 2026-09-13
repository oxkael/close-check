import unittest
from datetime import datetime

from closewatch.market_calendar import is_market_closed


class MarketCalendarTests(unittest.TestCase):
    def test_weekday_during_market_hours_is_open(self):
        timestamp = datetime(2026, 9, 14, 14, 30)
        self.assertFalse(is_market_closed("NASDAQ", timestamp))

    def test_weekday_after_hours_is_closed(self):
        timestamp = datetime(2026, 9, 14, 18, 0)
        self.assertTrue(is_market_closed("NASDAQ", timestamp))

    def test_weekend_is_closed(self):
        timestamp = datetime(2026, 9, 12, 12, 0)
        self.assertTrue(is_market_closed("NASDAQ", timestamp))

    def test_market_holiday_is_closed(self):
        timestamp = datetime(2026, 11, 26, 12, 0)
        self.assertTrue(is_market_closed("NASDAQ", timestamp))


if __name__ == "__main__":
    unittest.main()
