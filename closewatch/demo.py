from __future__ import annotations

from .database import Database
from .signal import current_gap_signal


def demo_signal_view() -> dict:
    db = Database(":memory:")
    try:
        db.init_db()

        db.insert_real_close("TSLA", "2026-09-11", 100.0)
        db.insert_token_price("TSLAx", "2026-09-12T12:00:00Z", 104.0)

        last_close = db.get_latest_real_close("TSLA")
        token_price = db.get_latest_token_price("TSLAx")
        if last_close is None or token_price is None:
            raise ValueError("Demo dataset is incomplete.")

        signal = current_gap_signal(
            symbol="TSLAx",
            last_real_close=float(last_close),
            token_price=float(token_price["price"]),
            exchange="NASDAQ",
            market_closed=True,
        )

        return {
            "headline": "Weekend closure gap on TSLAx",
            "signal": signal,
            "accuracy_summary": {
                "resolved_predictions": 1,
                "converged": 1,
                "accuracy_pct": 100.0,
            },
        }
    finally:
        db.close()
