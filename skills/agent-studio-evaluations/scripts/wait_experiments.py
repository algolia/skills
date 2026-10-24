#!/usr/bin/env python3
"""Wait for one or more experiments to reach a stopping state.

Polls `algobot evals experiments get <id>` for every id in parallel each
--interval seconds until each one is completed, failed, cancelled or
awaiting_review, or until --timeout seconds have passed (a hard cap: each
call's own timeout never exceeds the remaining wait, computed when the call
starts, and a call whose turn comes after the deadline is skipped). The CLI timeout message
("operation was aborted due to timeout") is retried on the next poll. After 3
consecutive other failures for an id (404, 401, bad id, unparseable output)
that id is marked `error` and no longer polled. An unrecognized status is
logged once and polled until the timeout. Status changes go to stderr, the final status
map is printed as JSON on stdout.

Observed on algobot-ai 2.1.0: about 10 minutes for 150 cases. Run this in the
background or with a long shell timeout.

Exit codes: 0 all completed, 1 any failed or cancelled, 2 timed out,
3 any awaiting_review (dataset needs review, then `experiments proceed`),
4 any id errored (checked first).
Read only.
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _algobot as ab  # noqa: E402

STOP_STATES = {"completed", "failed", "cancelled", "canceled", "awaiting_review"}
KNOWN_STATES = STOP_STATES | {"pending", "queued", "created", "resolving_profiles", "generating", "ready",
                              "running", "judging"}
MAX_CONSECUTIVE_FAILURES = 3
MAX_CALL_TIMEOUT = 300.0
CLOCK: Callable[[], float] = time.monotonic


def status_of(doc: Any) -> Optional[str]:
    if isinstance(doc, dict):
        if isinstance(doc.get("status"), str):
            return doc["status"].lower()
        for key in ("experiment", "data"):
            if isinstance(doc.get(key), dict) and isinstance(doc[key].get("status"), str):
                return doc[key]["status"].lower()
    return None


def poll_one(exp_id: str, profile: Optional[str], deadline: float) -> Tuple[str, str]:
    """Return ("ok", status), ("timeout", message) or ("fail", message).

    The call timeout is computed HERE, from the remaining wait: with more ids
    than poll workers, a second batch of the same round would otherwise start
    with a timeout computed before the first batch ran and blow past the
    deadline. A call whose turn comes after the deadline is skipped, not sent."""
    remaining = deadline - CLOCK()
    if remaining <= 0:
        return "timeout", "wait deadline already passed before this poll started"
    call_timeout = min(MAX_CALL_TIMEOUT, remaining)
    try:
        doc = ab.call(["evals", "experiments", "get", exp_id], profile=profile, retries=0, timeout=call_timeout)
    except ab.AlgobotError as exc:
        message = str(exc)
        if ab.is_timeout_message(message) or "local subprocess timeout" in message:
            return "timeout", message
        return "fail", message
    status = status_of(doc)
    if status is None:
        return "fail", "no status field in experiments get output"
    return "ok", status


def wait(ids: List[str], timeout: float, interval: float, profile: Optional[str]) -> Dict[str, str]:
    statuses = {i: "unknown" for i in ids}
    failures = {i: 0 for i in ids}
    logged_unknown = set()
    deadline = CLOCK() + timeout
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(ids)))) as pool:
        while True:
            pending = [i for i in ids if statuses[i] not in STOP_STATES and statuses[i] != "error"]
            results = list(pool.map(lambda i: poll_one(i, profile, deadline), pending))
            for exp_id, (kind, value) in zip(pending, results):
                if kind == "timeout":
                    ab.eprint("%s: CLI timeout, will retry" % exp_id)
                    continue
                if kind == "fail":
                    failures[exp_id] += 1
                    ab.eprint("%s: error %d of %d (%s)" % (exp_id, failures[exp_id], MAX_CONSECUTIVE_FAILURES, value[:200]))
                    if failures[exp_id] >= MAX_CONSECUTIVE_FAILURES:
                        statuses[exp_id] = "error"
                        ab.eprint("%s: giving up after %d consecutive errors" % (exp_id, MAX_CONSECUTIVE_FAILURES))
                    continue
                failures[exp_id] = 0
                if value not in KNOWN_STATES and value not in logged_unknown:
                    logged_unknown.add(value)
                    ab.eprint("%s: unrecognized status %r, polling until it stops or the timeout" % (exp_id, value))
                if value != statuses[exp_id]:
                    ab.eprint("%s: %s" % (exp_id, value))
                statuses[exp_id] = value
            if all(s in STOP_STATES or s == "error" for s in statuses.values()):
                return statuses
            if CLOCK() + interval > deadline:
                return statuses
            ab.SLEEP(interval)


def exit_code(statuses: Dict[str, str]) -> int:
    values = set(statuses.values())
    if "error" in values:
        return 4
    if not values <= STOP_STATES:
        return 2
    if values & {"failed", "cancelled", "canceled"}:
        return 1
    if "awaiting_review" in values:
        return 3
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ids", nargs="+", metavar="ID", help="experiment id(s)")
    parser.add_argument("--timeout", type=float, default=3600, help="maximum wait in seconds (default 3600)")
    parser.add_argument("--interval", type=float, default=30, help="seconds between polls (default 30)")
    parser.add_argument("--profile", "-p", help="algobot profile name (passed as --profile)")
    args = parser.parse_args(argv)
    ids = list(dict.fromkeys(args.ids))
    statuses = wait(ids, args.timeout, args.interval, args.profile)
    code = exit_code(statuses)
    print(json.dumps({"statuses": statuses, "timedOut": any(v not in STOP_STATES and v != "error" for v in statuses.values())},
                     indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
