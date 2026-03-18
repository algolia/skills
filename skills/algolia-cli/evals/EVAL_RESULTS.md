# Algolia CLI Skill — Evaluation Results

Evaluation performed on 2026-03-18 using Claude Opus 4.6 (1M context).

## Summary

The skill was evaluated across 3 realistic user scenarios, comparing **with-skill** (Claude reads the skill before responding) vs **without-skill** (Claude relies on general knowledge).

| Metric | Without Skill | With Skill (v1) | With Skill (v2) |
|--------|:------------:|:---------------:|:---------------:|
| **Eval 1** — Migrate records | 20% (1/5) | 80% (4/5) | **100% (5/5)** |
| **Eval 2** — Synonyms & rules | 50% (3/6) | 67% (4/6) | **100% (6/6)** |
| **Eval 3** — Backup & API key | 50% (3/6) | 100% (6/6) | **100% (6/6)** |
| **Average pass rate** | **40%** | **82%** | **100%** |

**v1** = original skill, **v2** = improved skill (current version).

## Eval Details

### Eval 1: Migrate Records Between Indices

**Prompt:** *"I need to export all records from my 'products' index and import them into a new 'products_v2' index, but only keep the title, price, and category fields. After copying, update the search settings to make 'category' a facet."*

| Assertion | Without Skill | With Skill v1 | With Skill v2 |
|-----------|:---:|:---:|:---:|
| Uses `--attributesToRetrieve` for field selection | FAIL | PASS | PASS |
| Pipes browse to import with `-F -` | FAIL | PASS | PASS |
| Uses `--attributesForFaceting` for category facet | PASS | PASS | PASS |
| Includes `-y` flag on write commands | FAIL | FAIL | PASS |
| Uses `-w` flag to sequence import before settings | FAIL | PASS | PASS |

**Key finding:** Without the skill, Claude exported all fields and filtered with `jq` instead of using `--attributesToRetrieve`. It also used intermediate files instead of piping. The v1→v2 improvement fixed the missing `-y` flag by adding it to the quick reference tables.

### Eval 2: Synonyms and Rules

**Prompt:** *"Set up synonyms for my 'ecommerce' index — 'sneakers' and 'trainers' should be equivalent, and searching 'TV' should also match 'television' and 'flat screen'. Also add a rule that boosts products with 'featured:true' to the top."*

| Assertion | Without Skill | With Skill v1 | With Skill v2 |
|-----------|:---:|:---:|:---:|
| Creates two-way synonym for sneakers/trainers | PASS | PASS | PASS |
| Creates one-way synonym from TV → television, flat screen | PASS | FAIL | PASS |
| Uses correct synonym types (`synonym` vs `oneWaySynonym`) | PASS | FAIL | PASS |
| Creates ndjson file for boost rule | FAIL | PASS | PASS |
| Uses `synonyms save` or `synonyms import` with ndjson | FAIL | PASS | PASS |
| Uses `rules import` with `-F` and `-y` | FAIL | PASS | PASS |

**Key finding:** The baseline actually got synonym directionality right but invented non-existent CLI commands (`algolia rules save --rule`). The v1 skill got commands right but missed the one-way synonym. The v2 Synonym Type Guide with the "rule of thumb" fixed this.

### Eval 3: Full Backup and API Key

**Prompt:** *"I want to back up my entire 'blog_posts' index — all records, settings, rules, and synonyms — to local files. Then I want to create an API key that only allows search access to that specific index."*

| Assertion | Without Skill | With Skill v1 | With Skill v2 |
|-----------|:---:|:---:|:---:|
| Exports records to `.ndjson` file | FAIL | PASS | PASS |
| Exports settings to `.json` file | PASS | PASS | PASS |
| Exports rules to `.ndjson` file | FAIL | PASS | PASS |
| Exports synonyms to `.ndjson` file | FAIL | PASS | PASS |
| Creates API key with `--acl search --indices blog_posts` | PASS | PASS | PASS |
| Settings use `.json` (not `.ndjson`) | PASS | PASS | PASS |

**Key finding:** Without the skill, Claude used `.json` for all exports. The skill's ndjson format documentation ensures correct file extensions — `.ndjson` for records/rules/synonyms, `.json` for settings.

## What the Skill Adds

The biggest areas where the skill outperforms general knowledge:

1. **ndjson format awareness** — Knowing which commands use newline-delimited JSON vs standard JSON
2. **Non-interactive flags** — Consistently using `-y` to prevent CLI hangs
3. **Piping patterns** — Using `-F -` for stdin instead of intermediate files
4. **Synonym type selection** — Choosing `oneWaySynonym` vs `synonym` based on user intent
5. **Correct CLI commands** — Preventing hallucinated commands like `algolia rules save --rule`
6. **Wait flag sequencing** — Using `-w` when operations must complete before the next step

## Trigger Accuracy

Description optimization was performed with 20 eval queries (11 should-trigger, 9 should-not-trigger).

| Metric | Value |
|--------|-------|
| Precision | 100% (never triggers falsely) |
| Recall | ~25% (undertriggers on valid queries) |
| Overall accuracy | 57% |

Low recall is a systemic limitation — Claude is confident enough in its Algolia knowledge to attempt tasks directly. Users can invoke `/algolia-cli` explicitly for reliable access.

## Improvements Made (v1 → v2)

1. **Added `-y` flag** to all write commands in quick reference tables
2. **New Synonym Type Guide** with decision rules for `synonym` vs `oneWaySynonym`
3. **Expanded non-interactive convention** listing every command that needs `-y`
4. **New Common Workflows section** (migrate, backup, restore patterns)
5. **Skill differentiation table** (algolia-cli vs algolia-mcp)
6. **Direct invocation guidance** (`/algolia-cli` fallback)
7. **Optimized description** for better triggering accuracy

## Reproducibility

- Model: Claude Opus 4.6 (1M context)
- Eval definitions: `evals/evals.json`
- Date: 2026-03-18
- Each eval was run once per configuration per iteration
