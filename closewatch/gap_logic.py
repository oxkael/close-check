from __future__ import annotations

from datetime import datetime

from .market_calendar import is_market_closed


def build_closure_windows(real_closes: list[tuple[str, float]], exchange: str = "NASDAQ") -> list[dict[str, float | str]]:
    """Create closure windows from a sequence of daily real closes.

    A closure window is created when the next trading day is separated by a weekend,
    a holiday, or when the date itself is a market closure date. The window stores the
    last real close before the closure and the next available market reopen value.
    """
    if not real_closes:
        return []

    sorted_closes = sorted(real_closes, key=lambda item: item[0])
    windows: list[dict[str, float | str]] = []

    for index in range(len(sorted_closes) - 1):
        prev_day, prev_close = sorted_closes[index]
        next_day, next_close = sorted_closes[index + 1]

        prev_dt = datetime.fromisoformat(f"{prev_day}T12:00:00")
        next_dt = datetime.fromisoformat(f"{next_day}T12:00:00")

        is_closed_gap = (
            is_market_closed(exchange, prev_dt)
            or is_market_closed(exchange, next_dt)
            or (next_dt.date() - prev_dt.date()).days > 1
        )

        if is_closed_gap:
            windows.append(
                {
                    "window_start": prev_day,
                    "window_end": next_day,
                    "last_real_close": float(prev_close),
                    "reopen_price": float(next_close),
                }
            )

    return windows


def calculate_gap_pct(last_real_close: float, token_price: float) -> float:
    if last_real_close == 0:
        return 0.0
    return ((token_price - last_real_close) / last_real_close) * 100.0
