# Connection Setup Reference

The Algolia MCP server is at `https://mcp.algolia.com/mcp` with OAuth authentication. It provides user-scoped, read-only access to all Algolia applications and indices the authenticated user can access.

## Prerequisites

- Algolia account
- Algolia MCP enabled in Dashboard (Generate AI → MCP Servers → Productivity)
- An MCP-compatible client

## Method 1: `/algolia-mcp:mcp-connect` command

Run `/algolia-mcp:mcp-connect` in a supported client. It detects the client, writes the configuration, starts the OAuth flow, and validates the connection.

## Method 2: Manual configuration

### Step 1: Enable Productivity MCP in Dashboard

Navigate to **Generate AI → MCP Servers → Productivity** and enable it.

Disabling the MCP server stops all connected workflows immediately.

### Step 2: Configure MCP client

Use the remote HTTP server URL directly:

```text
https://mcp.algolia.com/mcp
```

After adding the configuration, restart the MCP client for changes to take effect.

Use OAuth discovery for authentication. If your client shows OAuth client ID
or client secret fields, leave them empty.

#### Claude Code CLI

```bash
claude mcp add --transport http algolia https://mcp.algolia.com/mcp
```

Run `/mcp` in Claude Code and follow the browser login flow.

#### Codex CLI

```bash
codex mcp add algolia --url https://mcp.algolia.com/mcp
codex mcp login algolia
```

Equivalent `~/.codex/config.toml` entry:

```toml
[mcp_servers.algolia]
url = "https://mcp.algolia.com/mcp"
```

#### VS Code

Edit `~/.vscode/mcp.json`:

```json
{
  "servers": {
    "algolia": {
      "type": "http",
      "url": "https://mcp.algolia.com/mcp"
    }
  }
}
```

#### Cursor

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "algolia": {
      "url": "https://mcp.algolia.com/mcp"
    }
  }
}
```

#### Gemini CLI

Run the following command:

```bash
gemini mcp add algolia https://mcp.algolia.com/mcp -s user -t http
```

Or edit `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "algolia": {
      "httpUrl": "https://mcp.algolia.com/mcp"
    }
  }
}
```

Sign in when prompted.

### Step 3: Authenticate

On first use, an OAuth flow opens in the browser. Sign in with your Algolia account and grant permissions. MCP inherits your existing Algolia permissions.

## Supported clients

| Client          | Method                                   |
|-----------------|------------------------------------------|
| Claude Code CLI | HTTP (`claude mcp add --transport http`) |
| Codex CLI       | HTTP (`codex mcp add --url`)             |
| VS Code         | HTTP (`type` + `url`)                    |
| Cursor          | HTTP (`url`)                             |
| Gemini CLI      | HTTP (`gemini mcp add`)                  |

## Security

- Config files store the server URL; the MCP client manages OAuth tokens
- Access inherits from Algolia account permissions
- Read-only access only
- HTTPS for all connections
- Revoke access through Algolia Dashboard

## Config file locations

- **Claude Code CLI**: Managed via `claude mcp add` (stored internally)
- **Codex CLI**: Managed via `codex mcp add` (stored internally)
- **VS Code**: `~/.vscode/mcp.json`
- **Cursor**: `~/.cursor/mcp.json`
- **Gemini CLI**: `~/.gemini/settings.json`

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for detailed solutions.
