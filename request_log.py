"""
Request log for serve.py (unit 9 capstone).

Every request to the server gets written here as one JSON line, so I can
look back at what happened after the terminal is closed. The file is
logs/requests.jsonl and it only ever gets appended to.

    from request_log import log_request
    log_request({"query": "...", "outcome": "ok", "duration_ms": 1234})

The timestamp gets added for you.

To look at the log afterwards without writing any new code:

    python request_log.py          summary + the last 10 requests
    python request_log.py 25       summary + the last 25
"""

import json
import sys
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


def summary(records: list[dict]) -> str:
    """A few lines on what's in the log: how many of each outcome, and averages."""
    if not records:
        return "no requests logged yet"

    lines = [f"{len(records)} requests in {LOG_FILE}"]

    # how many of each outcome (ok, stopped, bad_request, crash)
    counts = {}
    for r in records:
        outcome = r.get("outcome", "unknown")
        counts[outcome] = counts.get(outcome, 0) + 1
    lines.append("  outcomes: " + ", ".join(f"{k} {v}" for k, v in counts.items()))

    # averages only over the ok ones, since a 400 takes 0 ms and uses no tokens
    # and would drag the average down
    ok = [r for r in records if r.get("outcome") == "ok"]
    if ok:
        avg_ms = sum(r.get("duration_ms", 0) for r in ok) / len(ok)
        avg_calls = sum(r.get("model_calls", 0) for r in ok) / len(ok)
        avg_prompt = sum(r.get("prompt_tokens", 0) for r in ok) / len(ok)
        avg_output = sum(r.get("output_tokens", 0) for r in ok) / len(ok)
        slowest = max(r.get("duration_ms", 0) for r in ok)
        lines.append(f"  ok requests: {len(ok)}")
        lines.append(f"    avg duration {avg_ms:.0f} ms, slowest {slowest} ms")
        lines.append(f"    avg model calls {avg_calls:.1f}")
        lines.append(f"    avg tokens {avg_prompt:.0f} prompt + {avg_output:.0f} output")
    return "\n".join(lines)


if __name__ == "__main__":
    how_many = 10
    if len(sys.argv) > 1:
        how_many = int(sys.argv[1])

    rows = read_log()
    print(summary(rows))
    if rows:
        print(f"\nlast {min(how_many, len(rows))}:")
        for r in rows[-how_many:]:
            print(
                f"  {r.get('timestamp')}  {r.get('request_id')}  "
                f"{r.get('status_code')} {str(r.get('outcome')):<11}  "
                f"{r.get('duration_ms')} ms  "
                f"{r.get('prompt_tokens', 0)}+{r.get('output_tokens', 0)} tok  "
                f"{r.get('query')!r}"
            )
