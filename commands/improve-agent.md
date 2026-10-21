---
description: Improve an Algolia Agent Studio agent by running evaluations on a safe clone, analyzing failures, and promoting validated changes on explicit approval.
---

# Improve Agent (eval-driven tuning)

Improve an Agent Studio agent's eval score: run an evaluation, analyze failing
cases, change agent settings on a draft clone, re-evaluate, compare, and
promote only with the user's explicit approval.

Load the `algobot-cli` skill (and `references/evaluations.md` inside it) before
running any command below.

## Step 0: Preconditions

1. Confirm the CLI has evals support: `algobot evals metrics list`. If unknown
   command, the installed `algobot-ai` predates evals (npm 2.0.0 does not
   ship it): stop and ask the user to install a release that does
   (`npm i -g algobot-ai@latest`).
2. Resolve the target agent: `algobot agents list` / `algobot agents get <id>`.
   Record: id, name, `status`, `providerId`, index (`tools[].indices[]`).
3. Ask the user for metrics if not specified (`algobot evals metrics list`),
   a case count (default 100), and any focus (tone, faithfulness, ...).
4. Announce the cost: every case = a real completion + judge calls.
   Generated dataset: `num-cases` cases per metric. Imported dataset: one
   metric per case.

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
# (recent releases: the scaffold already strips deprecated config fields and
#  captures providerId, which `agents create` forwards - see the version gate
#  in the skill; otherwise manually remove `enableAlgoliaMcp` and patch the
#  provider: algobot agents patch <cloneId> --json provider-patch.json)
algobot agents create --config agent-config.json --name "<name> [eval-tuning <date>]"
```

Keep the clone in `draft` for the entire loop: agents do not need to be
published to be evaluated, and a draft agent serves no traffic.

## Step 2: Dataset source + baseline

Ask the user which dataset the loop should run on (same choice for the whole
loop; the baseline and every candidate run must share it):

- **Generated (default)**: let `experiments create` resolve-or-create one.
  Broad synthetic catalog coverage, zero authoring.
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

Run the baseline eval on the CURRENT production agent config (not the clone)
and wait for completion (poll `algobot evals experiments get <id>`):

```bash
algobot evals experiments create --index-name <idx> --agent-uuid <srcId> \
    --metric-ids <m1,m2> --num-cases <n>
# with an imported dataset: add --dataset-id <importedDatasetId>
```

Record the experiment id, its dataset id, and its run id. Read
`algobot evals runs summary <expId> <runId>`: per-metric pass rates, mean
scores, confidence intervals, `underpowered` flag.

## Step 3: Failure analysis

1. `algobot evals runs judgments <expId> <runId> --limit 200` and cluster the
   judge `reason` fields into failure themes with counts.
2. For representative failures, `algobot evals runs case <expId> <runId> <caseId>`
   and read the retrieved records/tool calls to confirm the root cause.
3. Map themes to knobs using the table in `references/evaluations.md`
   (tone -> OUTPUT STYLE instructions; faithfulness -> ACCURACY instructions or
   tool returned fields; relevance -> index settings via the `algolia-cli`
   skill; tool errors -> tool config).

Present to the user: themes, counts, the planned change(s) to the CLONE's
config, and expected impact. Wait for approval before touching anything.

## Step 4: Tune the clone and re-run

Apply the approved change(s) to the clone only (e.g.
`algobot agents patch <cloneId> --json patch.json`), then re-run on the SAME
dataset and compare:

```bash
algobot evals experiments create --index-name <idx> --agent-uuid <cloneId> \
    --metric-ids <m1,m2> --num-cases <n> --dataset-id <baselineDatasetId>
algobot evals compare --run-a <baselineRunId> --run-b <cloneRunId>
```

Report before/after per metric. Iterate Step 3-4 while failures remain and the
user wants to continue. Keep the same dataset and num-cases so comparisons stay
valid; check `underpowered` before celebrating small deltas.

## Step 5: Promotion (never automatic)

Why promote to the original agent instead of switching to the clone: the clone
has a NEW agent id, and the frontend/integration embeds the ORIGINAL agent id.
That wiring is usually owned by a different team, so the tuning user cannot
repoint it. The only way the improvements go live without a frontend change is
to apply the validated changes to the original live agent: its id (and every
integration pointing at it) stays valid.

When the user is satisfied with the clone's results:

1. Take a rollback snapshot of the original agent BEFORE any change (if not
   already saved): `algobot agents scaffold <srcId>` (config + PROMPT.md) or
   save the `algobot agents get <srcId>` output. This is what makes the
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

Rollback path (spell it out, keep the snapshot dir until the user confirms the
promotion is good):

```bash
# restore the Step 5.1 snapshot config, then publish
algobot agents update <srcId> --config <snapshotDir>/agent-config.json
algobot agents publish <srcId>
```

Tell the user about the rollback path BEFORE they approve.

## Rules

- Never modify the production agent without an explicit, per-change approval
  and a visible diff.
- Never publish automatically.
- Never launch large evals without announcing the cost first.
- Track lineage in the conversation: source id, clone id, baseline
  experiment/run ids, candidate run ids.
- If any command fails with HTTP 422 mentioning a scaffold or provider issue,
  see the Gotchas in `references/evaluations.md`.
