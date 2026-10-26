#!/usr/bin/env python3
"""Re-judge the customer-facing text of failing cases (instrument check).

For each failing judgment of --metric in DIR (a fetch_run.py folder), this
sends `completion.responseText` (what the customer reads) to
`algobot evals judge --metric-slug <m> --query ... --response-text ...
--expected <case expected>` and prints the stored score next to the clean
score. `evals judge` stores nothing, but every call is a paid judge call.

Cases with several stored iterations (same metric and evalCaseId) are
judged once: the stored verdict is aggregated first (score = mean,
passed = majority of iterations with a verdict). Judgments with
`passed: null` (judge error) are never re-judged and never count as
failures; they are listed separately.

Without --yes it only prints the planned judge-call count and exits 0.
--limit N caps the cases re-judged (and so the calls), after the
deduplication above. A judge call is never retried: a timeout is reported
as "unknown" and counted, so calls made never exceed the planned count.
Results are written to DIR/rescore-<metric>.json.

Limits: the judge sees only the last query and the text; prior turns of a
multi-turn case are not sent. Whether faithfulness, compliance or text
statistics are skewed by answerText vs responseText is not measured.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _algobot as ab  # noqa: E402


def plan(run: Dict[str, Any], metric: str, include_passing: bool, limit: Optional[int]) -> Dict[str, Any]:
    targets, skipped, judge_errors = [], [], []
    by_case: Dict[str, List[Dict[str, Any]]] = {}
    for j in sorted(run["judgments"], key=lambda x: str(x.get("evalCaseId"))):
        if str(j.get("metricSlug")) != metric or j.get("evalCaseId") is None:
            continue
        if ab.passed_state(j) is None:
            judge_errors.append({"evalCaseId": str(j["evalCaseId"]),
                                 "why": "stored judgment has no verdict (passed is null): a judge error, not a failure"})
            continue
        by_case.setdefault(str(j["evalCaseId"]), []).append(j)
    for case_id, items in by_case.items():
        verdicts = [ab.passed_state(j) for j in items]
        stored_passed = sum(1 for v in verdicts if v) * 2 > len(verdicts)  # tie counts as failed
        if stored_passed and not include_passing:
            continue
        doc = ab.case_for(run, case_id)
        comp = ab.completion(doc)
        query = (doc.get("case") or {}).get("query") if isinstance(doc, dict) else None
        text = comp.get("responseText")
        if not query or not text:
            skipped.append({"evalCaseId": case_id, "why": "case file missing, or no query/responseText"})
            continue
        targets.append({"evalCaseId": case_id, "query": query, "responseText": text,
                        "answerTextDiffers": (comp.get("answerText") or "").strip() != text.strip(),
                        "expected": ab.expected(doc),
                        "storedScore": ab.mean(s for s in (ab.score_of(j) for j in items) if s is not None),
                        "storedPassed": stored_passed, "iterations": len(items)})
    if limit is not None:
        targets = targets[:limit]
    return {"metric": metric, "targets": targets, "skipped": skipped, "judgeErrors": judge_errors}


def verdict_fields(value: Any) -> Dict[str, Any]:
    node = value
    if isinstance(value, dict):
        for key in ("judgment", "verdict", "result"):
            if isinstance(value.get(key), dict):
                node = value[key]
                break
    node = node if isinstance(node, dict) else {}
    return {"score": ab.score_of(node), "passed": node.get("passed"), "reason": node.get("reason")}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dir", metavar="DIR", help="folder written by fetch_run.py")
    parser.add_argument("--metric", required=True, help="metric slug to re-judge, for example tone")
    parser.add_argument("--yes", action="store_true", help="actually spend the judge calls")
    parser.add_argument("--include-passing", action="store_true", help="also re-judge passing cases")
    parser.add_argument("--limit", type=int, help="re-judge at most N cases")
    parser.add_argument("--profile", "-p", help="algobot profile name (passed as --profile)")
    args = parser.parse_args(argv)

    run = ab.load_run_dir(args.dir)
    p = plan(run, args.metric, args.include_passing, args.limit)
    n = len(p["targets"])
    print("planned judge calls: %d (metric %s, %d skipped without case text, %d judge error(s) not re-judged)"
          % (n, args.metric, len(p["skipped"]), len(p["judgeErrors"])))
    if not args.yes:
        print("dry plan only: re-run with --yes to spend %d judge call(s)." % n)
        return 0

    rows = []
    calls = 0
    unknown = 0
    errors = 0
    for t in p["targets"]:
        status = "judged"
        calls += 1
        try:
            # retries=0: a judge call is paid and not idempotent, so it is never re-sent.
            out = ab.call(["evals", "judge", "--metric-slug", args.metric, "--query", t["query"],
                           "--response-text", t["responseText"], "--expected", json.dumps(t["expected"], sort_keys=True)],
                          profile=args.profile, retries=0)
            v = verdict_fields(out)
        except ab.AlgobotError as exc:
            message = str(exc)
            if ab.is_timeout_message(message) or "local subprocess timeout" in message:
                status = "unknown (timeout, not re-sent)"
                unknown += 1
            else:
                status = "error"
                errors += 1
            v = {"score": None, "passed": None, "reason": "%s: %s" % (status, message[:300])}
        rows.append({"evalCaseId": t["evalCaseId"], "storedScore": t["storedScore"], "storedPassed": t["storedPassed"],
                     "cleanScore": v["score"], "cleanPassed": v["passed"], "cleanReason": v["reason"],
                     "status": status, "answerTextDiffers": t["answerTextDiffers"]})

    stored_failing = [r for r in rows if not r["storedPassed"]]
    flipped_rows = [r for r in stored_failing if r["cleanPassed"] is True]
    with_evidence = [r for r in flipped_rows if r["answerTextDiffers"]]
    print("")
    print("| evalCaseId | stored score | clean score | clean passed | status | answerText differs |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print("| %s | %s | %s | %s | %s | %s |" % (r["evalCaseId"], ab.fmt(r["storedScore"], 2), ab.fmt(r["cleanScore"], 2),
                                              r["cleanPassed"], r["status"], "yes" if r["answerTextDiffers"] else "no"))
    print("")
    print("judge calls made: %d of %d planned; %d unknown (timeout, not re-sent), %d error(s)" % (calls, n, unknown, errors))
    print("%d of %d stored-failing case(s) pass when judged on responseText." % (len(flipped_rows), len(stored_failing)))
    if flipped_rows:
        print("Investigate those flips before tuning against them: judge variability alone can produce them,")
        print("so a flip is NOT by itself evidence of an instrument artifact.")
    if with_evidence:
        print("%d flip(s) had responseText != answerText: the original judge likely graded the contaminated "
              "answerText, and only those flips support an instrument-artifact reading. Check the original "
              "judge input (answerTextDiffers) before excluding any failure from tuning." % len(with_evidence))
    ab.write_json(os.path.join(args.dir, "rescore-%s.json" % ab.safe_name(args.metric)),
                  {"metric": args.metric, "rows": rows, "skipped": p["skipped"], "judgeErrors": p["judgeErrors"],
                   "callsMade": calls, "plannedCalls": n, "unknown": unknown, "errors": errors,
                   "flips": len(flipped_rows), "flipsWithContaminatedInput": len(with_evidence)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
