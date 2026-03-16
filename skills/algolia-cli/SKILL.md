---
name: algolia-cli
description: Manage Algolia indices, records, settings, rules, and synonyms using the Algolia CLI. Triggers on CLI, command-line, algolia, indices, objects, settings, rules, synonyms, import, export.
license: MIT
metadata:
  author: algolia
  version: "1.0"
---

# Algolia CLI

Manage Algolia search infrastructure from the terminal using the `algolia` CLI.

## Setup

Run `/algolia-cli:setup` to install the CLI and configure a profile, or follow [Getting Started](references/getting-started.md).

## Command Quick Reference

### Profile

| Task                          | Command                                                                            |
|-------------------------------|------------------------------------------------------------------------------------|
| Add profile (non-interactive) | `algolia profile add --name "default" --app-id "<ID>" --api-key "<KEY>" --default` |
| List profiles                 | `algolia profile list`                                                             |

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

## Key Conventions

1. **Always use non-interactive mode.** Pass all required flags explicitly so the CLI never prompts for input. Use `-y` (or `--confirm`) to skip confirmation prompts.
2. **ndjson format.** `objects browse`, `objects import`, `rules browse/import`, and `synonyms browse/import` use newline-delimited JSON (one JSON object per line), **not** JSON arrays.
3. **Profile flag.** Use `-p <profile>` to target a non-default profile. Omit it to use the default.
4. **Wait flag.** Use `-w` (or `--wait`) when subsequent commands depend on the operation completing (e.g., import then search).
5. **Pipe between commands.** Copy data across indices: `algolia objects browse SRC | algolia objects import DST -F -`
6. **JSON output.** Use `--output json` (or `-o json`) when you need machine-readable output.

## Reference Docs

- [Getting Started](references/getting-started.md) — Installation and profile setup
- [Command Reference](references/commands.md) — Full syntax, flags, and examples for every command
