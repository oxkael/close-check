"""CloseWatch package."""

from .database import Database
from .gap_logic import build_closure_windows, calculate_gap_pct
from .ingestion import get_ticker_catalog
from .market_calendar import is_market_closed, is_market_open

__all__ = [
    "Database",
    "build_closure_windows",
    "calculate_gap_pct",
    "get_ticker_catalog",
    "is_market_closed",
    "is_market_open",
]
