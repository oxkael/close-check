"""Background scheduler for periodic ingestion and recalibration.

This module exposes a `run_scheduler()` function that starts scheduled jobs
to ingest token prices from Bitget and recompute calibration buckets daily.
It prefers APScheduler if available, and falls back to a simple loop when not.
"""

from __future__ import annotations

import time
import datetime
from typing import Optional

from .ingestion import ingest_token_prices_bitget
from .database import Database


def _ingest_job(db: Optional[Database] = None) -> None:
    db = db or Database()
    print(f"[{datetime.datetime.utcnow().isoformat()}Z] Running Bitget ingestion...")
    summary = ingest_token_prices_bitget(db=db)
    print(f"Ingested: {summary}")


def _recalibrate_job(db: Optional[Database] = None) -> None:
    db = db or Database()
    print(f"[{datetime.datetime.utcnow().isoformat()}Z] Recomputing calibration buckets...")
    buckets = db.recompute_calibration_buckets()
    print(f"Recomputed {len(buckets)} buckets")


def run_scheduler(poll_interval_seconds: int = 60) -> None:
    """Start the scheduler. Uses APScheduler if present, otherwise a simple loop.

    The APScheduler-enabled scheduler runs ingestion hourly and recalibration
    once per day at 03:00 UTC. The fallback loop checks once per minute and
    runs jobs when their time arrives.
    """
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger

        sched = BlockingScheduler()
        # hourly ingestion
        sched.add_job(_ingest_job, CronTrigger(minute=0))
        # daily recalibration at 03:00 UTC
        sched.add_job(_recalibrate_job, CronTrigger(hour=3, minute=0))

        print("Scheduler starting (APScheduler)")
        sched.start()
    except Exception:
        print("APScheduler not available; using fallback scheduler loop")
        last_hour = None
        last_day = None
        db = Database()
        try:
            while True:
                now = datetime.datetime.utcnow()
                if last_hour is None or now.hour != last_hour:
                    _ingest_job(db=db)
                    last_hour = now.hour
                if last_day is None or now.date() != last_day:
                    # run daily recalibration once per UTC day
                    _recalibrate_job(db=db)
                    last_day = now.date()
                time.sleep(poll_interval_seconds)
        except KeyboardInterrupt:
            print("Scheduler stopped by user")
