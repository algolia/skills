#!/usr/bin/env python3
"""Compare two fetched runs on SHARED cases only (A = baseline, B = candidate).

Reads two folders written by fetch_run.py. Per metric it uses only the
evalCaseIds judged in both runs, then prints pass counts, mean score and the
paired deltas (B - A). Two separate 95 percent intervals are reported, one
for the paired pass-rate delta and one for the paired mean-score delta, both
from a paired percentile bootstrap (fixed seed, deterministic). Below 50
shared cases a metric is underpowered: its "CI excludes 0" is reported as
n/a, never as significant. It also prints mean and median input tokens,
output tokens and duration per run, and the tone pass rate grouped by each
case's `expected.tone_constraint`.

Judgments with `passed: null` (judge error) are excluded from pass counts
and shown in an errors column. When a run holds several judgments for the
same (metric, case), for example several iterations, they are aggregated:
score = mean of the iteration scores, passed = more than half of the
iterations with a verdict passed (a tie counts as failed).

Runs on different datasets, or a run whose meta.json has no datasetId, are
refused (exit 2) unless --allow-different-datasets is passed. Offline.
"""

import argparse
import json
import os
import random
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _algobot as ab  # noqa: E402

UNDERPOWERED_N = 50
CI_METHOD = "paired percentile bootstrap, %d resamples, seed %d"
Key = Tuple[str, str]


def index_judgments(run: Dict[str, Any]) -> Tuple[Dict[Key, Dict[str, Any]], int]:
    """Return {(metric, caseId): aggregated verdict} and the number of keys
    that had more than one judgment."""
    groups: Dict[Key, List[Dict[str, Any]]] = {}
    for j in run["judgments"]:
        if j.get("evalCaseId") is None:
            continue
        groups.setdefault((str(j.get("metricSlug") or "unknown"), str(j["evalCaseId"])), []).append(j)
    out: Dict[Key, Dict[str, Any]] = {}
    multi = 0
    for key, items in groups.items():
        if len(items) > 1:
            multi += 1
        scores = [s for s in (ab.score_of(j) for j in items) if s is not None]
        verdicts = [v for v in (ab.passed_state(j) for j in items) if v is not None]
        passed: Optional[bool] = None
        if verdicts:
            passed = sum(1 for v in verdicts if v) * 2 > len(verdicts)
        out[key] = {"passed": passed, "score": ab.mean(scores), "iterations": len(items)}
    return out, multi


def bootstrap_ci(diffs: Sequence[float], resamples: int, seed: int) -> Tuple[Optional[float], Optional[float]]:
    n = len(diffs)
    if n == 0:
        return None, None
    rng = random.Random(seed)
    means = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(n):
            total += diffs[rng.randrange(n)]
        means.append(total / n)
    means.sort()
    lo = means[int(0.025 * (resamples - 1))]
    hi = means[int(round(0.975 * (resamples - 1)))]
    return lo, hi


def excludes_zero(lo: Optional[float], hi: Optional[float], n: int) -> Optional[bool]:
    """None (n/a) when underpowered or the interval is missing or degenerate."""
    if n < UNDERPOWERED_N or lo is None or hi is None or lo == hi:
        return None
    return lo > 0 or hi < 0


def efficiency(run: Dict[str, Any], case_ids: Optional[set] = None) -> Dict[str, Any]:
    inputs, outputs, durations = [], [], []
    for case_id, doc in sorted(run["cases"].items()):
        if case_ids is not None and case_id not in case_ids:
            continue
        comp = ab.completion(doc)
        usage = comp.get("usage") or {}
        if isinstance(usage.get("inputTokens"), (int, float)):
            inputs.append(float(usage["inputTokens"]))
        if isinstance(usage.get("outputTokens"), (int, float)):
            outputs.append(float(usage["outputTokens"]))
        if isinstance(comp.get("durationMs"), (int, float)):
            durations.append(float(comp["durationMs"]))
    return {
        "cases": len(inputs),
        "inputTokensMean": ab.mean(inputs), "inputTokensMedian": ab.median(inputs),
        "outputTokensMean": ab.mean(outputs), "outputTokensMedian": ab.median(outputs),
        "durationMsMean": ab.mean(durations), "durationMsMedian": ab.median(durations),
    }


def compare(run_a: Dict[str, Any], run_b: Dict[str, Any], resamples: int = 2000, seed: int = 7) -> Dict[str, Any]:
    ja, multi_a = index_judgments(run_a)
    jb, multi_b = index_judgments(run_b)
    metrics = sorted({m for m, _ in ja} | {m for m, _ in jb})
    result: Dict[str, Any] = {"ciMethod": CI_METHOD % (resamples, seed), "metrics": {}, "efficiency": {},
                              "toneByContract": [], "aggregatedKeys": {"A": multi_a, "B": multi_b}}
    shared_case_ids = set()
    for metric in metrics:
        a_ids = {c for m, c in ja if m == metric}
        b_ids = {c for m, c in jb if m == metric}
        shared = sorted(a_ids & b_ids)
        shared_case_ids |= {ab.safe_name(c) for c in shared}
        errors_a = sum(1 for c in shared if ja[(metric, c)]["passed"] is None)
        errors_b = sum(1 for c in shared if jb[(metric, c)]["passed"] is None)
        judged = [c for c in shared if ja[(metric, c)]["passed"] is not None and jb[(metric, c)]["passed"] is not None]
        pass_a = sum(1 for c in judged if ja[(metric, c)]["passed"])
        pass_b = sum(1 for c in judged if jb[(metric, c)]["passed"])
        pass_diffs = [float(jb[(metric, c)]["passed"]) - float(ja[(metric, c)]["passed"]) for c in judged]
        score_pairs = [(ja[(metric, c)]["score"], jb[(metric, c)]["score"]) for c in shared]
        score_pairs = [(a, b) for a, b in score_pairs if a is not None and b is not None]
        score_diffs = [b - a for a, b in score_pairs]
        n = len(judged)
        p_lo, p_hi = bootstrap_ci(pass_diffs, resamples, seed)
        s_lo, s_hi = bootstrap_ci(score_diffs, resamples, seed)
        result["metrics"][metric] = {
            "onlyInA": len(a_ids - b_ids), "onlyInB": len(b_ids - a_ids), "sharedCases": len(shared),
            "judgedPairs": n, "errorsA": errors_a, "errorsB": errors_b,
            "passedA": pass_a, "passedB": pass_b,
            "passRateA": pass_a / n if n else None, "passRateB": pass_b / n if n else None,
            "passRateDelta": ab.mean(pass_diffs), "passRateDeltaCI95": [p_lo, p_hi],
            "passRateCiExcludesZero": excludes_zero(p_lo, p_hi, n),
            "meanScoreA": ab.mean(a for a, _ in score_pairs), "meanScoreB": ab.mean(b for _, b in score_pairs),
            "meanScoreDelta": ab.mean(score_diffs), "meanScoreDeltaCI95": [s_lo, s_hi],
            "meanScoreCiExcludesZero": excludes_zero(s_lo, s_hi, len(score_diffs)),
            "underpowered": n < UNDERPOWERED_N,
        }
    result["efficiency"] = {
        "A_allFetchedCases": efficiency(run_a), "B_allFetchedCases": efficiency(run_b),
        "A_sharedCases": efficiency(run_a, shared_case_ids), "B_sharedCases": efficiency(run_b, shared_case_ids),
    }
    groups: Dict[str, List[int]] = {}
    for metric, case_id in sorted(ja):
        if metric != "tone" or (metric, case_id) not in jb:
            continue
        va, vb = ja[(metric, case_id)]["passed"], jb[(metric, case_id)]["passed"]
        if va is None or vb is None:
            continue
        doc = ab.case_for(run_a, case_id) or ab.case_for(run_b, case_id)
        contract = str(ab.expected(doc).get("tone_constraint") or "(contract not fetched)")
        g = groups.setdefault(contract, [0, 0, 0])
        g[0] += 1
        g[1] += int(va)
        g[2] += int(vb)
    for contract in sorted(groups):
        n, pa, pb = groups[contract]
        result["toneByContract"].append({"toneConstraint": contract, "sharedCases": n, "passedA": pa, "passedB": pb})
    return result


def yes_no(value: Optional[bool]) -> str:
    return "n/a" if value is None else ("yes" if value else "no")


def render(result: Dict[str, Any], meta_a: Dict[str, Any], meta_b: Dict[str, Any]) -> str:
    lines = ["# Run comparison (A = baseline, B = candidate, deltas B - A)", ""]
    lines.append("- dataset A: %s, dataset B: %s" % (meta_a.get("datasetId") or "unknown", meta_b.get("datasetId") or "unknown"))
    lines.append("- CI method: %s. Two separate 95 percent intervals: one for the paired pass-rate delta, "
                 "one for the paired mean-score delta" % result["ciMethod"])
    lines.append("- underpowered: fewer than %d judged pairs; CI excludes 0 is then n/a (directional only)" % UNDERPOWERED_N)
    lines.append("- judge errors (passed = null) are excluded from pass counts and shown as errors A/B")
    agg = result["aggregatedKeys"]
    if agg["A"] or agg["B"]:
        lines.append("- aggregated repeated judgments (iterations): %d keys in A, %d in B; score = mean, "
                     "passed = more than half of iterations passed (tie = failed)" % (agg["A"], agg["B"]))
    lines.append("")
    lines.append("| metric | shared | errors A/B | pass A | pass B | delta pass rate [95% CI] | pass CI excl. 0 "
                 "| mean A | mean B | delta mean score [95% CI] | score CI excl. 0 | note |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for metric, m in result["metrics"].items():
        notes = []
        if m["underpowered"]:
            notes.append("underpowered")
        if m["onlyInA"] or m["onlyInB"]:
            notes.append("excluded %d A-only, %d B-only" % (m["onlyInA"], m["onlyInB"]))
        lines.append("| %s | %d | %d/%d | %d | %d | %s [%s, %s] | %s | %s | %s | %s [%s, %s] | %s | %s |" % (
            metric, m["sharedCases"], m["errorsA"], m["errorsB"], m["passedA"], m["passedB"],
            ab.fmt(m["passRateDelta"]), ab.fmt(m["passRateDeltaCI95"][0]), ab.fmt(m["passRateDeltaCI95"][1]),
            yes_no(m["passRateCiExcludesZero"]),
            ab.fmt(m["meanScoreA"]), ab.fmt(m["meanScoreB"]),
            ab.fmt(m["meanScoreDelta"]), ab.fmt(m["meanScoreDeltaCI95"][0]), ab.fmt(m["meanScoreDeltaCI95"][1]),
            yes_no(m["meanScoreCiExcludesZero"]), ", ".join(notes)))
    lines += ["", "## Efficiency per case", "",
              "| run | cases | input tokens mean | input median | output tokens mean | output median | duration ms mean | duration median |",
              "|---|---|---|---|---|---|---|---|"]
    for label, e in result["efficiency"].items():
        lines.append("| %s | %d | %s | %s | %s | %s | %s | %s |" % (
            label, e["cases"], ab.fmt(e["inputTokensMean"], 0), ab.fmt(e["inputTokensMedian"], 0),
            ab.fmt(e["outputTokensMean"], 0), ab.fmt(e["outputTokensMedian"], 0),
            ab.fmt(e["durationMsMean"], 0), ab.fmt(e["durationMsMedian"], 0)))
    if result["toneByContract"]:
        lines += ["", "## Tone pass rate by contract (shared, judged cases)", "",
                  "| tone_constraint | shared | pass A | pass B |", "|---|---|---|---|"]
        for g in result["toneByContract"]:
            lines.append("| %s | %d | %d | %d |" % (g["toneConstraint"].replace("|", "/")[:120], g["sharedCases"], g["passedA"], g["passedB"]))
    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dir_a", metavar="DIR_A", help="baseline run folder (fetch_run.py)")
    parser.add_argument("dir_b", metavar="DIR_B", help="candidate run folder (fetch_run.py)")
    parser.add_argument("--resamples", type=int, default=2000, help="bootstrap resamples (default 2000)")
    parser.add_argument("--seed", type=int, default=7, help="bootstrap seed (default 7)")
    parser.add_argument("--allow-different-datasets", action="store_true",
                        help="compare even when the dataset ids differ or are missing from meta.json")
    parser.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    args = parser.parse_args(argv)
    run_a, run_b = ab.load_run_dir(args.dir_a), ab.load_run_dir(args.dir_b)
    ds_a, ds_b = run_a["meta"].get("datasetId"), run_b["meta"].get("datasetId")
    if not args.allow_different_datasets:
        if not ds_a or not ds_b:
            ab.eprint("refusing to compare: datasetId missing from meta.json (A: %s, B: %s), so dataset provenance "
                      "cannot be checked. Re-fetch with fetch_run.py, or pass --allow-different-datasets."
                      % (ds_a or "missing", ds_b or "missing"))
            return 2
        if ds_a != ds_b:
            ab.eprint("refusing to compare: runs use different datasets (%s vs %s). "
                      "Re-run both agents with the same --dataset-id." % (ds_a, ds_b))
            return 2
    result = compare(run_a, run_b, resamples=args.resamples, seed=args.seed)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        sys.stdout.write(render(result, run_a["meta"], run_b["meta"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
