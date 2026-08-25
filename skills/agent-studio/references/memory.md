# Memory & Personalization — Full Reference

Memory lets the agent remember facts about users across conversations.

## Enabling memory

1. Enable in the Agent Studio dashboard: **Customizations > Memory** toggle.
2. Set data retention to 30 / 60 / 90 days (NOT 0 — 0 disables persistence).
3. Require user authentication (see `authentication.md`). Memory is scoped to
   the authenticated user via the `X-Algolia-Secure-User-Token`.

## Memory types

- **Semantic** — stable user facts and preferences ("User prefers dark mode",
  "User is allergic to peanuts").
- **Episodic** — agent reasoning chains (Observation / Thoughts / Action /
  Result).

## Memory tools (auto-added when memory is enabled)

- `algolia_memorize` — saves semantic memories.
- `algolia_ponder` — saves episodic memories (reasoning).
- `algolia_memory_search` — searches existing memories.

## Memory channel pattern

Send background context to the agent for memory storage without showing it in
the chat UI. Fire a completion request whose message is prefixed with
`[MEMORY]`, then consume (and discard) the response body.

```typescript
async function sendMemoryToAgent(memory: string): Promise<{ success: boolean }> {
  const token = await fetchAlgoliaToken();
  const response = await fetch(
    `https://${appId}.algolia.net/agent-studio/1/agents/${agentId}/completions?compatibilityMode=ai-sdk-5`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-algolia-application-id": appId,
        "x-algolia-api-Key": apiKey,
        "X-Algolia-Secure-User-Token": token,
      },
      body: JSON.stringify({
        id: crypto.randomUUID(),
        messages: [
          {
            role: "user",
            parts: [
              {
                type: "text",
                text: `[MEMORY] Remember this about the current user: ${memory}`,
              },
            ],
          },
        ],
      }),
    }
  );
  await response.text(); // Consume the streamed body
  return { success: response.ok };
}
```

**When to send memory events:**

- Product page views: `"User viewed '{name}' priced at ${price} by {brand}"`
- Add to cart: `"User added {quantity}x '{name}' to cart"`
- Purchases: `"User purchased {items} for ${total}"`

## Agent prompt for memory

Include a memory instruction in the agent's system prompt so it processes
context for personalization:

```text
**MEMORY**
When you receive context like [Context:...] ALWAYS extract things to remember
to drive more engaging and personalized conversations in future interactions.
Combine memory context with order history for the richest personalization.
```
