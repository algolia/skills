---
description: Improve an Algolia Agent Studio agent by running evaluations on a safe clone, analyzing failures, and promoting validated changes on explicit approval.
---

# Improve Agent (eval-driven tuning)

Improve an Agent Studio agent's eval score: run an evaluation, analyze failing
cases, change agent settings on a draft clone, re-evaluate, compare, and
promote only with the user's explicit approval.

Load the `agent-studio-evaluations` skill (and `references/evaluations.md`
inside it) before running any command below. For pure CLI mechanics (install,
auth, agents/chat/profiles command syntax) also see the `algobot-cli` skill.

`SKILL_DIR` below means the directory containing the
`agent-studio-evaluations` skill's `SKILL.md` (wherever your agent installed
it). Its helper scripts live in `$SKILL_DIR/scripts/` and its templates in
`$SKILL_DIR/templates/`. Thresholds (headroom, sample size, cost, promotion
gate) are defined once in `references/evaluations.md`; this command points to
them.

## Step 0: Preconditions

1. Confirm the CLI has evals support: `algobot evals metrics list`.
   Evaluations require `algobot-ai` >= 2.1.0 (npm latest). If the command is
   unknown, the installed version predates evals: stop and ask the user to
   upgrade (`npm i -g algobot-ai@latest`) and verify with `algobot --version`.
2. Resolve the target agent: `algobot agents list` / `algobot agents get <id>`.
   Record: id, name, `status`, `providerId`, index (`tools[].indices[]`).
3. Ask the user for metrics if not specified (`algobot evals metrics list`),
   a total case count (the CLI default is 25; e.g. 300 for 3 metrics x 100
   each), and any focus (tone, faithfulness, ...).
4. Announce the cost: every case = a real completion + judge calls.
   `--num-cases` is a TOTAL split across the selected metrics, not a
   per-metric count (observed: 100 with 2 metrics gave 50 each). For 3
   metrics x 100 cases each, pass `--num-cases 300` (about 300 completions
   and 300 judge calls). Imported dataset: one metric per case.
5. Run the zero-cost static audit first (`commands/audit-agent.md`) and fix
   blockers before spending on evals.
6. Dataset gate: every run you will compare passes `--dataset-id`. Before
   each paid run, print a run card
   (`$SKILL_DIR/templates/run-card.md`): dataset id and
   name, `agentProfileId`, `indexProfileId`, cases per metric, distinct tone
   contracts (`tone_constraint` + `specific_rule`). Observed:
   `experiments create` without `--dataset-id` resolved to an existing
   dataset for the same index built for a DIFFERENT agent, so a second agent
   inherited the first agent's tone contract. Refuse to compare runs from
   different datasets.
7. Take the rollback snapshot now, before any tuning, so the promotion gate
   can name it, and start a lineage ledger:

   ```bash
   algobot agents scaffold <srcId> --output-dir <snapshotDir>
   python3 "$SKILL_DIR/scripts/lineage.py" add source-agent <srcId>
   python3 "$SKILL_DIR/scripts/lineage.py" add snapshot <snapshotDir>
   ```

   Record every clone, dataset, experiment and run id as soon as it exists
   (`lineage.py add KIND ID`; run it with `--help`). When `experiments create`
   resolved to an EXISTING dataset instead of creating one, record it with
   `add dataset <datasetId> --reused`: `cleanup-plan` never deletes reused
   datasets and lists them under "left alone".

## Step 1: Mode selection (only if the agent is published)

| Target agent | Behavior |
|---|---|
| `published` (production, serving traffic) | Duplicate (recommended default). NEVER modify in place. |
| `draft` clone created by this loop (id recorded in the lineage, Step 2) | It is this loop's own testbed: modify freely |
| any other `draft` (never published, not live) | Modify freely, still show diffs |

A `published` agent named `... [eval-tuning <date>]` is treated like any other
published agent: the name is not proof it is this loop's testbed.

If duplicating (default), create the clone and record its id:

```bash
algobot agents scaffold <srcId>
# edit agent-config.json: set name to "<name> [eval-tuning <date>]"
# (2.1.0+: the scaffold already strips deprecated config fields and
#  captures providerId, which `agents create` forwards; otherwise manually
#  remove `enableAlgoliaMcp` and patch the provider:
#  algobot agents patch <cloneId> --json provider-patch.json)
algobot agents create --config agent-config.json --name "<name> [eval-tuning <date>]"
```

Keep the clone in `draft` for the entire loop: agents do not need to be
published to be evaluated, and a draft agent serves no traffic.

## Step 2: Dataset source + baseline

Ask the user which dataset the loop should run on (same choice for the whole
loop; the baseline and every candidate run must share it):

- **Generated (default)**: let `experiments create` resolve-or-create one, or
  create it explicitly from the source agent's profiles. Broad synthetic
  catalog coverage, zero authoring. If you let it resolve, check
  `experiments get` and confirm the dataset's agent profile was built on the
  source agent before trusting the baseline.
- **N per metric above the generation cap**: observed caps are
  `targetCount` <= 100 and `minPerMetric` <= 20 in `--generation-params`, and
  `metricSlugs` was ignored (every builtin metric was planned). Generate
  one dataset with `minPerMetric` 20, measure its per-metric yield with
  `datasets list-cases <id> --metric-slug <slug> --limit 200`, then generate
  as many more as that yield requires. Build import rows (query, metricSlug,
  expected, difficulty, language), `datasets import --name <name> ...
  --validate-only` then `--auto-finalize`, and run both agents on the merged
  dataset id. There is no CLI flag for an exact per-metric count. Full
  recipe: `references/evaluations.md`, "N per metric above the cap".
- **Real conversation history**: evaluate on the agent's actual user
  distribution. Build an imported dataset first (full recipe in
  `references/evaluations.md`, "Real conversation history datasets"):
  build the profiles (`algobot evals profiles build --index-name <idx>
  --agent-uuid <srcId>`; the response returns both profile ids - build the
  agent profile on the SOURCE agent, the dataset is reused for clone runs),
  extract the agent's conversations (`conversations list/get --agent-id`),
  transform each user turn into an import row (prior turns verbatim as
  `messages`, served responses dropped, PII scrubbed), `datasets import`
  with `--index-profile-id` / `--agent-profile-id`, `--validate-only` then
  `--auto-finalize`. This needs more authoring
  care (per-metric `expected` keys) but makes the baseline/candidate delta
  directly credible on real traffic. Prefer `faithfulness` + `tone` metrics
  here; author `relevance` targets only if you can do it confidently.
  Triage the history first (date concentration, duplicate first turns,
  user-token coverage, turns per conversation) and tell the user if it looks
  scripted rather than organic:
  `python3 "$SKILL_DIR/scripts/build_history_dataset.py" --from-json export.json --out <tmpdir>`
  writes `rows.jsonl` and `triage.json`. Delete the export and rows after
  the import.

Tone contract review (before the baseline): list the distinct tone contracts
of the dataset's tone cases and compare them with the agent's voice
instructions. Observed: generated tone cases carry a fixed contract (for
example no exclamation marks, no emoji, no ampersands, or no slang or hype
words) whatever the agent's voice. If a contract conflicts, rewrite those
`expected` blocks from
`$SKILL_DIR/templates/brand-voice-tone-contract.json`
and re-import as a new dataset (`references/evaluations.md`, "Tone contract
review"). Use that dataset for baseline and candidates alike.

Run the baseline eval on the CURRENT production agent config (not the clone)
and wait for completion (poll `algobot evals experiments get <id>`):

```bash
algobot evals experiments create --index-name <idx> --agent-uuid <srcId> \
    --metric-ids <m1,m2> --num-cases <total> [--dataset-id <datasetId>]
# imported, merged or rewritten dataset: --dataset-id is required
```

Long runs: a 150-case experiment took about 10 minutes in our runs. Do not
hold a foreground poll past the shell timeout; wait with
`python3 "$SKILL_DIR/scripts/wait_experiments.py" <expId> [<expId> ...] --timeout <seconds>`
(run it with `--help` for its exit codes; a nonzero exit means at least one
experiment did not complete, including an id that errored).
If the CLI prints "operation was aborted due to timeout", check whether the
call landed before retrying it.

If the experiment enters `awaiting_review`, the generated cases need a review
pass before it can run:

```bash
algobot evals datasets list-cases <datasetId> --status suggested
algobot evals datasets bulk-status <datasetId> --status approved --filter-status suggested
algobot evals datasets finalize <datasetId>
algobot evals experiments run <expId>
```

Record the **candidate id** for the whole loop: the clone id when duplicating
(Step 1), otherwise the draft agent's own id when modifying it freely.

Record the experiment id, its dataset id, and its run id (also in the
lineage ledger). Read `algobot evals runs summary <expId> <runId>`:
per-metric pass rates, mean scores, confidence intervals, `underpowered`
flag. Skip tuning metrics without headroom (threshold in
`references/evaluations.md`, "Statistics rules").

## Step 2b: Efficiency baseline

Report cost and latency beside pass rates: mean and median input tokens,
output tokens and duration per case. Fetch the run locally once and reuse it:

```bash
python3 "$SKILL_DIR/scripts/fetch_run.py" <expId> <runId> --out <dirA>
```

If input tokens are high, size one typical search payload and rank record
attributes by serialized size:

```bash
algolia search <index> --query "<typical query>" > search.json
python3 "$SKILL_DIR/scripts/size_payload.py" search.json
```

Propose (do not apply yet) a Search tool `searchParameters` change in the
agent config: `hitsPerPage`, an `attributesToRetrieve` whitelist, empty
`attributesToHighlight` and `attributesToSnippet` (template in
`references/evaluations.md`, "Efficiency"). Warn the user that a static
whitelist can override attributes the prompt tells the agent to retrieve,
and that a low hit cap may reduce recall (observed: a small relevance dip at
8 hits, none at 12). In one tuning session, trimming a search of about
250 KB for 20 hits roughly halved mean input tokens and cut latency 25 to 40
percent with quality within noise; treat that as an illustration, not a
promise.

## Step 3: Failure analysis

1. **Instrument check first.** Take 2 failing cases per metric you plan to
   tune and read them with `algobot evals runs case <expId> <runId> <caseId>`.
   Compare `completion.responseText` (what the user reads) with
   `completion.answerText` (observed in `runs case` output: the prose plus
   the argument values of display tools). Re-judge the clean text, nothing is
   stored, at most 2 judge calls per metric:
   `algobot evals judge --metric-slug <m> --query "<query>" --response-text "<responseText>" --expected expected.json`
   (or `python3 "$SKILL_DIR/scripts/rescore_clean.py" <dirA> --metric tone --limit 2 --yes`;
   without `--yes` it prints the planned judge-call count). Observed: for an
   agent ending on a grouped-results display tool, one tone case scored 1.0
   on `responseText` and 0.2 on `answerText`, with reasons citing "logs, tool
   calls, raw data". Apply the instrument-check rule in
   `references/evaluations.md`, "Instrument check": an artifact is reported,
   never tuned against. A flip on the clean re-score counts as artifact
   evidence only when `responseText != answerText`; judge variability alone
   can produce a flip.
2. `algobot evals runs judgments <expId> <runId> --limit 200` (page with
   `--offset`) and cluster the judge `reason` fields into failure themes with
   counts, or `python3 "$SKILL_DIR/scripts/cluster_failures.py" <dirA>`.
3. For representative failures, `algobot evals runs case <expId> <runId> <caseId>`
   and read the retrieved records/tool calls to confirm the root cause.
4. Map themes to knobs using the table in `references/evaluations.md`
   (tone -> OUTPUT STYLE instructions; faithfulness -> ACCURACY instructions or
   tool returned fields; relevance -> index settings via the `algolia-cli`
   skill; tool errors -> tool config). For retrieval size and integration
   behavior, see the `algolia-agent-studio` skill's guide
   (`skills/algolia-agent-studio/references/agent-studio-guide.md`),
   sections "Integration Facts" and "Latency" (shrinking retrieval payloads).

Present to the user: themes, counts, the instrument-check result, the planned
change(s) to the candidate's config, and expected impact. Wait for approval
before touching anything.

## Step 4: Tune the candidate and re-run

Apply the approved change(s) to the CANDIDATE only - the clone when the target
was duplicated, otherwise the draft agent itself (e.g.
`algobot agents patch <candidateId> --json patch.json`).

Smoke test the draft before a full run. A draft cannot be chatted with
(observed: `algobot ask` returns HTTP 422 "Agent is not published"), so run a
3-case experiment on the shared dataset and read one case for the tool names
called and the answer:

```bash
algobot evals experiments create --index-name <idx> --agent-uuid <candidateId> \
    --metric-ids <m1,m2> --num-cases 3 --dataset-id <baselineDatasetId>
algobot evals runs case <smokeExpId> <smokeRunId> <caseId>
```

Then print the run card, re-run on the SAME dataset and compare:

```bash
algobot evals experiments create --index-name <idx> --agent-uuid <candidateId> \
    --metric-ids <m1,m2> --num-cases <total> --dataset-id <baselineDatasetId>
algobot evals compare --run-a <baselineRunId> --run-b <candidateRunId>
python3 "$SKILL_DIR/scripts/compare_runs.py" <dirA> <dirB>
```

Report before/after per metric on SHARED cases only (`compare` reports
`sharedCases`; raw pass counts over different case counts are not
comparable), with the delta and its interval, plus the token and latency
change. Apply the statistics rules in `references/evaluations.md`
("Statistics rules"). `compare_runs.py` refuses to compare when a run's
dataset id is missing or the two differ, excludes judge errors, and reports
the CI check as n/a for underpowered metrics. Iterate Step 3-4 while
failures remain and the user wants to continue. Keep the same dataset and
num-cases so comparisons stay valid. Write the result with
`$SKILL_DIR/templates/eval-report.md`.

## Step 5: Promotion (never automatic)

Why promote to the original agent instead of switching to the clone: the clone
has a NEW agent id, and the frontend/integration embeds the ORIGINAL agent id.
That wiring is usually owned by a different team, so the tuning user cannot
repoint it. The only way the improvements go live without a frontend change is
to apply the validated changes to the original live agent: its id (and every
integration pointing at it) stays valid.

Promotion gate: recommend promotion only when the gate defined in
`references/evaluations.md`, "Promotion gate", is met, and say which
conditions are not. Always show the instructions/tools diff and the Step 0
rollback snapshot path with the recommendation.

When the user is satisfied with the clone's results:

1. Confirm the rollback snapshot from Step 0 exists (if it is missing, take
   it now, BEFORE any change: `algobot agents scaffold <srcId> --output-dir <snapshotDir>`,
   or save the `algobot agents get <srcId>` output). This is what makes the
   promotion reversible.
2. Show the exact config diff between the production agent and the clone
   (instructions, config, tools). Build `patch.json` from the **tuned fields
   only** (`instructions`, `config`, `tools`). NEVER include `name`, `id`,
   `status`, `providerId`, or timestamps (the clone's name/suffix and ids
   must not leak onto the production agent). Show `patch.json` itself to the
   user as the diff being approved.
3. Ask for explicit approval, warning what will happen:
   - once published, the changes are IMMEDIATELY live for all users of the
     original agent, on every surface that integrates it;
   - users with an open conversation may see the behavior change mid-session;
   - the frontend and integrations keep working unchanged (agent id unchanged,
     no re-wiring needed);
   - recommend doing it outside peak traffic if the change is large.
4. On approval: apply the approved patch to the original agent
   (`algobot agents patch <srcId> --json patch.json`) and publish
   (`--publish` or `algobot agents publish <srcId>`).
5. Optionally run a small confirmation eval on the original agent id to verify
   the promoted config scores like the clone did.
6. Offer cleanup: delete the clone and any scratch artifacts, or keep them.
   `python3 "$SKILL_DIR/scripts/lineage.py" cleanup-plan` prints the delete
   commands in a safe order (experiments, datasets, then the clone) without
   running them. Datasets recorded as `--reused` are never deleted and are
   listed under "left alone"; a dataset still generating cannot be deleted
   yet. Run the commands only after the user confirms.

Rollback path (spell it out, keep the snapshot dir until the user confirms the
promotion is good):

```bash
# restore the Step 0 snapshot config, then publish
algobot agents update <srcId> --config <snapshotDir>/agent-config.json
algobot agents publish <srcId>
```

Tell the user about the rollback path BEFORE they approve.

## Rules

- Never modify the production agent without an explicit, per-change approval
  and a visible diff.
- Never publish automatically.
- Never launch large evals without announcing the cost first.
- Never compare runs from different datasets; always pass `--dataset-id`
  and print a run card before a paid run.
- Track lineage in the conversation and in the ledger (`lineage.py`): source
  id, clone id, datasets, baseline experiment/run ids, candidate run ids,
  snapshot path.
- If any command fails with HTTP 422 mentioning a scaffold or provider issue,
  see the Gotchas in `references/evaluations.md`.
