#!/usr/bin/env python3
"""
Runs my five capstone criteria (criteria.md, "Capstone criteria (unit 9)")
against the real server, three trials each.

    python run_capstone.py              3 trials, results saved as "before"
    python run_capstone.py after        same thing, saved as "after"

What one trial does:
  1. starts `python serve.py` with the cache off and waits for /health
  2. sends the 10 test queries, the no match query and the 5 bad bodies
     (criteria 1, 2, 3 and 5 all come out of these 16 requests)
  3. stops it, starts it again with a wrong GEMINI_API_KEY, sends
     'denim jacket under $50' 3 times (criterion 4), stops it
  4. reads the new lines out of logs/requests.jsonl and scores everything

Then it waits 60 seconds before the next trial, like criterion 2 says.

Everything goes to results/capstone_<date>_<time>_<label>.md, including the
real log lines, so the results are on disk and not just in my terminal.
It needs nothing new installed, it uses urllib to send the requests.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

import config
from request_log import LOG_FILE

PORT = 5000
BASE = f"http://localhost:{PORT}"

TEST_QUERIES = [
    "vintage graphic tee under $30",
    "90s track jacket in size M",
    "silk slip dress in midi length under $40",
    "platform sneakers size 8",
    "denim jacket under $50",
    "black leather jacket under $80",
    "baggy jeans size 32",
    "cozy oversized hoodie",
    "chunky knit sweater under $45",
    "brown leather belt",
]
NO_MATCH_QUERY = "designer ballgown size XXS under $5"

# (body exactly as sent, content type)
BAD_BODIES = [
    ("{}", "application/json"),
    ('{"query": ""}', "application/json"),
    ('["vintage", "tee"]', "application/json"),
    ('{"query": 42}', "application/json"),
    ("hello", "text/plain"),
]

FAIL_QUERY = "denim jacket under $50"
REQUIRED_FIELDS = ["timestamp", "request_id", "outcome", "status_code", "duration_ms"]


# ── talking to the server ─────────────────────────────────────────────────────

def send(body: str, content_type: str = "application/json") -> dict:
    """POST one body to /ask. Gives back the status, the request id and the JSON."""
    req = urllib.request.Request(
        BASE + "/ask",
        data=body.encode("utf-8"),
        headers={"Content-Type": content_type},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            status = resp.status
            request_id = resp.headers.get("X-Request-Id")
            text = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        # 400s and 500s land here, but they still have a body and headers
        status = e.code
        request_id = e.headers.get("X-Request-Id")
        text = e.read().decode("utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {"not_json": text[:200]}
    return {"status": status, "request_id": request_id, "json": data}


def ask(query: str) -> dict:
    return send(json.dumps({"query": query}))


def start_server(server_out, wrong_key: bool = False):
    env = dict(os.environ)
    env["AI201_CACHE"] = "0"
    env["PORT"] = str(PORT)
    if wrong_key:
        env["GEMINI_API_KEY"] = "deliberately_wrong_key_for_criterion_4"
    proc = subprocess.Popen(
        [sys.executable, "serve.py"],
        cwd=config.ROOT,
        env=env,
        stdout=server_out,
        stderr=subprocess.STDOUT,
    )
    # wait for /health, up to 30 seconds
    for _ in range(60):
        try:
            with urllib.request.urlopen(BASE + "/health", timeout=2):
                return proc
        except Exception:
            time.sleep(0.5)
    proc.terminate()
    raise RuntimeError("serve.py didn't answer /health within 30 seconds")


def stop_server(proc) -> None:
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def log_line_count() -> int:
    if not LOG_FILE.exists():
        return 0
    with open(LOG_FILE, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def new_log_lines(start_count: int) -> list[dict]:
    with open(LOG_FILE, encoding="utf-8") as f:
        lines = [line for line in f if line.strip()]
    return [json.loads(line) for line in lines[start_count:]]


# ── one trial ─────────────────────────────────────────────────────────────────

def run_trial(n: int, server_out) -> dict:
    print(f"\n=== trial {n} ===", flush=True)
    before = log_line_count()

    proc = start_server(server_out)
    try:
        matching = []
        for q in TEST_QUERIES:
            r = ask(q)
            print(f"  {r['status']} {r['request_id']}  {q}", flush=True)
            matching.append(r)
        no_match = ask(NO_MATCH_QUERY)
        print(f"  {no_match['status']} {no_match['request_id']}  {NO_MATCH_QUERY}", flush=True)
        bad = []
        for body, ctype in BAD_BODIES:
            r = send(body, ctype)
            print(f"  {r['status']} {r['request_id']}  bad body {body}", flush=True)
            bad.append(r)
    finally:
        stop_server(proc)

    proc = start_server(server_out, wrong_key=True)
    try:
        failing = []
        for _ in range(3):
            r = ask(FAIL_QUERY)
            print(f"  {r['status']} {r['request_id']}  wrong key: {FAIL_QUERY}", flush=True)
            failing.append(r)
    finally:
        stop_server(proc)

    lines = new_log_lines(before)
    by_id = {}
    for line in lines:
        by_id.setdefault(line.get("request_id"), []).append(line)

    def line_for(r):
        found = by_id.get(r["request_id"]) or []
        return found[0] if len(found) == 1 else None

    results = {}

    # 1. every request leaves exactly one complete line (the first 16 requests)
    c1_requests = matching + [no_match] + bad
    c1_good = 0
    c1_notes = []
    c1_ids = {r["request_id"] for r in c1_requests}
    c1_lines = [l for l in lines if l.get("request_id") in c1_ids]
    for r in c1_requests:
        found = by_id.get(r["request_id"]) or []
        if len(found) != 1:
            c1_notes.append(f"{r['request_id']}: {len(found)} lines")
            continue
        missing = [f for f in REQUIRED_FIELDS if found[0].get(f) is None]
        if missing:
            c1_notes.append(f"{r['request_id']}: missing {missing}")
            continue
        c1_good += 1
    results[1] = {"score": c1_good, "out_of": len(c1_requests),
                  "pass": c1_good == len(c1_requests) and len(c1_lines) == len(c1_requests),
                  "notes": c1_notes + [f"{len(c1_lines)} log lines for these {len(c1_requests)} requests"]}

    # 2. at least 8 of 10 matching queries under 8000 ms
    durations = []
    for r in matching:
        l = line_for(r)
        durations.append(l.get("duration_ms") if l else None)
    under = sum(1 for d in durations if d is not None and d < 8000)
    results[2] = {"score": under, "out_of": 10, "pass": under >= 8,
                  "notes": [f"duration_ms: {durations}"]}

    # 3. model_calls == 2 and 1 <= tokens <= 600 for all 10
    c3_good = 0
    c3_rows = []
    for r in matching:
        l = line_for(r) or {}
        calls = l.get("model_calls")
        tokens = (l.get("prompt_tokens") or 0) + (l.get("output_tokens") or 0)
        ok = calls == 2 and 1 <= tokens <= 600
        c3_good += ok
        c3_rows.append(f"{calls} calls / {tokens} tok")
    results[3] = {"score": c3_good, "out_of": 10, "pass": c3_good == 10,
                  "notes": ["; ".join(c3_rows)]}

    # 4. wrong key: status >= 500 in the response AND the log, error mentions api key
    c4_good = 0
    c4_rows = []
    for r in failing:
        l = line_for(r) or {}
        err = str(l.get("error") or "").lower()
        ok = (r["status"] >= 500 and l.get("status_code") == r["status"]
              and "api key" in err)
        c4_good += ok
        c4_rows.append(f"response {r['status']}, log status_code {l.get('status_code')}, "
                       f"outcome {l.get('outcome')}, mentions api key: {'api key' in err}")
    results[4] = {"score": c4_good, "out_of": 3, "pass": c4_good == 3, "notes": c4_rows}

    # 5. bad bodies: 400, error has 'query', logged as bad_request, no model calls, raw_body
    c5_good = 0
    c5_rows = []
    for (body, _), r in zip(BAD_BODIES, bad):
        l = line_for(r) or {}
        msg = str(r["json"].get("error") or "")
        ok = (r["status"] == 400 and "query" in msg
              and l.get("outcome") == "bad_request"
              and l.get("model_calls") in (0, None)
              and l.get("raw_body") == body[:200])
        c5_good += ok
        c5_rows.append(f"{body!r}: {r['status']}, outcome {l.get('outcome')}, "
                       f"raw_body {l.get('raw_body')!r}")
    results[5] = {"score": c5_good, "out_of": 5, "pass": c5_good == 5, "notes": c5_rows}

    for k, v in results.items():
        print(f"  criterion {k}: {v['score']}/{v['out_of']} {'MET' if v['pass'] else 'MISSED'}")

    return {"results": results, "lines": lines}


# ── the report ────────────────────────────────────────────────────────────────

NAMES = {
    1: "1. Every request leaves exactly one complete log line",
    2: "2. A matching query answers in under 8 seconds",
    3: "3. 2 model calls and 1 to 600 tokens per matching query",
    4: "4. Wrong API key gets 500 or higher, not 200",
    5: "5. Bad input gets a 400 and uses no model calls",
}
TARGETS = {1: "16 of 16", 2: "8 of 10", 3: "10 of 10", 4: "3 of 3", 5: "5 of 5"}


def write_report(trials: list[dict], label: str, stamp: str, server_file: str) -> str:
    out = [f"# Capstone run {stamp} ({label})", ""]
    out.append(f"Made by `run_capstone.py`. Server output: `{server_file}`.")
    out.append("")
    out.append("| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |")
    out.append("|---|---|---|---|---|---|")
    for k in range(1, 6):
        cells = [f"{t['results'][k]['score']}/{t['results'][k]['out_of']}" for t in trials]
        verdict = "MET" if all(t["results"][k]["pass"] for t in trials) else "MISSED"
        out.append(f"| {NAMES[k]} | {TARGETS[k]} | {' | '.join(cells)} | {verdict} |")
    out.append("")
    for i, t in enumerate(trials, start=1):
        out.append(f"## Trial {i}")
        out.append("")
        for k in range(1, 6):
            out.append(f"**Criterion {k}:** {t['results'][k]['score']}/{t['results'][k]['out_of']}")
            out.append("")
            out.append("```")
            out.extend(t["results"][k]["notes"])
            out.append("```")
            out.append("")
        out.append(f"All {len(t['lines'])} log lines from this trial (`logs/requests.jsonl`):")
        out.append("")
        out.append("```")
        out.extend(json.dumps(l, ensure_ascii=False) for l in t["lines"])
        out.append("```")
        out.append("")

    config.RESULTS_DIR.mkdir(exist_ok=True)
    path = config.RESULTS_DIR / f"capstone_{stamp}_{label}.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return str(path)


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "before"
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    server_file = f"results/capstone_{stamp}_{label}_server.txt"

    trials = []
    with open(config.ROOT / server_file, "w", encoding="utf-8") as server_out:
        for n in (1, 2, 3):
            if n > 1:
                print("\n  waiting 60 seconds before the next trial (criterion 2 says so)", flush=True)
                time.sleep(60)
            trials.append(run_trial(n, server_out))

    path = write_report(trials, label, stamp, server_file)
    print(f"\nsaved {path}")


if __name__ == "__main__":
    main()
