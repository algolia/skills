import io
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

from _fixtures import SCRIPTS, ab, capture, fake_algobot, no_network, tempdir

import audit_agent
import build_history_dataset
import lineage
import size_payload
import wait_experiments


def msg(role, text, mid=None):
    m = {"role": role, "parts": [{"type": "text", "text": text}]}
    if mid:
        m["id"] = mid
    return m


class BuildHistoryDatasetTest(unittest.TestCase):
    def export(self):
        convs = []
        for i in range(24):
            convs.append({"id": "conv-%d" % i, "createdAt": "2026-01-05T10:00:00Z",
                          "messages": [msg("user", "Do you ship abroad?"), msg("assistant", "Yes, to many countries."),
                                       msg("user", "Contact me at someone@example.com")]})
        convs.append({"id": "conv-x", "createdAt": "2026-01-06T10:00:00Z", "userToken": "anon-1",
                      "messages": [msg("user", "first"), msg("user", "What fabric is this jacket?"),
                                   {"role": "assistant", "content": "It is cotton."}, {"role": "tool", "content": "{}"},
                                   msg("user", "Any discount today?")]})
        convs.append({"id": "eval-experiment_run_abc", "messages": [msg("user", "harness")]})
        convs.append({"id": "conv-y", "messages": [msg("user", "harness 2", mid="evalcase-1")]})
        return convs

    def run_build(self, tmp, extra=()):
        path = os.path.join(tmp, "export.json")
        with open(path, "w") as fh:
            json.dump(self.export(), fh)
        out = os.path.join(tmp, "out")
        code, stdout, _ = capture(build_history_dataset.main, ["--from-json", path, "--out", out] + list(extra))
        with open(os.path.join(out, "rows.jsonl"), encoding="utf-8") as fh:
            rows = [json.loads(line) for line in fh]
        return code, stdout, rows, ab.load_json(os.path.join(out, "triage.json"))

    def test_triage_and_rows(self):
        with tempdir() as tmp, no_network():
            code, out, rows, tri = self.run_build(tmp)
        self.assertEqual(code, 0)
        self.assertEqual(tri["evalArtifactsDropped"], 2)
        self.assertEqual(tri["verdict"], "looks scripted")
        self.assertIn("looks scripted", out)
        self.assertGreater(tri["duplicateFirstTurnRate"], 0.8)
        queries = [r["query"] for r in rows]
        self.assertEqual(queries.count("Do you ship abroad?"), 1)
        self.assertEqual(queries.count("Contact me at [EMAIL]"), 1)
        for r in rows:
            self.assertEqual(set(r["metrics"]), {"faithfulness"})
            self.assertEqual(r["difficulty"], "medium")
            if "messages" in r:
                self.assertNotEqual(r["messages"][-1]["role"], "user")
                self.assertTrue(all(m["role"] in ("user", "assistant") for m in r["messages"]))
        fabric = [r for r in rows if r["query"].startswith("What fabric")][0]
        self.assertNotIn("messages", fabric)
        self.assertEqual(fabric["metrics"]["faithfulness"]["fact_type"], "materials")
        discount = [r for r in rows if r["query"].startswith("Any discount")][0]
        self.assertEqual(discount["messages"][-1], {"role": "assistant", "content": "It is cotton."})
        self.assertEqual(discount["metrics"]["faithfulness"]["fact_type"], "pricing")
        self.assertIn("fallback", out)
        self.assertGreaterEqual(tri["transform"]["trimmedUserTurns"], 1)

    def test_tone_contract_makes_wide_rows(self):
        with tempdir() as tmp:
            contract = os.path.join(tmp, "tone.json")
            with open(contract, "w") as fh:
                json.dump({"tone_constraint": "Warm and upbeat", "bad_response_patterns": []}, fh)
            _, out, rows, tri = self.run_build(tmp, ["--tone-contract", contract])
        self.assertTrue(all(r["metrics"]["tone"]["tone_constraint"] == "Warm and upbeat" for r in rows))
        self.assertEqual(tri["casesAfterImport"], 2 * len(rows))
        self.assertIn("2 metric(s) per row", out)


class SizePayloadTest(unittest.TestCase):
    def response(self):
        hits = []
        for i in range(4):
            hits.append({"objectID": str(i), "name": "Item %d" % i, "price": 10 + i, "color": "blue",
                         "description": "long text " * 60,
                         "_highlightResult": {"name": {"value": "<em>Item</em>", "matchLevel": "full"}}})
        return {"hits": hits, "nbHits": 4, "hitsPerPage": 4}

    def test_ranks_and_flags(self):
        r = size_payload.analyze(self.response())
        self.assertEqual(r["hits"], 4)
        self.assertEqual(r["attributes"][0]["attribute"], "description")
        flags = {a["attribute"]: a["heavy"] for a in r["attributes"]}
        self.assertTrue(flags["description"])
        self.assertTrue(flags["_highlightResult"])
        self.assertFalse(flags["price"])
        s = r["suggestedSearchParameters"]
        self.assertNotIn("description", s["attributesToRetrieve"])
        self.assertNotIn("_highlightResult", s["attributesToRetrieve"])
        self.assertIn("price", s["attributesToRetrieve"])
        self.assertEqual((s["attributesToHighlight"], s["attributesToSnippet"], s["hitsPerPage"]), ([], [], 4))
        self.assertEqual(r["excludedLargeAttributes"], ["description"])

    def test_capitalized_key_and_bare_array(self):
        hits = self.response()["hits"]
        self.assertEqual(size_payload.analyze({"Hits": hits})["hits"], 4)
        self.assertEqual(size_payload.analyze(hits)["hits"], 4)
        with self.assertRaises(SystemExit):
            size_payload.analyze({"nothing": 1})

    def test_results_shape_and_stdin(self):
        doc = {"results": [self.response(), self.response()]}
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(doc))):
            code, out, _ = capture(size_payload.main, ["-", "--hits-per-page", "12"])
        self.assertEqual(code, 0)
        self.assertIn("hits: 8", out)
        self.assertIn("starting point to review", out)
        self.assertIn('"hitsPerPage": 12', out)


AGENT = {
    "id": "agent-synthetic",
    "instructions": ("Search the `products_v2` index for items. Then call `displayResults` to show them. "
                     "Use the `faq_lookup` tool for policies. Mention `price` when known. Use `search_tool`."),
    "config": {"max_iterations": 0, "enableAlgoliaMcp": True},
    "tools": [
        {"type": "algolia_search_index", "name": "search_tool",
         "indices": [{"index": "products", "description": "catalog", "searchParameters": None},
                     {"index": "articles", "description": "help", "searchParameters": {"hitsPerPage": None}}]},
        {"type": "algolia_display_results", "name": "display_grouped_results"},
    ],
}


class AuditAgentTest(unittest.TestCase):
    def test_findings_ranked(self):
        findings = audit_agent.audit(AGENT)
        titles = " | ".join(f["title"] for f in findings)
        self.assertIn("index `products_v2`", titles)
        self.assertIn("display tool `displayResults`", titles)
        self.assertIn("`faq_lookup`", titles)
        self.assertIn("null or missing searchParameters", titles)
        self.assertIn("searchParameters.hitsPerPage to null", titles)
        self.assertIn("max_iterations is 0", titles)
        self.assertIn("enableAlgoliaMcp", titles)
        self.assertNotIn("Prompt names `search_tool`", titles)
        order = [audit_agent.SEVERITY_ORDER[f["severity"]] for f in findings]
        self.assertEqual(order, sorted(order))
        self.assertEqual(findings[0]["severity"], "high")
        price = [f for f in findings if "`price`" in f["title"]][0]
        self.assertEqual(price["severity"], "low")

    def test_file_input_exit_codes(self):
        with tempdir() as tmp, no_network():
            path = os.path.join(tmp, "agent.json")
            with open(path, "w") as fh:
                json.dump({"agent": AGENT}, fh)
            code, out, _ = capture(audit_agent.main, [path])
            self.assertEqual(code, 0)
            self.assertIn("[HIGH]", out)
            code, _, _ = capture(audit_agent.main, [path, "--strict"])
            self.assertEqual(code, 1)

    def test_fetch_by_id_and_clean_agent(self):
        clean = {"instructions": "Use `search_tool` on the `products` index.", "config": {"max_iterations": 5},
                 "tools": [{"type": "algolia_search_index", "name": "search_tool",
                            "indices": [{"index": "products", "description": "d", "searchParameters": {"hitsPerPage": 10}}]}]}
        with fake_algobot(lambda args: "log\n" + json.dumps(clean)) as runner:
            code, out, _ = capture(audit_agent.main, ["agent-synthetic", "--strict", "--profile", "demo"])
        self.assertEqual(code, 0)
        self.assertIn("findings: 0", out)
        self.assertEqual(runner.calls[0][3:], ["agents", "get", "agent-synthetic"])


class LineageTest(unittest.TestCase):
    def test_add_list_cleanup(self):
        with tempdir() as tmp:
            f = os.path.join(tmp, "lineage.json")
            for argv in (["add", "source-agent", "src-1"], ["add", "clone", "clone-1", "--note", "tuning"],
                         ["add", "snapshot", "snapshots/src-1.json"], ["add", "dataset", "ds-1"],
                         ["add", "experiment", "exp-1"], ["add", "experiment", "exp-2"],
                         ["add", "run", "run-1", "--experiment", "exp-1"], ["add", "dataset", "ds-1"]):
                code, _, _ = capture(lineage.main, ["--file", f] + argv)
                self.assertEqual(code, 0)
            data = ab.load_json(f)
            self.assertEqual(len(data["datasets"]), 1)
            self.assertEqual(data["runs"][0]["experimentId"], "exp-1")
            _, out, _ = capture(lineage.main, ["--file", f, "list"])
            self.assertIn("clone-1 (tuning)", out)
            with no_network():
                _, plan, _ = capture(lineage.main, ["--file", f, "cleanup-plan", "--profile", "demo"])
            cmds = [line for line in plan.splitlines() if line.startswith("algobot")]
            self.assertEqual(cmds, ["algobot --profile demo evals experiments delete exp-1",
                                    "algobot --profile demo evals experiments delete exp-2",
                                    "algobot --profile demo evals datasets delete ds-1",
                                    "algobot --profile demo agents delete clone-1"])
            self.assertIn("409", plan)
            self.assertNotIn("delete src-1", plan)

    def test_refuses_clone_equal_source(self):
        with tempdir() as tmp:
            f = os.path.join(tmp, "lineage.json")
            capture(lineage.main, ["--file", f, "add", "source-agent", "same"])
            with self.assertRaises(SystemExit):
                capture(lineage.main, ["--file", f, "add", "clone", "same"])


class WaitExperimentsTest(unittest.TestCase):
    def run_wait(self, sequences, argv):
        seqs = {k: list(v) for k, v in sequences.items()}

        def handler(args):
            exp_id = args[3]
            value = seqs[exp_id].pop(0) if len(seqs[exp_id]) > 1 else seqs[exp_id][0]
            if value == "TIMEOUT":
                return (1, "", "operation was aborted due to timeout")
            return json.dumps({"id": exp_id, "status": value})

        now = [0.0]
        old_clock = wait_experiments.CLOCK
        wait_experiments.CLOCK = lambda: now[0]
        try:
            with fake_algobot(handler):
                ab.SLEEP = lambda s: now.__setitem__(0, now[0] + s)
                code, out, err = capture(wait_experiments.main, argv)
        finally:
            wait_experiments.CLOCK = old_clock
        return code, json.loads(out), err

    def test_all_completed_with_transient_timeout(self):
        code, out, err = self.run_wait({"e1": ["running", "TIMEOUT", "TIMEOUT", "judging", "completed"],
                                        "e2": ["completed"]}, ["e1", "e2", "--interval", "10"])
        self.assertEqual(code, 0)
        self.assertEqual(out["statuses"], {"e1": "completed", "e2": "completed"})
        self.assertIn("e1: judging", err)

    def test_exit_codes(self):
        code, out, _ = self.run_wait({"e1": ["failed"], "e2": ["completed"]}, ["e1", "e2"])
        self.assertEqual(code, 1)
        code, _, _ = self.run_wait({"e1": ["awaiting_review"]}, ["e1"])
        self.assertEqual(code, 3)
        code, out, _ = self.run_wait({"e1": ["running"]}, ["e1", "--timeout", "60", "--interval", "10"])
        self.assertEqual(code, 2)
        self.assertTrue(out["timedOut"])


class HelpTest(unittest.TestCase):
    def test_every_script_has_help(self):
        scripts = sorted(f for f in os.listdir(SCRIPTS) if f.endswith(".py") and not f.startswith("_"))
        self.assertEqual(len(scripts), 9)
        for name in scripts:
            proc = subprocess.run([sys.executable, "-B", os.path.join(SCRIPTS, name), "--help"],
                                  capture_output=True, text=True,
                                  env=dict(os.environ, ALGOBOT_BIN="/nonexistent", PYTHONDONTWRITEBYTECODE="1"))
            self.assertEqual(proc.returncode, 0, name + proc.stderr)
            self.assertIn("usage:", proc.stdout)


class NoEmDashTest(unittest.TestCase):
    def test_no_em_dash_in_scripts(self):
        for root, _, files in os.walk(SCRIPTS):
            for name in files:
                if name.endswith((".py", ".md")):
                    with open(os.path.join(root, name), encoding="utf-8") as fh:
                        self.assertNotIn(chr(0x2014), fh.read(), name)


if __name__ == "__main__":
    unittest.main()
