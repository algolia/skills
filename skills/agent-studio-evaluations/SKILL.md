---
name: agent-studio-evaluations
description: >-
  Evaluate and improve Algolia Agent Studio agents with the algobot CLI:
  run Agent Studio evaluations, read pass rates and judge verdicts, create
  evaluation datasets (including importing the agent's real conversation
  history as eval cases), compare agent versions before and after a change,
  and run the eval-driven improvement loop (baseline eval, analyze failing
  cases, tune a draft clone, promote on explicit approval). Trigger on:
  "evaluate my agent", "improve my agent", "agent evals", "test my agent
  quality", "create evaluation cases", "evaluation cases from real
  conversation history", "compare agent versions", or Agent Studio
  evaluations. Do NOT use for the algobot CLI reference itself (install,
  auth, agents/chat/profiles/config-as-code commands) - use algobot-cli.
  Do NOT use for raw index ops (records, synonyms, settings) - use
  algolia-cli.
license: MIT
metadata:
  author: algolia
  version: "1.0"
---

# Agent Studio Evaluations

Evaluation and eval-driven improvement workflows for [Algolia Agent Studio](https://www.algolia.com/products/ai/agent-studio/) agents, powered by the `algobot evals` command group of the `algobot` CLI (`npm install -g algobot-ai`).

This skill owns the workflows: what to measure, how to build datasets, how to tune an agent safely. The CLI mechanics (install, auth, command syntax, global flags, agent/chat/profile management) live in the **algobot-cli** skill: load it for any command-level question, or see [references/evaluations.md](references/evaluations.md) for the full command map.

## Version gate

Requires `algobot-ai` >= 2.1.0 (npm latest), which ships the `evals` command group and the `agents`/`conversations` fixes these workflows rely on. Probe with `algobot evals metrics list`; if the command is unknown, the installed `algobot-ai` predates evals: stop and install the release that ships it (`npm i -g algobot-ai@latest`). Verify with `algobot --version`.

## Workflow 1: Evaluate an agent / create evaluation datasets

An evaluation measures an agent against a dataset of cases using judged metrics (profiles -> dataset -> experiment). Two dataset sources:

- **Generated (default)**: `experiments create` resolves-or-creates a dataset grounded on the index and agent profiles. Zero authoring. Best for a first pass.
- **Imported**: evaluate on the agent's actual user traffic. One row per real user turn, prior turns frozen as context. Best when the baseline/candidate delta must be credible on real distribution.

For the real conversation history recipe (export -> transform -> PII scrub -> profiles -> atomic import -> pilot), the required `expected` keys per metric, and every pitfall (100-conversation pagination cap with the long-form `--page` flag, `--jq` quoted output stripping, ANSI/NO_COLOR piping on `conversations list --json`, filtering `evalcase-` / `eval-experiment_run_*` artifacts out of the history, `parts[]` to content flattening), read [references/evaluations.md](references/evaluations.md), section "Real conversation history datasets (import)".

Reading results: `runs summary` (per-metric pass rates, mean, CI, `underpowered`), `runs judgments` (verdict + judge reason per case; cluster reasons into failure themes), `runs case` (single-case drilldown). Trust rules and the failure-theme -> knob mapping are in [references/evaluations.md](references/evaluations.md).

## Workflow 2: Eval-driven agent improvement

The loop (fully scripted in the `/improve-agent` command at the repo root, `commands/improve-agent.md`; mechanics in [references/evaluations.md](references/evaluations.md), "Clone-based tuning loop"):

1. **Baseline eval** on the CURRENT agent config; record experiment, dataset, and run ids.
2. **Analyze failing cases**: cluster judge `reason` fields, drill into representative cases, map themes to knobs (tone -> OUTPUT STYLE instructions; faithfulness -> ACCURACY instructions or tool returned fields; relevance -> index settings via the algolia-cli skill; tool errors -> tool config).
3. **Propose changes** and get user approval before touching anything.
4. **DRAFT clone** via `agents scaffold` + `agents create` (`agents copy` refuses same-env copies); keep the clone in `draft` for the whole loop. Agents do NOT need to be published to be evaluated (a draft serves no traffic) but DO need a provider linked.
5. **Re-eval on the SAME dataset** (`--dataset-id <baselineDatasetId>`) and `compare` (deltas are B - A). Keep dataset and num-cases constant; check `underpowered` before trusting small deltas.
6. **Promote to the ORIGINAL agent only with explicit approval** (the frontend embeds the original agent id, so the clone cannot be swapped in): snapshot the original config, build the patch from tuned fields only (`instructions`, `config`, `tools` - never `name`, `id`, `status`, `providerId`, timestamps), show the diff, warn publishing is immediately live, then patch + publish. Rollback = re-apply the snapshot and publish again.

Duplication-by-default decision rule:

| Target agent | Behavior |
|---|---|
| `published` (production, serving traffic) | Duplicate (recommended default). NEVER modify in place. |
| `draft` clone created by this loop | It is the loop's own testbed: modify freely |
| any other `draft` (never published, not live) | Modify freely, still show diffs |

A `published` agent named `... [eval-tuning <date>]` is treated like any other published agent: the name is not proof it is the loop's testbed.

## Cost rule

Every case is a real completion plus judge calls. Generated dataset: `num-cases` cases per metric. Imported dataset: one metric per case. Announce the approximate cost before launching large runs; prefer n >= 50 per metric for tuning decisions.

## Gotchas

- Agents do NOT need to be published to be evaluated: `evals experiments
  create` works on a `draft` agent (it runs completions server-side without
  serving traffic). Publish only when the tuning result should go live.
- `agents create --provider <name>` does not link the provider: the agent
  stays `draft` and publish 409s. 2.1.0+: `agents scaffold` captures
  `providerId` in the config and `agents create` forwards it; otherwise run
  `algobot agents patch <id> --json patch.json` with
  `{"providerId": "<uuid>"}` after create, then publish.

## Shareable prompt (no skills needed)

For ANY AI agent without this skill installed: [templates/eval-improvement-prompt.md](templates/eval-improvement-prompt.md) is a copy-paste prompt that installs the CLI, authenticates, runs an evaluation, and proposes improvements without touching the production agent.
