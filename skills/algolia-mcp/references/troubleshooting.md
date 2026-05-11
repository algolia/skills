# Troubleshooting Reference

## Connection errors

### "Server not responding" / connection timeout

1. Verify config file is valid JSON (`cat <config-file> | jq .`)
2. Verify Algolia MCP is enabled in Dashboard (Generate AI → MCP Servers → Productivity)
3. Restart MCP client after any config change
4. Test connectivity: `curl -I https://mcp.algolia.com`
5. Check firewall is not blocking `mcp.algolia.com`

### "Authentication failed" / 401 / 403

1. Restart MCP client to trigger a new OAuth flow
2. Verify Algolia MCP is enabled in Dashboard
3. Verify your Algolia user account has the required permissions:
   - SEARCH permission for search and recommendation tools
   - ANALYTICS permission for analytics tools

### "Index not found"

1. Call `algolia_search_list_indices` to get exact index names (case-sensitive)
2. Verify your user has access to the application containing the index

## Authentication and transport errors

### OAuth flow failed / "Invalid client"

1. Verify the server URL is `https://mcp.algolia.com/mcp`
2. Use OAuth discovery with empty OAuth client ID and client secret fields
3. Verify Algolia MCP is enabled in Dashboard
4. Ensure browser allows pop-ups for the OAuth redirect

### Remote HTTP setup

1. Verify your MCP client supports remote HTTP MCP servers
2. Restart or reload the MCP client after changing the configuration
3. Re-add the server with the client-specific setup in [connection-setup.md](connection-setup.md#method-2-manual-configuration)

### Claude Code CLI: "MCP server not found" after adding

1. Verify: `claude mcp list` should show `algolia`
2. Close and reopen terminal, then run `claude` again
3. Validate JSON: `echo '<your-json>' | python3 -m json.tool`

### Claude Code CLI: OAuth window doesn't open

1. Ensure a default browser is set
2. Run Claude Code from a graphical terminal (not SSH)
3. Check if the OAuth callback port is available

### Codex CLI: "Failed to start MCP server"

1. Verify the server was added as a remote HTTP server:
   ```bash
   codex mcp get algolia
   ```
2. Re-run OAuth login:
   ```bash
   codex mcp login algolia
   ```
3. Remove and re-add the server with `codex mcp add algolia --url https://mcp.algolia.com/mcp`.

## Analytics errors

### "No analytics data available"

1. Verify your user account has ANALYTICS permission
2. Check the date range contains actual search activity
3. Analytics data has a 1–4 hour processing delay; use date ranges ending at least 4 hours ago
4. Analytics must be enabled on the index (Dashboard → index → Configuration → Analytics)

### Inconsistent analytics data

- All analytics dates are UTC — "yesterday" may not align with your local timezone
- Use explicit `YYYY-MM-DD` dates for precision
- Wait 24 hours for complete daily data

## Recommendation errors

### "Recommendations not available" / "Feature not enabled"

1. Verify Recommend feature is enabled on your Algolia plan
2. Verify your user has SEARCH permission on the application
3. Check event data volume (minimum 1,000+ events/month needed)
4. Wait 24–48 hours after first events for model training

### "No recommendations found"

1. Lower threshold (try 50)
2. Verify the `objectID` exists in the index
3. `trending-items` requires the least data — test with that model first
4. Use more purchase events before testing `bought-together`

## Error message reference

| Error                   | Cause                                  | Fix                                           |
|-------------------------|----------------------------------------|-----------------------------------------------|
| "Tool not found"        | Tool name misspelled                   | Check tool names in SKILL.md                  |
| "Invalid parameters"    | Missing required params or wrong types | Check MCP tool schemas                        |
| "Server error 500"      | Internal server error                  | Retry; simplify request; report if persistent |
| "JSON-RPC parse error"  | Malformed JSON in request              | Restart MCP client; update to latest version  |
| "429 Too Many Requests" | Rate limit exceeded                    | Reduce request frequency                      |

## Debug checklist

- [ ] MCP client restarted after config changes?
- [ ] Config file is valid JSON?
- [ ] Algolia MCP enabled in Dashboard?
- [ ] OAuth flow completed successfully?
- [ ] Server URL is `https://mcp.algolia.com/mcp`?
- [ ] Index name spelled exactly right? (case-sensitive)
- [ ] Account has correct permissions? (SEARCH, ANALYTICS)
- [ ] Date ranges in `YYYY-MM-DD` format?
- [ ] Network connectivity working? (`curl -I https://mcp.algolia.com`)
- [ ] MCP server is read-only — writes require the Algolia API or Dashboard

If all checks pass, file an issue at https://github.com/algolia/skills/issues with the error message, client name, and steps to reproduce.
