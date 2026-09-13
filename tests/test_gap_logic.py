import unittest

from closewatch.gap_logic import calculate_gap_pct, build_closure_windows


class GapLogicTests(unittest.TestCase):
    def test_build_closure_windows_returns_market_closed_periods(self):
        closes = [
            ("2026-09-11", 100.0),
            ("2026-09-12", 98.0),
            ("2026-09-13", 101.0),
        ]
        windows = build_closure_windows(closes)
        self.assertTrue(len(windows) >= 1)
        self.assertEqual(windows[0]["last_real_close"], 100.0)

    def test_calculate_gap_pct_uses_close_vs_token_price(self):
        gap = calculate_gap_pct(100.0, 104.0)
        self.assertAlmostEqual(gap, 4.0)


if __name__ == "__main__":
    unittest.main()
