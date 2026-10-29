#!/usr/bin/env python3
"""Triage a conversation export, then build dataset import rows from it.

Input: a JSON export (a list of conversations, or {"data": [...]}) where each
conversation has `messages: [{role, parts: [{type: "text", text}]}]`; a
message may carry a string `content` instead of parts.

Writes to --out:
  triage.json  provenance signals and a "looks scripted" / "looks organic" verdict
  rows.jsonl   one wide row per user turn, ready for
               `algobot evals datasets import --rows-jsonl rows.jsonl --validate-only`

Transform rules: eval-harness artifacts are dropped (conversation ids that
start with `eval-experiment_run_`, message ids that start with `evalcase-`),
history is the prior turns only and never ends on a user turn (import rejects
that), rows are deduplicated by (history, query). Only emails, phone numbers
and Luhn-valid card numbers are redacted: a manual PII review (names,
addresses, order ids) is still required before importing. Triage signals:
one-day creation concentration, repeated first turns, no user tokens, and a
median of one user turn per conversation (ISO or epoch timestamps).
Every row carries `faithfulness` with a `fact_type` from a small keyword map (generic fallback, rate printed) and
`tone` when --tone-contract is given. A wide row becomes one case per metric:
the case count is printed. The export and rows.jsonl hold user text: keep
them in a temp folder and delete both after the import. Offline.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _algobot as ab  # noqa: E402

FACT_TYPES: List[Tuple[str, str]] = [
    ("shipping_policy", r"\b(ship|ships|shipping|shipped|deliver\w*|tracking|dispatch\w*)\b"),
    ("return_policy", r"\b(return\w*|refund\w*|exchang\w*)\b"),
    ("sizing", r"\b(size|sizes|sizing|fit|fits|fitting)\b"),
    ("pricing", r"\b(price\w*|cost\w*|cheap\w*|expensive|discount\w*|sales?|promo\w*|coupons?)\b"),
    ("availability", r"\b(in stock|stock|availab\w*|sold out|restock\w*)\b"),
    ("care_instructions", r"\b(wash\w*|clean\w*|care|dry clean\w*|iron\w*)\b"),
    ("materials", r"\b(materials?|fabrics?|cotton|wool|leather|ingredients?)\b"),
    ("product_attributes", r"\b(colou?rs?|dimensions?|weight|features?|specs?|specifications?)\b"),
    ("store_information", r"\b(stores?|opening hours|locations?|near me)\b"),
]
FALLBACK_FACT_TYPE = "product_information"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CARD_CANDIDATE_RE = re.compile(r"(?<![\w-])\d(?:[ -]?\d){12,18}(?![\w-])")
PHONE_CANDIDATE_RE = re.compile(r"(?<![\w-])(?:\+|\()?\d[\d ().-]{5,}\d(?![\w-])")
ISO_DATE_RE = re.compile(r"\d{4}-\d{1,2}-\d{1,2}")
YEAR_RANGE_RE = re.compile(r"^(19|20)\d{2}\s*[-/]\s*(19|20)?\d{2}$")
PII_NOTICE = ("Redaction covers only emails, phone numbers and card-like numbers (Luhn-checked). "
              "Review rows.jsonl manually for names, addresses, order ids and other PII before importing.")

USER_TOKEN_KEYS = ("userToken", "user_token", "secureUserToken", "userId", "user_id")
DATE_KEYS = ("createdAt", "created_at", "startedAt", "started_at", "timestamp")


def load_export(path: str) -> List[Dict[str, Any]]:
    data = ab.load_json(path)
    if isinstance(data, dict):
        for key in ("data", "conversations", "items"):
            if isinstance(data.get(key), list):
                return data[key]
        return [data]
    return data if isinstance(data, list) else []


def message_text(message: Dict[str, Any]) -> str:
    parts = message.get("parts")
    if isinstance(parts, list):
        texts = [str(p.get("text") or "") for p in parts if isinstance(p, dict) and p.get("type") == "text"]
        text = "\n".join(t for t in texts if t)
        if text:
            return text.strip()
    content = message.get("content")
    return content.strip() if isinstance(content, str) else ""


# Matches MAX_TURN_CONTEXT_CHARS in conversational-ai
# (common/data/external_evals/importing.py): the import rejects a row whose
# turnContext serializes to more canonical-JSON characters than this budget.
TURN_CONTEXT_MAX_CHARS = 20_000


def canonical_turn_context_json(context: Dict[str, Any]) -> str:
    """Mirror the importer's canonical serialization (server: importing.py).

    Keys sorted, no whitespace, ASCII escapes, NaN rejected, and `</` escaped
    so no value can forge a closing `</turn_context>` tag. The 20k budget is
    measured against THIS serialization, not json.dumps defaults.
    """
    return json.dumps(
        context, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).replace("</", "<\\/")


def redact_turn_context(value: Any) -> Tuple[Any, int]:
    """Recursively redact every string leaf of a turn context (PII invariant)."""
    if isinstance(value, dict):
        out: Dict[str, Any] = {}
        hits = 0
        for k, v in value.items():
            out[k], h = redact_turn_context(v)
            hits += h
        return out, hits
    if isinstance(value, list):
        out_list: List[Any] = []
        hits = 0
        for v in value:
            new_v, h = redact_turn_context(v)
            out_list.append(new_v)
            hits += h
        return out_list, hits
    if isinstance(value, str):
        return redact(value)
    return value, 0


def message_turn_context(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract the turnContext the agent saw when this user turn was asked.

    GET /conversations returns it as a flat parsed object on user messages;
    some exports nest it under metadata. Returns None when absent (never {}).
    """
    raw = message.get("turnContext")
    if raw is None and isinstance(message.get("metadata"), dict):
        raw = message["metadata"].get("turnContext")
    return raw if isinstance(raw, dict) and raw else None


def is_eval_artifact(conv: Dict[str, Any]) -> bool:
    cid = str(conv.get("id") or conv.get("conversationId") or "")
    if cid.startswith("eval-experiment_run_"):
        return True
    return any(str(m.get("id") or m.get("messageId") or "").startswith("evalcase-") for m in conv.get("messages") or [])


def luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def looks_like_phone(candidate: str) -> bool:
    digits = re.sub(r"\D", "", candidate)
    if not 7 <= len(digits) <= 15:
        return False
    if ISO_DATE_RE.search(candidate) or YEAR_RANGE_RE.match(candidate.strip()):
        return False
    has_plus_or_paren = candidate.startswith("+") or "(" in candidate
    groups = re.findall(r"\d+", candidate)
    if not has_plus_or_paren and len(groups) < 2:
        return False  # a bare digit run (order number, product code) has no phone shape
    if len(groups) >= 3 and all(len(g) <= 3 for g in groups):
        values = [int(g) for g in groups]
        steps = {b - a for a, b in zip(values, values[1:])}
        if len(steps) == 1 and 0 < abs(next(iter(steps))) <= 4:
            return False  # a size list such as "32 34 36 38"
    return True


def redact(text: str) -> Tuple[str, int]:
    hits = 0

    def sub_email(m: "re.Match[str]") -> str:
        nonlocal hits
        hits += 1
        return "[EMAIL]"

    def sub_card(m: "re.Match[str]") -> str:
        nonlocal hits
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 19 and luhn_ok(digits):
            hits += 1
            return "[CARD]"
        return m.group(0)

    def sub_phone(m: "re.Match[str]") -> str:
        nonlocal hits
        if looks_like_phone(m.group(0)):
            hits += 1
            return "[PHONE]"
        return m.group(0)

    text = EMAIL_RE.sub(sub_email, text)
    text = CARD_CANDIDATE_RE.sub(sub_card, text)
    text = PHONE_CANDIDATE_RE.sub(sub_phone, text)
    return text, hits


def day_of(value: Any) -> Optional[str]:
    """Bucket an ISO string or epoch seconds/milliseconds (number or digit string) into YYYY-MM-DD."""
    if isinstance(value, bool) or value is None or value == "":
        return None
    number: Optional[float] = None
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str) and re.fullmatch(r"\d{9,13}(\.\d+)?", value.strip()):
        number = float(value.strip())
    if number is not None:
        if number > 1e11:
            number /= 1000.0
        try:
            return datetime.fromtimestamp(number, tz=timezone.utc).strftime("%Y-%m-%d")
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value)
    return text[:10] if re.match(r"\d{4}-\d{2}-\d{2}", text) else None


def fact_type(query: str) -> Optional[str]:
    for name, pattern in FACT_TYPES:
        if re.search(pattern, query, re.IGNORECASE):
            return name
    return None


def triage(convs: List[Dict[str, Any]]) -> Dict[str, Any]:
    days: Counter = Counter()
    first_turns: Counter = Counter()
    with_token = 0
    turns = []
    for conv in convs:
        for key in DATE_KEYS:
            day = day_of(conv.get(key))
            if day:
                days[day] += 1
                break
        if any(conv.get(k) for k in USER_TOKEN_KEYS):
            with_token += 1
        user_msgs = [message_text(m) for m in conv.get("messages") or [] if m.get("role") == "user"]
        user_msgs = [t for t in user_msgs if t]
        turns.append(len(user_msgs))
        if user_msgs:
            first_turns[re.sub(r"\s+", " ", user_msgs[0].lower())] += 1
    n = len(convs)
    top_day, top_day_count = (days.most_common(1)[0] if days else (None, 0))
    total_first = sum(first_turns.values())
    dup_rate = 1 - (len(first_turns) / total_first) if total_first else 0.0
    signals = []
    top_share = top_day_count / n if n else 0.0
    if n >= 20 and top_share >= 0.5:
        signals.append("%.0f percent of conversations were created on one day" % (100 * top_share))
    if dup_rate >= 0.3:
        signals.append("%.0f percent of first user turns are repeats" % (100 * dup_rate))
    if n and with_token == 0:
        signals.append("no conversation carries a user token")
    median_turns = ab.median(turns) or 0.0
    if n >= 20 and median_turns <= 1:
        signals.append("the median conversation has %g user turn(s)" % median_turns)
    verdict = "looks scripted" if len(signals) >= 2 else ("mixed, review manually" if signals else "looks organic")
    return {
        "conversations": n,
        "creationDays": len(days), "topDay": top_day, "topDayShare": round(top_share, 4),
        "distinctFirstTurns": len(first_turns), "duplicateFirstTurnRate": round(dup_rate, 4),
        "maxFirstTurnRepeats": first_turns.most_common(1)[0][1] if first_turns else 0,
        "userTokenCoverage": round(with_token / n, 4) if n else 0.0,
        "userTurnsMean": round(ab.mean(turns) or 0.0, 3), "userTurnsMedian": median_turns,
        "signals": signals, "verdict": verdict,
    }


def build_rows(convs: List[Dict[str, Any]], tone: Optional[Dict[str, Any]], language: str) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    rows: List[Dict[str, Any]] = []
    seen = set()
    stats = {"userTurns": 0, "duplicates": 0, "piiRedactions": 0, "fallbackFactType": 0, "trimmedUserTurns": 0, "turnContextRows": 0, "turnContextOversized": 0}
    for conv in convs:
        history: List[Dict[str, str]] = []
        for m in conv.get("messages") or []:
            role = m.get("role")
            if role not in ("user", "assistant"):
                continue
            text, hits = redact(message_text(m))
            stats["piiRedactions"] += hits
            if not text:
                continue
            if role == "user":
                stats["userTurns"] += 1
                turn_context = message_turn_context(m)
                if turn_context is not None:
                    turn_context, ctx_hits = redact_turn_context(turn_context)
                    stats["piiRedactions"] += ctx_hits
                    if len(canonical_turn_context_json(turn_context)) > TURN_CONTEXT_MAX_CHARS:
                        stats["turnContextOversized"] += 1
                        turn_context = None
                    else:
                        stats["turnContextRows"] += 1
                prior = list(history)
                while prior and prior[-1]["role"] == "user":
                    prior.pop()
                    stats["trimmedUserTurns"] += 1
                context_key = canonical_turn_context_json(turn_context) if turn_context else "null"
                key = (json.dumps(prior, sort_keys=True), text, context_key)
                if key in seen:
                    stats["duplicates"] += 1
                else:
                    seen.add(key)
                    ft = fact_type(text)
                    if ft is None:
                        stats["fallbackFactType"] += 1
                        ft = FALLBACK_FACT_TYPE
                    metrics: Dict[str, Any] = {"faithfulness": {"fact_type": ft}}
                    if tone is not None:
                        metrics["tone"] = dict(tone)
                    row: Dict[str, Any] = {"query": text, "metrics": metrics, "difficulty": "medium", "language": language}
                    if prior:
                        row["messages"] = prior
                    if turn_context is not None:
                        row["turnContext"] = turn_context
                    rows.append(row)
            history.append({"role": role, "content": text})
    return rows, stats


def load_tone_contract(path: str) -> Dict[str, Any]:
    contract = ab.load_json(path)
    if not isinstance(contract, dict) or not contract.get("tone_constraint"):
        raise SystemExit("%s: tone contract must be a JSON object with a non-empty tone_constraint" % path)
    if not isinstance(contract.get("bad_response_patterns", []), list):
        raise SystemExit("%s: bad_response_patterns must be a list of strings" % path)
    return contract


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from-json", required=True, metavar="export.json", help="conversation export JSON")
    parser.add_argument("--out", required=True, metavar="DIR", help="output folder for rows.jsonl and triage.json")
    parser.add_argument("--tone-contract", metavar="FILE", help="JSON with tone_constraint and bad_response_patterns")
    parser.add_argument("--language", default="en", help="row language (default en)")
    args = parser.parse_args(argv)

    tone = load_tone_contract(args.tone_contract) if args.tone_contract else None
    raw = load_export(args.from_json)
    convs = [c for c in raw if isinstance(c, dict) and not is_eval_artifact(c)]
    tri = triage(convs)
    tri["evalArtifactsDropped"] = len(raw) - len(convs)
    rows, stats = build_rows(convs, tone, args.language)
    metrics_per_row = 2 if tone is not None else 1
    tri["rows"] = len(rows)
    tri["transform"] = stats
    tri["casesAfterImport"] = len(rows) * metrics_per_row
    tri["fallbackFactTypeRate"] = round(stats["fallbackFactType"] / len(rows), 4) if rows else 0.0

    os.makedirs(args.out, exist_ok=True)
    ab.write_json(os.path.join(args.out, "triage.json"), tri)
    with open(os.path.join(args.out, "rows.jsonl"), "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    print("triage: %s (%d conversations, %d eval artifacts dropped)" % (tri["verdict"], tri["conversations"], tri["evalArtifactsDropped"]))
    for s in tri["signals"]:
        print("  - %s" % s)
    print("rows: %d (%d duplicates removed, %d trailing user turns trimmed from history, %d PII redactions)"
          % (len(rows), stats["duplicates"], stats["trimmedUserTurns"], stats["piiRedactions"]))
    print("fact_type fallback (%s) rate: %.1f percent" % (FALLBACK_FACT_TYPE, 100 * tri["fallbackFactTypeRate"]))
    print("wide rows: %d metric(s) per row, the import will create %d cases" % (metrics_per_row, tri["casesAfterImport"]))
    if tri["verdict"] != "looks organic":
        print("warning: this history may not be real user traffic; review triage.json before importing")
    print(PII_NOTICE)
    print("reminder: delete %s and %s after the import" % (args.from_json, os.path.join(args.out, "rows.jsonl")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
