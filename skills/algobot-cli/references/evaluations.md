# Agent Studio Evaluations (`algobot evals`)

EXPERIMENTAL: the endpoints are undocumented (not in the public OpenAPI spec or
the official SDK) and may change without notice. Requires a recent
`algobot-ai` release that ships the `evals` command group; probe with
`algobot evals metrics list` first.

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
    --index-profile-id <id> --agent-profile-id <id>
# objective: full | retrieval_quality | instruction_adherence | custom
algobot evals datasets list / get / delete / drift-check / refresh-profiles
algobot evals datasets generate <datasetId>       # async generation
algobot evals datasets list-cases <datasetId> [--status suggested]
algobot evals datasets bulk-status <datasetId> --status approved --filter-status suggested
# case review status: suggested | approved | edited | rejected
algobot evals datasets finalize <datasetId>
algobot evals datasets import --name <name> --rows '<json|file>' [--auto-finalize]

# Experiments
algobot evals experiments create --index-name <idx> --agent-uuid <id> \
    --metric-ids <m1,m2> --num-cases 100 [--name ...] [--dataset-id <id>]
algobot evals experiments list / get / proceed / cancel / retry / delete
algobot evals experiments run <experimentId>      # execute a ready experiment
algobot evals experiments runs <experimentId>     # list runs

# Runs (read path)
algobot evals runs get <experimentId> <runId>            # receipt + progress counts
algobot evals runs summary <experimentId> <runId>        # per-metric stats, CI, macro
algobot evals runs judgments <experimentId> <runId> --limit 200   # verdicts + reasons
algobot evals runs case <experimentId> <runId> <caseId>  # one case drilldown

# Stateless helpers
algobot evals judge --metric-slug tone --query "..." --response-text "..."
algobot evals compare --run-a <baselineRun> --run-b <candidateRun>
```

JSON-valued flags accept inline JSON or a path to a JSON file
(`--rubrics rubric.json`). All commands print JSON and respect the global
`--jq`, `--dry-run` (kill switch: mutations blocked), and `--verbose` flags.

## Reading results

`runs summary` returns, per metric and overall: `judgedCases`, `passedCases`,
`meanScore`, `passRate`, confidence intervals, and `underpowered` (sample too
small to trust). `runs judgments` adds one verdict per case with a judge
`reason`: cluster those reasons to find failure themes. `runs case` gives one
case's full picture (retrieved records, tool calls, judge verdicts).

Trust rules:

- `passRate` on small runs is noisy; check `underpowered` and the CI before
  drawing conclusions. Prefer n >= 50 per metric for tuning decisions.
- Faithfulness failures usually mean the answer contains claims not supported
  by retrieved records (invented names, invented attributes).
- Tone failures are style-contract violations: exclamation marks, emojis,
  hype/superlatives, mirroring user excitement, ampersands.

## Failure theme -> knob mapping

| Failure theme | Where to fix |
|---|---|
| Tone violations (excitement mirroring, emojis, hype) | Agent instructions: add an explicit OUTPUT STYLE contract |
| Faithfulness (invented facts, invented variants/colors) | Agent instructions: ACCURACY section ("only reference attributes that appear in tool output"); check returned fields of the search tool |
| Wrong/irrelevant results | Index-side: settings, ranking, searchable attributes (use the `algolia-cli` skill) |
| Tool errors, wrong tool use | Agent tool configuration; instructions on tool-usage budget |
| Guardrail misses | Agent guardrails/entry points; instructions Prohibited section |
| Slow/costly runs | Model tier, `--num-cases` only as high as needed |

## Clone-based tuning loop (improve a production agent safely)

Most agents worth tuning are published and serving traffic. Never tune in
place by default: clone first, tune the clone, promote on explicit approval.
The full loop is encoded in the `/improve-agent` command
(`commands/improve-agent.md`); the mechanics:

```bash
# 1. Baseline eval on the CURRENT agent config (never changes during the loop)
algobot evals experiments create --index-name <idx> --agent-uuid <srcId> \
    --metric-ids <m1,m2> --num-cases 100

# 2. Clone (agents copy refuses same-env copies; scaffold -> create -> patch instead)
algobot agents scaffold <srcId>
# edit agent-config.json: remove deprecated config fields (enableAlgoliaMcp),
# set a tracking name like "<name> [eval-tuning <date>]"
algobot agents create --config agent-config.json --name "<name> [eval-tuning <date>]"
algobot agents patch <cloneId> --json provider-patch.json   # {"providerId": "<src providerId>"}

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
  duplicate (default, recommended) or modify in place (explicit confirmation;
  changes go live on publish).
- Show the exact config diff and get explicit approval before promoting to the
  production agent. Never publish automatically. Snapshot the original config
  first (rollback path: re-apply the snapshot and publish again), and warn
  that publishing makes the change immediately live for all users of the
  original agent on every surface that integrates it.
- Cost: every case is a real completion plus judge calls. Announce the
  approximate cost (num-cases x metrics) before launching large runs.
- Track lineage: source agent id, clone id, baseline run id, candidate run ids.

## Gotchas

- `evals experiments create` requires the agent to have a provider linked
  (scaffolded clones need `agents patch` with `providerId`, see issue
  algolia/genai-demos#23).
- `agents copy` refuses same-environment copies; use the scaffold -> create ->
  patch flow above.
- Datasets resolve-or-create per experiment: pass `--dataset-id` of the
  baseline experiment's dataset to make runs comparable.
- `compare` requires the two runs to share a dataset; deltas are B - A.
- Destructive evals commands (`delete`) print `{"deleted": true, "id": "..."}`.
- Do not build production tooling on this command group; endpoints may change.
