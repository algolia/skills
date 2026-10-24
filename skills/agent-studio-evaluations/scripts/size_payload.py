#!/usr/bin/env python3
"""Rank the attributes of an Algolia search response by serialized size.

Reads a search response JSON from FILE or stdin (`-`), for example the output
of `algolia search <index> --query "<q>"` saved to a file. Accepts
{"hits": [...]}, {"results": [{"hits": [...]}]} (key case ignored), or a
bare array of hits.

Prints total bytes, mean bytes per hit, and every attribute ranked by mean
serialized bytes with its percent of the hits payload. `_highlightResult`,
`_snippetResult`, `_rankingInfo` and any attribute above --threshold percent
(default 5) are flagged as heavy. Ends with a suggested `searchParameters`
JSON for the agent's Search tool: a STARTING POINT TO REVIEW, not a drop-in.
`attributesToRetrieve` is never empty: when every attribute is heavy it falls
back to all non-underscore attributes and prints a manual-review warning.
A static `attributesToRetrieve` whitelist can override attributes the prompt
tells the agent to retrieve, and a low `hitsPerPage` may reduce recall.
Offline.
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

ALWAYS_HEAVY = ("_highlightResult", "_snippetResult", "_rankingInfo")


def size_of(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _get(doc: Dict[str, Any], key: str) -> Any:
    """Case-insensitive key lookup (some CLI JSON renderings capitalize `Hits`)."""
    for k, v in doc.items():
        if k.lower() == key:
            return v
    return None


def extract_hits(doc: Any) -> List[Dict[str, Any]]:
    if isinstance(doc, dict):
        if isinstance(_get(doc, "hits"), list):
            return [h for h in _get(doc, "hits") if isinstance(h, dict)]
        if isinstance(_get(doc, "results"), list):
            hits: List[Dict[str, Any]] = []
            for result in _get(doc, "results"):
                if isinstance(result, dict) and isinstance(_get(result, "hits"), list):
                    hits += [h for h in _get(result, "hits") if isinstance(h, dict)]
            return hits
    if isinstance(doc, list) and all(isinstance(h, dict) for h in doc):
        return doc  # a bare hits array, for example from --output="jsonpath={$.Hits}"
    raise SystemExit("input is not a search response: expected {hits: [...]} or {results: [{hits: [...]}]}")


def analyze(doc: Any, threshold: float = 5.0, hits_per_page: Optional[int] = None) -> Dict[str, Any]:
    hits = extract_hits(doc)
    n = len(hits)
    hits_bytes = sum(size_of(h) for h in hits)
    totals: Dict[str, int] = {}
    present: Dict[str, int] = {}
    for hit in hits:
        for key, value in hit.items():
            totals[key] = totals.get(key, 0) + size_of({key: value}) - 2
            present[key] = present.get(key, 0) + 1
    attrs = []
    for key, total in totals.items():
        pct = 100.0 * total / hits_bytes if hits_bytes else 0.0
        reasons = []
        if key in ALWAYS_HEAVY:
            reasons.append("metadata")
        if pct > threshold:
            reasons.append("above %g percent" % threshold)
        attrs.append({"attribute": key, "meanBytes": round(total / n, 1) if n else 0.0, "percent": round(pct, 2),
                      "presentInHits": present[key], "heavy": bool(reasons), "why": reasons})
    attrs.sort(key=lambda a: (-a["meanBytes"], a["attribute"]))
    keep = sorted(a["attribute"] for a in attrs if not a["heavy"] and not a["attribute"].startswith("_"))
    dropped = [a["attribute"] for a in attrs if a["heavy"] and a["attribute"] not in ALWAYS_HEAVY]
    warning = None
    if not keep:
        # Never suggest an empty whitelist: fall back to every non-metadata attribute.
        keep = sorted(a["attribute"] for a in attrs if not a["attribute"].startswith("_"))
        dropped = []
        warning = ("every attribute was flagged heavy, so attributesToRetrieve falls back to all non-underscore "
                   "attributes; this suggestion needs manual review")
        if not keep:
            keep = ["*"]
            warning = "no retrievable attribute found in the hits, so attributesToRetrieve is [\"*\"]; review manually"
    suggestion = {
        "hitsPerPage": hits_per_page if hits_per_page is not None else n,
        "attributesToRetrieve": keep,
        "attributesToHighlight": [],
        "attributesToSnippet": [],
    }
    return {"totalBytes": size_of(doc), "hits": n, "hitsBytes": hits_bytes,
            "meanBytesPerHit": round(hits_bytes / n, 1) if n else 0.0, "attributes": attrs,
            "excludedLargeAttributes": dropped, "suggestedSearchParameters": suggestion, "warning": warning}


def render(r: Dict[str, Any]) -> str:
    lines = ["# Search payload size", "",
             "- total bytes: %d" % r["totalBytes"],
             "- hits: %d, hits bytes: %d, mean bytes per hit: %.1f" % (r["hits"], r["hitsBytes"], r["meanBytesPerHit"]),
             "", "| attribute | mean bytes | percent of hits | in hits | flag |", "|---|---|---|---|---|"]
    for a in r["attributes"]:
        lines.append("| %s | %.1f | %.2f | %d | %s |" % (a["attribute"], a["meanBytes"], a["percent"], a["presentInHits"],
                                                       "HEAVY (%s)" % ", ".join(a["why"]) if a["heavy"] else ""))
    if r.get("warning"):
        lines += ["", "WARNING: %s." % r["warning"]]
    lines += ["", "## Suggested searchParameters (starting point to review, not a drop-in)", "",
              "```json", json.dumps(r["suggestedSearchParameters"], indent=2), "```", ""]
    if r["excludedLargeAttributes"]:
        lines.append("Left out of attributesToRetrieve because they are large: %s. Add back any attribute the agent"
                     % ", ".join(r["excludedLargeAttributes"]))
        lines.append("needs to answer (descriptions, prices, variants).")
    lines.append("Review before applying: a static attributesToRetrieve whitelist can override attributes the prompt")
    lines.append("tells the agent to retrieve, and a low hitsPerPage may reduce recall. Re-run the eval after the change.")
    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", nargs="?", default="-", metavar="FILE|-", help="search response JSON (default stdin)")
    parser.add_argument("--threshold", type=float, default=5.0, help="flag attributes above this percent (default 5)")
    parser.add_argument("--hits-per-page", type=int, help="hitsPerPage to suggest (default: hits in the response)")
    parser.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    args = parser.parse_args(argv)
    text = sys.stdin.read() if args.file == "-" else open(args.file, "r", encoding="utf-8").read()
    try:
        doc = json.loads(text)
    except ValueError as exc:
        raise SystemExit("input is not JSON: %s" % exc)
    result = analyze(doc, args.threshold, args.hits_per_page)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        sys.stdout.write(render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
