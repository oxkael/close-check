from __future__ import annotations

import argparse
import json
import subprocess
import sys

from .demo import demo_signal_view
from .ingestion import ingest_recent_real_closes


def _run_demo() -> None:
    payload = demo_signal_view()
    print(json.dumps(payload, indent=2))


def _run_ingest() -> None:
    summary = ingest_recent_real_closes()
    print(json.dumps(summary, indent=2))


def _run_recalibrate() -> None:
    from .database import Database

    db = Database()
    print(json.dumps(db.recompute_calibration_buckets(), indent=2))


def _run_seed_demo() -> None:
    from .database import Database

    db = Database()
    sample_rows = [
        {
            "symbol": "TSLAx",
            "created_at": "2026-09-10T09:30:00Z",
            "status": "resolved",
            "gap_pct": 4.0,
            "resolved_at": "2026-09-11T10:00:00Z",
            "result": "converged",
        },
        {
            "symbol": "TSLAx",
            "created_at": "2026-09-11T09:30:00Z",
            "status": "resolved",
            "gap_pct": 5.5,
            "resolved_at": "2026-09-12T08:00:00Z",
            "result": "failed",
        },
        {
            "symbol": "TSLAx",
            "created_at": "2026-09-12T09:30:00Z",
            "status": "resolved",
            "gap_pct": 3.2,
            "resolved_at": "2026-09-13T11:00:00Z",
            "result": "converged",
        },
    ]

    for row in sample_rows:
        db.log_prediction(
            symbol=row["symbol"],
            created_at=row["created_at"],
            status=row["status"],
            gap_pct=row["gap_pct"],
            resolved_at=row["resolved_at"],
            result=row["result"],
        )

    buckets = db.recompute_calibration_buckets(symbol="TSLAx")
    payload = {
        "seeded_predictions": len(sample_rows),
        "accuracy_summary": db.get_accuracy_summary("TSLAx"),
        "buckets": buckets,
    }
    print(json.dumps(payload, indent=2))


def _run_api() -> None:
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "uvicorn is not installed. Run: python -m pip install -e .") from exc

    uvicorn.run("closewatch.api:app", host="127.0.0.1",
                port=8000, reload=False)


def _run_dashboard() -> None:
    try:
        import streamlit
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "streamlit is not installed. Run: python -m pip install -e .") from exc

    subprocess.run([sys.executable, "-m", "streamlit",
                   "run", "dashboard.py"], check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="CloseWatch CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("demo", help="Print the demo signal summary")
    subparsers.add_parser(
        "ingest", help="Fetch recent real closes for tracked tickers")
    subparsers.add_parser(
        "recalibrate", help="Refresh calibration buckets from resolved predictions")
    subparsers.add_parser(
        "seed-demo", help="Seed a few demo predictions and recompute calibration stats")
    subparsers.add_parser("api", help="Run the FastAPI server")
    subparsers.add_parser("dashboard", help="Run the Streamlit dashboard")
    subparsers.add_parser("scheduler", help="Run scheduled ingestion and recalibration")

    args = parser.parse_args()

    if args.command == "demo":
        _run_demo()
    elif args.command == "ingest":
        _run_ingest()
    elif args.command == "recalibrate":
        _run_recalibrate()
    elif args.command == "seed-demo":
        _run_seed_demo()
    elif args.command == "api":
        _run_api()
    elif args.command == "dashboard":
        _run_dashboard()
    elif args.command == "scheduler":
        try:
            from .scheduler import run_scheduler

            run_scheduler()
        except Exception as exc:  # pragma: no cover - runtime helper
            raise SystemExit(f"Failed to start scheduler: {exc}")


if __name__ == "__main__":
    main()
