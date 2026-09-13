from __future__ import annotations

TICKER_CATALOG = {
    "TSLAx": {"base_symbol": "TSLA", "exchange": "NASDAQ"},
    "NVDAx": {"base_symbol": "NVDA", "exchange": "NASDAQ"},
    "AAPLx": {"base_symbol": "AAPL", "exchange": "NASDAQ"},
    "MSFTx": {"base_symbol": "MSFT", "exchange": "NASDAQ"},
    "AMZNx": {"base_symbol": "AMZN", "exchange": "NASDAQ"},
}


def get_ticker_catalog() -> dict[str, dict[str, str]]:
    return TICKER_CATALOG.copy()
