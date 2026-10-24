"""Regression tests for the review hardening fixes. Synthetic data only."""

import json
import os
import unittest

from _fixtures import ab, capture, case_doc, fake_algobot, judgment, no_network, tempdir, write_run

import audit_agent
import build_history_dataset as bhd
import cluster_failures
import compare_runs
import fetch_run
import lineage
import rescore_clean
import size_payload
import wait_experiments

CALM = {"tone_constraint": "Calm", "bad_response_patterns": ["!"]}


# 1. rescore_clean: never retry a paid judge call
class RescoreNoRetryTest(unittest.TestCase):
    def setUp(self):
        self.js = [judgment("c%d" % i, "tone", False, 0.1) for i in range(3)]
        self.cases = {"c%d" % i: case_doc("q%d" % i, "Clean %d." % i, expected=CALM) for i in range(3)}

    def test_timeout_is_unknown_and_not_resent(self):
        with tempdir() as tmp, fake_algobot(lambda a: (1, "", "Error: operation was aborted due to timeout")) as runner:
            write_run(tmp, self.js, self.cases)
            code, out, _ = capture(rescore_clean.main, [tmp, "--metric", "tone", "--yes"])
            self.assertEqual(code, 0)
            self.assertEqual(len(runner.calls), 3)  # one per planned case, never re-sent
            self.assertIn("planned judge calls: 3", out)
            self.assertIn("judge calls made: 3 of 3 planned; 3 unknown", out)
            saved = ab.load_json(os.path.join(tmp, "rescore-tone.json"))
            self.assertEqual(saved["unknown"], 3)
            self.assertTrue(all(r["status"].startswith("unknown") for r in saved["rows"]))

    def test_limit_caps_calls(self):
        with tempdir() as tmp, fake_algobot(lambda a: json.dumps({"score": 1.0, "passed": True})) as runner:
            write_run(tmp, self.js, self.cases)
            _, out, _ = capture(rescore_clean.main, [tmp, "--metric", "tone", "--limit", "2", "--yes"])
            self.assertEqual(len(runner.calls), 2)
            self.assertIn("planned judge calls: 2", out)


# 2. lineage cleanup plan
class LineageHardeningTest(unittest.TestCase):
    def plan(self, adds):
        with tempdir() as tmp:
            f = os.path.join(tmp, "lineage.json")
            for argv in adds:
                capture(lineage.main, ["--file", f] + argv)
            _, out, _ = capture(lineage.main, ["--file", f, "cleanup-plan"])
            return out

    def test_no_clone_delete_without_source(self):
        out = self.plan([["add", "clone", "clone-1"]])
        self.assertNotIn("agents delete", out)
        self.assertIn("NOT printed", out)

    def test_reused_dataset_left_alone(self):
        out = self.plan([["add", "source-agent", "src-1"], ["add", "clone", "clone-1"],
                         ["add", "dataset", "ds-new"], ["add", "dataset", "ds-old", "--reused"]])
        self.assertIn("evals datasets delete ds-new", out)
        self.assertNotIn("delete ds-old", out)
        self.assertIn("left alone", out)
        self.assertIn("#   ds-old", out)
        self.assertIn("agents delete clone-1", out)

    def test_ids_are_shell_quoted(self):
        out = self.plan([["add", "experiment", "exp 1; rm -rf x"]])
        self.assertIn("evals experiments delete 'exp 1; rm -rf x'", out)

    def test_reused_only_for_dataset(self):
        with tempdir() as tmp, self.assertRaises(SystemExit):
            capture(lineage.main, ["--file", os.path.join(tmp, "l.json"), "add", "clone", "c", "--reused"])


# 3. compare_runs
def two_runs(tmp, ja, jb, ds_a="ds-1", ds_b="ds-1"):
    return write_run(os.path.join(tmp, "a"), ja, {}, ds_a), write_run(os.path.join(tmp, "b"), jb, {}, ds_b)


class CompareHardeningTest(unittest.TestCase):
    def test_underpowered_is_never_significant(self):
        with tempdir() as tmp:
            for n in (2, 10):
                a, b = two_runs(os.path.join(tmp, str(n)), [judgment("c%d" % i, "tone", False, 0.0) for i in range(n)],
                                [judgment("c%d" % i, "tone", i != 0 or n == 2, 1.0 if i else 0.5) for i in range(n)])
                m = compare_runs.compare(ab.load_run_dir(a), ab.load_run_dir(b))["metrics"]["tone"]
                if n == 10:  # a non-degenerate interval that excludes zero, still underpowered
                    lo, hi = m["passRateDeltaCI95"]
                    self.assertTrue(0 < lo < hi)
                self.assertIsNone(m["passRateCiExcludesZero"])
                self.assertIsNone(m["meanScoreCiExcludesZero"])
                _, out, _ = capture(compare_runs.main, [a, b])
                self.assertIn("| n/a |", out)
                self.assertIn("one for the paired mean-score delta", out)

    def test_repeated_judgments_are_aggregated(self):
        ja = [judgment("c1", "tone", True, 1.0), judgment("c1", "tone", False, 0.0),
              judgment("c2", "tone", True, 1.0), judgment("c2", "tone", True, 0.8), judgment("c2", "tone", False, 0.3)]
        jb = [judgment("c1", "tone", True, 1.0), judgment("c2", "tone", True, 1.0)]
        with tempdir() as tmp:
            a, b = two_runs(tmp, ja, jb)
            r = compare_runs.compare(ab.load_run_dir(a), ab.load_run_dir(b))
            m = r["metrics"]["tone"]
            self.assertEqual(m["passedA"], 1)  # c1 tie counts as failed, c2 majority passed
            self.assertAlmostEqual(m["meanScoreA"], (0.5 + 0.7) / 2)
            self.assertEqual(r["aggregatedKeys"], {"A": 2, "B": 0})
            _, out, _ = capture(compare_runs.main, [a, b])
            self.assertIn("aggregated repeated judgments", out)

    def test_missing_dataset_id_refused(self):
        with tempdir() as tmp:
            a, b = two_runs(tmp, [judgment("c1", "tone", True, 1.0)], [judgment("c1", "tone", True, 1.0)], ds_b=None)
            code, _, err = capture(compare_runs.main, [a, b])
            self.assertEqual(code, 2)
            self.assertIn("datasetId missing", err)
            code, _, _ = capture(compare_runs.main, [a, b, "--allow-different-datasets"])
            self.assertEqual(code, 0)

    def test_judge_errors_excluded_and_counted(self):
        err = judgment("c2", "tone", False, None)
        err["passed"] = None
        ja = [judgment("c1", "tone", True, 1.0), err, judgment("c3", "tone", False, 0.0)]
        jb = [judgment("c1", "tone", True, 1.0), judgment("c2", "tone", True, 1.0), judgment("c3", "tone", True, 1.0)]
        with tempdir() as tmp:
            a, b = two_runs(tmp, ja, jb)
            m = compare_runs.compare(ab.load_run_dir(a), ab.load_run_dir(b))["metrics"]["tone"]
            self.assertEqual((m["errorsA"], m["errorsB"], m["judgedPairs"]), (1, 0, 2))
            self.assertEqual((m["passedA"], m["passedB"]), (1, 2))
            _, out, _ = capture(compare_runs.main, [a, b])
            self.assertIn("errors A/B", out)
            self.assertIn("| 1/0 |", out)


# 4. fetch_run paging guards
class FetchPagingTest(unittest.TestCase):
    def test_server_ignoring_offset_stops(self):
        page = {"judgments": [judgment("c%03d" % i, "tone", True, 1.0) for i in range(200)]}
        holder = {}

        def run():
            holder["items"] = fetch_run.fetch_judgments("E", "R", None)
            return 0
        with fake_algobot(lambda a: json.dumps(page)) as runner:
            _, _, err = capture(run)
        self.assertEqual(len(holder["items"]), 200)
        self.assertIn("ignoring --offset", err)
        self.assertEqual(len(runner.calls), 2)

    def test_max_pages_guard(self):
        def handler(args):
            off = int(args[args.index("--offset") + 1])
            return json.dumps({"judgments": [judgment("c%06d" % (off + i), "tone", True, 1.0) for i in range(200)]})
        with fake_algobot(handler) as runner:
            _, _, err = capture(lambda: fetch_run.fetch_judgments("E", "R", None, max_pages=3) and 0)
        self.assertEqual(len(runner.calls), 3)
        self.assertIn("stopped after 3 judgment pages", err)


# 5. wait_experiments error handling
class WaitHardeningTest(unittest.TestCase):
    def run_wait(self, handler, argv):
        now = [0.0]
        old = wait_experiments.CLOCK
        wait_experiments.CLOCK = lambda: now[0]
        try:
            with fake_algobot(handler) as runner:
                ab.SLEEP = lambda s: now.__setitem__(0, now[0] + s)
                code, out, err = capture(wait_experiments.main, argv)
        finally:
            wait_experiments.CLOCK = old
        return code, json.loads(out), err, runner

    def test_persistent_failure_marks_error(self):
        def handler(args):
            if args[3] == "bad":
                return (1, "", "Error: 404 Experiment not found")
            return json.dumps({"status": "completed"})
        code, out, err, runner = self.run_wait(handler, ["bad", "good", "--interval", "5", "--timeout", "600"])
        self.assertEqual(code, 4)
        self.assertEqual(out["statuses"], {"bad": "error", "good": "completed"})
        self.assertEqual(sum(1 for c in runner.calls if "bad" in c), 3)

    def test_per_call_timeout_capped_by_remaining_wait(self):
        code, _, _, runner = self.run_wait(lambda a: json.dumps({"status": "running"}),
                                           ["e1", "--timeout", "40", "--interval", "15"])
        self.assertEqual(code, 2)
        self.assertTrue(all(t is not None and t <= 40 for t in runner.timeouts))
        self.assertLess(runner.timeouts[-1], runner.timeouts[0])

    def test_unrecognized_status_logged_once(self):
        code, _, err, _ = self.run_wait(lambda a: json.dumps({"status": "mystery"}),
                                        ["e1", "--timeout", "50", "--interval", "10"])
        self.assertEqual(code, 2)
        self.assertEqual(err.count("unrecognized status"), 1)


# 6. build_history_dataset PII, fact types, triage, dates
class HistoryHardeningTest(unittest.TestCase):
    def test_pii_redaction_is_narrow(self):
        keep = ["on 2026-01-05 ok", "years 2019-2021", "sizes 32 34 36 38", "order 123456789",
                "EAN 4006381333931", "ref ORD-2024-5567-12"]
        for text in keep:
            self.assertEqual(bhd.redact(text), (text, 0), text)
        self.assertEqual(bhd.redact("call +44 20 7946 0958")[0], "call [PHONE]")
        self.assertEqual(bhd.redact("(555) 010-0199")[0], "[PHONE]")
        self.assertEqual(bhd.redact("card 4111 1111 1111 1111")[0], "card [CARD]")
        self.assertEqual(bhd.redact("mail a.b@example.com")[0], "mail [EMAIL]")
        self.assertFalse(bhd.luhn_ok("4006381333931"))

    def test_fact_type_word_boundaries(self):
        for q in ("relationship advice", "a special offer", "restore my account"):
            self.assertIsNone(bhd.fact_type(q), q)
        self.assertEqual(bhd.fact_type("do you ship to my country"), "shipping_policy")
        self.assertEqual(bhd.fact_type("which specs does it have"), "product_attributes")
        self.assertEqual(bhd.fact_type("is it in stores"), "store_information")

    def test_epoch_dates_and_single_turn_signal(self):
        self.assertEqual(bhd.day_of(1767607200), "2026-01-05")
        self.assertEqual(bhd.day_of(1767607200000), "2026-01-05")
        self.assertEqual(bhd.day_of("2026-01-05T10:00:00Z"), "2026-01-05")
        convs = [{"id": "c%d" % i, "createdAt": 1767607200000 + i, "userToken": "u%d" % i,
                  "messages": [{"role": "user", "content": "question %d" % i}]} for i in range(25)]
        tri = bhd.triage(convs)
        self.assertEqual(tri["topDay"], "2026-01-05")
        self.assertTrue(any("single" in s or "user turn" in s for s in tri["signals"]))
        self.assertEqual(tri["verdict"], "looks scripted")

    def test_pii_notice_printed(self):
        with tempdir() as tmp:
            path = os.path.join(tmp, "e.json")
            with open(path, "w") as fh:
                json.dump([{"id": "c", "messages": [{"role": "user", "content": "hello"}]}], fh)
            _, out, _ = capture(bhd.main, ["--from-json", path, "--out", os.path.join(tmp, "o")])
        self.assertIn("manual", out)
        self.assertIn("names, addresses, order ids", out)


# 7. audit_agent false positives
class AuditHardeningTest(unittest.TestCase):
    TOOLS = [{"type": "algolia_search_index", "name": "search_tool",
              "indices": [{"index": "products", "description": "d", "searchParameters": None}]},
             {"type": "algolia_display_results", "name": "display_grouped_results"}]

    def findings(self, instructions, config=None):
        return audit_agent.audit({"instructions": instructions, "tools": self.TOOLS, "config": config or {}})

    def test_attribute_like_identifiers_are_low_or_absent(self):
        text = ("Use the `color` attribute when relevant. Answer with `price` from the index. Use "
                "`search_keywords` to refine. Link the `size_chart`. Show `display_name`. We sell `Acme` gear. "
                "Pass `maxPrice` to filter. Use `search_tool` for products.")
        f = self.findings(text)
        for ident in ("color", "price", "search_keywords", "size_chart", "display_name", "Acme", "maxPrice"):
            sev = [x["severity"] for x in f if "`%s`" % ident in x["title"]]
            self.assertTrue(all(s == "low" for s in sev), (ident, sev))
        self.assertFalse(any("`color`" in x["title"] for x in f))

    def test_real_defects_still_reported(self):
        f = self.findings("Search the `chat_docs` index first. Then call `display_results`.", {"max_iterations": 0})
        titles = [(x["severity"], x["title"]) for x in f]
        self.assertIn(("high", "Prompt references index `chat_docs`, which no attached Search tool lists"), titles)
        self.assertTrue(any(s == "high" and "display tool `display_results`" in t for s, t in titles))
        self.assertTrue(any("null or missing searchParameters" in t for _, t in titles))
        self.assertTrue(any("max_iterations is 0" in t for _, t in titles))

    def test_search_verb_before_snake_case_is_high(self):
        f = self.findings('When the question includes an environmental claim, search `chat_docs` with exactly '
                          '"environment". Then search the `size_chart` for fit. Also search `color` variants.')
        sev = {i: [x["severity"] for x in f if "`%s`" % i in x["title"]] for i in ("chat_docs", "size_chart", "color")}
        self.assertEqual(sev["chat_docs"], ["high"])
        self.assertEqual(sev["size_chart"], ["high"])
        self.assertEqual(sev["color"], ["low"])
        fix = [x["fix"] for x in f if "`chat_docs`" in x["title"]][0]
        self.assertIn("If this is an attribute, ignore", fix)
        q = self.findings("Query the `help_center` first.")
        self.assertEqual([x["severity"] for x in q if "`help_center`" in x["title"]], ["high"])

    def test_tool_noun_and_algolia_prefix_are_high(self):
        f = self.findings("Use the `faq_lookup` tool. Also try `algolia_recommend`.")
        high = [x["title"] for x in f if x["severity"] == "high"]
        self.assertTrue(any("`faq_lookup`" in t for t in high))
        self.assertTrue(any("`algolia_recommend`" in t for t in high))


# 8. size_payload never suggests an empty whitelist
class SizePayloadFallbackTest(unittest.TestCase):
    def test_all_heavy_falls_back(self):
        hits = [{k: "x" * 40 for k in ("a", "b", "c", "d", "e", "f")} for _ in range(3)]
        r = size_payload.analyze({"hits": hits})
        self.assertTrue(all(a["heavy"] for a in r["attributes"]))
        self.assertEqual(r["suggestedSearchParameters"]["attributesToRetrieve"], ["a", "b", "c", "d", "e", "f"])
        self.assertIn("manual review", r["warning"])
        self.assertIn("WARNING", size_payload.render(r))
        self.assertTrue(size_payload.analyze({"hits": []})["suggestedSearchParameters"]["attributesToRetrieve"])


# 9. cluster_failures detector scope
class ClusterHardeningTest(unittest.TestCase):
    def analyze(self, js):
        with tempdir() as tmp:
            write_run(tmp, js, {})
            return cluster_failures.analyze(ab.load_run_dir(tmp))

    def test_retrieval_metrics_skipped(self):
        r = self.analyze([judgment("c1", "relevance", False, 0.0, "raw data shows no matching category"),
                          judgment("c2", "recall_metric", False, 0.1, "retrieval_recall=0.10 raw data mismatch")])
        self.assertIsNone(r["instrumentArtifact"])
        self.assertEqual(r["metrics"]["relevance"]["artifactCheck"], "skipped (retrieval-scored metric)")
        self.assertEqual(r["metrics"]["recall_metric"]["artifactCheck"], "skipped (retrieval-scored metric)")

    def test_narrow_phrases(self):
        weak = [judgment("c%d" % i, "tone", False, 0.1, reason) for i, reason in enumerate(
            ["Response is formatted as json", "Duplicate product names", "It describes tool calls it will make"])]
        self.assertIsNone(self.analyze(weak)["instrumentArtifact"])
        for reason in ("Shows internal logs to the user", "Exposes tool call logic", "Contains raw JSON",
                       "Includes an internal monologue", "Repeated sections of text", "Leaks chain-of-thought"):
            r = self.analyze([judgment("c1", "tone", False, 0.1, reason)])
            self.assertIsNotNone(r["instrumentArtifact"], reason)


# 10. helper nits
class HelperHardeningTest(unittest.TestCase):
    def test_extract_json_ignores_short_tokens_and_prefers_last(self):
        self.assertEqual(ab.extract_json("[INFO] start\n[2] retry\n{\"ok\": 1}"), {"ok": 1})
        self.assertEqual(ab.extract_json('{"level": "info"}\nlog\n{"payload": true}'), {"payload": True})
        self.assertEqual(ab.extract_json("[2] warming up\n[{\"id\": \"a\"}]"), [{"id": "a"}])
        self.assertEqual(ab.extract_json("listing\n[]\n"), [])
        with self.assertRaises(ValueError):
            ab.extract_json("[2] only a token, then text")

    def test_timeout_marker_case_insensitive(self):
        replies = [(1, "", "Error: The Operation Was Aborted Due To Timeout"), (0, '{"ok": 1}', "")]
        with fake_algobot(lambda a: replies.pop(0)) as runner:
            self.assertEqual(ab.call(["x"]), {"ok": 1})
        self.assertEqual(len(runner.calls), 2)

    def test_judgments_list_unknown_shape(self):
        with self.assertRaises(ab.AlgobotError):
            ab.judgments_list({"weird": 1})
        with self.assertRaises(ab.AlgobotError):
            ab.judgments_list("text")
        self.assertEqual(ab.judgments_list({"judgments": []}), [])

    def test_safe_name_no_collision(self):
        self.assertEqual(ab.safe_name("case-123_ok.v2"), "case-123_ok.v2")
        self.assertNotEqual(ab.safe_name("a/b"), ab.safe_name("a_b"))
        self.assertNotEqual(ab.safe_name("a/b"), ab.safe_name("a:b"))


if __name__ == "__main__":
    unittest.main()
