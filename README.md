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
