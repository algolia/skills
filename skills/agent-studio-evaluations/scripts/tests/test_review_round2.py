"""Regression tests for the second review round. Synthetic data only."""

import json
import os
import unittest

from _fixtures import ab, capture, case_doc, fake_algobot, judgment, tempdir, write_run

import audit_agent
import cluster_failures
import compare_runs
import fetch_run
import lineage
import rescore_clean
import wait_experiments


# 1. rescore_clean: repeated iterations judged once, judge errors never re-judged
class RescoreDedupeTest(unittest.TestCase):
    def test_repeated_iterations_are_judged_once(self):
        err = judgment("c3", "tone", False, None)
        err["passed"] = None
        js = [judgment("c1", "tone", False, 0.0), judgment("c1", "tone", False, 0.2),
              judgment("c2", "tone", False, 0.1), err]
        cases = {c: case_doc("q " + c, "Clean " + c) for c in ("c1", "c2", "c3")}
        with tempdir() as tmp, fake_algobot(lambda a: json.dumps({"score": 1.0, "passed": True})) as runner:
            write_run(tmp, js, cases)
            code, out, _ = capture(rescore_clean.main, [tmp, "--metric", "tone", "--yes"])
            self.assertEqual(code, 0)
            self.assertEqual(len(runner.calls), 2)  # c1 deduped, c3 judge error skipped
            self.assertIn("planned judge calls: 2", out)
            self.assertIn("1 judge error(s) not re-judged", out)
            saved = ab.load_json(os.path.join(tmp, "rescore-tone.json"))
            rows = {r["evalCaseId"]: r for r in saved["rows"]}
            self.assertAlmostEqual(rows["c1"]["storedScore"], 0.1)  # mean of the two iterations
            self.assertFalse(rows["c1"]["storedPassed"])
            self.assertEqual(len(saved["judgeErrors"]), 1)

    def test_limit_counts_distinct_cases(self):
        js = [judgment("c1", "tone", False, 0.0), judgment("c1", "tone", False, 0.2),
              judgment("c2", "tone", False, 0.1), judgment("c3", "tone", False, 0.1)]
        cases = {c: case_doc("q " + c, "Clean " + c) for c in ("c1", "c2", "c3")}
        with tempdir() as tmp, fake_algobot(lambda a: json.dumps({"score": 1.0, "passed": True})) as runner:
            write_run(tmp, js, cases)
            capture(rescore_clean.main, [tmp, "--metric", "tone", "--limit", "2", "--yes"])
            self.assertEqual(len(runner.calls), 2)  # --limit 2 = 2 distinct cases, not 3 judgments

    def test_flip_without_text_evidence_is_not_called_an_artifact(self):
        js = [judgment("c1", "tone", False, 0.1)]
        cases = {"c1": case_doc("q1", "Clean answer.")}  # answerText == responseText: no evidence
        with tempdir() as tmp, fake_algobot(lambda a: json.dumps({"score": 1.0, "passed": True})):
            write_run(tmp, js, cases)
            _, out, _ = capture(rescore_clean.main, [tmp, "--metric", "tone", "--yes"])
            self.assertIn("NOT by itself evidence", out)
            self.assertNotIn("instrument-artifact reading", out)
            saved = ab.load_json(os.path.join(tmp, "rescore-tone.json"))
        self.assertEqual((saved["flips"], saved["flipsWithContaminatedInput"]), (1, 0))

    def test_flip_with_contaminated_input_names_the_evidence(self):
        js = [judgment("c1", "tone", False, 0.1)]
        cases = {"c1": case_doc("q1", "Clean answer.", answer="internal logs and raw data dump")}
        with tempdir() as tmp, fake_algobot(lambda a: json.dumps({"score": 1.0, "passed": True})):
            write_run(tmp, js, cases)
            _, out, _ = capture(rescore_clean.main, [tmp, "--metric", "tone", "--yes"])
        self.assertIn("instrument-artifact reading", out)
        self.assertIn("1 flip(s) had responseText != answerText", out)


# 2. cluster_failures: judge errors are infrastructure, not agent failures
class ClusterJudgeErrorsTest(unittest.TestCase):
    def test_judge_error_not_counted_as_failure_or_theme(self):
        err = judgment("c2", "tone", False, None, "Shows internal logs to the user")
        err["passed"] = None
        js = [judgment("c1", "tone", True, 1.0), err]
        with tempdir() as tmp:
            write_run(tmp, js, {})
            r = cluster_failures.analyze(ab.load_run_dir(tmp))
            m = r["metrics"]["tone"]
            self.assertEqual((m["judged"], m["failed"], m["judgeErrors"]), (2, 0, 1))
            self.assertIsNone(r["instrumentArtifact"])  # the error reason must not fire the warning
            self.assertEqual(m["themes"], [])
            _, out, _ = capture(cluster_failures.main, [tmp])
        self.assertIn("judge error", out)
        self.assertIn("0 of 2 failed", out)


# 3. compare_runs: both shared efficiency summaries sit on the same fetched cases
class CompareEfficiencyIntersectionTest(unittest.TestCase):
    def test_partial_fetch_cannot_make_b_look_cheaper(self):
        cases_a = {"c_cheap": case_doc("q", "ok", input_tokens=100),
                   "c_expensive": case_doc("q", "ok", input_tokens=100000)}
        cases_b = {"c_cheap": case_doc("q", "ok", input_tokens=100)}  # expensive case not fetched in B
        js = [judgment("c_cheap", "tone", True, 1.0), judgment("c_expensive", "tone", True, 1.0)]
        with tempdir() as tmp:
            a = write_run(os.path.join(tmp, "a"), js, cases_a)
            b = write_run(os.path.join(tmp, "b"), js, cases_b)
            r = compare_runs.compare(ab.load_run_dir(a), ab.load_run_dir(b))
            eff = r["efficiency"]
            self.assertEqual(eff["A_sharedCases"]["cases"], 1)
            self.assertEqual(eff["B_sharedCases"]["cases"], 1)  # same case set, not A=2 / B=1
            self.assertEqual(eff["A_sharedCases"]["inputTokensMean"], 100.0)
            self.assertEqual(eff["B_sharedCases"]["inputTokensMean"], 100.0)
            self.assertIn("excluded from BOTH", r["efficiencySharedCasesNote"])
            _, out, _ = capture(compare_runs.main, [a, b])
        self.assertIn("Note: 1 shared case(s)", out)


# 4. fetch_run: --out identity is verified before any write
class FetchIdentityTest(unittest.TestCase):
    def handler(self, judgments):
        def h(args):
            if args[:3] == ["evals", "experiments", "get"]:
                return json.dumps({"id": "exp-1", "datasetId": "dataset-synthetic-1"})
            if args[:3] == ["evals", "runs", "summary"]:
                return json.dumps({"overall": {}})
            if args[:3] == ["evals", "runs", "judgments"]:
                limit = int(args[args.index("--limit") + 1])
                offset = int(args[args.index("--offset") + 1])
                return json.dumps({"judgments": judgments[offset:offset + limit]})
            if args[:3] == ["evals", "runs", "case"]:
                return json.dumps(case_doc("q " + args[5], "a"))
            raise AssertionError(args)
        return h

    def test_refuses_other_run_in_same_out(self):
        js = [judgment("c1", "tone", True, 1.0)]
        with tempdir() as tmp:
            out = os.path.join(tmp, "run")
            with fake_algobot(self.handler(js)):
                code, _, _ = capture(fetch_run.main, ["exp-1", "run-1", "--out", out])
            self.assertEqual(code, 0)
            before = sorted(os.listdir(os.path.join(out, "cases")))
            with fake_algobot(self.handler(js)) as runner:
                code, _, err = capture(fetch_run.main, ["exp-1", "run-2", "--out", out])
            self.assertEqual(code, 2)
            self.assertIn("refusing to write", err)
            self.assertIn("run-1", err)
            self.assertEqual(runner.calls, [])  # nothing fetched, nothing overwritten
            self.assertEqual(sorted(os.listdir(os.path.join(out, "cases"))), before)

    def test_refuses_unverifiable_directory(self):
        with tempdir() as tmp:
            out = os.path.join(tmp, "run")
            os.makedirs(os.path.join(out, "cases"))
            with open(os.path.join(out, "cases", "c1.json"), "w") as fh:
                fh.write("{}")
            with fake_algobot(self.handler([judgment("c1", "tone", True, 1.0)])) as runner:
                code, _, err = capture(fetch_run.main, ["exp-1", "run-1", "--out", out])
            self.assertEqual(code, 2)
            self.assertIn("cannot be verified", err)
            self.assertEqual(runner.calls, [])

    def test_same_identity_reuses_cache(self):
        js = [judgment("c1", "tone", True, 1.0)]
        with tempdir() as tmp:
            out = os.path.join(tmp, "run")
            with fake_algobot(self.handler(js)):
                capture(fetch_run.main, ["exp-1", "run-1", "--out", out])
            with fake_algobot(self.handler(js)) as runner:
                code, _, _ = capture(fetch_run.main, ["exp-1", "run-1", "--out", out])
            self.assertEqual(code, 0)
            self.assertFalse(any("case" in c for c in runner.calls))


# 5. lineage: dataset origin is reconciled, reused is never downgraded
class LineageOriginReconcileTest(unittest.TestCase):
    def test_late_reused_correction_updates_origin(self):
        with tempdir() as tmp:
            f = os.path.join(tmp, "l.json")
            capture(lineage.main, ["--file", f, "add", "dataset", "ds-1"])
            _, out, _ = capture(lineage.main, ["--file", f, "add", "dataset", "ds-1", "--reused"])
            self.assertIn("corrected created -> reused", out)
            _, plan, _ = capture(lineage.main, ["--file", f, "cleanup-plan"])
            self.assertNotIn("datasets delete ds-1", plan)
            self.assertIn("left alone", plan)
            self.assertEqual(ab.load_json(f)["datasets"][0]["origin"], "reused")

    def test_reused_origin_is_never_downgraded(self):
        with tempdir() as tmp:
            f = os.path.join(tmp, "l.json")
            capture(lineage.main, ["--file", f, "add", "dataset", "ds-1", "--reused"])
            _, out, _ = capture(lineage.main, ["--file", f, "add", "dataset", "ds-1"])
            self.assertIn("keeping that origin", out)
            _, plan, _ = capture(lineage.main, ["--file", f, "cleanup-plan"])
            self.assertNotIn("datasets delete ds-1", plan)
            self.assertEqual(ab.load_json(f)["datasets"][0]["origin"], "reused")


# 6. audit_agent: scaffolded configs reference PROMPT.md, not the prompt text
class AuditInstructionsFileTest(unittest.TestCase):
    def test_scaffold_config_audits_the_prompt_file(self):
        with tempdir() as tmp:
            config = os.path.join(tmp, "agent-config.json")
            ab.write_json(config, {"instructions": "PROMPT.md", "tools": []})
            with open(os.path.join(tmp, "PROMPT.md"), "w") as fh:
                fh.write("Use the `mystery_tool` tool for lookups.")
            _, out, _ = capture(audit_agent.main, [config])
            self.assertIn("`mystery_tool`", out)  # finding from the prompt text...

    def test_missing_prompt_file_fails_loudly(self):
        with tempdir() as tmp:
            config = os.path.join(tmp, "agent-config.json")
            ab.write_json(config, {"instructions": "PROMPT.md", "tools": []})
            with self.assertRaises(SystemExit):
                capture(audit_agent.main, [config])  # ... instead of silently passing --strict

    def test_remote_instructions_untouched(self):
        agent = {"instructions": "PROMPT.md"}
        self.assertIs(audit_agent.resolve_instructions(agent, None), agent)


# 7. wait_experiments: the deadline holds across poll batches
class WaitDeadlineTest(unittest.TestCase):
    def test_poll_after_deadline_is_skipped(self):
        with fake_algobot(lambda a: json.dumps({"status": "running"})) as runner:
            kind, message = wait_experiments.poll_one("e1", None, wait_experiments.CLOCK() - 1.0)
        self.assertEqual(kind, "timeout")
        self.assertIn("deadline", message)
        self.assertEqual(runner.calls, [])

    def test_late_batches_shrink_and_skip(self):
        now = [0.0]

        def clock():
            value = now[0]
            now[0] += 30.0  # every clock read costs 30 fake seconds
            return value

        old = wait_experiments.CLOCK
        wait_experiments.CLOCK = clock
        try:
            with fake_algobot(lambda a: json.dumps({"status": "running"})) as runner:
                code, out, _ = capture(wait_experiments.main,
                                       ["e%d" % i for i in range(9)] + ["--timeout", "40", "--interval", "999"])
        finally:
            wait_experiments.CLOCK = old
        self.assertEqual(code, 2)
        self.assertTrue(all(t is not None and t <= 40 for t in runner.timeouts))
        self.assertLess(len(runner.calls), 9)  # calls after the deadline were skipped, not sent
        statuses = json.loads(out)["statuses"]
        self.assertTrue(all(v in ("running", "unknown") for v in statuses.values()))


if __name__ == "__main__":
    unittest.main()
