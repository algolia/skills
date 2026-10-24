#!/usr/bin/env python3
"""Fetch one evaluation run into a local folder of JSON files.

Writes, under --out (default ./run-<runId>):
  meta.json        experiment id, run id, dataset and profile ids, counts
  experiment.json  `algobot evals experiments get <experimentId>`
  summary.json     `algobot evals runs summary <experimentId> <runId>`
  judgments.json   every verdict, paged with --limit 200 and --offset (stops
                   when a page adds no new judgment id, max 200 pages)
  cases/<evalCaseId>.json  `algobot evals runs case ...` per distinct case

Case files already on disk are reused (cache); pass --refresh to refetch.
Read only: nothing remote is created, changed or deleted.
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _algobot as ab  # noqa: E402

PAGE_SIZE = 200  # observed maximum for `runs judgments --limit` on 2.1.0
MAX_PAGES = 200  # guard: 40,000 judgments


def find_key(value: Any, key: str) -> Optional[Any]:
    """Depth-first search for the first occurrence of `key` in nested JSON."""
    if isinstance(value, dict):
        if key in value and value[key] not in (None, ""):
            return value[key]
        for child in value.values():
            found = find_key(child, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_key(child, key)
            if found is not None:
                return found
    return None


def judgment_key(j: Dict[str, Any]) -> str:
    if j.get("id") is not None:
        return "id:%s" % j["id"]
    return "k:%s|%s|%s" % (j.get("evalCaseId"), j.get("metricSlug"), json.dumps(j, sort_keys=True))


def fetch_judgments(experiment_id: str, run_id: str, profile: Optional[str],
                    max_pages: int = MAX_PAGES) -> List[Dict[str, Any]]:
    """Page with --limit/--offset. Stops on a short page, on a page that adds
    no new judgment (a server ignoring --offset would otherwise loop forever),
    or after max_pages (warned)."""
    items: List[Dict[str, Any]] = []
    seen = set()
    offset = 0
    for _ in range(max_pages):
        page = ab.judgments_list(
            ab.call(
                ["evals", "runs", "judgments", experiment_id, run_id,
                 "--limit", str(PAGE_SIZE), "--offset", str(offset)],
                profile=profile,
            )
        )
        new = [j for j in page if judgment_key(j) not in seen]
        for j in new:
            seen.add(judgment_key(j))
        items.extend(new)
        if len(page) < PAGE_SIZE:
            return items
        if not new:
            ab.eprint("warning: judgments page at offset %d added no new judgment ids; the server may be "
                      "ignoring --offset. Stopped paging with %d judgments." % (offset, len(items)))
            return items
        offset += PAGE_SIZE
    ab.eprint("warning: stopped after %d judgment pages (%d judgments); the run may be incomplete."
              % (max_pages, len(items)))
    return items


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiment_id", metavar="experimentId")
    parser.add_argument("run_id", metavar="runId")
    parser.add_argument("--out", help="output folder (default ./run-<runId>)")
    parser.add_argument("--profile", "-p", help="algobot profile name (passed as --profile)")
    parser.add_argument("--workers", type=int, default=4, help="parallel `runs case` calls (default 4)")
    parser.add_argument("--refresh", action="store_true", help="refetch case files already on disk")
    parser.add_argument("--skip-cases", action="store_true", help="only fetch summary and judgments")
    args = parser.parse_args(argv)

    out = args.out or "run-%s" % ab.safe_name(args.run_id)
    cases_dir = os.path.join(out, "cases")
    os.makedirs(cases_dir, exist_ok=True)

    experiment = ab.call(["evals", "experiments", "get", args.experiment_id], profile=args.profile)
    ab.write_json(os.path.join(out, "experiment.json"), experiment)
    summary = ab.call(["evals", "runs", "summary", args.experiment_id, args.run_id], profile=args.profile)
    ab.write_json(os.path.join(out, "summary.json"), summary)
    judgments = fetch_judgments(args.experiment_id, args.run_id, args.profile)
    ab.write_json(os.path.join(out, "judgments.json"), {"judgments": judgments})

    case_ids = sorted({str(j["evalCaseId"]) for j in judgments if j.get("evalCaseId")})
    fetched = 0
    cached = 0
    failed: List[str] = []

    def fetch_one(case_id: str) -> str:
        path = os.path.join(cases_dir, ab.safe_name(case_id) + ".json")
        if os.path.exists(path) and not args.refresh:
            return "cached"
        try:
            doc = ab.call(["evals", "runs", "case", args.experiment_id, args.run_id, case_id], profile=args.profile)
        except ab.AlgobotError as exc:
            ab.eprint("case %s: %s" % (case_id, exc))
            return "failed"
        ab.write_json(path, doc)
        return "fetched"

    if not args.skip_cases and case_ids:
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            for case_id, status in zip(case_ids, pool.map(fetch_one, case_ids)):
                if status == "fetched":
                    fetched += 1
                elif status == "cached":
                    cached += 1
                else:
                    failed.append(case_id)

    metrics: Dict[str, int] = {}
    for j in judgments:
        slug = str(j.get("metricSlug") or "unknown")
        metrics[slug] = metrics.get(slug, 0) + 1
    meta = {
        "experimentId": args.experiment_id,
        "runId": args.run_id,
        "datasetId": find_key(experiment, "datasetId"),
        "agentProfileId": find_key(experiment, "agentProfileId"),
        "indexProfileId": find_key(experiment, "indexProfileId"),
        "judgments": len(judgments),
        "judgmentsPerMetric": dict(sorted(metrics.items())),
        "distinctCases": len(case_ids),
        "casesFailedToFetch": sorted(failed),
    }
    ab.write_json(os.path.join(out, "meta.json"), meta)
    print("wrote %s: %d judgments, %d cases (%d fetched, %d cached, %d failed)"
          % (out, len(judgments), len(case_ids), fetched, cached, len(failed)))
    if meta["datasetId"] is None:
        print("note: no datasetId found in experiment.json; compare_runs.py cannot check dataset provenance")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
