from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from .database import Database
from .ingestion import canonicalize_ticker_symbol, get_ticker_catalog
from .market_calendar import is_market_closed
from .signal import current_gap_signal


def _normalize_token_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper().replace(" ", "")
    if cleaned.endswith("USDT"):
        cleaned = cleaned[:-4]
    if cleaned.startswith("R") and len(cleaned) > 1:
        cleaned = cleaned[1:]
    if cleaned.endswith("X"):
        return cleaned[:-1] + "x"
    if cleaned in {"TSLA", "NVDA", "AAPL", "MSFT", "AMZN"}:
        return f"{cleaned}x"
    return cleaned


def _lookup_ticker_config(symbol: str) -> tuple[str | None, dict[str, str] | None]:
    catalog = get_ticker_catalog()
    normalized_symbol = _normalize_token_symbol(symbol)
    for key, config in catalog.items():
        if _normalize_token_symbol(key) == normalized_symbol:
            return key, config
    return None, None


def _fallback_signal_inputs(symbol: str) -> tuple[float, float]:
    normalized = _normalize_token_symbol(symbol)
    fallback_map = {
        "TSLAx": (100.0, 104.0),
        "NVDAx": (120.0, 126.0),
        "AAPLx": (180.0, 184.0),
        "MSFTx": (310.0, 316.0),
        "AMZNx": (140.0, 145.0),
        "rTSLA": (100.0, 104.0),
        "rNVDA": (120.0, 126.0),
        "rAAPL": (180.0, 184.0),
        "rMSFT": (310.0, 316.0),
        "rAMZN": (140.0, 145.0),
    }
    return fallback_map.get(normalized, (100.0, 104.0))


def create_app() -> FastAPI:
    app = FastAPI(title="CloseWatch API", version="0.1.0")
    db = Database("closewatch.db")
    db.init_db()

    @app.on_event("shutdown")
    def shutdown_db() -> None:
        db.close()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/tickers")
    def tickers() -> dict[str, list[dict[str, str]]]:
        catalog = []
        for symbol, config in get_ticker_catalog().items():
            catalog.append(
                {"symbol": symbol, "base_symbol": config["base_symbol"], "exchange": config["exchange"]})
        return {"tickers": catalog}

    @app.get("/ticker/{symbol}/status")
    def ticker_status(symbol: str) -> dict[str, object]:
        config_key, config = _lookup_ticker_config(symbol)
        if config is None:
            raise HTTPException(status_code=404, detail="Ticker not found")

        now = datetime.now(timezone.utc)
        is_closed = is_market_closed(config["exchange"], now)
        latest_close = db.get_latest_real_close(config["base_symbol"])
        if latest_close is None:
            latest_close = _fallback_signal_inputs(symbol)[0]

        return {
            "symbol": config_key or symbol.strip() or _normalize_token_symbol(symbol),
            "base_symbol": config["base_symbol"],
            "exchange": config["exchange"],
            "market_closed": is_closed,
            "last_real_close": latest_close,
            "timestamp_utc": now.isoformat(),
        }

    @app.get("/summary")
    def summary() -> dict[str, object]:
        items = [ticker_signal(symbol) for symbol in get_ticker_catalog()]
        return {
            "tickers": items,
            "count": len(items),
            "accuracy_summary": db.get_accuracy_summary(),
        }

    @app.get("/accuracy/summary")
    def accuracy_summary() -> dict[str, object]:
        return db.get_accuracy_summary()

    @app.get("/ticker/{symbol}/calibration")
    def ticker_calibration(symbol: str, bucket: str | None = None) -> dict[str, object]:
        config_key, config = _lookup_ticker_config(symbol)
        if config is None:
            raise HTTPException(status_code=404, detail="Ticker not found")

        resolved_symbol = config_key or _normalize_token_symbol(symbol)
        buckets = db.get_bucket_stats(resolved_symbol, bucket=bucket)
        return {
            "symbol": resolved_symbol,
            "base_symbol": config["base_symbol"],
            "exchange": config["exchange"],
            "bucket": bucket,
            "buckets": buckets,
        }

    @app.post("/admin/recompute-calibration")
    def recompute_calibration() -> dict[str, object]:
        buckets = db.recompute_calibration_buckets()
        return {"updated": True, "buckets": buckets}

    @app.get("/ticker/{symbol}/signal")
    def ticker_signal(symbol: str) -> dict[str, object]:
        config_key, config = _lookup_ticker_config(symbol)
        if config is None:
            raise HTTPException(status_code=404, detail="Ticker not found")

        resolved_symbol = config_key or _normalize_token_symbol(symbol)
        display_symbol = symbol.strip() if symbol.strip() else resolved_symbol

        now = datetime.now(timezone.utc)
        closed = is_market_closed(config["exchange"], now)
        last_close = db.get_latest_real_close(config["base_symbol"])
        token_price = 100.0
        latest_price = db.get_latest_token_price(resolved_symbol)
        if latest_price is not None:
            token_price = float(latest_price["price"])

        if last_close is None:
            last_close, token_price = _fallback_signal_inputs(display_symbol)

        gap_signal = current_gap_signal(
            symbol=display_symbol,
            last_real_close=float(last_close),
            token_price=float(token_price),
            exchange=config["exchange"],
            market_closed=closed,
        )
        if not closed:
            db.resolve_pending_predictions(
                symbol=resolved_symbol,
                last_real_close=float(last_close),
                reopen_price=float(token_price),
                resolved_at=now.isoformat(),
            )

        db.log_prediction(
            symbol=resolved_symbol,
            created_at=now.isoformat(),
            status="pending",
            gap_pct=float(gap_signal["gap_pct"]),
        )
        bucket_stats = db.get_bucket_stats(
            resolved_symbol, gap_signal["bucket"])
        gap_signal["bucket_stats"] = bucket_stats[0] if bucket_stats else {
            "bucket": gap_signal["bucket"],
            "symbol": resolved_symbol,
            "sample_size": 0,
            "convergence_rate": 0.0,
            "avg_time_to_converge_hours": None,
            "worst_case_gap_pct": None,
            "last_updated": None,
        }
        gap_signal["accuracy_summary"] = db.get_accuracy_summary(
            resolved_symbol)
        return gap_signal

    return app


app = create_app()
