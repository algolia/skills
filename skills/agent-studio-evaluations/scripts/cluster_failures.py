#!/usr/bin/env python3
"""Cluster failing judgments of a fetched run into themes, per metric.

Reads DIR written by fetch_run.py. For every metric it prints the failure
count, keyword themes found in the judge reasons, and the most frequent
reasons. It raises an INSTRUMENT ARTIFACT warning when failing reasons talk
about internal logs, tool-call details, raw data, repeated text or
chain-of-thought. It applies only to LLM-judged metrics: `relevance`, and
any metric whose reasons look like `retrieval_recall=...`, are skipped. In our
runs that pattern meant the judge graded text the customer never sees, not
an agent defect. Verify before tuning prompts against it.

Offline: reads local files only.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _algobot as ab  # noqa: E402

THEMES: List[Tuple[str, str]] = [
    ("invented or unsupported facts", r"not supported|unsupported|invent|fabricat|hallucin|not (present|found) in (the )?(retrieved|records|context)|no evidence"),
    ("emoji", r"emoji"),
    ("exclamation marks", r"exclamation"),
    ("hype or slang", r"hype|slang|superlative|salesy|over-?enthusias|excit"),
    ("tone or voice mismatch", r"\btone\b|voice|formal|casual|style"),
    ("too long or verbose", r"verbose|too long|lengthy|wordy"),
    ("irrelevant or missing results", r"irrelevant|not relevant|missing (categor|keyword|result)|no results|does not (address|answer)"),
    ("tool use errors", r"wrong tool|tool error|failed to call|did not (call|use)|no tool"),
    ("guardrail or refusal", r"refus|declin|guardrail|block"),
    ("language mismatch", r"language|english|translat"),
]

# Phrases that, in our runs, meant the judge saw text the customer does not
# read. Deliberately narrow: bare "json", "duplicate" or "tool calls" alone
# are not enough.
ARTIFACT_RE = re.compile(
    r"\b(internal|system|debug|execution|raw) logs?\b|\blog (dump|output|lines)\b|"
    r"\btool[ _-]?call (logic|details|output|results|traces?|logs?)\b|"
    r"\braw (data|json|output|records?)\b|"
    r"\bchain[ -]of[ -]thought\b|\binternal (monologue|reasoning|notes)\b|\breasoning trace\b|"
    r"\brepeated (text|sections?|content|paragraphs?|blocks?)\b",
    re.IGNORECASE,
)
# Metrics scored by retrieval statistics, not an LLM judge reading the text.
RETRIEVAL_METRICS = {"relevance"}
RETRIEVAL_REASON_RE = re.compile(r"\b[a-z_]*(recall|precision|f1|ndcg|mrr)[a-z_]*\s*=\s*[0-9.]+", re.IGNORECASE)


def normalize_reason(reason: str) -> str:
    text = re.sub(r"\s+", " ", reason or "").strip()
    text = re.sub(r"\d+(\.\d+)?", "#", text)
    return text[:160]


def analyze(run: Dict[str, Any], top: int = 5) -> Dict[str, Any]:
    by_metric: Dict[str, Dict[str, Any]] = {}
    for j in run["judgments"]:
        slug = str(j.get("metricSlug") or "unknown")
        entry = by_metric.setdefault(slug, {"judged": 0, "failed": 0, "judgeErrors": 0, "themes": Counter(),
                                            "reasons": Counter(), "artifactCases": [], "retrievalReasons": 0})
        entry["judged"] += 1
        state = ab.passed_state(j)
        if state is None:
            # A judge error is infrastructure, not an agent failure: its reason
            # must not shape themes or trigger the instrument-artifact warning.
            entry["judgeErrors"] += 1
            continue
        if state:
            continue
        entry["failed"] += 1
        reason = str(j.get("reason") or "")
        for name, pattern in THEMES:
            if re.search(pattern, reason, re.IGNORECASE):
                entry["themes"][name] += 1
        entry["reasons"][normalize_reason(reason)] += 1
        if RETRIEVAL_REASON_RE.search(reason):
            entry["retrievalReasons"] += 1
        if ARTIFACT_RE.search(reason):
            entry["artifactCases"].append(str(j.get("evalCaseId") or ""))

    result: Dict[str, Any] = {"metrics": {}, "instrumentArtifact": None}
    artifact_total: List[Tuple[str, str]] = []
    for slug in sorted(by_metric):
        e = by_metric[slug]
        retrieval_based = slug in RETRIEVAL_METRICS or (e["failed"] and e["retrievalReasons"] * 2 >= e["failed"])
        if retrieval_based:
            e["artifactCases"] = []  # the detector only applies to LLM-judged metrics
        result["metrics"][slug] = {
            "artifactCheck": "skipped (retrieval-scored metric)" if retrieval_based else "applied",
            "judged": e["judged"],
            "failed": e["failed"],
            "judgeErrors": e["judgeErrors"],
            "themes": sorted(e["themes"].items(), key=lambda kv: (-kv[1], kv[0])),
            "topReasons": sorted(e["reasons"].items(), key=lambda kv: (-kv[1], kv[0]))[:top],
            "artifactReasonCount": len(e["artifactCases"]),
        }
        artifact_total += [(slug, c) for c in e["artifactCases"]]

    if artifact_total:
        differs = []
        for slug, case_id in artifact_total:
            comp = ab.completion(ab.case_for(run, case_id))
            if comp:
                rt = (comp.get("responseText") or "").strip()
                at = (comp.get("answerText") or "").strip()
                differs.append({"metric": slug, "evalCaseId": case_id, "responseTextDiffersFromAnswerText": rt != at,
                                "responseTextChars": len(rt), "answerTextChars": len(at)})
        result["instrumentArtifact"] = {
            "count": len(artifact_total),
            "examples": [{"metric": s, "evalCaseId": c} for s, c in sorted(artifact_total)[:5]],
            "caseTextCheck": sorted(differs, key=lambda d: (d["metric"], d["evalCaseId"]))[:10],
        }
    return result


def render(result: Dict[str, Any]) -> str:
    lines = ["# Failure themes", ""]
    for slug, m in result["metrics"].items():
        suffix = "" if not m["judgeErrors"] else " (+%d judge error(s) with no verdict, excluded)" % m["judgeErrors"]
        lines.append("## %s: %d of %d failed%s" % (slug, m["failed"], m["judged"], suffix))
        if m["failed"] == 0:
            lines += ["", "No failures.", ""]
            continue
        lines.append("")
        lines.append("Themes (keyword match on judge reasons, one reason can hit several):")
        if m["themes"]:
            for name, count in m["themes"]:
                lines.append("- %s: %d" % (name, count))
        else:
            lines.append("- no keyword theme matched, read the reasons below")
        lines.append("")
        lines.append("Top reasons:")
        for reason, count in m["topReasons"]:
            lines.append("- (%d) %s" % (count, reason))
        lines.append("")
    art = result.get("instrumentArtifact")
    if art:
        lines += [
            "## INSTRUMENT ARTIFACT warning",
            "",
            "%d failing reason(s) of LLM-judged metrics mention internal logs, tool-call details, raw data,"
            % art["count"],
            "repeated text or chain-of-thought.",
            "In our runs this meant the judge graded `completion.answerText` (prose plus display-tool",
            "argument values) rather than `completion.responseText` (what the customer reads).",
            "Do not tune prompts against these failures until verified:",
            "",
            "1. Open 2 of the cases below and compare `completion.responseText` with `completion.answerText`.",
            "2. If the customer-facing text is clean, re-judge it: `rescore_clean.py DIR --metric <slug>`",
            "   (prints the planned judge-call count; add `--yes` to spend them).",
            "3. A flip after a clean re-score still needs investigation: judge variability alone can produce",
            "   it. Treat a flip as an instrument artifact only when the original judge input was contaminated",
            "   (the case text check above shows the two texts differ).",
            "",
            "Examples:",
        ]
        for ex in art["examples"]:
            lines.append("- %s %s" % (ex["metric"], ex["evalCaseId"]))
        if art["caseTextCheck"]:
            lines.append("")
            lines.append("Case text check (from fetched case files):")
            for d in art["caseTextCheck"]:
                lines.append("- %s %s: responseText %d chars, answerText %d chars, differ=%s" % (
                    d["metric"], d["evalCaseId"], d["responseTextChars"], d["answerTextChars"],
                    "yes" if d["responseTextDiffersFromAnswerText"] else "no"))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dir", metavar="DIR", help="folder written by fetch_run.py")
    parser.add_argument("--top", type=int, default=5, help="top reasons per metric (default 5)")
    parser.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    args = parser.parse_args(argv)
    result = analyze(ab.load_run_dir(args.dir), top=args.top)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        sys.stdout.write(render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
