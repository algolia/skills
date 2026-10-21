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
   command, ask the user to `npm update -g algobot-ai` and stop.
2. Resolve the target agent: `algobot agents list` / `algobot agents get <id>`.
   Record: id, name, `status`, `providerId`, index (`tools[].indices[]`).
3. Ask the user for metrics if not specified (`algobot evals metrics list`),
   a case count (default 100), and any focus (tone, faithfulness, ...).
4. Announce the cost: each case = a real completion + judge calls per metric.

## Step 1: Mode selection (only if the agent is published)

| Target agent | Behavior |
|---|---|
| `published` + created by the user (production) | Ask: duplicate (recommended default) or modify in place (requires explicit confirmation; changes go live on publish) |
| `published` + named `... [eval-tuning <date>]` (created by this loop) | It is this loop's own testbed: modify freely |
| `draft` (never published, not live) | Modify freely, still show diffs |

If duplicating (default), create the clone and record its id:

```bash
algobot agents scaffold <srcId>
# edit agent-config.json: remove deprecated config fields (enableAlgoliaMcp),
# set name to "<name> [eval-tuning <date>]"
algobot agents create --config agent-config.json --name "<name> [eval-tuning <date>]"
algobot agents patch <cloneId> --json <(echo '{"providerId": "<srcProviderId>"}')
```

Keep the clone in `draft` for the entire loop: agents do not need to be
published to be evaluated, and a draft agent serves no traffic.

## Step 2: Baseline

Run the baseline eval on the CURRENT production agent config (not the clone)
and wait for completion (poll `algobot evals experiments get <id>`):

```bash
algobot evals experiments create --index-name <idx> --agent-uuid <srcId> \
    --metric-ids <m1,m2> --num-cases <n>
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

When the user is satisfied:

1. Show the exact config diff between the production agent and the clone
   (instructions, config, tools).
2. Ask for explicit approval to apply it to the production agent. If the
   in-place mode was chosen at Step 1, this approval already happened per
   change; still show each diff before applying.
3. On approval: `algobot agents patch <srcId> --json patch.json` (and
   `--publish` / `algobot agents publish <srcId>` if the agent must go live).
4. Offer cleanup: delete the clone and any scratch artifacts, or keep them.

## Rules

- Never modify the production agent without an explicit, per-change approval
  and a visible diff.
- Never publish automatically.
- Never launch large evals without announcing the cost first.
- Track lineage in the conversation: source id, clone id, baseline
  experiment/run ids, candidate run ids.
- If any command fails with HTTP 422 mentioning a scaffold or provider issue,
  see the Gotchas in `references/evaluations.md`.
