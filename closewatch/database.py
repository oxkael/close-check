from __future__ import annotations

import sqlite3
from typing import Optional


class Database:
    def __init__(self, db_path: str = "closewatch.db"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

    def _connect(self) -> sqlite3.Connection:
        return self._conn

    def close(self) -> None:
        if getattr(self, "_conn", None) is not None:
            self._conn.close()
            self._conn = None

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS real_closes (
                    symbol TEXT NOT NULL,
                    close_date TEXT NOT NULL,
                    close_price REAL NOT NULL,
                    PRIMARY KEY (symbol, close_date)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS token_prices (
                    symbol TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    price REAL NOT NULL,
                    PRIMARY KEY (symbol, timestamp)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS closure_windows (
                    symbol TEXT NOT NULL,
                    window_start TEXT NOT NULL,
                    window_end TEXT NOT NULL,
                    last_real_close TEXT NOT NULL,
                    reopen_price REAL,
                    PRIMARY KEY (symbol, window_start, window_end)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prediction_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    gap_pct REAL,
                    resolved_at TEXT,
                    result TEXT
                )
                """
            )

    def init_db(self) -> None:
        self._ensure_schema()

    def insert_real_close(self, symbol: str, close_date: str, close_price: float) -> None:
        self._ensure_schema()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO real_closes (symbol, close_date, close_price)
                VALUES (?, ?, ?)
                """,
                (symbol.upper(), close_date, float(close_price)),
            )

    def get_latest_real_close(self, symbol: str) -> Optional[float]:
        self._ensure_schema()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT close_price
                FROM real_closes
                WHERE symbol = ?
                ORDER BY close_date DESC
                LIMIT 1
                """,
                (symbol.upper(),),
            ).fetchone()
            if row is None:
                return None
            return float(row["close_price"])

    def insert_token_price(self, symbol: str, timestamp: str, price: float) -> None:
        self._ensure_schema()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO token_prices (symbol, timestamp, price)
                VALUES (?, ?, ?)
                """,
                (symbol.upper(), timestamp, float(price)),
            )

    def get_latest_token_price(self, symbol: str) -> Optional[dict]:
        self._ensure_schema()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT symbol, timestamp, price
                FROM token_prices
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (symbol.upper(),),
            ).fetchone()
            if row is None:
                return None
            return {"symbol": row["symbol"], "timestamp": row["timestamp"], "price": float(row["price"])}

    def save_closure_window(
        self,
        symbol: str,
        window_start: str,
        window_end: str,
        last_real_close: str,
        reopen_price: Optional[float] = None,
    ) -> None:
        self._ensure_schema()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO closure_windows (
                    symbol, window_start, window_end, last_real_close, reopen_price
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (symbol.upper(), window_start, window_end,
                 last_real_close, reopen_price),
            )

    def log_prediction(
        self,
        symbol: str,
        created_at: str,
        status: str,
        gap_pct: Optional[float] = None,
        resolved_at: Optional[str] = None,
        result: Optional[str] = None,
    ) -> int:
        self._ensure_schema()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO prediction_log (symbol, created_at, status, gap_pct, resolved_at, result)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (symbol.upper(), created_at, status, gap_pct, resolved_at, result),
            )
            return int(cursor.lastrowid)

    def resolve_prediction(
        self,
        prediction_id: int,
        resolved_at: Optional[str] = None,
        result: Optional[str] = None,
    ) -> None:
        self._ensure_schema()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE prediction_log
                SET status = 'resolved', resolved_at = ?, result = ?
                WHERE id = ?
                """,
                (resolved_at, result, prediction_id),
            )

    def resolve_pending_predictions(
        self,
        symbol: str,
        last_real_close: float,
        reopen_price: float,
        resolved_at: Optional[str] = None,
    ) -> list[int]:
        self._ensure_schema()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM prediction_log
                WHERE symbol = ? AND status = 'pending'
                ORDER BY created_at ASC
                """,
                (symbol.upper(),),
            ).fetchall()

            resolved_ids: list[int] = []
            for row in rows:
                original_gap = float(
                    row["gap_pct"]) if row["gap_pct"] is not None else 0.0
                if last_real_close == 0:
                    reopen_gap = 0.0
                else:
                    reopen_gap = (
                        (reopen_price - last_real_close) / last_real_close) * 100.0

                if abs(original_gap) <= 1e-9:
                    result = "converged"
                elif abs(reopen_gap) <= abs(original_gap) * 0.75 and abs(reopen_gap) < abs(original_gap):
                    result = "converged"
                else:
                    result = "failed"

                conn.execute(
                    """
                    UPDATE prediction_log
                    SET status = 'resolved', resolved_at = ?, result = ?
                    WHERE id = ?
                    """,
                    (resolved_at, result, int(row["id"])),
                )
                resolved_ids.append(int(row["id"]))

            return resolved_ids

    def get_prediction(self, prediction_id: int) -> Optional[dict]:
        self._ensure_schema()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM prediction_log
                WHERE id = ?
                """,
                (prediction_id,),
            ).fetchone()
            if row is None:
                return None
            return {
                "id": int(row["id"]),
                "symbol": row["symbol"],
                "created_at": row["created_at"],
                "status": row["status"],
                "gap_pct": row["gap_pct"],
                "resolved_at": row["resolved_at"],
                "result": row["result"],
            }

    def get_accuracy_summary(self, symbol: Optional[str] = None) -> dict:
        self._ensure_schema()
        with self._connect() as conn:
            query = """
                SELECT result
                FROM prediction_log
                WHERE status = 'resolved'
            """
            params: list[str] = []
            if symbol is not None:
                query += " AND symbol = ?"
                params.append(symbol.upper())

            rows = conn.execute(query, params).fetchall()

        resolved_predictions = len(rows)
        converged = sum(
            1 for row in rows if str(row["result"]).lower() == "converged"
        )
        accuracy_pct = (converged / resolved_predictions *
                        100.0) if resolved_predictions else 0.0

        return {
            "resolved_predictions": resolved_predictions,
            "converged": converged,
            "accuracy_pct": float(accuracy_pct),
        }
