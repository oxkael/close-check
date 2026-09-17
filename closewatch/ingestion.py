from __future__ import annotations

from typing import Callable, Iterable

from .database import Database

TICKER_CATALOG = {
    "rTSLA": {"base_symbol": "TSLA", "exchange": "NASDAQ", "bitget_symbol": "RTSLAUSDT"},
    "rNVDA": {"base_symbol": "NVDA", "exchange": "NASDAQ", "bitget_symbol": "RNVDAUSDT"},
    "rAAPL": {"base_symbol": "AAPL", "exchange": "NASDAQ", "bitget_symbol": "RAAPLUSDT"},
    "rMSFT": {"base_symbol": "MSFT", "exchange": "NASDAQ", "bitget_symbol": "RMSFTUSDT"},
    "rAMZN": {"base_symbol": "AMZN", "exchange": "NASDAQ", "bitget_symbol": "RAMZNUSDT"},
}


def canonicalize_ticker_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper().replace(" ", "")
    if cleaned.endswith("USDT"):
        cleaned = cleaned[:-4]
    if cleaned.startswith("R") and len(cleaned) > 1:
        cleaned = cleaned[1:]
    if cleaned.endswith("X"):
        cleaned = cleaned[:-1]
    return cleaned


def resolve_ticker_key(symbol: str) -> str:
    normalized = canonicalize_ticker_symbol(symbol)
    for key in TICKER_CATALOG:
        if canonicalize_ticker_symbol(key) == normalized:
            return key
    return symbol.strip()


def get_ticker_catalog() -> dict[str, dict[str, str]]:
    return TICKER_CATALOG.copy()


def ingest_token_prices_bitget(
    db: Database | None = None,
    symbols: Iterable[str] | None = None,
    limit: int = 200,
) -> dict[str, int]:
    """Fetch token candles from Bitget and persist latest prices into token_prices.

    Symbols should be provided in the rToken or legacy TSLAx form and mapped
    via the ticker catalog to Bitget symbol names.
    """
    if db is None:
        db = Database()
    db.init_db()

    if symbols is None:
        symbols = list(get_ticker_catalog().keys())

    from .bitget import fetch_candles

    summary: dict[str, int] = {}
    catalog = get_ticker_catalog()
    for token_symbol in symbols:
        token_key = resolve_ticker_key(token_symbol)
        config = catalog.get(token_key)
        if config is None:
            continue
        bitget_symbol = config.get("bitget_symbol")
        if not bitget_symbol:
            summary[token_symbol] = 0
            continue

        candles = fetch_candles(bitget_symbol, limit=limit)
        inserted = 0
        # Bitget returns arrays; the last available candle contains latest price
        for c in candles[:1]:
            try:
                # Some APIs return [ts, open, high, low, close, volume]
                close = float(c[4]) if isinstance(c, (list, tuple)) and len(c) > 4 else None
            except Exception:
                close = None
            if close is None:
                continue
            # Use current UTC timestamp for token price row
            import datetime

            ts = datetime.datetime.utcnow().isoformat() + "Z"
            db.insert_token_price(token_key, ts, float(close))
            inserted += 1

        summary[token_symbol] = inserted

    return summary


def ingest_recent_real_closes(
    db: Database | None = None,
    symbols: Iterable[str] | None = None,
    days: int = 90,
    fetcher: Callable[[str], object] | None = None,
) -> dict[str, int]:
    """Fetch recent daily closes for configured tickers and persist them to the database."""
    if db is None:
        db = Database()
    db.init_db()

    if symbols is None:
        symbols = list(get_ticker_catalog().keys())

    if fetcher is None:
        try:
            import yfinance as yf
        except ImportError as exc:  # pragma: no cover - local script use only
            raise RuntimeError(
                "yfinance is required to ingest real closes. Install the project dependencies first."
            ) from exc

        def fetcher(symbol: str) -> object:
            return yf.Ticker(symbol)

    summary: dict[str, int] = {}
    catalog = get_ticker_catalog()
    for token_symbol in symbols:
        token_key = resolve_ticker_key(token_symbol)
        config = catalog.get(token_key)
        if config is None:
            normalized = token_symbol.strip().upper()
            config = next((cfg for key, cfg in catalog.items()
                          if key.upper() == normalized), None)
        if config is None:
            raise ValueError(
                f"Unsupported ticker for ingestion: {token_symbol}")

        ticker = fetcher(config["base_symbol"])
        history = ticker.history(period=f"{days}d", interval="1d")
        inserted_count = 0
        for timestamp, row in history.iterrows():
            if isinstance(row, dict):
                close_price = row.get("Close")
            else:
                close_price = row["Close"]
            if close_price is None:
                continue

            close_date = timestamp.strftime(
                "%Y-%m-%d") if hasattr(timestamp, "strftime") else str(timestamp)[:10]
            db.insert_real_close(
                config["base_symbol"],
                close_date,
                float(close_price),
            )
            inserted_count += 1

        summary[token_symbol] = inserted_count

    return summary
