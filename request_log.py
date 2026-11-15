"""
Request log for serve.py (unit 9 capstone).

Every request to the server gets written here as one JSON line, so I can
look back at what happened after the terminal is closed. The file is
logs/requests.jsonl and it only ever gets appended to.

    from request_log import log_request
    log_request({"query": "...", "outcome": "ok", "duration_ms": 1234})

The timestamp gets added for you.
"""

import json
from datetime import datetime, timezone

import config

LOG_DIR = config.ROOT / "logs"
LOG_FILE = LOG_DIR / "requests.jsonl"


def log_request(record: dict) -> None:
    """Add one record to the end of the log file, with a timestamp on it."""
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    entry.update(record)

    # if the log can't be written I don't want the whole request to fail,
    # the user should still get their answer. so just print a warning.
    try:
        LOG_DIR.mkdir(exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"  [log] couldn't write to {LOG_FILE}: {e}", flush=True)


def read_log() -> list[dict]:
    """Read every record back out of the log. Empty list if there's no log yet."""
    if not LOG_FILE.exists():
        return []
    records = []
    with open(LOG_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # a half written line shouldn't stop me reading the rest
                print(f"  [log] skipping a line that isn't valid JSON: {line[:60]}")
    return records


if __name__ == "__main__":
    # quick check: python request_log.py writes a test line and reads it back
    log_request({"route": "test", "query": "just checking the log works"})
    rows = read_log()
    print(f"{len(rows)} records in {LOG_FILE}")
    print(rows[-1])
