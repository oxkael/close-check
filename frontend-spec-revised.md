# Frontend Spec (Revised)

This file restores the source-of-truth frontend requirements referenced by the newer build task.

## Stack
- React + Next.js + TypeScript + Tailwind
- Not Streamlit for the final product build
- Streamlit is acceptable only as a temporary local prototype or internal smoke-test UI

## Core product behavior
The frontend must show the CloseWatch signal for tokenized US equities on Bitget rTokens.

It must surface:
- ticker symbol and underlying stock mapping
- whether the real market is currently closed
- current gap versus the last real close
- historical bucket odds for the active gap bucket
- worst-case historical tail outcome for that bucket
- model accuracy summary from logged predictions
- a clear, non-trading, informational framing

## Required pages and sections
### 1. Summary dashboard
A top-level dashboard page containing:
- summary cards for all tracked tickers
- current status (Open / Closed)
- current gap % if the market is closed
- bucket range and bucket odds
- worst-case tail
- model accuracy summary

### 2. Per-ticker detail card
Each ticker should show:
- ticker symbol and underlying stock name
- token price and last real close
- market status
- current gap %
- bucket label
- historical convergence rate for that bucket
- average time-to-converge
- worst-case tail stat
- confidence / sample-size caveat when small sample size is present

### 3. Accuracy panel
Visible summary panel with:
- number of predictions logged
- number of resolved predictions
- converged count
- overall accuracy percentage
- date or last recalibration timestamp

## Data contract expected from the backend
The UI must consume the API rather than DB tables directly.

Expected fields:
- symbol
- exchange
- market_closed
- last_real_close
- token_price
- gap_pct
- bucket
- bucket_stats
- accuracy_summary

The frontend should gracefully handle empty or low-sample buckets and show a “insufficient data” message instead of inventing numbers.

## Design constraints
- No trade orders or wallet flows
- No financial-advice wording
- No autonomous execution
- Use informational language only: historical statistics, risk context, and model calibration output

## Acceptance criteria
- At least 2–3 tickers are displayed with live status, gap, bucket odds, and worst-case stat
- The accuracy panel shows a real number from logged predictions
- The UI reads from the API layer, not directly from SQLite
- The dashboard is clearly product-facing and demo-ready

## Scope note
This file supersedes the older Streamlit-only frontend path and should be treated as the actual product UI specification for the next implementation phase.
