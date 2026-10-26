"""Synthetic fixtures and a fake algobot runner. No real ids or customer text."""

import contextlib
import io
import json
import os
import sys
import tempfile
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import _algobot as ab  # noqa: E402


class FakeRunner:
    """Replaces subprocess.run. `handler(args)` returns stdout text, or a tuple
    (returncode, stdout, stderr). `args` excludes the binary and global flags."""

    def __init__(self, handler: Callable[[List[str]], Any]):
        self.handler = handler
        self.calls: List[List[str]] = []
        self.envs: List[Dict[str, str]] = []
        self.timeouts: List[Optional[float]] = []

    def __call__(self, cmd, capture_output=True, text=True, env=None, timeout=None):
        self.calls.append(list(cmd))
        self.envs.append(dict(env or {}))
        self.timeouts.append(timeout)
        args = list(cmd[1:])
        while args and args[0] in ("--profile", "--agent"):
            args = args[2:]
        out = self.handler(args)
        if isinstance(out, tuple):
            code, stdout, stderr = out
        else:
            code, stdout, stderr = 0, out, ""
        return SimpleNamespace(returncode=code, stdout=stdout, stderr=stderr)


@contextlib.contextmanager
def fake_algobot(handler: Callable[[List[str]], Any]):
    runner = FakeRunner(handler)
    old_runner, old_sleep = ab.RUNNER, ab.SLEEP
    ab.RUNNER = runner
    ab.SLEEP = lambda s: None
    try:
        yield runner
    finally:
        ab.RUNNER, ab.SLEEP = old_runner, old_sleep


@contextlib.contextmanager
def no_network():
    def refuse(args):
        raise AssertionError("unexpected algobot call: %r" % (args,))
    with fake_algobot(refuse) as runner:
        yield runner


def capture(fn: Callable[..., int], *args: Any, **kwargs: Any):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = fn(*args, **kwargs)
    return code, out.getvalue(), err.getvalue()


def judgment(case_id: str, metric: str, passed: bool, score: float, reason: str = "") -> Dict[str, Any]:
    return {"id": "j-" + case_id + "-" + metric, "evalCaseId": case_id, "metricSlug": metric,
            "passed": passed, "score": score, "reason": reason}


def case_doc(query: str, response: str, answer: Optional[str] = None, expected: Optional[Dict[str, Any]] = None,
             input_tokens: int = 1000, output_tokens: int = 100, duration_ms: int = 2000) -> Dict[str, Any]:
    return {
        "case": {"query": query, "casePayload": {"expected": expected or {}}},
        "completion": {"usage": {"inputTokens": input_tokens, "outputTokens": output_tokens},
                       "durationMs": duration_ms, "responseText": response,
                       "answerText": answer if answer is not None else response,
                       "toolCalls": [{"tool_name": "search_tool", "args": {"query": query}}]},
    }


def write_run(directory: str, judgments: List[Dict[str, Any]], cases: Dict[str, Dict[str, Any]],
              dataset_id: Optional[str] = "dataset-synthetic-1") -> str:
    os.makedirs(os.path.join(directory, "cases"), exist_ok=True)
    with open(os.path.join(directory, "judgments.json"), "w") as fh:
        json.dump({"judgments": judgments}, fh)
    for cid, doc in cases.items():
        with open(os.path.join(directory, "cases", cid + ".json"), "w") as fh:
            json.dump(doc, fh)
    with open(os.path.join(directory, "meta.json"), "w") as fh:
        json.dump({"datasetId": dataset_id}, fh)
    return directory


def tempdir() -> tempfile.TemporaryDirectory:
    return tempfile.TemporaryDirectory(prefix="eval-scripts-test-")
