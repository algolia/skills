---
name: algobot-cli
description: >-
  Use for anything AI/agent/conversational built on Algolia: algobot CLI,
  Agent Studio, RAG systems, conversational product discovery, genAI content
  generation from search results (carousels, descriptions, headers), chatbots
  or recommendation agents using Algolia as retrieval, config-as-code
  workflows, multi-environment deploy (dev/staging/prod), memory and
  personalization, MCP tool integrations, conversation history / GDPR
  retention, Agent Studio evaluations (run evals, analyze results, improve an
  agent's score), or adding a chat widget alongside InstantSearch. Trigger on:
  "algobot", "Agent Studio", "RAG with Algolia", "conversational experience",
  "AI agent" + Algolia, "genAI carousel", "chat widget", "agent evals",
  "improve my agent", or building AI features on top of Algolia search.
  Do NOT use for raw index ops (records,
  synonyms, settings) — use algolia-cli. Do NOT use for pure frontend search
  UI (InstantSearch, autocomplete) with no AI/agent layer.
license: MIT
metadata:
  author: algolia
  version: "1.1"
---

# Algobot CLI

[Algolia Agent Studio](https://www.algolia.com/products/ai/agent-studio/) is Algolia's platform for building AI agents — RAG systems, conversational experiences, genAI content generation — with Algolia search and recommendations as the retrieval backbone. `algobot` (`npm install -g algobot-ai`) is its CLI for creating, testing, and deploying agents.

## When to Use Algobot vs Other Tools

| Need | Use |
|------|-----|
| Build/manage AI agents on Algolia (RAG, chatbot, genAI UI) | **algobot-cli** (this skill) |
| Algolia search index ops (records, settings, synonyms) | **algolia-cli** |
| Search queries, analytics, recommendations | **algolia-mcp** |

## Setup

```bash
npm install -g algobot-ai
algobot init                    # Interactive wizard (creates first agent + profile)
```

Or add a profile manually (CI-safe, non-interactive):
```bash
algobot profiles add --name prod --env prod
```

## Non-Interactive Mode (Critical for Agents)

**The TUI won't render in non-TTY environments** (CI, scripts, agent subprocesses). Use these instead:

```bash
algobot ask "What is your return policy?"                    # One-shot
algobot interactive --text "hello ||| list my orders ||| /context"  # Multi-turn
algobot agents list --jq '.[] | .name'                       # JSON filtering
```

`--jq` is built-in — no need to install jq separately.

## Core Commands

### Agent Management

```bash
algobot agents list
algobot agents get <agent-id>
algobot agents create --name "Support Bot" --model gpt-4o
algobot agents update <agent-id> --name "New Name"
algobot agents publish <agent-id>
algobot agents unpublish <agent-id>
algobot agents delete <agent-id>
algobot agents copy <id> --from-env dev --to-env prod
```

### Chatting with an Agent

```bash
algobot ask "Find wireless headphones under $100"
algobot --profile staging ask "hello"        # Target specific environment
algobot --verbose ask "debug this"           # Show full HTTP traces
```

### Profile / Environment Management

```bash
algobot profiles list
algobot profiles add --name dev --env dev
algobot profiles setdefault prod
algobot --profile prod agents list
algobot --env dev agents list
```

## Config-as-Code Workflow

Version-control agent definitions with mustache templates — ideal for repeatable deployments across events, teams, or environments.

```bash
# 1. Scaffold from an existing agent
algobot agents scaffold <agent-id>           # → agent-config.json + PROMPT.md

# 2. Preview (API-level kill switch — mutations blocked by construction)
algobot --dry-run agents create --config agent-config.json --var event="Spring 2026"

# 3. Deploy
algobot agents create --config agent-config.json --var event_name="Spring 2026"

# 4. Update + publish in one step
algobot agents update <id> --config agent-config.json --var event_name="Summer 2026" --publish
```

`{{key}}` in JSON fields: JSON-safe escaping. In `.md` instructions: raw substitution.

## Agent Studio Capabilities (via agent config)

Beyond basic chat, Agent Studio agents support:

- **Tools**: Algolia Search, Algolia Browse, Algolia Recommend, client-side tools, and [MCP tools](https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/tools/mcp-tools) (connect CRMs, inventory systems, external APIs alongside Algolia). Manage with `algobot tools list/add/remove`
- **Memory**: Semantic (facts/preferences) and episodic (past interactions) memory across sessions, using `algolia_memorize`, `algolia_ponder`, and `algolia_memory_search` tools. Configure retrieval mode (preload vs preflight) in agent config.
- **Conversation storage**: Persistent history with configurable retention — see `algobot conversations` for export/delete
- **Experimental**: Citation markers `[1][2]` on responses, date injection, response caching — enable in agent config

Use `algobot agents scaffold` to inspect/edit these settings, `algobot --dry-run` to preview before applying.

## Live Development

```bash
algobot agents watch patch.json             # Auto-apply patches on file change
```

## Agent Studio Evaluations (EXPERIMENTAL)

`algobot evals` runs Agent Studio Evaluations from the terminal: metric catalog,
profile snapshots, dataset lifecycle, experiment runs, per-case verdicts, and
before/after comparison.

**Version gate:** the `evals` command group (and several `agents`/`conversations`
fixes this skill relies on) is NOT in npm 2.0.0 (published 2026-03). Probe with
`algobot evals metrics list`; if the command is unknown, the installed
`algobot-ai` predates evals — stop and install the release that ships it
(`npm i -g algobot-ai@latest`).

```bash
algobot evals metrics list                                        # pick metric UUIDs
algobot evals experiments create --index-name <idx> --agent-uuid <id> \
    --metric-ids <m1,m2> --num-cases 100
algobot evals runs summary <experimentId> <runId>                 # pass rates, mean, CI
algobot evals runs judgments <experimentId> <runId> --limit 200   # every verdict + reason
algobot evals compare --run-a <baselineRun> --run-b <candidateRun>
```

Key facts: experiments are asynchronous (poll `evals experiments get`);
`runs summary` / `runs case` are the analysis entry points; agents do NOT need
to be published to be evaluated (a draft agent serves no traffic), but they DO
need a provider. Each case is a real completion plus judge calls, so cost
scales with `--num-cases`.

For the full command map, dataset lifecycle, output schemas, and the
clone-based "improve my agent" tuning loop, read
[references/evaluations.md](references/evaluations.md).

## Global Flags

| Flag | Effect |
|------|--------|
| `--env dev\|staging\|prod\|local` | Target environment |
| `--profile <name>` | Use named profile |
| `--dry-run` | Preview without mutating (API-enforced) |
| `--verbose` | Full HTTP logs |
| `--jq '<expr>'` | Filter JSON output |
| `--confirm` | Skip exec tool confirmations |

## Gotchas

- **TUI requires TTY.** `algobot` with no args launches the TUI — hangs in scripts. Always use `ask` or `--text` in non-interactive contexts. Recent releases reject unknown subcommands with exit 1 instead of silently becoming a chat message (probe: `algobot frobnicate` must exit 1; see the version gate above). On npm 2.0.0 a typo'd command in a script may still print a chat reply with exit 0.
- **Exit codes are 0/1 only** in v2.0. Can't distinguish "not found" from "auth error" — parse stderr if needed.
- **`--output json` missing on most commands** in v2.0. Use `--jq` or JSON-structured stdout.
- **`algobot init` is interactive.** Don't use in CI — use `profiles add` with flags instead.
- **`prod` resolves to the EU host.** v2.0.0 hardcodes three API hosts — `agent-studio.eu.algolia.com` (prod), `agent-studio-staging.eu.algolia.com` (staging), `conversational-ai-dev.algolia.com` (dev). There is no region flag, and the only environment variables read are `ALGOLIA_APP_ID`, `ALGOLIA_APPLICATION_ID`, `ALGOLIA_API_KEY`, and `ALGOLIA_AGENT_ID` — none of which override the host. If an app's agents are not in EU, `agents list` returns `[]` and `agents get <id>` returns 404 for an agent that is live and serving completions. An admin API key does not change this. Confirm the host with `algobot --verbose agents list` before assuming a credential problem.
- **Credentials are stored in `~/.algobot-profiles`** (encrypted), not `~/.algobot-cookie`. `algobot auth show` was removed in v2.0 — use `algobot profiles list`, or `algobot profiles show <name>` for full detail. Note that `profiles show` prints the API key in plaintext, so avoid it in shared terminals, screenshares, and logs.
- **`--config` auto-discovers `agent-config.json`** in cwd. Explicit: `--config path/to/config.json`.
- **algobot = dev/deploy tool; REST API = production invocation.** Use algobot to build and publish agents; call the Agent Studio completions API directly from your app. Don't guess the endpoint URL — run `algobot agents get <id>` to retrieve it, or check the Agent Studio dashboard.
- **Completions URL has no `/agent-studio` prefix.** Use `agent-studio.<region>.algolia.com/1/agents/<id>/completions?stream=false&compatibilityMode=ai-sdk-4`. `compatibilityMode` is required (omitting → 422). Response: `{ id, role, content }` with `content` as a flat string.
- **Agents do not need to be published to be evaluated.** `evals experiments create` works on a `draft` agent (it runs completions server-side without serving traffic). Publish only when the tuning result should go live.
- **`agents create --provider <name>` does not link the provider.** Agent stays `draft`, publish 409s. Prefer passing `providerId` in the config: recent releases make `agents scaffold` capture it and `agents create` forward it (see the version gate above). Otherwise after create, run `algobot agents patch <id> --json patch.json` with `{"providerId": "<uuid>"}`, then publish.

## Reference Docs

- [Command Reference](references/commands.md) — Full flags for every command
- [Config-as-Code Guide](references/config-as-code.md) — Templates, variables, multi-env patterns
