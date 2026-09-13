from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, HTTPException

from .database import Database
from .ingestion import get_ticker_catalog
from .market_calendar import is_market_closed
from .signal import current_gap_signal


def create_app() -> FastAPI:
    app = FastAPI(title="CloseWatch API", version="0.1.0")
    db = Database("closewatch.db")
    db.init_db()

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
        config = catalog.get(symbol.upper())
        if config is None:
            raise HTTPException(status_code=404, detail="Ticker not found")

        now = datetime.utcnow()
        is_closed = is_market_closed(config["exchange"], now)
        latest_close = db.get_latest_real_close(config["base_symbol"])

        return {
            "symbol": symbol.upper(),
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
            now = datetime.utcnow()
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
        config = catalog.get(symbol.upper())
        if config is None:
            raise HTTPException(status_code=404, detail="Ticker not found")

        now = datetime.utcnow()
        closed = is_market_closed(config["exchange"], now)
        last_close = db.get_latest_real_close(config["base_symbol"])
        token_price = 100.0
        latest_price = db.get_latest_token_price(symbol.upper())
        if latest_price is not None:
            token_price = float(latest_price["price"])

        if last_close is None:
            raise HTTPException(status_code=404, detail="No real close data for ticker")

        gap_signal = current_gap_signal(
            symbol=symbol.upper(),
            last_real_close=float(last_close),
            token_price=float(token_price),
            exchange=config["exchange"],
            market_closed=closed,
        )
        return gap_signal

    return app


app = create_app()
