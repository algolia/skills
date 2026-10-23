# Agent Studio Evaluations (`algobot evals`)

EXPERIMENTAL: the endpoints are undocumented (not in the public OpenAPI spec or
the official SDK) and may change without notice. Requires `algobot-ai` >= 2.1.0
(npm latest), which ships the `evals` command group and the `agents`/
`conversations` fixes this guide relies on; probe with
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
algobot evals datasets import --name <name> --rows '<json|file>' \
    [--rows-jsonl <file>] --index-profile-id <id> --agent-profile-id <id> \
    [--validate-only] [--auto-finalize]

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
- Tone failures are violations of the case's `tone_constraint` /
  `bad_response_patterns` (e.g. emojis, exclamation marks, hype).

## Failure theme -> knob mapping

| Failure theme | Where to fix |
|---|---|
| Tone violations (excitement mirroring, emojis, hype) | Agent instructions: add an explicit OUTPUT STYLE contract |
| Faithfulness (invented facts, invented variants/colors) | Agent instructions: ACCURACY section ("only reference attributes that appear in tool output"); check returned fields of the search tool |
| Wrong/irrelevant results | Index-side: settings, ranking, searchable attributes (use the `algolia-cli` skill) |
| Tool errors, wrong tool use | Agent tool configuration; instructions on tool-usage budget |
| Guardrail misses | Agent guardrails/entry points; instructions Prohibited section |
| Slow/costly runs | Model tier, `--num-cases` only as high as needed |

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
#    evenly (ceil) across the selected metrics, not a per-metric count. Caps: 1000 rows / 1000 cases.
algobot evals experiments create --index-name <idx> --agent-uuid <agentId> \
    --metric-ids <m1,m2> --dataset-id <datasetId> --num-cases 12
```

## Clone-based tuning loop (improve a production agent safely)

Most agents worth tuning are published and serving traffic. Never tune in
place by default: clone first, tune the clone, promote on explicit approval.
The full loop is encoded in the `/improve-agent` command
(`commands/improve-agent.md`); the mechanics:

```bash
# 1. Baseline eval on the CURRENT agent config (never changes during the loop)
algobot evals experiments create --index-name <idx> --agent-uuid <srcId> \
    --metric-ids <m1,m2> --num-cases 100

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
  `--num-cases` is a TOTAL split evenly (ceil) across the selected metrics
  (`numCasesPerMetric` is the separate API field for an exact per-metric
  count). Imported dataset: one metric per case. Announce the approximate
  cost before launching large runs.
- Track lineage: source agent id, clone id, baseline run id, candidate run ids.

## Gotchas

- `evals experiments create` requires the agent to have a provider linked.
  2.1.0+: `agents scaffold` captures `providerId` and `agents create`
  forwards it, so the clone flow above needs no manual patch (see the
  version gate in SKILL.md).
- `agents copy` refuses same-environment copies; use the scaffold -> create
  flow above.
- Datasets resolve-or-create per experiment: pass `--dataset-id` of the
  baseline experiment's dataset to make runs comparable.
- `compare` requires the two runs to share a dataset; deltas are B - A.
- Destructive evals commands (`delete`) print `{"deleted": true, "id": "..."}`.
- Do not build production tooling on this command group; endpoints may change.
