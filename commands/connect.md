# Algolia MCP Connection Setup

This command guides you through connecting your MCP client to the Algolia MCP server.

## What This Command Does

1. **Detects your MCP client** - Finds Claude Desktop, Claude Code, Codex, VS Code, Cursor, or other client
2. **Writes configuration** - Automatically updates your config file or runs the appropriate CLI command
3. **Starts OAuth flow** - Authenticates with your Algolia account
4. **Validates connection** - Tests that everything works

## Prerequisites

Before running this command, ensure you have:

- Algolia account ([sign up free](https://www.algolia.com/users/sign_up))
- Algolia MCP enabled in Dashboard (Generate AI → MCP Servers → Productivity)
- MCP client installed (Claude Desktop, Claude Code, Codex, VS Code, Cursor, etc.)
- For CLI/IDE clients: Node.js 18+ installed (required for `mcp-remote` bridge)

## Usage

```
/algolia-mcp:connect
```

## Step-by-Step Process

### Step 1: Enable Productivity MCP in Algolia Dashboard

1. Go to **Generate AI** → **MCP Servers** → **Productivity**
2. Click **Enable**

OAuth-based authentication — no embedded credentials. Disabling the MCP server stops all connected workflows immediately.

### Step 2: Detect MCP Client

The command detects your MCP client by checking:

1. **Claude Desktop**
   - macOS: `~/.config/claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/claude/claude_desktop_config.json`

2. **Claude Code CLI**
   - Detected via `claude` command in PATH
   - Configured via `claude mcp add-json`

3. **Codex CLI**
   - Detected via `codex` command in PATH
   - Configured via `codex mcp add`

4. **VS Code**
   - Config: `~/.vscode/mcp.json`

5. **Cursor**
   - Config: `~/.cursor/mcp.json`

If multiple clients are detected, you'll be asked which one to configure.

### Step 3: Write Configuration

Apply the configuration from [connection-setup.md](../skills/algolia-mcp/references/connection-setup.md#method-2-manual-configuration) for the detected client.

The command will:
- Read your existing config (if it exists)
- Merge the Algolia server configuration
- Preserve other servers you've configured
- Write the updated config back
- Create a backup (`.bak` file)

### Step 4: Restart MCP Client

**Important:** You must restart your MCP client for changes to take effect.

**Claude Desktop:**
1. Quit Claude Desktop (Cmd/Ctrl + Q)
2. Wait 5 seconds
3. Reopen Claude Desktop

**VS Code / Cursor:**
1. Open Command Palette (Cmd/Ctrl + Shift + P)
2. Type "Reload Window"
3. Press Enter

**Claude Code / Codex:**
- Close and reopen your terminal session

### Step 5: Authenticate

When you first use the MCP client:

1. **OAuth flow starts** - Browser opens automatically
2. **Sign in** - Log in with your Algolia account
3. **Grant permissions** - Approve access to your resources
4. **Access granted** - MCP inherits your dashboard permissions

### Step 6: Verify Connection

After restarting, the command will test the connection:

```
Test 1: List available tools ✓
Test 2: List accessible indices ✓
Test 3: Perform test search ✓
```

## Troubleshooting

### "Algolia API request failed"

**Cause:** Network issue or server problem

**Solutions:**
1. Check network connectivity: `curl https://mcp.algolia.com`
2. Verify Algolia MCP is enabled in Dashboard
3. Re-run OAuth flow if authentication expired

### "Can't find MCP client config file"

**Cause:** MCP client not installed or non-standard location

**Solutions:**
1. Verify MCP client is installed
2. Manually create config directory:
   ```bash
   mkdir -p ~/.config/claude
   ```
3. Provide custom config file path when prompted

### "Config file is not valid JSON"

**Cause:** Corrupted or malformed config file

**Solutions:**
1. Validate JSON syntax:
   ```bash
   cat ~/.config/claude/claude_desktop_config.json | jq .
   ```
2. Fix syntax errors (missing commas, brackets, quotes)
3. Or restore backup:
   ```bash
   cp ~/.config/claude/claude_desktop_config.json.bak \
      ~/.config/claude/claude_desktop_config.json
   ```

### "Connection test failed after restart"

**Cause:** Config not applied or server issue

**Solutions:**
1. Verify MCP client fully restarted (not just minimized)
2. Check config file was actually written
3. Check Algolia status: https://status.algolia.com
