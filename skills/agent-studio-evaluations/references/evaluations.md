# Agent Studio Evaluations (`algobot evals`)

EXPERIMENTAL: the endpoints are undocumented (not in the public OpenAPI spec or
the official SDK) and may change without notice. Requires `algobot-ai` >= 2.1.0
(npm latest), which ships the `evals` command group and the `agents`/
`conversations` fixes this guide relies on; probe with
`algobot evals metrics list` first.

Observed CLI limits and quirks (page sizes, generation caps, status values,
timeouts) are collected in [known-limits.md](known-limits.md). Helper scripts
(stdlib Python 3.9+, run any of them with `--help`) live in the `scripts/`
folder of this skill's directory. Below, `SKILL_DIR` means the directory
containing this skill's `SKILL.md`, wherever it was installed, and scripts are
called as `python3 "$SKILL_DIR/scripts/<name>.py"`.

## Mental model

An evaluation measures an agent against a dataset of cases using judged
metrics. The lifecycle has three stages:

1. **Profiles** (stage 1: Analyse): snapshots of the index and the agent that
   generation is grounded on.
2. **Dataset** (stage 2): generated or imported cases, reviewed and finalized.
3. **Experiment** (stage 3): executes the agent on the dataset (real
   completions), then judges every case per metric.

Experiments are asynchronous: `create` returns immediately, poll with
`algobot evals experiments get <id>`. Statuses flow through
`resolving_profiles` -> `generating`/`awaiting_review` -> `running` ->
`judging` -> `completed`.

## Command map

```bash
# Profiles
algobot evals profiles build --index-name <idx> [--agent-uuid <id>]
algobot evals profiles build-status <taskId>
algobot evals profiles list-index / list-agent
algobot evals profiles get-index / get-agent / delete-index / delete-agent <profileId>

# Metrics (rubric catalog; builtins: relevance, faithfulness, tone, compliance, tool_correctness)
algobot evals metrics list
algobot evals metrics create --slug <slug> --name <name> --rubrics '<json|file>'
algobot evals metrics update <metricId> --json patch.json
algobot evals metrics delete <metricId>          # builtins are refused

# Datasets (usually implicit: experiments create resolve-or-create one)
algobot evals datasets create --name <name> --objective full \
    --index-profile-id <id> --agent-profile-id <id> [--generation-params '<json|file>']
# objective: full | retrieval_quality | instruction_adherence | custom
algobot evals datasets list / get / delete / drift-check / refresh-profiles
algobot evals datasets generate <datasetId>       # async generation
algobot evals datasets build-status <datasetId> <taskId>  # STARTED | SUCCESS | FAILURE
algobot evals datasets list-cases <datasetId> [--status suggested] \
    [--metric-slug <slug>] [--limit 200] [--offset <n>]
algobot evals cases update <caseId> [--expected '<json|file>'] [--status approved]
algobot evals datasets bulk-status <datasetId> --status approved --filter-status suggested
# case review status: suggested | approved | edited | rejected
algobot evals datasets finalize <datasetId>
algobot evals datasets import --name <name> --rows '<json|file>' \
    [--rows-jsonl <file>] --index-profile-id <id> --agent-profile-id <id> \
    [--validate-only] [--auto-finalize]

# Experiments
algobot evals experiments create --index-name <idx> --agent-uuid <id> \
    --metric-ids <m1,m2> --num-cases 100 [--name ...] [--dataset-id <id>] \
    [--iterations <n>] [--require-dataset-review]
# --num-cases is a TOTAL across the selected metrics (CLI default 25)
algobot evals experiments list / get / proceed / cancel / retry / delete
algobot evals experiments run <experimentId>      # execute a ready experiment
algobot evals experiments runs <experimentId>     # list runs

# Runs (read path)
algobot evals runs get <experimentId> <runId>            # receipt + progress counts
algobot evals runs summary <experimentId> <runId>        # per-metric stats, CI, macro
algobot evals runs judgments <experimentId> <runId> --limit 200   # verdicts + reasons
algobot evals runs case <experimentId> <runId> <caseId>  # one case drilldown;
    # <caseId> = the judgment's `evalCaseId` field (NOT the judgment `id` -
    # that returns a misleading 404 "Case ... is not part of run ...")

# Stateless helpers
algobot evals judge --metric-slug tone --query "..." --response-text "..."
algobot evals compare --run-a <baselineRun> --run-b <candidateRun>

# Stored-completion verdicts (score a served completion WITHOUT regenerating)
algobot evals judgments create <messageId>   # judge one stored completion
algobot evals judgments list <messageId>     # every recorded verdict for it
```

JSON-valued flags accept inline JSON or a path to a JSON file
(`--rubrics rubric.json`). All commands print JSON and respect the global
`--jq`, `--dry-run` (kill switch: mutations blocked), and `--verbose` flags.

## Dataset provenance gate

A comparison is only as good as the dataset under it. Before any paid run,
print a run card ([../templates/run-card.md](../templates/run-card.md)):
dataset id and name, `agentProfileId`, `indexProfileId`, case count per metric,
and the distinct tone contracts (`tone_constraint` + `specific_rule`).

- Always pass `--dataset-id` on every run you intend to compare.
- Observed on 2.1.0: `experiments create` without `--dataset-id` resolved to
  an existing dataset for the same index even though the agent was different.
  The second agent inherited the first agent's tone contract and scored 0 of
  17 on tone, although its prompt asked for an energetic voice. When you let a
  baseline resolve-or-create, read `experiments get` and confirm the dataset's
  agent profile was built on THIS agent before trusting the scores.
- Refuse to compare runs from different datasets. `compare` requires a shared
  dataset; raw pass counts across datasets are not comparable either.

## Case counts and generation limits

`experiments create --num-cases` is a TOTAL split across the selected
metrics, not a per-metric count (observed: an even split; `--num-cases 100`
with 2 metrics gave 50 cases each). There is no CLI flag for an exact
per-metric count: a `numCasesPerMetric` key in `--generation-params` was
observed to be accepted but ignored (planning followed `targetCount`). For N
cases per metric, use "N per metric above the cap" below. Worked example: 3 metrics x 100 cases each =
`--num-cases 300`, which costs about 300 completions plus 300 judge calls.
Imported datasets have one metric per case (wide rows explode into one case
per metric, disclosed in the import report).

Generation limits (observed on 2.1.0, experimental):

| `datasets create --generation-params` | Observed behavior |
|---|---|
| `targetCount` | Accepted up to 100 |
| `minPerMetric` | Accepted up to 20; with 20, about 20 cases per metric were planned |
| `numCasesPerMetric` | Accepted but ignored; planning followed `targetCount` |
| `metricSlugs` | Ignored: every builtin metric was planned |
| delete while generating | Refused with HTTP 409 |

### N per metric above the cap

To get N cases for each wanted metric when N exceeds what one generation
yields:

1. Create one dataset from the source agent's profiles with
   `--generation-params '{"minPerMetric": 20}'`, run `datasets generate
   <datasetId>`, capture the `taskId` it returns, and poll
   `datasets build-status <datasetId> <taskId>` until it reports `SUCCESS`.
2. Measure the yield: because `metricSlugs` is ignored and every builtin
   metric is planned, count the cases per wanted metric with
   `datasets list-cases <datasetId> --metric-slug <slug> --limit 200 --offset <k>`.
   Only then compute how many more datasets you need for N per metric
   (about 20 per metric per dataset was observed with `minPerMetric` 20, but
   use your measured yield), and generate them the same way.
3. For each dataset and each wanted metric, page `list-cases` as in step 2.
4. Build one import row per case with `query`, `metricSlug`, `expected`,
   `difficulty`, `language` (copy them from the listed case; confirm the field
   names against one listed case first). Dedupe by `(metricSlug, query)`.
5. Validate, then import:

   ```bash
   algobot evals datasets import --name "<name>-merged" --rows-jsonl rows.jsonl \
       --index-profile-id <id> --agent-profile-id <id> --validate-only
   algobot evals datasets import --name "<name>-merged" --rows-jsonl rows.jsonl \
       --index-profile-id <id> --agent-profile-id <id> --auto-finalize
   ```

6. Run baseline and candidate on the merged dataset id. Delete the source
   datasets only after generation has finished.

## Tone contract review

Observed: generated tone cases carry a fixed style contract (for example no
exclamation marks, no emoji, no ampersands, or no slang or hype words)
regardless of the agent profile. A tone score against a contract that
contradicts the agent's brand voice measures the contract, not the agent.

1. List the distinct contracts: page `list-cases --metric-slug tone` and
   collect each case's `expected.tone_constraint`, `expected.specific_rule`
   and `expected.bad_response_patterns`.
2. Compare each contract with the voice instructions in the agent's prompt.
3. If they conflict, rewrite the `expected` block of the conflicting tone
   cases from a brand voice contract
   ([../templates/brand-voice-tone-contract.json](../templates/brand-voice-tone-contract.json))
   and re-import them as a new dataset (`--validate-only`, then
   `--auto-finalize`). `cases update <caseId> --expected <file>` also exists;
   we have not verified it on a finalized dataset.
4. Use the rewritten dataset for baseline AND candidate. Never compare a run on
   the original contracts with a run on rewritten ones.

Rewrite snippet (stdlib Python; input is a JSONL of import rows built as in
"N per metric above the cap"):

```python
import json, sys
contract = json.load(open("brand-voice-tone-contract.json"))
with open(sys.argv[1]) as src, open(sys.argv[2], "w") as dst:
    for line in src:
        row = json.loads(line)
        if row.get("metricSlug") == "tone":
            row["expected"] = {**row.get("expected", {}), **contract}
        dst.write(json.dumps(row, ensure_ascii=False) + "\n")
```

## Reading results

`runs summary` returns, per metric and overall: `judgedCases`, `passedCases`,
`meanScore`, `passRate`, confidence intervals, and `underpowered` (sample too
small to trust). `runs judgments` adds one verdict per case with a judge
`reason`: cluster those reasons to find failure themes. `runs case` gives one
case's full picture (retrieved records, tool calls, judge verdicts).

`python3 "$SKILL_DIR/scripts/fetch_run.py" <experimentId> <runId>` pages
judgments (200 per page) and case details into a local folder;
`python3 "$SKILL_DIR/scripts/cluster_failures.py" DIR` groups
failing reasons into themes per metric and flags likely instrument artifacts.

Trust rules:

- Faithfulness failures usually mean the answer contains claims not supported
  by retrieved records (invented names, invented attributes).
- Tone failures are violations of the case's `tone_constraint` /
  `bad_response_patterns` (e.g. emojis, exclamation marks, hype). Check the
  contract itself first (see "Tone contract review").

## Statistics rules

This section and "Promotion gate" are the single source for the thresholds
used across this skill, `/improve-agent` and the report template.

- Headroom: do not tune a metric whose baseline pass rate is >= 95 percent.
- Compare on SHARED cases only. `compare` reports `sharedCases`; raw pass
  counts over different case counts are not comparable.
  `python3 "$SKILL_DIR/scripts/compare_runs.py" DIR_A DIR_B` restricts to
  shared cases, excludes judge errors, adds token and latency deltas, and
  refuses to run when a run's dataset id is missing or the two differ.
- Claim an improvement only when the paired delta's confidence interval
  excludes zero.
- Fewer than about 50 cases per metric, or `underpowered: true`, is
  directional only (`compare_runs.py` reports its CI check as n/a there).
  Say so in the report.

## Promotion gate

Recommend promoting a candidate only when ALL of these hold:

1. No metric regressed on any dataset used in the loop. "Regressed" means the
   paired-delta CI for that metric lies entirely below zero, or the point
   estimate is below zero on a run that is not underpowered.
2. At least one metric improved (paired-delta CI entirely above zero), OR
   cost fell by >= 20 percent (mean input plus output tokens per case) with
   every metric's delta CI containing zero. The cost-only path additionally
   requires every metric to be not underpowered.
3. The instrument check passed, or its artifacts were excluded and reported.

Always show the instructions/tools diff and the rollback snapshot path. The
snapshot is taken in `/improve-agent` Step 0, before any tuning
(`lineage.py add snapshot <path>`), so the gate can always name it.

## Instrument check

Run this before clustering failures or proposing any change. It costs at most
2 judge calls per metric checked (keep `--limit 2` on the script below).

1. Take 2 failing cases of the metric and read them with
   `runs case <experimentId> <runId> <caseId>`.
2. Compare `completion.responseText` (what the user reads) with
   `completion.answerText` (observed in `runs case` output: the prose plus
   the argument values of display tools).
3. Re-judge the clean text (nothing is stored):

   ```bash
   algobot evals judge --metric-slug tone --query "<query>" \
       --response-text "<responseText>" --expected expected.json
   ```

   `python3 "$SKILL_DIR/scripts/rescore_clean.py" DIR --metric tone --limit 2 --yes`
   does this for the first 2 failing cases of a fetched run (without `--yes`
   it only prints the planned call count; drop `--limit` to re-judge every
   failing case, which costs one judge call each).

Observed on 2.1.0: for an agent ending its turn with a grouped-results display
tool, one tone case scored 1.0 on `responseText` and 0.2 on `answerText`, and
judge reasons mentioned "logs, tool calls, raw data".

Rule: if the reasons mention logs, tool calls, raw data, repeated text or
chain-of-thought but the answer the user sees is clean, treat it as an
instrument artifact, not an agent defect. Do not tune prompts against it, and
report it. A failure that PASSES a clean re-judge (a flip) is evidence for
this reading only when the two texts differ: judge variability alone can
produce a flip, so investigate it before excluding the case from tuning.
Relevance appeared to grade displayed values by design in our
runs, so do not apply the rule to relevance. We have not measured whether faithfulness, compliance or
text-statistics metrics are skewed the same way.

## Efficiency

Report cost and latency beside pass rates for every run: mean and median input
tokens, output tokens and duration per case (`compare_runs.py` prints
them for two fetched runs).

Payload sizing: one Search tool call can dominate input tokens. Save a raw
search and rank record attributes by serialized size:

```bash
algolia search <index> --query "<typical query>" > search.json
python3 "$SKILL_DIR/scripts/size_payload.py" search.json   # or pipe JSON in with -
```

Proposal template for the Search tool's `searchParameters` in the agent
config (not the request-time `algolia.searchParameters` of a completions
call, which rejects these keys; see the `algolia-agent-studio` skill's guide,
Integration Facts):

```json
{
  "hitsPerPage": 12,
  "attributesToRetrieve": ["objectID", "name", "price", "url", "<attributes the prompt cites>"],
  "attributesToHighlight": [],
  "attributesToSnippet": []
}
```

Warnings:

- A static `attributesToRetrieve` whitelist can override attributes the prompt
  tells the agent to retrieve. Include every attribute the instructions name.
- A low hit cap can reduce recall. Observed: a small relevance dip at 8 hits,
  none at 12.

Illustration from one tuning session (not a guarantee): one search returned
about 250 KB for 20 hits; trimming roughly halved mean input tokens and cut
latency 25 to 40 percent, with quality within noise.

## Failure theme -> knob mapping

| Failure theme | Where to fix |
|---|---|
| Tone violations (excitement mirroring, emojis, hype) | Agent instructions: add an explicit OUTPUT STYLE contract |
| Tone failures against a contract that contradicts the agent's voice | Not an agent defect: rewrite the tone contract (see "Tone contract review") |
| Reasons mention logs, tool calls, raw data, repeated text, chain-of-thought, but the visible answer is clean | Instrument artifact: run the instrument check, do not tune the prompt |
| Faithfulness (invented facts, invented variants/colors) | Agent instructions: ACCURACY section ("only reference attributes that appear in tool output"); check returned fields of the search tool |
| Wrong/irrelevant results | Index-side: settings, ranking, searchable attributes (use the `algolia-cli` skill) |
| Tool errors, wrong tool use | Agent tool configuration; instructions on tool-usage budget; run `commands/audit-agent.md` for prompt/tool name mismatches |
| Guardrail misses | Agent guardrails/entry points; instructions Prohibited section |
| Slow/costly runs, high input tokens | Search tool retrieval size (see "Efficiency"), model tier, `--num-cases` only as high as needed |

## Real conversation history datasets (import)

Generated datasets cover the catalog synthetically. Imported datasets let you
evaluate the agent on its actual user traffic: each row is a question a real
user asked (with the conversation's prior turns as frozen context). Import
format version 1; the report from `--validate-only` is the authoritative check
that your rows match it.

Row shapes (JSONL, one row per line):

```jsonc
// narrow: one case
{"query": "...", "metricSlug": "faithfulness", "expected": {"fact_type": "..."},
 "difficulty": "medium", "language": "en"}
// wide: explodes into one case per metrics entry (cost is disclosed in the
// import report before anything is created)
{"query": "...", "metrics": {"relevance": {...}, "faithfulness": {...}}}
// multi-turn: freeze the prior turns verbatim; "query" is the last turn. At
// run time the history is replayed ahead of the query and only the last turn
// is generated and scored.
{"query": "so which of those two is machine washable?",
 "metrics": {"faithfulness": {"fact_type": "care_instructions"}},
 "messages": [{"role": "user", "content": "..."},
              {"role": "assistant", "content": "..."}]}
```

Asymmetry rule: capture inputs only (query + prior turns) and drop the
response the agent actually served. The run regenerates the answer, which is
what makes baseline vs candidate deltas meaningful on the same real inputs.
(Scoring a served historical completion without re-generating is a different
tool: `evals judgments create`.)

Required `expected` keys per metric (caught by `--validate-only`):

- `faithfulness`: `{"fact_type": "..."}` minimum; no golden answer needed.
  Best default metric for history datasets.
- `relevance`: requires NON-EMPTY `should_contain_categories` and/or
  `keywords_in_results`; the scorer is retrieval F1 and empty targets score 0.
  Targets must be product terms that can appear in the catalog corpus, never
  query function words ("what's", "return policy"). Skip relevance if you
  cannot author them confidently.
- `tone`: `{"tone_constraint": "<style contract>", "bad_response_patterns": ["<substring patterns>"]}`;
  `compliance`: `{"expectedOutcome": "allow"|"block"}` (rewritten server-side to per-case rules).
  Generated tone cases also carried a `specific_rule` key (observed); include
  it when you copy a contract.

### History triage (before building rows)

Conversation history is not always real users. Triage the export first and
print a verdict, "looks organic" or "looks scripted":

| Signal | Scripted when (rule of thumb) |
|---|---|
| Creation-date concentration | Most conversations fall on one or two days |
| Duplicate first-turn rate | Many conversations open with the exact same question |
| User-token coverage | No or almost no conversations carry a user token |
| Turns per conversation | Uniform, short sessions with no follow-ups |

Observed in one session: 111 conversations, 106 created on one day, 57
distinct first questions repeated up to 6 times, no user tokens. That was
scripted QA traffic, not users. A dataset built from it measures the QA
script. Ask the user before using scripted traffic as "real history".

Transform rules:

- Dedupe by (frozen history, query).
- Trim trailing user turns from `messages` (observed: import rejects a row
  whose history ends on a user turn that differs from the query).
- Scan for PII and scrub it before anything leaves the machine.
- Wide rows (several metrics per row) multiply the case count: disclose the
  exploded count and its cost.
- Delete the raw export and `rows.jsonl` after the import.

`python3 "$SKILL_DIR/scripts/build_history_dataset.py" --from-json export.json --out DIR` writes
`rows.jsonl` plus `triage.json` (the signals above and the verdict). Run it
with `--help` for the tone contract and metric options; it assigns
`fact_type` from a small keyword map with a generic fallback and prints the
fallback rate, so review rows with the fallback before importing.

Recipe:

```bash
# 1. Extract the agent's conversations.
#    REQUIRES algobot-ai >= 2.1.0: the global --agent/--agent-id override
#    reaches ALL conversations commands and `conversations list` supports
#    --json with ANSI-free, untruncated piped output (see the version gate
#    in SKILL.md). On older releases neither exists, so real-history
#    extraction is impossible: stop and upgrade instead of working around.
algobot conversations list --agent-id <agentId> --json --jq '.data[].id'
#    NOTE: paginate with the LONG form `--page 2`; the short `-p` collides
#    with the global `--profile` flag ("Profile '2' not found").
#    --jq returns JSON-QUOTED strings (no raw mode): strip the quotes before
#    feeding an id to the next command, e.g.
#    ... --jq '.data[0].id' | tr -d '"'
algobot conversations get <convId> --agent-id <agentId> --json
#    Alternative for bulk extraction: `conversations export --agent-id
#    <agentId> --start-date <date> -o /tmp/<tmpdir>/convs.json` dumps full
#    conversation JSON.

# 2. Transform (script it): one row per user turn; flatten each message's
#    parts array ({type:'text', text}) into a content string; history = prior
#    turns verbatim; SCRUB PII FIRST - imported cases are visible in the
#    dashboard
#    FILTER NON-USER TRAFFIC: the history contains artifacts of previous eval
#    runs (messageIds starting with `evalcase-`, conversationIds matching
#    `eval-experiment_run_*`) and technical test conversations. Exclude them,
#    or the dataset evaluates the eval harness instead of real users.
#    Apply the triage and transform rules above (dedupe, trim trailing user
#    turns, disclose wide-row case counts).
#    DATA HYGIENE: the export and rows.jsonl hold real user conversations -
#    write them to a temp dir and DELETE both after the import; never commit
#    them.

# 3. Profiles (async): the `profiles build` RESPONSE ITSELF returns
#    indexProfileId and agentProfileId (build-status only reports progress) -
#    use those ids in step 4
algobot evals profiles build --index-name <idx> --agent-uuid <agentId>

# 4. Import: validate first, then create (atomic: any bad line fails the
#    whole import; cases land APPROVED, report errors are line-numbered)
algobot evals datasets import --name "real-history-<date>" \
    --rows-jsonl rows.jsonl --index-profile-id <id> --agent-profile-id <id> \
    --validate-only
algobot evals datasets import --name "real-history-<date>" \
    --rows-jsonl rows.jsonl --index-profile-id <id> --agent-profile-id <id> \
    --auto-finalize

# 5. Pilot small before a full run: the dataset is free to build. Cost rule:
#    IMPORTED case = one metric, so a run costs num-cases completions and
#    num-cases judgments. GENERATED datasets: --num-cases is a TOTAL split
#    across the selected metrics, not a per-metric count
#    (3 metrics x 100 each = --num-cases 300). Caps: 1000 rows / 1000 cases.
algobot evals experiments create --index-name <idx> --agent-uuid <agentId> \
    --metric-ids <m1,m2> --dataset-id <datasetId> --num-cases 12
```

## Clone-based tuning loop (improve a production agent safely)

Most agents worth tuning are published and serving traffic. Never tune in
place by default: clone first, tune the clone, promote on explicit approval.
The full loop is encoded in the `/improve-agent` command
(`commands/improve-agent.md`); the mechanics:

```bash
# 1. Baseline eval on the CURRENT agent config (never changes during the loop).
#    Print the run card first; pass --dataset-id when you have one. Without
#    it, confirm the resolved dataset's agent profile is this agent's
#    (see "Dataset provenance gate").
algobot evals experiments create --index-name <idx> --agent-uuid <srcId> \
    --metric-ids <m1,m2> --num-cases 100 [--dataset-id <datasetId>]

# 2. Clone (agents copy refuses same-env copies; scaffold -> create instead)
#    2.1.0+: scaffold strips deprecated config fields
#    (enableAlgoliaMcp) and captures providerId, which agents create forwards
#    - no manual provider patch needed (see the version gate in SKILL.md).
algobot agents scaffold <srcId>
# edit agent-config.json: set a tracking name like "<name> [eval-tuning <date>]"
algobot agents create --config agent-config.json --name "<name> [eval-tuning <date>]"

# 3. Tune the DRAFT clone and re-run on the SAME dataset
algobot agents patch <cloneId> --json instructions-patch.json
algobot evals experiments create --index-name <idx> --agent-uuid <cloneId> \
    --metric-ids <m1,m2> --num-cases 100 --dataset-id <baselineDatasetId>
algobot evals compare --run-a <baselineRun> --run-b <cloneRun>

# 4. Promotion is a separate, explicit step. The clone has a NEW agent id and
#    the frontend embeds the ORIGINAL agent id (wiring usually owned by
#    another team), so the improvements go live by applying them to the
#    original agent, not by switching to the clone. Snapshot the original
#    config first (agents scaffold) for rollback, show the diff, warn that
#    publishing makes the change immediately live for all users, get
#    approval, then patch + publish the original agent.
```

Safety rules for the loop:

- Agents do not need to be published to be evaluated: keep the clone in
  `draft` for the whole loop (it serves no traffic).
- The user decides the mode up front when the target agent is published:
  duplicate (default, recommended). Never modify a published agent in place.
- Show the exact config diff and get explicit approval before promoting to the
  production agent. Build the promotion patch from the tuned fields only
  (instructions, config, tools); never include `name`, `id`, `status`,
  `providerId`, or timestamps. Never publish automatically. Snapshot the
  original config first (rollback path: re-apply the snapshot and publish
  again), and warn that publishing makes the change immediately live for all
  users of the original agent on every surface that integrates it.
- Cost: every case is a real completion plus judge calls. Generated dataset:
  `--num-cases` is a TOTAL split across the selected metrics (observed);
  there is no CLI flag for an exact per-metric count (see "Case counts and
  generation limits"). Imported dataset: one metric per case. Announce the approximate
  cost before launching large runs.
- Track lineage: source agent id, clone id, datasets, experiments, runs, and
  the rollback snapshot path. `python3 "$SKILL_DIR/scripts/lineage.py" add|list|cleanup-plan`
  keeps them in `lineage.json`; `cleanup-plan` only prints the delete
  commands in a safe order (experiments, then datasets, then the clone) and
  never runs them. Datasets still generating cannot be deleted yet. When
  `experiments create` resolved to an existing dataset, record it with
  `add dataset <datasetId> --reused`: reused datasets are never deleted by
  `cleanup-plan` and are listed under "left alone". Re-adding a dataset with
  `--reused` corrects a `created` entry, and a `reused` origin is never
  downgraded by a later plain `add`.
- Long runs: experiments are asynchronous and a 150-case run took about 10
  minutes in our runs. `python3 "$SKILL_DIR/scripts/wait_experiments.py" ID [ID ...] --timeout S`
  polls several experiments, treats the CLI timeout message as retryable and
  exits on `completed`, `failed`, `cancelled` or `awaiting_review`; a nonzero
  exit code means not every experiment completed, including an id that
  errored (codes in `--help`).

## Gotchas

- `evals experiments create` requires the agent to have a provider linked.
  2.1.0+: `agents scaffold` captures `providerId` and `agents create`
  forwards it, so the clone flow above needs no manual patch (see the
  version gate in SKILL.md).
- `agents copy` refuses same-environment copies; use the scaffold -> create
  flow above.
- Datasets resolve-or-create per experiment: pass `--dataset-id` of the
  baseline experiment's dataset to make runs comparable. Resolve-or-create
  can pick another agent's dataset for the same index (observed; see
  "Dataset provenance gate").
- A `draft` agent cannot be chatted with (`algobot ask` returned HTTP 422
  "Agent is not published", observed). Smoke test drafts with a 3-case
  experiment on the shared dataset and read `runs case` for tool names and
  the answer.
- `compare` requires the two runs to share a dataset; deltas are B - A.
- Destructive evals commands (`delete`) print `{"deleted": true, "id": "..."}`.
- Do not build production tooling on this command group; endpoints may change.
