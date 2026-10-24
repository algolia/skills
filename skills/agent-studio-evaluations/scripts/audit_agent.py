#!/usr/bin/env python3
"""Static audit of an agent config before any paid eval (zero eval cost).

Input: an agent id (fetched with `algobot agents get <id>`) or a saved JSON
file (`agents get` output or an `agents scaffold` agent-config.json).

Checks, ranked high to low in a markdown fix list:
- backticked identifiers in `instructions` that match no attached tool name,
  tool type or index name. HIGH only when the identifier starts with
  `algolia_` or sits right next to the noun "tool" or "index" ("the `x`
  index", "tool `x`"), or is snake_case right after a search verb ("search
  `x`", "query the `x`"); otherwise LOW (often a record attribute). Identifiers
  followed by "attribute" or "field" are skipped. When a saved config file
  stores a filename in `instructions` (the `agents scaffold` convention,
  for example "PROMPT.md"), the referenced Markdown is audited instead and a
  missing file is a hard error;
- display-tool name mismatch (the prompt uses a display-tool alias such as
  `display_results` that is not the attached display tool's name);
- Search tool indices with null or missing `searchParameters`, and null
  values inside them;
- `max_iterations` / `maxIterations` set to 0 (falls back to a default);
- deprecated config keys.

Exit code is 0 even when findings exist; --strict exits 1 on any finding.
Read only: nothing remote is changed.
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Set

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _algobot as ab  # noqa: E402

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
DEPRECATED_KEYS = {
    "enableAlgoliaMcp": "deprecated config field (stripped by `agents scaffold` on algobot-ai 2.1.0+)",
}
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-]{1,63}$")
# Exact display-tool aliases a prompt may use. Anything else that merely
# contains "display" (display_name, displayPrice) is not treated as a tool.
DISPLAY_ALIASES = ("display_results", "algolia_display_results", "displayResults", "algolia_displayResults")
NOUN_AFTER_RE = re.compile(r"^\s*(tool|tools|index|indexes|indices)\b", re.IGNORECASE)
NOUN_BEFORE_RE = re.compile(r"\b(tool|index|indexes|indices)\s+(named\s+|called\s+)?$", re.IGNORECASE)
# "search `x`", "search the `x`", "query in `x`": a search verb plus at most one filler word.
SEARCH_VERB_BEFORE_RE = re.compile(
    r"\b(search|searches|searching|query|queries|querying)\s+((the|in|on|through|across)\s+)?$", re.IGNORECASE)
SNAKE_RE = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)+$")
ATTRIBUTE_AFTER_RE =re.compile(r"^\s*(attribute|attributes|field|fields)\b", re.IGNORECASE)


def unwrap(doc: Any) -> Dict[str, Any]:
    if isinstance(doc, dict):
        for key in ("agent", "data"):
            if isinstance(doc.get(key), dict) and ("instructions" in doc[key] or "tools" in doc[key]):
                return doc[key]
        return doc
    raise SystemExit("agent JSON must be an object")


def tools_of(agent: Dict[str, Any]) -> List[Dict[str, Any]]:
    tools = agent.get("tools")
    if tools is None and isinstance(agent.get("config"), dict):
        tools = agent["config"].get("tools")
    return [t for t in tools or [] if isinstance(t, dict)]


def walk_keys(value: Any, path: str = ""):
    if isinstance(value, dict):
        for k, v in value.items():
            p = "%s.%s" % (path, k) if path else k
            yield p, k, v
            yield from walk_keys(v, p)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from walk_keys(v, "%s[%d]" % (path, i))


def audit(agent: Dict[str, Any]) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    instructions = str(agent.get("instructions") or "")
    tools = tools_of(agent)
    names: Set[str] = set()
    index_names: Set[str] = set()
    display_names: Set[str] = set()
    for t in tools:
        for key in ("name", "type"):
            if t.get(key):
                names.add(str(t[key]))
        if "display" in str(t.get("type", "")).lower() or "display" in str(t.get("name", "")).lower():
            if t.get("name"):
                display_names.add(str(t["name"]))
        for idx in t.get("indices") or []:
            if isinstance(idx, dict) and idx.get("index"):
                index_names.add(str(idx["index"]))
    known = names | index_names

    def add(sev: str, title: str, fix: str) -> None:
        findings.append({"severity": sev, "title": title, "fix": fix})

    seen: Set[str] = set()
    for m in re.finditer(r"`([^`\n]+)`", instructions):
        ident = m.group(1).strip()
        if not IDENT_RE.match(ident) or ident in known or ident in seen or ident in DISPLAY_ALIASES:
            continue
        seen.add(ident)
        before = instructions[max(0, m.start() - 40): m.start()]
        after = instructions[m.end(): m.end() + 30]
        if ATTRIBUTE_AFTER_RE.search(after):
            continue  # "the `color` attribute": a record field, not a tool or index
        noun = NOUN_AFTER_RE.search(after) or NOUN_BEFORE_RE.search(before)
        noun_word = noun.group(1).lower() if noun else ""
        if noun_word.startswith("ind"):
            add("high", "Prompt references index `%s`, which no attached Search tool lists" % ident,
                "Attach the index to the Search tool, or change the prompt to an attached index: %s"
                % (", ".join("`%s`" % i for i in sorted(index_names)) or "none attached"))
        elif SEARCH_VERB_BEFORE_RE.search(before) and (SNAKE_RE.match(ident) or ident.startswith("algolia_")):
            add("high", "Prompt tells the agent to search `%s`, which is not an attached index or tool" % ident,
                "Attach that index or tool, or point the prompt at an attached one (indices: %s; tools: %s). "
                "If this is an attribute, ignore"
                % (", ".join("`%s`" % i for i in sorted(index_names)) or "none",
                   ", ".join("`%s`" % n for n in sorted(names)) or "none"))
        elif noun_word.startswith("tool") or ident.startswith("algolia_"):
            add("high", "Prompt names tool `%s`, which matches no attached tool name or type" % ident,
                "Rename it in the prompt to an attached tool (%s), or attach that tool"
                % (", ".join("`%s`" % n for n in sorted(names)) or "no tools attached"))
        else:
            add("low", "Backticked `%s` matches no tool, tool type or index" % ident,
                "Probably a record attribute, argument or literal; verify it is intended")

    for alias in DISPLAY_ALIASES:
        if alias in known or not re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(alias), instructions):
            continue
        if display_names:
            add("high", "Prompt names display tool `%s`, but the attached display tool is %s"
                % (alias, ", ".join("`%s`" % n for n in sorted(display_names))),
                "Use the attached display tool name in the prompt, or the agent may never call it")
        else:
            add("high", "Prompt names display tool `%s`, but no display tool is attached" % alias,
                "Attach the display tool under that name, or remove the instruction")

    for t in tools:
        if t.get("type") != "algolia_search_index":
            continue
        tname = t.get("name") or t.get("type")
        for idx in t.get("indices") or []:
            if not isinstance(idx, dict):
                continue
            iname = idx.get("index") or "?"
            if "searchParameters" in idx or "search_parameters" in idx:
                params = idx.get("searchParameters", idx.get("search_parameters"))
            else:
                params = None
            if params is None:
                add("medium", "Search tool `%s` index `%s` has null or missing searchParameters" % (tname, iname),
                    "Set explicit searchParameters (hitsPerPage, attributesToRetrieve, empty attributesToHighlight "
                    "and attributesToSnippet). Size the payload first with size_payload.py")
            elif isinstance(params, dict):
                for k in sorted(k for k, v in params.items() if v is None):
                    add("low", "Search tool `%s` index `%s` sets searchParameters.%s to null" % (tname, iname, k),
                        "Remove the key or give it a value")

    config = agent.get("config") if isinstance(agent.get("config"), dict) else {}
    for key in ("max_iterations", "maxIterations"):
        if key in config and config[key] == 0:
            add("medium", "config.%s is 0" % key,
                "0 falls back to the service default (observed). Set an explicit tool-iteration budget")
    for path, key, _ in walk_keys(config, "config"):
        if key in DEPRECATED_KEYS:
            add("low", "Deprecated key `%s`" % path, "Remove it: %s" % DEPRECATED_KEYS[key])
    for key in DEPRECATED_KEYS:
        if key in agent:
            add("low", "Deprecated key `%s`" % key, "Remove it: %s" % DEPRECATED_KEYS[key])

    findings.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["title"]))
    return findings


def render(agent: Dict[str, Any], findings: List[Dict[str, str]]) -> str:
    lines = ["# Agent audit", "",
             "- tools attached: %s" % (", ".join(sorted("%s (%s)" % (t.get("name") or "-", t.get("type") or "-")
                                                          for t in tools_of(agent))) or "none"),
             "- findings: %d" % len(findings), ""]
    if not findings:
        lines.append("No findings. This is a static check only; it does not replace an eval.")
    for i, f in enumerate(findings, 1):
        lines.append("%d. [%s] %s" % (i, f["severity"].upper(), f["title"]))
        lines.append("   Fix: %s" % f["fix"])
    return "\n".join(lines) + "\n"


def resolve_instructions(agent: Dict[str, Any], config_dir: Optional[str]) -> Dict[str, Any]:
    """Scaffolded agent configs store `"instructions": "PROMPT.md"`, a filename
    reference rather than the prompt text. Audit the referenced Markdown (read
    relative to the config file), not the filename; fail explicitly when it
    cannot be read. Remote `agents get` output carries prompt text and is
    returned unchanged."""
    text = agent.get("instructions")
    if not isinstance(text, str) or not text.strip().lower().endswith(".md"):
        return agent
    if config_dir is None:
        return agent
    path = os.path.join(config_dir, text.strip())
    if not os.path.isfile(path):
        raise SystemExit("instructions reference the file %r but %s does not exist. Scaffolded configs store a "
                         "filename in `instructions`: run the audit next to the config, or restore the referenced "
                         "Markdown file." % (text.strip(), path))
    with open(path, "r", encoding="utf-8") as fh:
        agent["instructions"] = fh.read()
    return agent


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", metavar="agent-id-or-json-file", help="agent id, or a saved agent JSON file")
    parser.add_argument("--profile", "-p", help="algobot profile name (passed as --profile)")
    parser.add_argument("--strict", action="store_true", help="exit 1 when any finding exists")
    parser.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    args = parser.parse_args(argv)
    if os.path.isfile(args.target):
        doc = ab.load_json(args.target)
    else:
        doc = ab.call(["agents", "get", args.target], profile=args.profile)
    agent = unwrap(doc)
    agent = resolve_instructions(agent, os.path.dirname(os.path.abspath(args.target)) if os.path.isfile(args.target) else None)
    findings = audit(agent)
    if args.json:
        print(json.dumps({"findings": findings}, indent=2, sort_keys=True))
    else:
        sys.stdout.write(render(agent, findings))
    return 1 if (args.strict and findings) else 0


if __name__ == "__main__":
    sys.exit(main())
