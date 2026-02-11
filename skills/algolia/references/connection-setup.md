# Connection Setup Reference

The Algolia MCP server is at `https://mcp.algolia.com/mcp` with OAuth authentication. It provides user-scoped, read-only access to all Algolia applications and indices the authenticated user can access.

## Prerequisites

- Algolia account
- Algolia MCP enabled in Dashboard (Generate AI → MCP Servers → Productivity)
- An MCP-compatible client

## Method 1: `/algolia:connect` command

Run `/algolia:connect` in a supported client. It detects the client, writes the configuration, starts the OAuth flow, and validates the connection.

## Method 2: Manual configuration

### Step 1: Enable Productivity MCP in Dashboard

Navigate to **Generate AI → MCP Servers → Productivity** and enable it.

Disabling the MCP server stops all connected workflows immediately.

### Step 2: Configure MCP client

Use the `mcp-remote` bridge (requires Node.js 18+ and `npx`).

After adding the configuration, restart the MCP client for changes to take effect.

**Node.js version note:** Some clients (Claude Desktop, Cursor) bundle their own Node.js runtime. If you encounter issues, ensure your system Node.js is v18+ or pin `mcp-remote@0.1.18`.

#### Claude Code CLI

```bash
claude mcp add-json algolia-mcp '{"type":"stdio","command":"npx","args":["mcp-remote","https://mcp.algolia.com/mcp","16453","--static-oauth-client-info","{\"client_id\":\"pnIP637iQf9_KY4Nm7rPo5hUH4Oe1njRThXGtz84h_o\"}"]}'
```

#### Codex CLI

```bash
codex mcp add algolia-mcp -- npx -y mcp-remote https://mcp.algolia.com/mcp 16453 --static-oauth-client-info "{\"client_id\":\"pnIP637iQf9_KY4Nm7rPo5hUH4Oe1njRThXGtz84h_o\"}"
```

#### VS Code

Edit `~/.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "algolia-mcp": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.algolia.com/mcp",
        "16453",
        "--static-oauth-client-info",
        "{\"client_id\":\"pnIP637iQf9_KY4Nm7rPo5hUH4Oe1njRThXGtz84h_o\"}"
      ]
    }
  }
}
```

#### Cursor

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "algolia-mcp": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.algolia.com/mcp",
        "16453",
        "--static-oauth-client-info",
        "{\"client_id\":\"pnIP637iQf9_KY4Nm7rPo5hUH4Oe1njRThXGtz84h_o\"}"
      ]
    }
  }
}
```

#### Claude Desktop

Edit `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "algolia-mcp": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.algolia.com/mcp",
        "16453",
        "--static-oauth-client-info",
        "{\"client_id\":\"pnIP637iQf9_KY4Nm7rPo5hUH4Oe1njRThXGtz84h_o\"}"
      ]
    }
  }
}
```

### Step 3: Authenticate

On first use, an OAuth flow opens in the browser. Sign in with your Algolia account and grant permissions. MCP inherits your existing Algolia permissions.

## OAuth client IDs

| Method              | Client ID                                     |
|---------------------|-----------------------------------------------|
| `mcp-remote` bridge | `pnIP637iQf9_KY4Nm7rPo5hUH4Oe1njRThXGtz84h_o` |

## Supported clients

| Client          | Method                               |
|-----------------|--------------------------------------|
| Claude Desktop  | `mcp-remote` (`command` + `args`)    |
| Claude Code CLI | `mcp-remote` (`claude mcp add-json`) |
| Codex CLI       | `mcp-remote` (`codex mcp add`)       |
| VS Code         | `mcp-remote` (`command` + `args`)    |
| Cursor          | `mcp-remote` (`command` + `args`)    |

## Security

- No credentials stored in config files (OAuth via `mcp-remote` bridge)
- Access inherits from Algolia account permissions
- Read-only access only
- HTTPS for all connections
- Revoke access through Algolia Dashboard

## Config file locations

- **Claude Desktop** (macOS/Linux): `~/.config/claude/claude_desktop_config.json`
- **Claude Desktop** (Windows): `%APPDATA%\Claude\claude_desktop_config.json`
- **Claude Code CLI**: Managed via `claude mcp add-json` (stored internally)
- **Codex CLI**: Managed via `codex mcp add` (stored internally)
- **VS Code**: `~/.vscode/mcp.json`
- **Cursor**: `~/.cursor/mcp.json`

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for detailed solutions.
