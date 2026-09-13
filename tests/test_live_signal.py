import unittest

from closewatch.signal import current_gap_signal


class LiveSignalTests(unittest.TestCase):
    def test_current_gap_signal_builds_expected_payload(self):
        payload = current_gap_signal(
            symbol="TSLAx",
            last_real_close=100.0,
            token_price=104.0,
            exchange="NASDAQ",
            market_closed=True,
        )

        self.assertEqual(payload["symbol"], "TSLAx")
        self.assertAlmostEqual(payload["gap_pct"], 4.0)
        self.assertTrue(payload["market_closed"])
        self.assertIn("bucket", payload)


if __name__ == "__main__":
    unittest.main()
