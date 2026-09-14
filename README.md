<div align="center">

# Algolia Skills

**[Agent skills](https://agentskills.io/) for managing Algolia search, analytics, recommendations, and index configuration.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## ✨ Skills

| Skill           | Description                                                                        |
| --------------- | ---------------------------------------------------------------------------------- |
| `algolia-mcp`   | Search, analytics, and recommendations via the Algolia MCP server                  |
| `algolia-cli`   | Manage indices, settings, rules, and synonyms via the Algolia CLI                  |
| `algobot-cli`   | AI agents, Agent Studio, RAG, and conversational experiences built on Algolia      |
| `instantsearch` | Build search UIs (autocomplete, search results, faceted search) with InstantSearch |
| `algolia-crawler` | Crawl web pages or whole sites into a RAG-optimized index with the Algolia Crawler |
| `algolia-migration` | Migrate API client code to the latest major version (JS, Python, Go, PHP, Java, C#, Ruby, Kotlin, Scala, Swift) |
| `algolia-quickstart` | Create an Algolia account and provision an application (App ID / API key) via the CLI |

### Implementation planning suite (`algolia-implementation`)

A companion bundle that plans, sequences, and validates Algolia implementations end to end. It routes live operations to `algolia-cli` / `algolia-mcp` / `algobot-cli` and code-level UI work to `instantsearch`. Install as a bundle — `algolia-discovery-planning` is the entry point and loads the companion skills per phase.

| Skill                          | Description                                                                    |
| ------------------------------ | ------------------------------------------------------------------------------ |
| `algolia-discovery-planning`   | Entry point: maps any request to lifecycle phases and loads companion skills   |
| `algolia-search-implementation`| Execution checklist and readiness signposts for net-new builds                 |
| `algolia-data-modeling`        | Record shape, variants, objectID, facets, and event-attribution readiness      |
| `algolia-index-configuration`  | Relevance settings, ranking, synonyms, rules, replicas, rollback planning      |
| `algolia-ui-libraries`         | Living selector for current Algolia UI libraries and docs paths                |
| `algolia-instantsearch-ui`     | Customer-readiness layer for InstantSearch results/browse experiences          |
| `algolia-autocomplete`         | Source strategy, selection contracts, and QA for autocomplete/suggestions      |
| `algolia-events-insights`      | Click/conversion/view event taxonomy, queryID and userToken guidance           |
| `algolia-neuralsearch`         | NeuralSearch readiness, rollout planning, evaluation, and measurement          |
| `algolia-agent-studio`         | Agent Studio planning, readiness gates, guardrails, and launch validation      |
| `algolia-release-qa`           | Launch QA with severity-led findings, event checks, and residual risk          |

---

## 🚀 Installation

#### Marketplace (recommended)

```bash
/plugin marketplace add algolia/skills
/plugin install <skill>   # e.g. algolia-mcp, algolia-cli, algobot-cli, instantsearch, algolia-crawler, algolia-migration, algolia-quickstart
```

Or install directly:

```bash
/plugin install <skill>@algolia-skills   # e.g. algolia-mcp, algolia-cli, algobot-cli, instantsearch, algolia-crawler, algolia-migration, algolia-quickstart
```

#### npx

```bash
npx skills add https://github.com/algolia/skills
```

#### Clone / Copy

```bash
git clone https://github.com/algolia/skills.git
cp -r skills/<skill> <skills-directory>   # e.g. algolia-mcp, algolia-cli, algobot-cli, instantsearch, algolia-crawler, algolia-migration, algolia-quickstart
```

<details>
<summary>Skills directories by agent</summary>

| Agent        | Directory                    |
| ------------ | ---------------------------- |
| Claude Code  | `~/.claude/skills/`          |
| Cursor       | `~/.cursor/skills/`          |
| OpenAI Codex | `~/.codex/skills/`           |
| OpenCode     | `~/.config/opencode/skills/` |

</details>

Restart your agent to load the skill.

## 🎯 Make sure your agent actually uses them

Installed skills only help when the agent reads them. In our benchmarking, an agent with all
skills installed but left to route freely invoked **1 of 18** skills on an audit-style task and
performed identically to having none — while one trigger line in the prompt doubled its
live-verified fix rate. On a smaller model the effect was starker: left to route freely it
invoked **no skill at all**; with the trigger line it loaded seven. Two ways to make invocation
reliable:

**Add one line to your agent's project config** (`CLAUDE.md`, `AGENTS.md`, or equivalent):

```markdown
For any Algolia work, invoke the `algolia-discovery-planning` skill first.
When auditing or reviewing an existing Algolia implementation, invoke `algolia-audit` first.
```

**Or invoke explicitly per task** — Claude Code: ask it to "use the algolia-discovery-planning
skill"; Codex/ChatGPT: `$algolia-discovery-planning` (or `$algolia-audit` for reviews).

`algolia-discovery-planning` (builds) and `algolia-audit` (existing implementations) are the two
entry points; each loads the companion skills the task needs.

## 🧭 Which model to run them on

The skills are instructions; how much they help depends on whether the model can carry them
out. We ran the same tasks (a one-line "add search to our store" brief and an audit of a
deliberately broken store) on four models, with and without the skills, blind-graded against
the live index. Directional — one or two pairs per model outside the mid-tier — but consistent:

| Model tier | What we saw | Guidance |
| --- | --- | --- |
| **Mid-tier** (Claude Sonnet 5, GPT-5.6 on Codex) | Skills won 7 of 9 pairs (one tie, one loss). Analytics wired 3 of 3 times vs 1 of 3 without; nearly double the live-verified defect fixes on an existing store; a working storefront in every round on this tier. Sonnet routes to the entry skills unprompted after the trigger-language fixes. | **Recommended.** This is the tier the skills were tuned on. |
| **Top tier** (Claude Opus 5) | Without skills it already scored 10/10 on live checks and wired verified events. With skills it built more (suggestions index, synonyms, rules) at +65% time and shipped one shopper-facing regression its own QA missed (autocomplete-only input; Enter did nothing). | Skills add scope discipline, not knowledge. Keep them for the QA gates and the event taxonomy; expect little quality lift. |
| **Small / fast tier** (Claude Haiku 4.5) | Runs in 4–8 minutes on a third of the tokens, and the skills' *content* works when it is read (a mandated audit repaired 5 of 10 live-checked settings defects through the CLI). But it verifies by re-reading its edits rather than loading the page: three skills builds shipped a dead Insights loader or broken product cards, and each QA report said "verified." | Only with the trigger line **and** the mechanical page-smoke gate in `algolia-release-qa` (`scripts/page-smoke.mjs`). Do not accept "launch-ready" from this tier without the gate's output. |

Whatever the model: put the trigger line above in your agent config, and treat any "verified"
claim that isn't backed by a browser session or the smoke gate's output as untested.
