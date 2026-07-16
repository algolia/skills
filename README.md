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
| `algolia-quickstart` | Create an Algolia account and provision an application (App ID / API key) via the CLI |

---

## 🚀 Installation

#### Marketplace (recommended)

```bash
/plugin marketplace add algolia/skills
/plugin install <skill>   # e.g. algolia-mcp, algolia-cli, algobot-cli, instantsearch, algolia-crawler, algolia-quickstart
```

Or install directly:

```bash
/plugin install <skill>@algolia-skills   # e.g. algolia-mcp, algolia-cli, algobot-cli, instantsearch, algolia-crawler, algolia-quickstart
```

#### npx

```bash
npx skills add https://github.com/algolia/skills
```

#### Clone / Copy

```bash
git clone https://github.com/algolia/skills.git
cp -r skills/<skill> <skills-directory>   # e.g. algolia-mcp, algolia-cli, algobot-cli, instantsearch, algolia-crawler, algolia-quickstart
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
