import json
import os
import unittest

from _fixtures import ab, capture, case_doc, fake_algobot, judgment, no_network, tempdir, write_run

import cluster_failures
import compare_runs
import rescore_clean

CALM = {"tone_constraint": "Calm and factual, no exclamation marks", "bad_response_patterns": ["!"]}
ENERGETIC = {"tone_constraint": "Energetic, upbeat", "bad_response_patterns": []}


class ClusterFailuresTest(unittest.TestCase):
    def test_themes_and_instrument_warning(self):
        js = [
            judgment("c1", "tone", False, 0.2, "Response contains logs, tool calls and raw data instead of prose"),
            judgment("c2", "tone", False, 0.3, "Uses exclamation marks and emoji"),
            judgment("c3", "faithfulness", False, 0.0, "Claims a color not supported by retrieved records"),
            judgment("c4", "faithfulness", True, 1.0, "ok"),
        ]
        cases = {"c1": case_doc("q1", "Clean answer.", answer="Clean answer. {\"objectID\": \"1\"}")}
        with tempdir() as tmp, no_network():
            write_run(tmp, js, cases)
            code, out, _ = capture(cluster_failures.main, [tmp])
            self.assertEqual(code, 0)
            self.assertIn("INSTRUMENT ARTIFACT", out)
            self.assertIn("rescore_clean.py", out)
            self.assertIn("responseText", out)
            self.assertIn("differ=yes", out)
            self.assertIn("## faithfulness: 1 of 2 failed", out)
            self.assertIn("invented or unsupported facts: 1", out)
            self.assertIn("emoji: 1", out)
            result = cluster_failures.analyze(ab.load_run_dir(tmp))
            self.assertEqual(result["instrumentArtifact"]["count"], 1)

    def test_no_warning_on_plain_failures(self):
        with tempdir() as tmp:
            write_run(tmp, [judgment("c1", "tone", False, 0.1, "Too much hype")], {})
            _, out, _ = capture(cluster_failures.main, [tmp])
            self.assertNotIn("INSTRUMENT ARTIFACT", out)
            self.assertIn("hype or slang: 1", out)


def build_pair(tmp, n=60, b_better=True, ds_b="dataset-synthetic-1"):
    ja, jb, ca, cb = [], [], {}, {}
    for i in range(n):
        cid = "c%03d" % i
        ja.append(judgment(cid, "tone", i % 2 == 0, 0.5))
        jb.append(judgment(cid, "tone", True if b_better else i % 2 == 0, 0.9 if b_better else 0.5))
        exp = CALM if i % 3 else ENERGETIC
        ca[cid] = case_doc("q", "a", expected=exp, input_tokens=2000 + i, duration_ms=4000)
        cb[cid] = case_doc("q", "a", expected=exp, input_tokens=1000 + i, duration_ms=3000)
    ja.append(judgment("only-a", "tone", False, 0.0))
    jb.append(judgment("only-b", "tone", True, 1.0))
    a = write_run(os.path.join(tmp, "a"), ja, ca)
    b = write_run(os.path.join(tmp, "b"), jb, cb, dataset_id=ds_b)
    return a, b


class CompareRunsTest(unittest.TestCase):
    def test_shared_cases_delta_and_ci(self):
        with tempdir() as tmp, no_network():
            a, b = build_pair(tmp)
            result = compare_runs.compare(ab.load_run_dir(a), ab.load_run_dir(b))
            tone = result["metrics"]["tone"]
            self.assertEqual(tone["sharedCases"], 60)
            self.assertEqual((tone["onlyInA"], tone["onlyInB"]), (1, 1))
            self.assertEqual((tone["passedA"], tone["passedB"]), (30, 60))
            self.assertAlmostEqual(tone["passRateDelta"], 0.5)
            self.assertTrue(tone["passRateCiExcludesZero"])
            self.assertFalse(tone["underpowered"])
            lo, hi = tone["passRateDeltaCI95"]
            self.assertTrue(0 < lo <= 0.5 <= hi)
            again = compare_runs.compare(ab.load_run_dir(a), ab.load_run_dir(b))
            self.assertEqual(again, result)
            self.assertEqual(result["efficiency"]["A_sharedCases"]["inputTokensMedian"], 2029.5)
            self.assertEqual(result["efficiency"]["B_sharedCases"]["durationMsMean"], 3000)
            groups = {g["toneConstraint"]: g for g in result["toneByContract"]}
            self.assertEqual(groups[ENERGETIC["tone_constraint"]]["sharedCases"], 20)
            self.assertEqual(groups[CALM["tone_constraint"]]["passedB"], 40)

    def test_markdown_states_method(self):
        with tempdir() as tmp:
            a, b = build_pair(tmp, n=10, b_better=False)
            code, out, _ = capture(compare_runs.main, [a, b])
            self.assertEqual(code, 0)
            self.assertIn("paired percentile bootstrap", out)
            self.assertIn("underpowered", out)
            self.assertIn("Tone pass rate by contract", out)

    def test_refuses_different_datasets(self):
        with tempdir() as tmp:
            a, b = build_pair(tmp, n=5, ds_b="dataset-synthetic-2")
            code, _, err = capture(compare_runs.main, [a, b])
            self.assertEqual(code, 2)
            self.assertIn("different datasets", err)
            code, _, _ = capture(compare_runs.main, [a, b, "--allow-different-datasets"])
            self.assertEqual(code, 0)


class RescoreCleanTest(unittest.TestCase):
    def setUp(self):
        self.js = [judgment("c1", "tone", False, 0.2, "logs"), judgment("c2", "tone", False, 0.3, "x"),
                   judgment("c3", "tone", True, 1.0), judgment("c4", "faithfulness", False, 0.0)]
        self.cases = {"c1": case_doc("q1", "Clean one.", answer="dump", expected=CALM),
                      "c2": case_doc("q2", "Clean two.", expected=CALM)}

    def test_without_yes_plans_only(self):
        with tempdir() as tmp, no_network() as runner:
            write_run(tmp, self.js, self.cases)
            code, out, _ = capture(rescore_clean.main, [tmp, "--metric", "tone"])
            self.assertEqual(code, 0)
            self.assertIn("planned judge calls: 2", out)
            self.assertEqual(runner.calls, [])
            self.assertFalse(os.path.exists(os.path.join(tmp, "rescore-tone.json")))

    def test_with_yes_calls_judge(self):
        def handler(args):
            self.assertEqual(args[:2], ["evals", "judge"])
            self.assertEqual(args[args.index("--metric-slug") + 1], "tone")
            self.assertTrue(args[args.index("--response-text") + 1].startswith("Clean"))
            self.assertEqual(json.loads(args[args.index("--expected") + 1]), CALM)
            return json.dumps({"score": 1.0, "passed": True, "reason": "fine"})
        with tempdir() as tmp, fake_algobot(handler) as runner:
            write_run(tmp, self.js, self.cases)
            code, out, _ = capture(rescore_clean.main, [tmp, "--metric", "tone", "--yes"])
            self.assertEqual(code, 0)
            self.assertEqual(len(runner.calls), 2)
            self.assertIn("2 of 2 stored-failing case(s) pass", out)
            saved = ab.load_json(os.path.join(tmp, "rescore-tone.json"))
            self.assertEqual([r["cleanScore"] for r in saved["rows"]], [1.0, 1.0])


if __name__ == "__main__":
    unittest.main()
