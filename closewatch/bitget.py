"""Minimal Bitget helpers for token list and candles used by ingestion.

This module provides lightweight wrappers around the public Bitget market
endpoints so the ingestion layer can fetch token prices and the rToken list.
"""

from __future__ import annotations

import requests
from typing import Any, List, Dict

BASE = "https://api.bitget.com/api/v3"


def fetch_weekend_eligible_symbols() -> List[str]:
    """Return a list of weekend-eligible rToken symbols (if available).

    Falls back to an empty list on any error so ingestion remains robust.
    """
    try:
        url = f"{BASE}/reality/market/stock-info"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("data") or []
        symbols = [item.get("symbol") for item in items if item.get("symbol")]
        return symbols
    except Exception:
        return []


def fetch_candles(symbol: str, interval: str = "1h", limit: int = 200) -> List[Dict[str, Any]]:
    """Fetch recent candles for a Spot symbol (symbol is the Bitget format like RAAPLUSDT).

    Returns a list of candle arrays as Bitget provides. On error, returns an empty list.
    """
    try:
        params = {"category": "SPOT", "symbol": symbol, "interval": interval, "limit": limit}
        url = f"{BASE}/market/candles"
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data") or []
    except Exception:
        return []
