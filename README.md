# Algolia Agent Skill

An [Agent Skill](https://agentskills.io/) that connects to Algolia for natural language search, analytics, and recommendations.

### ✨ Features

- 🔍 **Natural Language Search** - Search your Algolia indices conversationally
- 📊 **Analytics Insights** - Get search analytics through simple questions
- 🎯 **Smart Recommendations** - Product recommendations (bought-together, related, trending, similar)
- 🚀 **Easy Setup** - Connect in minutes with `/algolia-mcp:connect` in Claude Code
- 📚 **Usage Examples** - Run `/algolia-mcp:examples` for copy-paste prompts

### 🛠️ Usage

The skill gives you `/algolia-mcp:connect` and `/algolia-mcp:examples` slash commands, plus guided setup and interactive examples.

#### Installation

##### Option 1: From Marketplace (Recommended)

**Two steps:**

1. Add the Algolia marketplace:
   ```bash
   /plugin marketplace add algolia/skills
   ```

2. Install the plugin:
   ```bash
   /plugin install algolia-mcp
   ```

**Or direct install (one step):**

```bash
/plugin install algolia-mcp@algolia-skills
```

##### Option 2: Via npx

```bash
npx skills add https://github.com/algolia/skills
```

##### Option 3: Manual

1. Clone this repository:
   ```bash
   git clone https://github.com/algolia/skills.git
   cd skills
   ```

2. Copy the skill to your Claude skills directory:
   ```bash
   mkdir -p ~/.claude/skills
   cp -r skills/algolia-mcp ~/.claude/skills/
   ```

3. Restart Claude Code to load the skill.

#### Verify Installation

```
What skills are available?
```

You should see `algolia-mcp` in the list.

#### Getting Started

Once installed, set up your Algolia MCP connection:

- **If your client supports commands**, run `/algolia-mcp:connect` — it will guide you through the entire setup.
- **Otherwise**, ask the agent to set up Algolia MCP (e.g. *"Set up Algolia MCP"*) and it will follow the skill's instructions.

Then try:

```
"Search my products index for laptop under $1000"
"What were the top searches yesterday?"
"Show me trending products in electronics"
```

#### Commands

##### `/algolia-mcp:connect`

Set up or update your Algolia MCP connection.

```
/algolia-mcp:connect
```

[Full command documentation](commands/connect.md)

##### `/algolia-mcp:examples`

Interactive usage examples with copy-paste prompts.

```
/algolia-mcp:examples                  # All examples
/algolia-mcp:examples search           # Search patterns
/algolia-mcp:examples analytics        # Analytics patterns
/algolia-mcp:examples recommendations  # Recommendations patterns
```

[Full command documentation](commands/examples.md)

### 📋 Prerequisites

- **Algolia account** - [Sign up free](https://www.algolia.com/users/sign_up)
- **At least one index** with data in your Algolia application
- **Algolia MCP enabled** in Dashboard (Generate AI → MCP Servers → Productivity)
- **MCP client** - Claude Code (for the full skill experience), or Codex, VS Code, Cursor, etc.
- **Node.js 18+** - Required for the `mcp-remote` bridge used by non-Claude Code clients

---

## Algolia CLI Skill

Manage Algolia indices, records, settings, rules, and synonyms directly from the terminal using the [Algolia CLI](https://www.algolia.com/doc/tools/cli/get-started).

#### Installation

```bash
/plugin install algolia-cli@algolia-skills
```

#### Getting Started

Run `/algolia-cli:setup` to install the CLI and configure your credentials — or ask the agent to set up the Algolia CLI.

Then try:

```
"List all my Algolia indices"
"Export all records from the products index"
"Copy settings from staging to production index"
```

#### Commands

##### `/algolia-cli:setup`

Install the Algolia CLI and configure a profile.

```
/algolia-cli:setup
```

[Full command documentation](commands/setup.md)

#### Prerequisites

- **Algolia account** — [Sign up free](https://www.algolia.com/users/sign_up)
- **Application ID and Admin API key** — Found in [Dashboard → Settings → API Keys](https://dashboard.algolia.com/account/api-keys/all)
- **Homebrew** (macOS) or package manager for installation

---

### 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
