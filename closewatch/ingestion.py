from __future__ import annotations

from typing import Callable, Iterable

from .database import Database

TICKER_CATALOG = {
    "TSLAx": {"base_symbol": "TSLA", "exchange": "NASDAQ"},
    "NVDAx": {"base_symbol": "NVDA", "exchange": "NASDAQ"},
    "AAPLx": {"base_symbol": "AAPL", "exchange": "NASDAQ"},
    "MSFTx": {"base_symbol": "MSFT", "exchange": "NASDAQ"},
    "AMZNx": {"base_symbol": "AMZN", "exchange": "NASDAQ"},
}


def get_ticker_catalog() -> dict[str, dict[str, str]]:
    return TICKER_CATALOG.copy()


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
        config = catalog.get(token_symbol)
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
