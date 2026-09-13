from __future__ import annotations

import streamlit as st

from closewatch.ingestion import get_ticker_catalog
from closewatch.market_calendar import is_market_closed

st.set_page_config(page_title="CloseWatch", layout="wide")
st.title("CloseWatch")
st.caption("Market-closure gap signal dashboard")

catalog = get_ticker_catalog()
for symbol, config in catalog.items():
    status = is_market_closed(config["exchange"], st.session_state.get("now", __import__("datetime").datetime.utcnow()))
    st.metric(label=symbol, value="Closed" if status else "Open", delta=config["base_symbol"])

st.write("Dashboard scaffolding is in place. Next steps: wire the live gap detector and calibration output.")
