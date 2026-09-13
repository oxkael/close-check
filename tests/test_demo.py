import unittest

from closewatch.demo import demo_signal_view


class DemoTests(unittest.TestCase):
    def test_demo_signal_view_includes_summary(self):
        payload = demo_signal_view()
        self.assertEqual(payload["headline"], "Weekend closure gap on TSLAx")
        self.assertIn("signal", payload)
        self.assertIn("accuracy_summary", payload)
        self.assertGreater(payload["signal"]["gap_pct"], 0)


if __name__ == "__main__":
    unittest.main()
