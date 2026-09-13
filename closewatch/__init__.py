"""CloseWatch package."""

from .calibration import build_calibration_buckets, bucket_gap
from .database import Database
from .gap_logic import build_closure_windows, calculate_gap_pct
from .ingestion import get_ticker_catalog, ingest_recent_real_closes
from .market_calendar import is_market_closed, is_market_open
from .signal import current_gap_signal

__all__ = [
    "Database",
    "build_calibration_buckets",
    "build_closure_windows",
    "bucket_gap",
    "calculate_gap_pct",
    "current_gap_signal",
    "get_ticker_catalog",
    "ingest_recent_real_closes",
    "is_market_closed",
    "is_market_open",
]
