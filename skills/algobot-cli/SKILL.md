---
name: algobot-cli
description: >-
  Use this skill when a user wants to manage Algolia Agent Studio agents from
  the terminal — creating, listing, updating, publishing, or deleting agents,
  testing agents interactively, deploying agents across environments (dev/staging/prod),
  or automating agent operations in CI/CD pipelines. Also use for config-as-code
  workflows (scaffolding, mustache templates, dry-run previews) and conversation
  history management. The key signal is that the user wants to *act on* Agent
  Studio agents or chat with them via CLI. Do NOT use for Algolia search index
  operations (records, settings, synonyms, rules) — use algolia-cli instead.
  Do NOT use for building Agent Studio frontend/UI, or for general LLM/AI tasks
  unrelated to Algolia Agent Studio.
license: MIT
metadata:
  author: algolia
  version: "1.0"
---

# Algobot CLI

Manage and test [Algolia Agent Studio](https://www.algolia.com/products/ai/agent-studio/) agents from the terminal using `algobot`.

## Setup

```bash
npm install -g algobot-ai
algobot init                    # Interactive wizard (creates first agent + profile)
```

Or add a profile manually:
```bash
algobot profiles add --name prod --env prod
# Then enter App ID + Admin API Key when prompted
```

## When to Use Algobot vs Other Tools

| Need | Use |
|------|-----|
| Manage/test Agent Studio agents | **algobot-cli** (this skill) |
| Algolia search index ops (records, settings, synonyms) | **algolia-cli** |
| Search queries, analytics, recommendations | **algolia-mcp** |

## Non-Interactive Mode (Critical for Agents)

**The TUI won't render in non-TTY environments** (CI, scripts, agent subprocesses). Use these instead:

```bash
# One-shot query
algobot ask "What is your return policy?"

# Scripted multi-turn with ||| separator
algobot interactive --text "hello ||| list my orders ||| /context"

# Pipe-friendly JSON
algobot agents list --jq '.[] | .name'
```

`--jq` is a built-in flag — no need to install jq separately.

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
algobot agents export <agent-id>             # Export config to JSON
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
algobot profiles show prod                   # JSON output

# Per-command override
algobot --profile prod agents list
algobot --env dev agents list               # Uses default profile for that env
```

## Config-as-Code Workflow

Version-control agent definitions with mustache templates. Ideal for repeatable deployments (events, teams, multi-region).

```bash
# 1. Scaffold from an existing agent
algobot agents scaffold <agent-id>           # → agent-config.json + PROMPT.md

# 2. Preview resolved config (API-level kill switch — mutations blocked)
algobot --dry-run agents create --config agent-config.json --var event="Spring 2026"

# 3. Deploy
algobot agents create --config agent-config.json --var event_name="Spring 2026" --var event_id="spring-2026"

# 4. Update + publish in one step
algobot agents update <id> --config agent-config.json --var event_name="Summer 2026" --publish
```

`--dry-run` is enforced at the API layer, not just a flag check — safe to use in previews.

`{{key}}` placeholders resolve differently by field type:
- JSON config fields: JSON-safe escaping
- Instructions (`.md` files): raw substitution

## Live Development

```bash
algobot agents watch patch.json             # Auto-apply patches on file change (like hot reload)
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

- **TUI requires TTY.** `algobot` with no args launches the TUI — it hangs in scripts. Always use `ask` or `--text` in non-interactive contexts.
- **Exit codes are 0/1 only** in v2.0. Can't distinguish "not found" from "auth error" by exit code — parse stderr if needed.
- **`--output json` missing on most commands** in v2.0. Use `--jq` or rely on JSON-structured stdout where available.
- **`algobot init` is interactive.** Don't use in CI — use `profiles add` with flags instead.
- **Auth stored in `~/.algobot-cookie`** (AES-256-GCM). Run `algobot auth show` to inspect current credentials.
- **`--config` auto-discovers `agent-config.json`** in cwd. Explicit path: `--config path/to/config.json`.

## Reference Docs

- [Command Reference](references/commands.md) — Full flags for every command
- [Config-as-Code Guide](references/config-as-code.md) — Templates, variables, multi-env patterns
