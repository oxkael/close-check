from __future__ import annotations

import math
from collections import defaultdict


def bucket_gap(gap_pct: float, width: float = 2.0) -> str:
    """Group a gap percentage into a band sized by width, like 2.0%-4.0%."""
    bucket_start = math.floor(gap_pct / width) * width
    bucket_end = bucket_start + width
    return f"{bucket_start:.1f}%-{bucket_end:.1f}%"


def build_calibration_buckets(observations: list[dict], width: float = 2.0) -> list[dict]:
    """Aggregate historical gap observations into calibration buckets.

    Each observation is expected to include:
    - gap_pct: float
    - converged: bool
    - hours_to_converge: optional float
    - worst_case_gap_pct: float or None
    """
    grouped: dict[str, list[dict]] = defaultdict(list)
    for observation in observations:
        grouped[bucket_gap(float(observation["gap_pct"]),
                           width=width)].append(observation)

    result: list[dict] = []
    for key in sorted(grouped, key=lambda label: float(label.split("%")[0])):
        items = grouped[key]
        sample_size = len(items)
        converged_items = [
            item for item in items if bool(item.get("converged"))]
        converged_count = len(converged_items)
        converged_times = [
            float(item["hours_to_converge"])
            for item in converged_items
            if item.get("hours_to_converge") is not None
        ]
        worst_case_gap = min(
            [float(item.get("worst_case_gap_pct", 0.0)) for item in items],
            default=0.0,
        )

        result.append(
            {
                "bucket": key,
                "sample_size": sample_size,
                "convergence_rate": (converged_count / sample_size) if sample_size else 0.0,
                "avg_time_to_converge_hours": (
                    sum(converged_times) /
                    len(converged_times) if converged_times else None
                ),
                "worst_case_gap_pct": worst_case_gap,
            }
        )

    return result
