from __future__ import annotations

from .calibration import bucket_gap
from .gap_logic import calculate_gap_pct


def current_gap_signal(
    symbol: str,
    last_real_close: float,
    token_price: float,
    exchange: str,
    market_closed: bool,
    bucket_width: float = 2.0,
) -> dict:
    gap_value = calculate_gap_pct(last_real_close, token_price)
    bucket = bucket_gap(gap_value, width=bucket_width)

    return {
        "symbol": symbol,
        "exchange": exchange,
        "market_closed": market_closed,
        "last_real_close": float(last_real_close),
        "token_price": float(token_price),
        "gap_pct": float(gap_value),
        "bucket": bucket,
    }
