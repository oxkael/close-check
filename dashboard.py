from __future__ import annotations

import json
import urllib.request

import streamlit as st


def fetch_summary() -> dict:
    try:
        with urllib.request.urlopen("http://localhost:8000/summary", timeout=3) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)
    except Exception:
        return {
            "tickers": [
                {"symbol": "TSLAx", "base_symbol": "TSLA", "market_closed": True},
                {"symbol": "NVDAx", "base_symbol": "NVDA", "market_closed": True},
            ],
            "count": 2,
        }


st.set_page_config(page_title="CloseWatch", layout="wide")
st.title("CloseWatch")
st.caption("Market-closure gap signal dashboard")

summary = fetch_summary()
for item in summary.get("tickers", []):
    st.metric(
        label=item.get("symbol", "Unknown"),
        value="Closed" if item.get("market_closed") else "Open",
        delta=item.get("base_symbol", ""),
    )

st.write("Dashboard is reading ticker status from the API layer. The live gap detector and calibration data can be surfaced next.")
