from __future__ import annotations

from closewatch.ingestion import ingest_recent_real_closes


def main() -> None:
    summary = ingest_recent_real_closes(days=90)
    print(summary)


if __name__ == "__main__":
    main()
