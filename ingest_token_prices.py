from __future__ import annotations

from closewatch.database import Database
from closewatch.ingestion import get_ticker_catalog


def main() -> None:
    db = Database()
    db.init_db()

    for token_symbol, config in get_ticker_catalog().items():
        # Placeholder intake layer: the actual token-pair fetch can be wired to CoinGecko later.
        db.insert_token_price(token_symbol, "2026-09-12T12:00:00Z", 100.0)

    print("Token price ingestion placeholder complete.")


if __name__ == "__main__":
    main()
