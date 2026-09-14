from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

from .config import EXCHANGE_HOURS, MARKET_HOLIDAYS


def _as_et(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=ZoneInfo("America/New_York"))
    return timestamp.astimezone(ZoneInfo("America/New_York"))


def _is_us_market_holiday(dt: date) -> bool:
    year_holidays = MARKET_HOLIDAYS.get(dt.year, set())
    return dt in year_holidays


def is_market_closed(exchange: str, timestamp: datetime) -> bool:
    """Return True when the exchange is closed at the supplied timestamp."""
    exchange_name = exchange.upper()
    if exchange_name not in EXCHANGE_HOURS:
        raise ValueError(f"Unsupported exchange: {exchange}")

    dt = _as_et(timestamp)
    weekday = dt.weekday()
    if weekday >= 5:
        return True

    if _is_us_market_holiday(dt.date()):
        return True

    open_hour, open_minute, close_hour, close_minute = EXCHANGE_HOURS[exchange_name]
    market_open = time(open_hour, open_minute)
    market_close = time(close_hour, close_minute)

    current_time = dt.timetz()
    return not (market_open <= current_time < market_close)


def is_market_open(exchange: str, timestamp: datetime) -> bool:
    return not is_market_closed(exchange, timestamp)
