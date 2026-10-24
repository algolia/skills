# Evaluation helper scripts

Stdlib-only Python 3.9+ helpers for the `agent-studio-evaluations` skill.
They read through the `algobot` CLI (`algobot-ai` >= 2.1.0) and local JSON
files only. None of them deletes or changes a remote object: `lineage.py
cleanup-plan` prints commands for you to review, and `rescore_clean.py` spends
judge calls only with `--yes`. The evals endpoints are experimental. The
behavior these scripts work around was observed on algobot-ai 2.1.0 and may
change.

Pass `--profile <name>` to any script that calls `algobot`; it is forwarded
as the global `--profile` flag (placed before the subcommand, because the
short `-p` collides with `--page` on some subcommands). Set `ALGOBOT_BIN` to
use a different `algobot` binary.

Run the tests (no network, synthetic fixtures only):

```bash
python3 -B -m unittest discover -s skills/agent-studio-evaluations/scripts/tests
```

## fetch_run.py

`fetch_run.py <experimentId> <runId> [--out DIR] [--profile P] [--workers N] [--refresh] [--skip-cases]`

Writes `meta.json`, `experiment.json`, `summary.json`, `judgments.json`
(paged with `--limit 200` and `--offset`; paging stops with a warning when a
page adds no new judgment id, and after 200 pages) and
`cases/<evalCaseId>.json` (one `runs case` call per distinct case, small
thread pool, reused when already on disk; ids that need sanitizing get a short
hash suffix). Default folder: `./run-<runId>`.

```bash
python3 fetch_run.py <EXPERIMENT_ID> <RUN_ID> --out runs/baseline --profile <PROFILE>
```

## cluster_failures.py

`cluster_failures.py DIR [--top N] [--json]`

Failure count, keyword themes and top judge reasons per metric. Prints an
INSTRUMENT ARTIFACT warning when failing reasons of LLM-judged metrics use
phrases such as "internal logs", "tool call logic", "raw data", "raw JSON",
"repeated text", "chain-of-thought" or "internal monologue", with the
verification steps. `relevance`, and any metric whose reasons look like
`retrieval_recall=...`, are skipped.

```bash
python3 cluster_failures.py runs/baseline
```

## compare_runs.py

`compare_runs.py DIR_A DIR_B [--resamples N] [--seed S] [--allow-different-datasets] [--json]`

A = baseline, B = candidate, deltas B - A, on shared evalCaseIds only. Per
metric: pass counts, mean score, and two separate 95 percent paired
percentile bootstrap intervals (seeded, deterministic), one for the
pass-rate delta and one for the mean-score delta. Below 50 judged pairs a
metric is underpowered and "CI excludes 0" is n/a. Judge errors
(`passed: null`) are excluded from pass counts and shown as errors A/B.
Repeated judgments of one (metric, case) are aggregated: score = mean,
passed = more than half of the iterations passed (tie = failed). Also mean
and median input tokens, output tokens and duration per run, and tone pass
rate by `expected.tone_constraint`. Exits 2 when the dataset ids differ or
either `meta.json` has no `datasetId` (override: `--allow-different-datasets`).

```bash
python3 compare_runs.py runs/baseline runs/candidate
```

## rescore_clean.py

`rescore_clean.py DIR --metric tone [--yes] [--include-passing] [--limit N] [--profile P]`

Re-judges `completion.responseText` of failing cases with `algobot evals
judge` (nothing stored, but each call is a paid judge call). Without `--yes`
it prints the planned judge-call count and exits 0. `--limit N` caps the
cases re-judged. A judge call is never retried: a timeout is reported as
unknown and counted, so calls made never exceed the plan. Writes
`DIR/rescore-<metric>.json`.

```bash
python3 rescore_clean.py runs/baseline --metric tone            # plan only
python3 rescore_clean.py runs/baseline --metric tone --limit 2 --yes --profile <PROFILE>
```

## build_history_dataset.py

`build_history_dataset.py --from-json export.json --out DIR [--tone-contract FILE] [--language en]`

Triage first (creation-date concentration, duplicate first-turn rate,
user-token coverage, turns per conversation, verdict "looks scripted" or
"looks organic"), then `rows.jsonl` for `algobot evals datasets import`.
Drops eval-harness artifacts, trims trailing user turns from history,
deduplicates by (history, query), and assigns `fact_type` from a
word-boundary keyword map (fallback rate printed). Timestamps may be ISO
strings or epoch seconds or milliseconds; a median of one user turn per
conversation counts as a scripted signal.

Redaction covers only emails, phone numbers (a `+`, parentheses, or 7 to 15
digits with separators; dates, year ranges and size lists are left alone) and
Luhn-valid 13 to 19 digit card numbers. A manual PII review (names,
addresses, order ids) is still required before importing. Delete the export
and `rows.jsonl` after the import.

```bash
python3 build_history_dataset.py --from-json /tmp/<TMP_DIR>/convs.json --out /tmp/<TMP_DIR>/rows \
    --tone-contract brand-voice-tone-contract.json
```

## size_payload.py

`size_payload.py [FILE|-] [--threshold PCT] [--hits-per-page N] [--json]`

Ranks hit attributes by mean serialized bytes, flags `_highlightResult`,
`_snippetResult`, `_rankingInfo` and anything above 5 percent, and prints a
suggested `searchParameters` JSON as a starting point to review.
`attributesToRetrieve` is never empty: if every attribute is heavy it falls
back to all non-underscore attributes and prints a manual-review warning.

```bash
algolia search <INDEX_NAME> --query "<QUERY>" > /tmp/<TMP_DIR>/response.json
python3 size_payload.py /tmp/<TMP_DIR>/response.json --hits-per-page 12
```

## audit_agent.py

`audit_agent.py <agent-id-or-json-file> [--profile P] [--strict] [--json]`

Static audit, zero eval cost: backticked identifiers in the instructions vs
attached tool names, types and index names, display-tool name mismatch, null
Search-tool `searchParameters`, `max_iterations` 0, deprecated config keys.
An unknown identifier is HIGH only when it starts with `algolia_` or sits
next to the noun "tool" or "index" ("the `x` index"), or is snake_case right
after "search" or "query" with at most one filler word ("search `x`",
"query the `x`"); otherwise LOW. A snake_case attribute after "search" is
therefore reported HIGH: ignore it if it is an attribute.
Identifiers followed by "attribute" or "field" are skipped. Ranked markdown
fix list. Exit 0 even with findings; `--strict` exits 1.

```bash
python3 audit_agent.py <AGENT_ID> --profile <PROFILE>
python3 audit_agent.py agent-config.json --strict
```

## lineage.py

`lineage.py [--file lineage.json] add KIND ID [--note TEXT] [--experiment EXPERIMENT_ID] [--reused]`
`lineage.py [--file lineage.json] list [--json]`
`lineage.py [--file lineage.json] cleanup-plan [--profile P]`

KIND: `source-agent`, `clone`, `snapshot`, `dataset`, `experiment`, `run`.
Datasets are recorded as `created` by the loop unless `--reused` is passed.
`cleanup-plan` prints shell-quoted delete commands in a safe order
(experiments, then created datasets, then the clone), lists reused datasets
under "left alone", prints the clone delete only when a source agent is
recorded and differs from the clone, never lists the source agent, and warns
that a dataset cannot be deleted while it is generating.

```bash
python3 lineage.py add source-agent <SOURCE_AGENT_ID>
python3 lineage.py add clone <CLONE_AGENT_ID> --note "eval-tuning"
python3 lineage.py add dataset <DATASET_ID>             # created by this loop
python3 lineage.py add dataset <BASELINE_DATASET_ID> --reused
python3 lineage.py add run <RUN_ID> --experiment <EXPERIMENT_ID>
python3 lineage.py cleanup-plan --profile <PROFILE>
```

## wait_experiments.py

`wait_experiments.py ID [ID ...] [--timeout S] [--interval S] [--profile P]`

Polls every id in parallel until completed, failed, cancelled or
awaiting_review, or until the timeout (default 3600 seconds; a hard cap, each
call's own timeout never exceeds the remaining wait). The CLI timeout message
is retried. After 3 consecutive other failures (404, 401, bad id, unparseable
output) an id is marked `error` and no longer polled. An unrecognized status
is logged once and polled until the timeout. Exit codes: 0 all completed,
1 any failed or cancelled, 2 timed out, 3 any awaiting_review, 4 any id
errored (checked first). In our runs 150 cases took about 10 minutes.

```bash
python3 wait_experiments.py <EXPERIMENT_ID_A> <EXPERIMENT_ID_B> --timeout 1800 --profile <PROFILE>
```
