#!/usr/bin/env python3
"""Track the objects a tuning loop creates, and print a safe cleanup plan.

Maintains lineage.json in the current folder (or --file):
  sourceAgent, clone, snapshot (rollback config path), datasets,
  experiments, runs (each with an optional note).

Subcommands:
  add KIND ID [--note TEXT] [--experiment EXPERIMENT_ID] [--reused]
      KIND is one of: source-agent, clone, snapshot, dataset, experiment, run
      datasets are recorded as `created` by the loop unless --reused
  list [--json]
  cleanup-plan [--profile P]
      PRINTS delete commands in a safe order (experiments, then datasets
      the loop created, then the clone). Reused datasets are listed as left
      alone. The clone delete is printed only when a source agent is
      recorded and differs from it. Ids are shell-quoted. It runs nothing
      and never lists the source agent.

Local file only: no network, nothing remote is created or deleted.
"""

import argparse
import json
import os
import shlex
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _algobot as ab  # noqa: E402

SINGLE = {"source-agent": "sourceAgent", "clone": "clone", "snapshot": "snapshot"}
MULTI = {"dataset": "datasets", "experiment": "experiments", "run": "runs"}


def empty() -> Dict[str, Any]:
    return {"version": 1, "sourceAgent": None, "clone": None, "snapshot": None,
            "datasets": [], "experiments": [], "runs": []}


def load(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return empty()
    data = ab.load_json(path)
    base = empty()
    base.update(data if isinstance(data, dict) else {})
    return base


def add(data: Dict[str, Any], kind: str, ident: str, note: Optional[str], experiment: Optional[str],
        reused: bool = False) -> str:
    entry: Dict[str, Any] = {"id": ident}
    if kind == "dataset":
        entry["origin"] = "reused" if reused else "created"
    elif reused:
        raise SystemExit("--reused only applies to kind dataset")
    if note:
        entry["note"] = note
    if kind in SINGLE:
        key = SINGLE[kind]
        if kind == "clone" and data.get("sourceAgent") and data["sourceAgent"].get("id") == ident:
            raise SystemExit("refusing: clone id equals the source agent id")
        if kind == "source-agent" and data.get("clone") and data["clone"].get("id") == ident:
            raise SystemExit("refusing: source agent id equals the clone id")
        data[key] = entry
        return "set %s = %s" % (key, ident)
    key = MULTI[kind]
    if kind == "run" and experiment:
        entry["experimentId"] = experiment
    if any(e.get("id") == ident for e in data[key]):
        return "%s %s already recorded" % (kind, ident)
    data[key].append(entry)
    return "added %s %s%s" % (kind, ident, " (%s)" % entry["origin"] if "origin" in entry else "")


def render_list(data: Dict[str, Any]) -> str:
    lines = ["# Lineage", ""]
    for key in ("sourceAgent", "clone", "snapshot"):
        e = data.get(key)
        lines.append("- %s: %s%s" % (key, e["id"] if e else "not set", " (%s)" % e["note"] if e and e.get("note") else ""))
    for key in ("datasets", "experiments", "runs"):
        lines.append("- %s:%s" % (key, "" if data[key] else " none"))
        for e in data[key]:
            extra = []
            if e.get("origin"):
                extra.append(e["origin"])
            if e.get("experimentId"):
                extra.append("experiment %s" % e["experimentId"])
            if e.get("note"):
                extra.append(e["note"])
            lines.append("  - %s%s" % (e["id"], " (%s)" % ", ".join(extra) if extra else ""))
    return "\n".join(lines) + "\n"


def cleanup_plan(data: Dict[str, Any], profile: Optional[str]) -> str:
    q = shlex.quote
    prefix = "algobot --profile %s" % q(profile) if profile else "algobot"
    lines = ["# Cleanup plan. Review before running: this script deletes nothing.",
             "# Order: experiments (their runs cascade), then datasets the loop created, then the clone.", ""]
    if data["experiments"]:
        lines.append("# 1. Experiments")
        for e in data["experiments"]:
            lines.append("%s evals experiments delete %s" % (prefix, q(str(e["id"]))))
        lines.append("")
    created = [e for e in data["datasets"] if e.get("origin", "created") != "reused"]
    reused = [e for e in data["datasets"] if e.get("origin") == "reused"]
    if created:
        lines.append("# 2. Datasets created by this loop. A dataset cannot be deleted while it is generating")
        lines.append("#    (observed HTTP 409): check its status with `%s evals datasets get <id>` first." % prefix)
        lines.append("#    Skip any dataset you still want for future comparisons.")
        for e in created:
            lines.append("%s evals datasets delete %s" % (prefix, q(str(e["id"]))))
        lines.append("")
    if reused:
        lines.append("# Datasets left alone (reused, not created by this loop):")
        for e in reused:
            lines.append("#   %s" % q(str(e["id"])))
        lines.append("")
    clone = data.get("clone")
    source = data.get("sourceAgent")
    if clone and source and source.get("id") and source.get("id") != clone.get("id"):
        lines.append("# 3. Clone agent (draft). Only after any promotion is done and verified.")
        lines.append("%s agents delete %s" % (prefix, q(str(clone["id"]))))
        lines.append("")
    elif clone:
        lines.append("# Clone delete NOT printed: record a source agent that differs from the clone first")
        lines.append("# (lineage.py add source-agent <SOURCE_AGENT_ID>).")
        lines.append("")
    if source:
        lines.append("# The source agent %s is never part of this plan." % q(str(source["id"])))
    if data.get("snapshot"):
        lines.append("# Keep the rollback snapshot: %s" % q(str(data["snapshot"]["id"])))
    return "\n".join(lines).rstrip() + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", default="lineage.json", help="lineage file (default ./lineage.json)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_add = sub.add_parser("add", help="record an object")
    p_add.add_argument("kind", choices=sorted(list(SINGLE) + list(MULTI)))
    p_add.add_argument("id", metavar="ID", help="object id (or path, for snapshot)")
    p_add.add_argument("--note", help="free-text note")
    p_add.add_argument("--experiment", help="parent experiment id (for kind run)")
    p_add.add_argument("--reused", action="store_true",
                       help="kind dataset only: the loop reused an existing dataset (never put in the cleanup plan)")
    p_list = sub.add_parser("list", help="show recorded objects")
    p_list.add_argument("--json", action="store_true")
    p_plan = sub.add_parser("cleanup-plan", help="print delete commands in a safe order (runs nothing)")
    p_plan.add_argument("--profile", "-p", help="algobot profile to put in the printed commands")
    args = parser.parse_args(argv)

    data = load(args.file)
    if args.cmd == "add":
        print(add(data, args.kind, args.id, args.note, args.experiment, args.reused))
        ab.write_json(args.file, data)
    elif args.cmd == "list":
        if args.json:
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            sys.stdout.write(render_list(data))
    else:
        sys.stdout.write(cleanup_plan(data, args.profile))
    return 0


if __name__ == "__main__":
    sys.exit(main())
