import unittest

from closewatch.calibration import build_calibration_buckets, bucket_gap


class CalibrationTests(unittest.TestCase):
    def test_bucket_gap_groups_by_percent_band(self):
        self.assertEqual(bucket_gap(3.2, width=2.0), "2.0%-4.0%")
        self.assertEqual(bucket_gap(-2.1, width=2.0), "-4.0%--2.0%")

    def test_build_calibration_buckets_computes_stats(self):
        observations = [
            {"gap_pct": 1.5, "converged": True, "hours_to_converge": 4, "worst_case_gap_pct": -2.0},
            {"gap_pct": 1.8, "converged": False, "hours_to_converge": None, "worst_case_gap_pct": -3.0},
            {"gap_pct": 3.2, "converged": True, "hours_to_converge": 8, "worst_case_gap_pct": -5.0},
            {"gap_pct": 3.1, "converged": True, "hours_to_converge": 6, "worst_case_gap_pct": -4.0},
        ]

        buckets = build_calibration_buckets(observations)
        self.assertTrue(len(buckets) >= 2)
        self.assertGreater(buckets[0]["convergence_rate"], 0)
        self.assertGreaterEqual(buckets[0]["sample_size"], 1)


if __name__ == "__main__":
    unittest.main()
