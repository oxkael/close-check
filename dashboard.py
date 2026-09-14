"""Temporary Streamlit MVP dashboard.

This is a local prototype used while the product frontend is being upgraded to the
revised React/Next.js/Tailwind build defined in frontend-spec-revised.md.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any

import streamlit as st


def fetch_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=3) as response:
        payload = response.read().decode("utf-8")
        return json.loads(payload)


def fetch_summary() -> dict[str, Any]:
    try:
        payload = fetch_json("http://localhost:8000/summary")
        if "accuracy_summary" not in payload:
            payload["accuracy_summary"] = {
                "resolved_predictions": 0, "converged": 0, "accuracy_pct": 0.0}
        return payload
    except Exception:
        return {
            "tickers": [
                {"symbol": "TSLAx", "base_symbol": "TSLA", "market_closed": True},
                {"symbol": "NVDAx", "base_symbol": "NVDA", "market_closed": True},
                {"symbol": "AAPLx", "base_symbol": "AAPL", "market_closed": True},
            ],
            "count": 3,
            "accuracy_summary": {"resolved_predictions": 0, "converged": 0, "accuracy_pct": 0.0},
        }


def fetch_signal(symbol: str) -> dict[str, Any]:
    url = f"http://localhost:8000/ticker/{symbol}/signal"
    try:
        payload = fetch_json(url)
        if "accuracy_summary" not in payload:
            payload["accuracy_summary"] = {
                "resolved_predictions": 0, "converged": 0, "accuracy_pct": 0.0}
        return payload
    except Exception:
        return {
            "symbol": symbol,
            "exchange": "NASDAQ",
            "market_closed": True,
            "last_real_close": 100.0,
            "token_price": 104.0,
            "gap_pct": 4.0,
            "bucket": "4.0%-6.0%",
            "accuracy_summary": {"resolved_predictions": 0, "converged": 0, "accuracy_pct": 0.0},
        }


st.set_page_config(page_title="CloseWatch", layout="wide")
st.title("CloseWatch")
st.caption("Market-closure gap signal dashboard")

summary = fetch_summary()
accuracy_summary = summary.get("accuracy_summary", {
                               "resolved_predictions": 0, "converged": 0, "accuracy_pct": 0.0})
ticker_items = summary.get("tickers", [])

st.subheader("Model Accuracy")
st.metric(
    "Resolved predictions",
    int(accuracy_summary.get("resolved_predictions", 0)),
)
st.metric(
    "Accuracy",
    f"{float(accuracy_summary.get('accuracy_pct', 0.0)):.1f}%",
)

if not ticker_items:
    st.info(
        "No ticker metadata is available yet. The app is waiting for its source feed.")
    st.stop()

for symbol in [item.get("symbol") for item in ticker_items if item.get("symbol")]:
    signal = fetch_signal(symbol)
    status = "Closed" if signal.get("market_closed") else "Open"
    gap_pct = float(signal.get("gap_pct", 0.0))
    accuracy = signal.get("accuracy_summary", {})
    resolved = accuracy.get("resolved_predictions", 0)
    accuracy_pct = float(accuracy.get("accuracy_pct", 0.0))
    bucket_stats = signal.get("bucket_stats", {})
    bucket_odds = float(bucket_stats.get(
        "convergence_rate", 0.0) * 100.0 if bucket_stats else 0.0)
    worst_case = bucket_stats.get("worst_case_gap_pct")

    with st.container():
        st.subheader(symbol)
        cols = st.columns([1.5, 1.5, 1.5, 1.5, 2])
        cols[0].metric("Market", status)
        cols[1].metric("Gap %", f"{gap_pct:.2f}%")
        cols[2].metric("Bucket", signal.get("bucket", "N/A"))
        cols[3].metric("Accuracy", f"{accuracy_pct:.1f}%")
        cols[4].markdown(
            f"**Base:** {signal.get('exchange', 'N/A')}  \n"
            f"**Last real close:** {signal.get('last_real_close', 0.0):.2f}  \n"
            f"**Token price:** {signal.get('token_price', 0.0):.2f}  \n"
            f"**Historical odds:** {bucket_odds:.1f}%  \n"
            f"**Worst case:** {worst_case if worst_case is not None else 'N/A'}  \n"
            f"**Resolved predictions:** {resolved}"
        )
        st.divider()
