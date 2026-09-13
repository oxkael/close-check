from __future__ import annotations

from closewatch.database import Database
from closewatch.ingestion import get_ticker_catalog

try:
    import yfinance as yf
except ImportError as exc:  # pragma: no cover - only for local script use
    raise SystemExit("yfinance is required to ingest real closes. Install the project dependencies first.") from exc


def main() -> None:
    db = Database()
    db.init_db()

    for token_symbol, config in get_ticker_catalog().items():
        ticker = yf.Ticker(config["base_symbol"])
        history = ticker.history(period="3mo", interval="1d")
        for timestamp, row in history.iterrows():
            db.insert_real_close(config["base_symbol"], timestamp.strftime("%Y-%m-%d"), float(row["Close"]))

    print("Real close ingestion complete.")


if __name__ == "__main__":
    main()
