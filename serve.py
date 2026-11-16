#!/usr/bin/env python3
"""
FitFindr over HTTP. ← UNIT 9

    python serve.py                       run it on your machine
    gunicorn serve:app                    run it the way a host runs it

Everything else in this repo exits after one command. A host has nothing to
keep running, so a command line cannot be deployed. This file is the smallest
thing that can: it starts a web server, waits, and hands each request to the
same `run_agent()` your CLI calls. **No new agent logic lives here.** If your
loop works from `python app.py ask`, it works from here; if it doesn't, fix it
there, not in this file.

Two routes:

    POST /ask       {"query": "vintage graphic tee under $30",
                     "wardrobe": {...}}     ← wardrobe is optional
    GET  /health    is it awake?

`/ask` returns the session dict from `run_agent()` as JSON, unchanged — the
same keys you print from the command line, including `error`. Read
`session["error"]` first, exactly as you do everywhere else.

It runs **one request at a time**, and one route is deliberately slower than a
web server has to be. The reason is worth reading before you deploy: see the
note above `_one_at_a_time` below — it also decides which gunicorn worker you
can use.

UNIT 9 CAPSTONE: every request to /ask now writes one line to
logs/requests.jsonl (see request_log.py). That includes the 400s and the
500s, not only the ones that worked. Each line has a request id, the query,
what came back, how long it took, and the model calls and tokens it used.
"""

import os
import sys
import threading
import time
import uuid

# config first, and before anything that talks to the model: it loads your .env
# and fixes the Windows console encoding for every module that imports it.
import config  # noqa: F401

from flask import Flask, jsonify, request

import generate
from agent import run_agent
from request_log import log_request
from utils.data_loader import get_example_wardrobe

app = Flask(__name__)


# ── one request at a time ─────────────────────────────────────────────────────
# Here's why this exists.
#
# A web server will happily run two requests at once. Two things in this repo
# assume otherwise:
#
#   • If you moved a tool onto MCP in unit 4, `mcp_client.call_tool` starts
#     `mcp_server.py` as a separate process over stdio, one per call. Two
#     overlapping requests means two extra Python interpreters, and the free
#     tier you're deploying to has 512 MB for all of it. That is the reason
#     that would still be here even if everything else were perfect.
#   • `generate.py`'s pacing window and its call counter are plain module
#     globals — deliberately, because that file is teaching pacing and quota,
#     not locking. Two threads sharing them means the per-minute limiter is
#     counting something that isn't true.
#
# What the lock covers is exactly the agent run: the part that spawns
# processes and calls the model. Reading the request, rejecting a bad one, and
# turning the answer into JSON all happen outside it — so a request with a
# malformed body comes straight back with a 400 instead of queueing behind
# somebody else's agent.
#
# Serialising the runs costs you nothing here — this is one user asking one
# question — and it keeps the deployed behaviour identical to the CLI's. When
# that stops being an acceptable trade, the fix is a real queue, not a bigger
# lock.
#
# The same constraint decides your start command, and this is the part that
# bites in deployment rather than on your machine. `mcp_client.call_tool`
# wraps `asyncio.run()`, and `asyncio.run()` refuses to start when an event
# loop is already running. An async worker always has one running. So under
# `gunicorn -k gevent` (or `-k eventlet`, or `serve:app` wrapped for an ASGI
# server like uvicorn) EVERY MCP call fails with "asyncio.run() cannot be
# called from a running event loop" — not some of them under load, all of
# them, every time, in a place your laptop never showed you.
#
#     gunicorn serve:app              ← right: the DEFAULT sync worker
#     gunicorn -k gevent serve:app    ← breaks every MCP call you make

_one_at_a_time = threading.Lock()


@app.get("/health")
def health():
    """Is the server awake? A host pings something like this to find out."""
    return jsonify({"status": "ok"})


@app.post("/ask")
def ask():
    """
    Run the agent on one query.

    In:   {"query": "...", "wardrobe": {...}}   wardrobe optional — leave it
                                                out and you get the same
                                                example wardrobe the CLI uses.
    Out:  the session dict from run_agent(), as JSON.
    """
    # start the clock first thing so duration_ms is the whole request
    start = time.perf_counter()
    request_id = uuid.uuid4().hex[:8]

    payload = request.get_json(silent=True) or {}
    # get_json can give back a list or a string too, not just a dict
    if not isinstance(payload, dict):
        payload = {}
    query = payload.get("query") or ""
    if not isinstance(query, str):
        query = ""
    query = query.strip()
    if not query:
        # 400 rather than a stack trace: the caller can act on this one.
        message = ("Send JSON with a 'query' field, e.g. "
                   '{"query": "vintage graphic tee under $30"}')
        log_request({
            "request_id": request_id,
            "route": "/ask",
            "status_code": 400,
            "outcome": "bad_request",
            "query": None,
            # so I can see what they actually sent, cut short in case it's huge
            "raw_body": request.get_data(as_text=True)[:200],
            "error": message,
            "duration_ms": round((time.perf_counter() - start) * 1000),
        })
        return _with_id(jsonify({"error": message}), request_id), 400

    wardrobe = payload.get("wardrobe")
    used_example_wardrobe = False
    if not isinstance(wardrobe, dict):
        wardrobe = get_example_wardrobe()
        used_example_wardrobe = True

    # A queued request should look like a queued request. Without this the
    # second caller just sits there, and "slow" and "waiting its turn" are
    # indistinguishable from the outside — which is how people conclude the
    # deployment is broken when it is behaving exactly as designed.
    #
    # This is NOT the logging you add in the follow-along. It prints nothing
    # on the normal path, carries no timing and counts nothing; it says only
    # that this request had to wait. `locked()` can be a moment out of date,
    # so the note is occasionally missed — which costs nothing, because
    # nothing depends on it.
    had_to_wait = _one_at_a_time.locked()
    if had_to_wait:
        print(
            "  [serve] another request is still running. This one is waiting "
            "its turn — serve.py handles one at a time, on purpose.",
            file=sys.stderr,
            flush=True,
        )

    failure = None
    session = None
    with _one_at_a_time:
        # generate.py keeps running totals for the whole process, so I take a
        # reading before and after and the difference is what THIS request used.
        # it has to be inside the lock or another request could add to it.
        calls_before = generate.call_count()
        tokens_before = generate.token_counts()
        agent_start = time.perf_counter()
        try:
            session = run_agent(query, wardrobe)
        except Exception as exc:  # noqa: BLE001 — a 500 with a sentence beats a hang
            failure = f"{type(exc).__name__}: {exc}"
        agent_ms = round((time.perf_counter() - agent_start) * 1000)
        model_calls = generate.call_count() - calls_before
        tokens_after = generate.token_counts()

    # Outside the lock: building a response is not work the next caller should
    # be waiting on.
    record = {
        "request_id": request_id,
        "route": "/ask",
        "query": query,
        "used_example_wardrobe": used_example_wardrobe,
        "waited_for_lock": had_to_wait,
        "cache_enabled": config.CACHE_ENABLED,
        "model_calls": model_calls,
        "prompt_tokens": tokens_after["prompt"] - tokens_before["prompt"],
        "output_tokens": tokens_after["output"] - tokens_before["output"],
        "agent_ms": agent_ms,
    }

    if failure is not None:
        record["status_code"] = 500
        record["outcome"] = "crash"
        record["error"] = failure
        record["duration_ms"] = round((time.perf_counter() - start) * 1000)
        log_request(record)
        return _with_id(jsonify({"error": failure}), request_id), 500

    item = session.get("selected_item") or {}
    record["parsed"] = session.get("parsed")
    record["num_results"] = len(session.get("search_results") or [])
    record["selected_item_id"] = item.get("id")
    record["selected_price"] = item.get("price")
    record["fit_card"] = session.get("fit_card")
    record["error"] = session.get("error")
    record["error_kind"] = session.get("error_kind")
    # UNIT 9 improvement: if the model couldn't be reached the server is
    # broken, so say so with a 503 instead of a 200. The body is still the
    # whole session, so the caller still gets the sentence explaining it.
    # No matches is still a 200, because that's a real answer.
    status = 200
    if session.get("error_kind") == "model_unavailable":
        status = 503
        record["outcome"] = "model_error"
    elif session.get("error"):
        # the agent stopped early for a normal reason (like no matches),
        # so mark it so it doesn't look like a normal success
        record["outcome"] = "stopped"
    else:
        record["outcome"] = "ok"
    record["status_code"] = status
    record["duration_ms"] = round((time.perf_counter() - start) * 1000)
    log_request(record)

    return _with_id(jsonify(session), request_id), status


def _with_id(response, request_id):
    """Put the request id on the response so I can find its line in the log."""
    response.headers["X-Request-Id"] = request_id
    return response


if __name__ == "__main__":
    # PORT and 0.0.0.0 are not decoration. A host tells you which port to
    # listen on through PORT, and it reaches your process from outside the
    # container — bind 127.0.0.1 and nothing but the container itself can
    # connect, which looks exactly like a broken app from the browser.
    port = int(os.getenv("PORT", "5000"))

    # Never on by default. Flask's debugger executes code typed into a browser,
    # and a deployed app with it on is a stranger's shell. Set AI201_DEBUG=1 in
    # your own terminal when you want the reloader.
    debug = os.getenv("AI201_DEBUG", "0") == "1"

    print(f"\nFitFindr is listening on http://localhost:{port}")
    print("It runs one request at a time — a second one waits for the first.")
    print("Ask it something (single quotes, as always):\n")
    print(
        f"  curl -X POST http://localhost:{port}/ask \\\n"
        f"    -H 'Content-Type: application/json' \\\n"
        f"    -d '{{\"query\": \"vintage graphic tee under $30\"}}'\n"
    )
    print("Ctrl-C to stop.\n")

    app.run(host="0.0.0.0", port=port, debug=debug)
