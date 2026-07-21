# Config-as-Code Guide

Version-control agent definitions as files. Deploy repeatable agents across environments, events, or teams.

## File Structure

```
my-agent/
├── agent-config.json    # Agent definition (model, tools, settings)
└── PROMPT.md            # Agent instructions (referenced from config)
```

## Scaffolding

Generate from an existing agent:

```bash
algobot agents scaffold <agent-id>
```

Produces `agent-config.json` with the agent's current config, and `PROMPT.md` if instructions exist.

## agent-config.json Format

```json
{
  "name": "{{event_name}} Support Bot",
  "model": "gpt-4o",
  "instructions": "PROMPT.md",
  "tools": [
    {
      "type": "algolia_search_index",
      "name": "search_products",
      "indices": [
        {
          "index": "{{index_name}}",
          "description": "Product catalog. Search by title, brand, or category."
        }
      ]
    }
  ]
}
```

- `"instructions": "PROMPT.md"` — loads instructions from the referenced `.md` file.
- `{{key}}` — mustache placeholder, resolved via `--var key=value`.
- JSON config fields: JSON-safe escaping. Instructions (`.md`): raw substitution.

> Top-level `indexName` is silently stripped — index names belong in `tools[].indices[].index`.

### Search tool: static vs dynamic indices

The `algolia_search_index` tool has a `mode` field for dynamic-index support. `static` is the default, so existing agents are unaffected.

```json
{
  "type": "algolia_search_index",
  "name": "search_products",
  "mode": "dynamic",
  "allowUnlistedIndices": false,
  "indices": [
    {
      "index": "{{index_name}}",
      "description": "Product catalog. Search by title, brand, or category.",
      "enhancedDescription": "Extra attribute and facet hints for the model.",
      "searchParameters": { "optionalFilters": ["brand:Acme"] }
    }
  ]
}
```

- `mode` (default `"static"`):
  - `static` — `indices` is the only set the tool searches. A per-request `algolia.indices` override returns HTTP 422.
  - `dynamic` — a completion request can pass `algolia.indices` (up to 10) to replace the list for that request; without it, `indices` is used. Per-request names must be a subset of `indices` by default; net-new names return 422 (`index_not_listed_on_tool`).
- `allowUnlistedIndices` (default `false`, dynamic only) — set `true` to accept any index the agent's API key can reach, not only those listed. It errors at save time under `mode: "static"`.
- Per index, besides `index` and `description`: `enhancedDescription`, `searchParameters` (default Algolia search parameters), and `searchControls` (used when Algolia MCP is enabled).

## Template Variables

```bash
# Single variable
algobot agents create --config agent-config.json --var event_name="Spring 2026"

# Multiple variables
algobot agents create --config agent-config.json \
  --var event_name="Spring 2026" \
  --var event_id="spring-2026" \
  --var index_name="products_spring"

# CLI flags override config file
algobot agents create --config agent-config.json --name "Override Name" --var event="Spring"
```

## Dry Run

Preview resolved config before deploying — mutations blocked at API layer:

```bash
algobot --dry-run agents create --config agent-config.json --var event="Spring"
# Shows resolved config, makes no network mutations
```

## Multi-Environment Workflow

```bash
# Deploy to dev first
algobot --profile dev agents create --config agent-config.json --var env=dev

# Promote to staging
algobot --profile staging agents create --config agent-config.json --var env=staging

# Copy an agent between environments directly
algobot agents copy <agent-id> --from-env dev --to-env prod

# Update + publish in one step
algobot --profile prod agents update <id> --config agent-config.json --var env=prod --publish
```

## Live Reload (Development)

Watch a patch file and auto-apply on save:

```bash
algobot agents watch patch.json
```

Patch file is a JSON object with the fields to update. Useful for rapid iteration on model, instructions, tools.

## CI/CD Pattern

```bash
# In CI (non-interactive):
algobot profiles add --name ci --env prod    # One-time setup (use env vars for creds)
algobot --profile ci --dry-run agents create --config agent-config.json --var release=v2
algobot --profile ci agents create --config agent-config.json --var release=v2 --publish
```

Credentials via environment (CI-safe, no interactive prompts):
```bash
ALGOBOT_APP_ID=XXX ALGOBOT_API_KEY=YYY algobot agents list
```
