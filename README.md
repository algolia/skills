# Algolia Skills

[Agent skills](https://agentskills.io/) for managing Algolia search, analytics, recommendations, and index configuration.

## ✨ Skills

Pick the skill that fits your workflow.

| Skill                       | Description                                                       |
|-----------------------------|-------------------------------------------------------------------|
| [algolia-mcp](#algolia-mcp) | Search, analytics, and recommendations via the Algolia MCP server |
| [algolia-cli](#algolia-cli) | Manage indices, settings, rules, and synonyms via the Algolia CLI |

### algolia-mcp

Search your Algolia indices with natural language, explore search analytics, and get product recommendations (bought-together, related, trending, similar) — all through the Algolia MCP server.

#### Commands

| Command                 | Description                                        | Docs                                |
|-------------------------|----------------------------------------------------|-------------------------------------|
| `/algolia-mcp:connect`  | Set up or update your Algolia MCP connection       | [connect.md](commands/connect.md)   |
| `/algolia-mcp:examples` | Interactive usage examples with copy-paste prompts | [examples.md](commands/examples.md) |

`/algolia-mcp:examples` accepts an optional category: `search`, `analytics`, or `recommendations`.

#### Prerequisites

- [Algolia account](https://www.algolia.com/users/sign_up) with at least one index containing data
- Algolia MCP enabled in Dashboard (Generate AI > MCP Servers > Productivity)
- MCP client — Claude Code, Codex, VS Code, Cursor, etc.
- Node.js 18+ (required for `mcp-remote` bridge on non-Claude Code clients)

### algolia-cli

Manage Algolia indices, records, settings, rules, and synonyms from the terminal using the [Algolia CLI](https://www.algolia.com/doc/tools/cli/get-started).

#### Commands

| Command              | Description                                     | Docs                          |
|----------------------|-------------------------------------------------|-------------------------------|
| `/algolia-cli:setup` | Install the Algolia CLI and configure a profile | [setup.md](commands/setup.md) |

#### Prerequisites

- [Algolia account](https://www.algolia.com/users/sign_up) with Application ID and Admin API key ([Dashboard > Settings > API Keys](https://dashboard.algolia.com/account/api-keys/all))
- Homebrew (macOS) or a compatible package manager

## 🛠️ Installation

### From Marketplace (recommended)

```bash
/plugin marketplace add algolia/skills
/plugin install algolia-mcp   # or algolia-cli
```

Or install directly:

```bash
/plugin install algolia-mcp@algolia-skills   # or algolia-cli@algolia-skills
```

### Via npx

```bash
npx skills add https://github.com/algolia/skills
```

### Clone / Copy

Clone the repo and copy the skill folder to your agent's skills directory:

```bash
git clone https://github.com/algolia/skills.git
cp -r skills/algolia-mcp <skills-directory>   # or algolia-cli
```

| Agent        | Skills directory             |
|--------------|------------------------------|
| Claude Code  | `~/.claude/skills/`          |
| Cursor       | `~/.cursor/skills/`          |
| OpenAI Codex | `~/.codex/skills/`           |
| OpenCode     | `~/.config/opencode/skills/` |

Restart your agent to load the skill.

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
