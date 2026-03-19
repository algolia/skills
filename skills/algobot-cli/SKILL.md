---
name: algobot-cli
description: >-
  ALWAYS use this skill when the user mentions Algolia Agent Studio, algobot,
  or wants any AI agent / RAG / conversational experience built on Algolia.
  Covers: RAG systems on Algolia, conversational product discovery, genAI
  content generation from search results (carousels, product descriptions, page
  headers), chatbots or recommendation agents using Algolia as retrieval,
  algobot CLI (install, init, ask, interactive), Agent Studio agent
  create/update/publish/delete, config-as-code workflows, multi-environment
  deploy (dev/staging/prod), memory and personalization across sessions,
  MCP tool integrations (CRM or inventory alongside Algolia), conversation
  history / GDPR retention, or adding a chat widget alongside InstantSearch.
  Make sure to use this skill any time the user says "algobot", "Agent Studio",
  "RAG with Algolia", "conversational experience", "AI agent" + Algolia,
  "genAI carousel", "chat widget", or asks about building AI features on top
  of Algolia search — even if they don't say "Agent Studio" or "algobot" by name.
  Do NOT use for raw Algolia index ops (records, synonyms, settings, facets,
  rankings) — use algolia-cli instead. Do NOT use for pure frontend search UI
  (InstantSearch components, autocomplete) with no AI/agent layer.
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

- **TUI requires TTY.** `algobot` with no args launches the TUI — hangs in scripts. Always use `ask` or `--text` in non-interactive contexts.
- **Exit codes are 0/1 only** in v2.0. Can't distinguish "not found" from "auth error" — parse stderr if needed.
- **`--output json` missing on most commands** in v2.0. Use `--jq` or JSON-structured stdout.
- **`algobot init` is interactive.** Don't use in CI — use `profiles add` with flags instead.
- **Auth stored in `~/.algobot-cookie`** (AES-256-GCM). Inspect with `algobot auth show`.
- **`--config` auto-discovers `agent-config.json`** in cwd. Explicit: `--config path/to/config.json`.
- **algobot = dev/deploy tool; REST API = production invocation.** Use algobot to build and publish agents; call the Agent Studio completions API directly from your app. Don't guess the endpoint URL — run `algobot agents get <id>` to retrieve it, or check the Agent Studio dashboard.

## Reference Docs

- [Command Reference](references/commands.md) — Full flags for every command
- [Config-as-Code Guide](references/config-as-code.md) — Templates, variables, multi-env patterns
