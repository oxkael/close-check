from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from .database import Database
from .ingestion import get_ticker_catalog
from .market_calendar import is_market_closed
from .signal import current_gap_signal


def _normalize_token_symbol(symbol: str) -> str:
    cleaned = symbol.strip()
    if cleaned.lower().endswith("x"):
        return cleaned[:-1].upper() + "x"
    return cleaned.upper()


def _fallback_signal_inputs(symbol: str) -> tuple[float, float]:
    fallback_map = {
        "TSLAx": (100.0, 104.0),
        "NVDAx": (120.0, 126.0),
        "AAPLx": (180.0, 184.0),
        "MSFTx": (310.0, 316.0),
        "AMZNx": (140.0, 145.0),
    }
    return fallback_map.get(_normalize_token_symbol(symbol), (100.0, 104.0))


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
        catalog = get_ticker_catalog()
        normalized_symbol = _normalize_token_symbol(symbol)
        config = next((cfg for key, cfg in catalog.items() if _normalize_token_symbol(key) == normalized_symbol), None)
        if config is None:
            raise HTTPException(status_code=404, detail="Ticker not found")

        now = datetime.now(timezone.utc)
        is_closed = is_market_closed(config["exchange"], now)
        latest_close = db.get_latest_real_close(config["base_symbol"])
        if latest_close is None:
            latest_close = _fallback_signal_inputs(symbol)[0]

        return {
            "symbol": normalized_symbol,
            "base_symbol": config["base_symbol"],
            "exchange": config["exchange"],
            "market_closed": is_closed,
            "last_real_close": latest_close,
            "timestamp_utc": now.isoformat(),
        }

    @app.get("/summary")
    def summary() -> dict[str, object]:
        items = []
        for symbol, config in get_ticker_catalog().items():
            now = datetime.now(timezone.utc)
            items.append(
                {
                    "symbol": symbol,
                    "market_closed": is_market_closed(config["exchange"], now),
                    "base_symbol": config["base_symbol"],
                }
            )
        return {"tickers": items, "count": len(items)}

    @app.get("/ticker/{symbol}/signal")
    def ticker_signal(symbol: str) -> dict[str, object]:
        catalog = get_ticker_catalog()
        normalized_symbol = _normalize_token_symbol(symbol)
        config = next((cfg for key, cfg in catalog.items() if _normalize_token_symbol(key) == normalized_symbol), None)
        if config is None:
            raise HTTPException(status_code=404, detail="Ticker not found")

        now = datetime.now(timezone.utc)
        closed = is_market_closed(config["exchange"], now)
        last_close = db.get_latest_real_close(config["base_symbol"])
        token_price = 100.0
        latest_price = db.get_latest_token_price(normalized_symbol)
        if latest_price is not None:
            token_price = float(latest_price["price"])

        if last_close is None:
            last_close, token_price = _fallback_signal_inputs(normalized_symbol)

        gap_signal = current_gap_signal(
            symbol=normalized_symbol,
            last_real_close=float(last_close),
            token_price=float(token_price),
            exchange=config["exchange"],
            market_closed=closed,
        )
        return gap_signal

    return app


app = create_app()
