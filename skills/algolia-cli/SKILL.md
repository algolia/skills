---
name: algolia-cli
description: >-
  Use this skill whenever a user wants to execute operations against Algolia
  indices or accounts — deleting records, copying/migrating indices, backing up
  data, importing/exporting records, managing API keys, editing synonyms,
  configuring rules, changing settings like facets, clearing indices, or
  automating Algolia in CI/CD pipelines. The key signal is that the user wants
  to *act on* their Algolia data or configuration (server-side / backend /
  admin operations), regardless of whether they mention "CLI" or "command
  line." If someone names a specific Algolia index and wants to change, move,
  query, or manage it, use this skill. Do NOT use for frontend search UI work
  (InstantSearch, React components, autocomplete widgets), Algolia dashboard
  GUI questions, or evaluating Algolia vs. other providers.
license: MIT
metadata:
  author: algolia
  version: "1.0"
---

# Algolia CLI

Manage Algolia search infrastructure from the terminal using the `algolia` CLI.

## When to Use This Skill vs. algolia-mcp

| Need | Use |
|------|-----|
| Write/modify data (import, delete, update records) | **algolia-cli** (this skill) |
| Manage configuration (settings, rules, synonyms) | **algolia-cli** (this skill) |
| Auth (login, logout, signup via OAuth)                 | **algolia-cli** (this skill) |
| Admin operations (API keys, profiles, index copy/move) | **algolia-cli** (this skill) |
| Backup/restore indices | **algolia-cli** (this skill) |
| Search queries and view results | **algolia-mcp** |
| Analytics (top searches, click rates, no-results) | **algolia-mcp** |
| Recommendations (related products, trending) | **algolia-mcp** |

**Rule of thumb:** If the user wants to *read or analyze* data → algolia-mcp. If they want to *change, move, or manage* data → algolia-cli.

## Setup

Run `/algolia-cli:setup` to install the CLI and configure a profile, or follow [Getting Started](references/getting-started.md).

**Tip:** `algolia auth login` is the easiest way to set up credentials — it handles OAuth sign-in and profile creation in one step. Use `algolia profile add` for non-interactive / CI setups where you already have an API key.

## Command Quick Reference

### Auth

| Task                        | Command                                            |
|-----------------------------|----------------------------------------------------|
| Sign in (opens browser)     | `algolia auth login`                               |
| Sign in (select app by name)| `algolia auth login --app-name "My App" --default` |
| Sign in (no browser / SSH)  | `algolia auth login --no-browser`                  |
| Sign out                    | `algolia auth logout`                              |
| Create new account          | `algolia auth signup`                              |

### Profile

| Task                          | Command                                                                            |
|-------------------------------|------------------------------------------------------------------------------------|
| Add profile (non-interactive) | `algolia profile add --name "default" --app-id "<ID>" --api-key "<KEY>" --default` |
| List profiles                 | `algolia profile list`                                                             |
| Remove a profile              | `algolia profile remove "<name>" -y`                                               |
| Set default profile           | `algolia profile setdefault "<name>"`                                              |

### Application

| Task                              | Command                                                          |
|-----------------------------------|------------------------------------------------------------------|
| List applications                 | `algolia application list`                                       |
| Create application                | `algolia application create --name "My App" --region CA`         |
| Create (non-interactive, dry-run) | `algolia application create --name "My App" --region CA --dry-run` |
| Switch active application         | `algolia application select --app-name "My App"`                 |

### API Keys

| Task             | Command                                                                              |
|------------------|--------------------------------------------------------------------------------------|
| List API keys    | `algolia apikeys list`                                                               |
| Create API key   | `algolia apikeys create --acl search,browse --description "..." --indices "idx1,idx2"` |
| Get API key      | `algolia apikeys get <key>`                                                          |
| Delete API key   | `algolia apikeys delete <key> -y`                                                    |

### Search

| Task                | Command                                                              |
|---------------------|----------------------------------------------------------------------|
| Search an index     | `algolia search <index> --query "<query>"`                           |
| Search with filters | `algolia search <index> --query "<query>" --filters "<filter>"`      |
| Paginated search    | `algolia search <index> --query "<query>" --hitsPerPage 10 --page 2` |

### Indices

| Task                          | Command                                                |
|-------------------------------|--------------------------------------------------------|
| List all indices              | `algolia indices list`                                 |
| Delete an index               | `algolia indices delete <index> -y`                    |
| Clear records (keep settings) | `algolia indices clear <index> -y`                     |
| Copy index                    | `algolia indices copy <src> <dst> -y`                  |
| Copy only settings            | `algolia indices copy <src> <dst> --scope settings -y` |
| Move/rename index             | `algolia indices move <src> <dst> -y`                  |

### Objects (Records)

| Task                       | Command                                                             |
|----------------------------|---------------------------------------------------------------------|
| Browse all records         | `algolia objects browse <index>`                                    |
| Browse specific attributes | `algolia objects browse <index> --attributesToRetrieve title,price` |
| Import records from file   | `algolia objects import <index> -F data.ndjson`                     |
| Import from stdin          | `cat data.ndjson \| algolia objects import <index> -F -`            |
| Delete by IDs              | `algolia objects delete <index> --object-ids id1,id2 -y`            |
| Delete by filter           | `algolia objects delete <index> --filters "type:obsolete" -y`       |
| Partial update             | `algolia objects update <index> -F updates.ndjson`                  |

### Settings

| Task                           | Command                                                |
|--------------------------------|--------------------------------------------------------|
| Get settings                   | `algolia settings get <index>`                         |
| Set a setting                  | `algolia settings set <index> --typoTolerance="false"` |
| Import settings from file      | `algolia settings import <index> -F settings.json`     |
| Import and forward to replicas | `algolia settings import <index> -F settings.json -f`  |

### Rules

| Task               | Command                                              |
|--------------------|------------------------------------------------------|
| Browse all rules   | `algolia rules browse <index>`                       |
| Import rules       | `algolia rules import <index> -F rules.ndjson -y`    |
| Replace all rules  | `algolia rules import <index> -F rules.ndjson -c -y` |
| Delete rules by ID | `algolia rules delete <index> --rule-ids id1,id2 -y` |

### Synonyms

| Task                  | Command                                                        |
|-----------------------|----------------------------------------------------------------|
| Browse all synonyms   | `algolia synonyms browse <index>`                              |
| Import synonyms       | `algolia synonyms import <index> -F synonyms.ndjson`           |
| Replace all synonyms  | `algolia synonyms import <index> -F synonyms.ndjson -r`        |
| Delete synonyms by ID | `algolia synonyms delete <index> --synonym-ids id1,id2 -y`     |
| Save a single synonym | `algolia synonyms save <index> --id my-syn --synonyms foo,bar` |

### Crawler

| Task                          | Command                                                                 |
|-------------------------------|-------------------------------------------------------------------------|
| List crawlers                 | `algolia crawler list`                                                  |
| List by app                   | `algolia crawler list --app-id <app-id>`                                |
| Get crawler details           | `algolia crawler get <id>`                                              |
| Get config only               | `algolia crawler get <id> --config-only`                                |
| Create crawler                | `algolia crawler create <name> -F config.json`                          |
| Start/resume crawler          | `algolia crawler run <id>`                                              |
| Pause crawler(s)              | `algolia crawler pause <id> [<id2> ...]`                                |
| Reindex crawler(s)            | `algolia crawler reindex <id> [<id2> ...]`                              |
| Unblock crawler               | `algolia crawler unblock <id> -y`                                       |
| Crawl specific URLs           | `algolia crawler crawl <id> --urls url1,url2`                           |
| Test URL against crawler      | `algolia crawler test <id> --url <url>`                                 |
| Test with config override     | `algolia crawler test <id> --url <url> -F config.json`                  |
| Get crawl statistics          | `algolia crawler stats <id>`                                            |

Most crawler commands support `--dry-run` to preview the request without sending it: `create`, `run`, `pause`, `reindex`, `unblock`, `test`.

**Auth:** Crawler commands require `ALGOLIA_CRAWLER_USER_ID` and `ALGOLIA_CRAWLER_API_KEY` env vars, or `crawler_user_id`/`crawler_api_key` in the profile config file.

## Synonym Type Guide

Choosing the right synonym type matters for search quality:

- **`synonym` (regular/two-way):** All terms are interchangeable. Use when the words truly mean the same thing in both directions.
  Example: "sneakers" ↔ "trainers" — searching either should find the other.
- **`oneWaySynonym`:** Only the `input` term expands to include the `synonyms`, not the reverse. Use when a short/abbreviated term should match longer/specific terms, but not vice versa.
  Example: "TV" → "television", "flat screen" — searching "TV" finds "television" results, but searching "television" does NOT return "TV" results.

**Rule of thumb:** If the user says "searching X should *also match* Y", that's one-way (`input: X`, `synonyms: [Y]`). If they say "X and Y should be equivalent/interchangeable", that's two-way.

### Describe

| Task                       | Command                          |
|----------------------------|----------------------------------|
| Describe root command tree | `algolia describe`               |
| Describe a command         | `algolia describe search`        |
| Describe a subcommand      | `algolia describe objects browse` |

## Key Conventions

1. **Always use non-interactive mode.** Destructive commands need `-y` (or `--confirm`) to skip confirmation prompts. This includes `objects delete`, `indices delete/clear/copy/move`, `rules import/delete`, `synonyms delete`, and `apikeys delete`. Without `-y`, the CLI will hang waiting for user input. Note: `objects import`, `objects update`, and `synonyms import` do **not** have a `-y` flag — they run non-interactively by default.
2. **ndjson format.** `objects browse`, `objects import`, `rules browse/import`, and `synonyms browse/import` use newline-delimited JSON (one JSON object per line), **not** JSON arrays.
3. **Profile flag.** Use `-p <profile>` to target a non-default profile. Omit it to use the default.
4. **Credential precedence.** Environment variables override all other configuration. The resolution order is: **env vars** > **CLI flags** (`--application-id`, `--api-key`) > **profile config file** > **default profile**. Supported env vars: `ALGOLIA_APPLICATION_ID`, `ALGOLIA_API_KEY`, `ALGOLIA_ADMIN_API_KEY`, `ALGOLIA_SEARCH_HOSTS`, `ALGOLIA_CRAWLER_USER_ID`, `ALGOLIA_CRAWLER_API_KEY`. If env vars are set, `--profile`/`-p` is ignored for those credentials.
5. **Wait flag.** Use `-w` (or `--wait`) when subsequent commands depend on the operation completing (e.g., import then search).
6. **Pipe between commands.** Copy data across indices: `algolia objects browse SRC | algolia objects import DST -F -`
7. **JSON output.** Use `--output json` (or `-o json`) when you need machine-readable output.

## Common Workflows

### Migrate records between indices (with field filtering)
```bash
algolia objects browse SOURCE --attributesToRetrieve objectID,title,price \
  | algolia objects import DEST -F - -w
```

### Full index backup
```bash
algolia objects browse MY_INDEX > my_index_records.ndjson
algolia settings get MY_INDEX > my_index_settings.json
algolia rules browse MY_INDEX > my_index_rules.ndjson
algolia synonyms browse MY_INDEX > my_index_synonyms.ndjson
```
Note: settings use `.json` (standard JSON), everything else uses `.ndjson` (newline-delimited JSON).

### Restore from backup
```bash
algolia objects import MY_INDEX -F my_index_records.ndjson -w
algolia settings import MY_INDEX -F my_index_settings.json -w
algolia rules import MY_INDEX -F my_index_rules.ndjson -c -y -w
algolia synonyms import MY_INDEX -F my_index_synonyms.ndjson -r -w
```

## Direct Invocation

If the skill doesn't trigger automatically, users can invoke it directly:

- **`/algolia-cli`** — Load the full skill into context for any Algolia CLI task
- **`/algolia-cli:setup`** — Install the CLI and configure a profile

This is useful when the request is brief (e.g., "import my data into Algolia") and the skill might not auto-trigger.

## Reference Docs

- [Getting Started](references/getting-started.md) — Installation and profile setup
- [Command Reference](references/commands.md) — Full syntax, flags, and examples for every command
