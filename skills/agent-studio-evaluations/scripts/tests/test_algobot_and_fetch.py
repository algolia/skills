import json
import os
import unittest

from _fixtures import ab, capture, case_doc, fake_algobot, judgment, tempdir

import fetch_run


class ExtractJsonTest(unittest.TestCase):
    def test_strips_ansi_and_log_prefix(self):
        text = "\x1b[33mwarn\x1b[0m some log line: ok\n{\"a\": [1, 2]}\ntrailing"
        self.assertEqual(ab.extract_json(text), {"a": [1, 2]})

    def test_array_and_bracket_in_prefix(self):
        self.assertEqual(ab.extract_json("[info] fetching\n[1, 2]"), [1, 2])

    def test_no_json(self):
        with self.assertRaises(ValueError):
            ab.extract_json("nothing here")


class CallTest(unittest.TestCase):
    def test_profile_before_subcommand_and_no_color(self):
        with fake_algobot(lambda args: "{}") as runner:
            ab.call(["evals", "runs", "summary", "E", "R"], profile="demo")
        self.assertEqual(runner.calls[0][:3], ["algobot", "--profile", "demo"])
        self.assertEqual(runner.calls[0][3:], ["evals", "runs", "summary", "E", "R"])
        self.assertEqual(runner.envs[0]["NO_COLOR"], "1")

    def test_agent_passthrough(self):
        with fake_algobot(lambda args: "{}") as runner:
            ab.call(["conversations", "list", "--json"], agent_id="agent-x")
        self.assertIn("--agent", runner.calls[0])

    def test_retries_on_timeout_message(self):
        replies = [(1, "", "Error: The operation was aborted due to timeout"), (0, '{"ok": true}', "")]
        with fake_algobot(lambda args: replies.pop(0)) as runner:
            self.assertEqual(ab.call(["evals", "experiments", "get", "E"]), {"ok": True})
        self.assertEqual(len(runner.calls), 2)

    def test_timeout_message_with_json_is_success(self):
        with fake_algobot(lambda args: (1, '{"ok": 1}', "operation was aborted due to timeout")) as runner:
            self.assertEqual(ab.call(["x"]), {"ok": 1})
        self.assertEqual(len(runner.calls), 1)

    def test_other_failure_raises_without_retry(self):
        with fake_algobot(lambda args: (1, "", "Error: 404 not found")) as runner:
            with self.assertRaises(ab.AlgobotError):
                ab.call(["x"])
        self.assertEqual(len(runner.calls), 1)


class FetchRunTest(unittest.TestCase):
    def handler(self, judgments):
        def h(args):
            if args[:3] == ["evals", "experiments", "get"]:
                return json.dumps({"id": "exp-1", "datasetId": "dataset-synthetic-1",
                                   "refs": {"agentProfileId": "ap-1", "indexProfileId": "ip-1"}})
            if args[:3] == ["evals", "runs", "summary"]:
                return json.dumps({"overall": {}, "metrics": []})
            if args[:3] == ["evals", "runs", "judgments"]:
                limit = int(args[args.index("--limit") + 1])
                offset = int(args[args.index("--offset") + 1])
                return json.dumps({"judgments": judgments[offset:offset + limit]})
            if args[:3] == ["evals", "runs", "case"]:
                return "log prefix\n" + json.dumps(case_doc("q " + args[5], "a"))
            raise AssertionError(args)
        return h

    def test_pages_and_caches(self):
        judgments = [judgment("case-%03d" % i, "tone", i % 2 == 0, 1.0) for i in range(250)]
        with tempdir() as tmp:
            out = os.path.join(tmp, "run")
            with fake_algobot(self.handler(judgments)) as runner:
                code, stdout, _ = capture(fetch_run.main, ["exp-1", "run-1", "--out", out, "--profile", "demo"])
            self.assertEqual(code, 0)
            offsets = [c[c.index("--offset") + 1] for c in runner.calls if "judgments" in c]
            self.assertEqual(offsets, ["0", "200"])
            self.assertTrue(all(c[c.index("--limit") + 1] == "200" for c in runner.calls if "judgments" in c))
            self.assertEqual(len(os.listdir(os.path.join(out, "cases"))), 250)
            meta = ab.load_json(os.path.join(out, "meta.json"))
            self.assertEqual(meta["datasetId"], "dataset-synthetic-1")
            self.assertEqual(meta["agentProfileId"], "ap-1")
            self.assertEqual(meta["judgments"], 250)
            with fake_algobot(self.handler(judgments)) as runner:
                capture(fetch_run.main, ["exp-1", "run-1", "--out", out])
            self.assertFalse(any("case" in c for c in runner.calls))


if __name__ == "__main__":
    unittest.main()
