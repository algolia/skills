"""Shared helpers for the agent-studio-evaluations scripts.

Stdlib only, Python 3.9+. The only network access any script performs goes
through `call()`, which shells out to the `algobot` CLI. Tests replace
`RUNNER` with a fake so no subprocess is ever started.

Behavior observed on algobot-ai 2.1.0 (the evals endpoints are experimental):
- output may carry ANSI colors or log lines before the JSON body, so the
  last well-formed top-level JSON object (or non-trivial array) is used;
- the CLI sometimes prints "operation was aborted due to timeout" even though
  the call went through, so a read is retried when that message appears and
  no JSON could be parsed.

Only use `call()` for READ commands. Retrying a mutation could apply it twice.
"""

import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

ALGOBOT_BIN = os.environ.get("ALGOBOT_BIN", "algobot")
TIMEOUT_MARKER = "operation was aborted due to timeout"
_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07")

# Replaced in tests. Signature mirrors subprocess.run.
RUNNER: Callable[..., Any] = subprocess.run
SLEEP: Callable[[float], None] = time.sleep


class AlgobotError(RuntimeError):
    """Raised when algobot fails or prints no parseable JSON."""


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text or "")


def _acceptable(value: Any, rest: str) -> bool:
    """A dict is always a payload. A list is one only when it holds objects or
    arrays, or when nothing but whitespace follows it (so a stray `[2]` in a
    log line is never taken for the payload)."""
    if isinstance(value, dict):
        return True
    if isinstance(value, list):
        if any(isinstance(v, (dict, list)) for v in value):
            return True
        return rest.strip() == ""
    return False


def extract_json(text: str) -> Any:
    """Return the LAST well-formed top-level JSON object or array in `text`.

    Log lines, ANSI colors and tokens such as `[INFO]` or `[2]` before the
    payload are ignored."""
    clean = strip_ansi(text)
    decoder = json.JSONDecoder()
    found = []
    pos = 0
    while True:
        match = re.compile(r"[\[{]").search(clean, pos)
        if not match:
            break
        start = match.start()
        try:
            value, end = decoder.raw_decode(clean, start)
        except ValueError:
            pos = start + 1
            continue
        if _acceptable(value, clean[end:]):
            found.append(value)
            pos = end
        else:
            pos = start + 1
    if not found:
        raise ValueError("no JSON value found in output")
    return found[-1]


def is_timeout_message(text: str) -> bool:
    return TIMEOUT_MARKER in (text or "").lower()


def build_command(
    args: Sequence[str], profile: Optional[str] = None, agent_id: Optional[str] = None
) -> List[str]:
    """Global flags go before the subcommand (`-p` collides with `--page`)."""
    cmd = [ALGOBOT_BIN]
    if profile:
        cmd += ["--profile", profile]
    if agent_id:
        cmd += ["--agent", agent_id]
    cmd += list(args)
    return cmd


def call(
    args: Sequence[str],
    profile: Optional[str] = None,
    agent_id: Optional[str] = None,
    retries: int = 3,
    backoff: float = 2.0,
    timeout: Optional[float] = 300,
) -> Any:
    """Run a read-only algobot command and return its parsed JSON output."""
    cmd = build_command(args, profile, agent_id)
    env = dict(os.environ)
    env["NO_COLOR"] = "1"
    env["FORCE_COLOR"] = "0"
    last_error = ""
    for attempt in range(retries + 1):
        try:
            proc = RUNNER(cmd, capture_output=True, text=True, env=env, timeout=timeout)
        except FileNotFoundError as exc:
            raise AlgobotError(
                "algobot not found on PATH (npm i -g algobot-ai, version >= 2.1.0)"
            ) from exc
        except subprocess.TimeoutExpired:
            last_error = "local subprocess timeout"
            if attempt < retries:
                SLEEP(backoff * (attempt + 1))
                continue
            break
        out = proc.stdout or ""
        err = proc.stderr or ""
        try:
            value = extract_json(out)
        except ValueError:
            value = None
        if value is not None and (proc.returncode == 0 or is_timeout_message(out + err)):
            return value
        combined = strip_ansi(out + "\n" + err).strip()
        last_error = combined[-500:] or "exit code %s" % proc.returncode
        if is_timeout_message(combined) and attempt < retries:
            SLEEP(backoff * (attempt + 1))
            continue
        break
    raise AlgobotError("algobot %s failed: %s" % (" ".join(args), last_error))


# ---------------------------------------------------------------- run folders


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: str, value: Any) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(value, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


def safe_name(identifier: str) -> str:
    """File-safe name. When sanitizing changes the name, a short hash of the
    original is appended so two different ids never map to one file."""
    original = str(identifier)
    clean = re.sub(r"[^A-Za-z0-9_.-]", "_", original)
    if clean != original or clean in ("", ".", ".."):
        clean = "%s-%s" % (clean, hashlib.sha1(original.encode("utf-8")).hexdigest()[:8])
    return clean


def judgments_list(value: Any) -> List[Dict[str, Any]]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("judgments", "data", "items", "results"):
            if isinstance(value.get(key), list):
                return value[key]
        raise AlgobotError("unexpected judgments shape: object with keys %s (expected a `judgments` list)"
                           % sorted(value.keys())[:10])
    raise AlgobotError("unexpected judgments shape: %s (expected a `judgments` list)" % type(value).__name__)


def load_run_dir(directory: str) -> Dict[str, Any]:
    """Load a folder written by fetch_run.py."""
    jpath = os.path.join(directory, "judgments.json")
    if not os.path.exists(jpath):
        raise SystemExit("%s: judgments.json not found (run fetch_run.py first)" % directory)
    judgments = judgments_list(load_json(jpath))
    cases: Dict[str, Any] = {}
    cdir = os.path.join(directory, "cases")
    if os.path.isdir(cdir):
        for name in sorted(os.listdir(cdir)):
            if name.endswith(".json"):
                cases[name[: -len(".json")]] = load_json(os.path.join(cdir, name))
    meta_path = os.path.join(directory, "meta.json")
    meta = load_json(meta_path) if os.path.exists(meta_path) else {}
    return {"judgments": judgments, "cases": cases, "meta": meta}


def case_for(run: Dict[str, Any], case_id: str) -> Dict[str, Any]:
    return run["cases"].get(safe_name(case_id)) or {}


def completion(case_doc: Dict[str, Any]) -> Dict[str, Any]:
    value = case_doc.get("completion") if isinstance(case_doc, dict) else None
    return value if isinstance(value, dict) else {}


def expected(case_doc: Dict[str, Any]) -> Dict[str, Any]:
    case = case_doc.get("case") if isinstance(case_doc, dict) else None
    if not isinstance(case, dict):
        return {}
    payload = case.get("casePayload") or {}
    value = payload.get("expected") if isinstance(payload, dict) else None
    return value if isinstance(value, dict) else {}


def is_passed(judgment: Dict[str, Any]) -> bool:
    return bool(judgment.get("passed"))


def passed_state(judgment: Dict[str, Any]) -> Optional[bool]:
    """True or False, or None when the judge produced no verdict (error)."""
    value = judgment.get("passed")
    return None if value is None else bool(value)


def score_of(judgment: Dict[str, Any]) -> Optional[float]:
    score = judgment.get("score")
    try:
        return float(score) if score is not None else None
    except (TypeError, ValueError):
        return None


def mean(values: Iterable[float]) -> Optional[float]:
    vals = list(values)
    return sum(vals) / len(vals) if vals else None


def median(values: Iterable[float]) -> Optional[float]:
    vals = list(values)
    return float(statistics.median(vals)) if vals else None


def fmt(value: Optional[float], digits: int = 3) -> str:
    if value is None:
        return "n/a"
    return ("%." + str(digits) + "f") % value


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)
