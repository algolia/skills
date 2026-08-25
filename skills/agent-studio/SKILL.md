---
name: agent-studio
description: |
  Build agentic chat experiences with Algolia Agent Studio and the react-instantsearch Chat widget. Use this skill whenever the user wants to: integrate Agent Studio into a React app, add a chat widget, create client-side tools for the chat agent, customize the chat UI/CSS, send Algolia Insights events, implement user authentication with secure tokens, set up memory/personalization, inject context into chat conversations, create prompt starters, or build any AI-powered conversational shopping/search experience with Algolia. Also use when the user mentions Agent Studio, InstantSearch Chat, or asks about connecting an LLM to Algolia search data.
---

# Agent Studio Integration Skill

This skill guides you through building agentic chat experiences using Algolia
Agent Studio with the `react-instantsearch` Chat component.

Long code samples and any topic-specific detail live in `references/`. Each
section below links to its reference file. When you need deeper detail, read
the linked reference.

## Official Documentation

- Agent Studio Guide: https://www.algolia.com/doc/guides/algolia-ai/agent-studio
- Agent Studio API Reference: https://www.algolia.com/doc/rest-api/agent-studio
- Chat Widget (React): https://www.algolia.com/doc/api-reference/widgets/chat/react
- Client-Side Tools: https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/tools/client-side-tools
- Memory: https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/memory/overview
- User Authentication: https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/user-authentication
- Integration Guide: https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/integration
- Full docs index: https://algolia.com/doc/llms.txt

When you need deeper detail on any topic, fetch the relevant URL above.

## Architecture Overview

An Agent Studio integration has these layers:

```text
React App
├── InstantSearch provider (wraps everything)
│   └── <Chat> component (the widget)
│       ├── transport (API endpoint + auth headers)
│       ├── tools (client-side tool handlers)
│       ├── itemComponent (renders product cards in chat)
│       └── suggestionsComponent (renders suggestion chips)
├── ChatContext (open/close state, context injection)
├── Algolia Insights (event tracking)
└── Memory Channel (personalization via background messages)

Server
├── Auth endpoints (JWT tokens)
├── Algolia secure token generation (for user-scoped memory/conversations)
└── Business logic endpoints (orders, cart, etc.)
```

## Framework notes

The examples target a **client-rendered React app** (Vite/CRA): they use
`import.meta.env`/`VITE_*`, `sessionStorage`, browser-only DOM APIs
(`MutationObserver`, `document.querySelector`), and `<BrowserRouter>`. They do
not run as-is on the Next.js App Router. For Next.js:

- Mark chat components with `"use client"`.
- Use `NEXT_PUBLIC_*` env vars instead of `import.meta.env`.
- Use `<InstantSearchNext>` from `react-instantsearch-nextjs` (per Algolia's
  InstantSearch SSR guidance) instead of `<InstantSearch>`.
- SSR support for the streaming `<Chat>` widget is limited — render it
  client-side.

## 1. Basic Setup

### Dependencies

```bash
npm install react-instantsearch algoliasearch instantsearch.css
```

### Environment Variables

Client-side:

```text
VITE_ALGOLIA_APP_ID=<your-app-id>
VITE_ALGOLIA_SEARCH_API_KEY=<your-search-api-key>
VITE_ALGOLIA_AGENT_ID=<your-agent-id>
VITE_ALGOLIA_INDEX_NAME=products
```

Server-side (for authenticated features):

```text
ALGOLIA_SECRET_KEY=sk-alg-...  # From Agent Studio Settings > Authentication
ALGOLIA_KEY_ID=<key-id>        # From the same page
```

### Minimal Chat Integration

```tsx
import { liteClient as algoliasearch } from "algoliasearch/lite";
import { InstantSearch, Chat } from "react-instantsearch";
import "instantsearch.css/components/chat.css";

const searchClient = algoliasearch(appId, apiKey);

function App() {
  return (
    <InstantSearch searchClient={searchClient} indexName="products">
      <Chat agentId={agentId} />
    </InstantSearch>
  );
}
```

The `agentId` prop is the simplest way to connect. For custom headers (auth
tokens, etc.), use the `transport` prop instead.

### Custom Transport (required for authenticated users)

```tsx
<Chat
  transport={{
    api: `https://${appId}.algolia.net/agent-studio/1/agents/${agentId}/completions?compatibilityMode=ai-sdk-5`,
    headers: async () => ({
      "x-algolia-application-id": appId,
      "x-algolia-api-Key": apiKey,
      // Optional, for memory/personalization:
      "X-Algolia-Secure-User-Token": await fetchAlgoliaToken(),
    }),
  }}
/>
```

The `compatibilityMode=ai-sdk-5` query parameter is REQUIRED when using the
transport prop. The `X-Algolia-Secure-User-Token` header carries the JWT that
scopes memory and conversations to a user (see section 6).

## 2. Client-Side Tools

Client-side tools let the agent trigger actions in your frontend (fetch user
data, update UI, add to cart, etc.). They follow the OpenAI Function Calling
spec: define the schema in the Agent Studio dashboard under
**Tools > Client-side tools**, and register a handler on `<Chat>`.

### The layoutComponent pattern (IMPORTANT)

Use `layoutComponent` (NOT `onToolCall`) for async client-side tools. The
`onToolCall` callback runs during the library's stream-processing phase, which
can deadlock the internal `SerialJobExecutor` with async work.
`layoutComponent` defers execution to React's render cycle and avoids it.

```tsx
function MyToolHandler({ message, addToolResult }) {
  const fetchedRef = useRef(false);
  useEffect(() => {
    if (message.state !== "input-available" || fetchedRef.current) return;
    fetchedRef.current = true;
    fetchSomeData()
      .then((data) => addToolResult({ output: data }))
      .catch((err) => addToolResult({ output: { error: err.message } }));
  }, [message.state, addToolResult]);
  return <></>; // Render UI, or empty fragment for invisible tools
}

<Chat tools={{ my_tool_name: { layoutComponent: MyToolHandler } }} />;
```

Key rules:

- Check `message.state === "input-available"` before executing.
- Use `useRef` to prevent duplicate executions.
- Always call `addToolResult` (even on error) so the agent can continue.
- Tool keys must match the tool name configured in Agent Studio.
- In production, set `"strict": true` on the tool schema; then ALL properties
  must be in `required`, and optional fields use the union type
  `["type", "null"]`.

Full handler typing and the tool-definition JSON schemas (with and without
parameters) are in [references/client-side-tools.md](references/client-side-tools.md).

## 3. Custom Components

The Chat component accepts render-prop components for product cards
(`itemComponent`), suggestion chips (`suggestionsComponent`), header/footer
icons, message wrappers, and more. Use the built-in class names (for example
`ais-ChatPromptSuggestions-suggestion`) so default styles and your overrides
apply.

Minimal product card:

```tsx
<Chat
  itemComponent={({ item }) => (
    <a href={`/product/${item.objectID}`}>
      <img src={item.image} alt={item.name} />
      <p>{item.name}</p>
      <span>${item.price}</span>
    </a>
  )}
/>
```

The item component receives Algolia hit objects; field names follow your index
schema (`objectID`, `name`/`title`, `price`, `image`, `brand`, `category`).

Full component list, the suggestions component, and translations
(`textareaPlaceholder`, `disclaimer`, header `title`, etc.) are in
[references/components-and-css.md](references/components-and-css.md).

## 4. CSS Customization

Import the base styles, then override with CSS custom properties (design
tokens) and class selectors:

```css
@import "instantsearch.css/components/chat.css";

.ais-Chat {
  --ais-primary-color-rgb: 0, 0, 0;           /* Brand color (RGB) */
  --ais-text-color-rgb: 26, 28, 29;           /* Main text */
  --ais-background-color-rgb: 255, 255, 255;  /* Background */
  --ais-font-family: "Inter", system-ui, sans-serif;
}
```

Key class names include `.ais-Chat` (root), `.ais-Chat-container--open` (open
state), `.ais-ChatToggleButton`, `.ais-ChatMessage--user` /
`.ais-ChatMessage--assistant`, `.ais-ChatPrompt-textarea`, and
`.ais-ChatToolSearchIndexCarousel-item` (product cards).

The full class-name table, design-token list, mobile bottom-sheet pattern, and
product-carousel styling are in [references/components-and-css.md](references/components-and-css.md).
A complete monochrome override file is in [references/css-overrides-example.md](references/css-overrides-example.md).

## 5. Context Injection

Context injection sends hidden system context to the agent (for example "user
is on product page X") without the user seeing it.

Pattern:

1. Format messages as a `[Context: {system info}]{visible user message}` string.
2. Inject the string into the Chat textarea using the native
   `HTMLTextAreaElement` value setter (so React's `onChange` fires), then submit
   the form programmatically. If the chat is closed, open it first.
3. Strip the `[Context: ...]` prefix from the DOM before the user sees it: a
   `MutationObserver` plus polling scans user message elements, matches their
   text against a context pattern, and either hides context-only messages or
   replaces the text with just the visible portion.

A `sendWithContext(context, visibleMessage?)` action (exposed via a
`ChatContext` provider) builds the string, injects, and submits. Use it to
auto-inject product context when the chat opens on a product page, or to power
prompt starters that carry context while showing the user only a question.

The full `ChatProvider`, the `useContextStripping()` hook (including the context
regex and DOM-matching logic), the provider hierarchy, and usage examples are in
[references/context-injection.md](references/context-injection.md).

## 6. User Authentication & Secure Tokens

Memory and conversation scoping require user authentication via JWT tokens. Mint
the token server-side (so the Agent Studio secret never reaches the browser) and
pass it to the Chat transport as the `X-Algolia-Secure-User-Token` header.

- Server: sign an HS256 JWT with `sub = userId`, `expiresIn`, and a header `kid`
  equal to your Key ID. The secret (`sk-alg-...`) and Key ID come from Agent
  Studio **Settings > Authentication**.
- Client: cache the token, refresh it before `exp`, and fall back to `null` for
  anonymous users. Read it in the transport `headers` callback.
- Account switching: on logout/switch, clear session storage keys prefixed with
  `instantsearch-chat-initial-messages`, and re-key `<InstantSearch>` with
  `key={user?.id ?? "anon"}` so the chat remounts with a fresh session.

Full server and client token code and the account-switching snippet are in
[references/authentication.md](references/authentication.md).

## 7. Memory & Personalization

Memory lets the agent remember facts about users across conversations.

- Enable it in the dashboard: **Customizations > Memory**, with data retention
  set to 30/60/90 days (NOT 0), and require user authentication (section 6).
- Memory types: **semantic** (stable user facts/preferences) and **episodic**
  (agent reasoning chains).
- When enabled, three tools are auto-added: `algolia_memorize` (semantic),
  `algolia_ponder` (episodic), and `algolia_memory_search`.
- Memory channel pattern: send background context to the agent by firing a
  completion request whose message is prefixed with `[MEMORY]`, then consume and
  discard the response body. Fire it on product views, add-to-cart, and
  purchases.
- Include a memory instruction in the agent's system prompt so it extracts
  facts from `[Context:...]` messages for future personalization.

The full memory-channel `fetch` implementation, the event triggers, and the
memory system-prompt block are in [references/memory.md](references/memory.md).

## 8. Algolia Insights Events

Track user behavior to power Algolia analytics and AI Personalization. Send
events with the lite client's `pushEvents` method.

- Setup: `algoliasearch(appId, apiKey)` from `algoliasearch/lite`.
- User token: stable random `anon-...` token in localStorage for anonymous
  users; switch to the authenticated user ID on login.
- Event shapes:
  - View: `eventType: "view"`, `objectIDs`.
  - Click after search: `eventType: "click"` with `positions` (1-based) and the
    search response's `queryID`.
  - Add to cart: `eventType: "conversion"`, `eventSubtype: "addToCart"`, with
    `objectData` (`price`, `quantity`) and `currency`.
  - Purchase: `eventType: "conversion"`, `eventSubtype: "purchase"`, with
    per-item `objectData` and `currency`.
- Search-context attribution: on a search-result click, store `queryID` +
  `position` in sessionStorage keyed by `objectID`; consume it on the product
  page to attribute later clicks/conversions to the originating query.
- Attribute chat events to the agent's search: the agent searches server-side,
  but `react-instantsearch` stamps the `queryID` onto each hit as
  `item.__queryID`. The chat's `itemComponent` receives the hit (`item`) and a
  built-in `sendEvent` helper, so the queryID comes from the hit — do NOT read
  the assistant message's streamed `parts` and do NOT match on a tool name (the
  search tool is renameable per agent, and the chat's message-footer component
  receives no message in this library version, so it cannot read the results).
  - Clicks: fire `sendEvent("click", item, "…")` in the `itemComponent`;
    InstantSearch derives the `queryID` and position from the hit (no manual
    `pushEvents`).
  - Conversions (add-to-cart/purchase): triggered by a client-side tool, not a
    hit click, so they cannot use `sendEvent`. Record
    `objectID → { queryID, price }` as cards render, then look it up on the
    conversion and send a conversion-after-search event carrying that `queryID`
    (in `objectData` with `price`/`quantity`; no `positions` needed).
  - Agent Studio runs these searches with click analytics and tags them
    `alg#agent-studio`. Without the `queryID`, events are still recorded but do
    not count as click- or conversion-after-search, so the agent's
    click-through, conversion, and revenue analytics are lost.

Full event payloads, the user-token helpers, the chat-attribution helpers, and
the search-context store/consume helpers are in [references/insights-events.md](references/insights-events.md).

## 9. Prompt Starters

Generate personalized conversation starters on product pages using a separate
agent:

1. Create a dedicated Agent Studio agent for prompt generation.
2. Call the agent API directly with product context and a
   `display_prompt_starters` tool.
3. Parse the streamed response for tool-call arguments.
4. Render the starters as clickable buttons that inject context into the main
   chat (via `sendWithContext`, section 5).

The full prompt-starters component with streaming-response parsing is in
[references/prompt-starters.md](references/prompt-starters.md).

## 10. Agent Prompt Best Practices

When writing the agent's system prompt in Agent Studio:

- **Search strategy**: use short keywords, not natural language. Use facet
  filters only for exact categorical matches (brand, category). Never use facet
  filters for price — search without them and post-filter.
- **Tool results**: don't summarize products returned by search — they're
  already displayed as cards. Just give brief context ("I found 5 laptops
  matching your criteria").
- **Personalization flow**: when the user references past purchases, call
  `get_user_orders` FIRST before searching.
- **Memory**: instruct the agent to extract context from `[Context:...]`
  messages for future personalization.
- **Limits**: set a max number of search calls per session (e.g. 5) to control
  costs.
- **Error handling**: on tool errors, apologize once and invite the user to
  rephrase.

A complete example agent system prompt is in
[references/agent-prompt-example.md](references/agent-prompt-example.md).

## Reference Files

For detailed implementation examples beyond this guide, read the reference files
in this skill's `references/` directory:

- [references/client-side-tools.md](references/client-side-tools.md) — full
  tool handler typing and tool-definition JSON schemas
- [references/components-and-css.md](references/components-and-css.md) — full
  component list, translations, CSS class-name table, design tokens, and
  customization patterns
- [references/css-overrides-example.md](references/css-overrides-example.md) —
  complete CSS override file for a monochrome design system
- [references/context-injection.md](references/context-injection.md) — full
  ChatContext provider and useContextStripping implementations
- [references/authentication.md](references/authentication.md) — server/client
  secure-token code and account-switching cleanup
- [references/memory.md](references/memory.md) — memory-channel fetch
  implementation and memory system-prompt block
- [references/insights-events.md](references/insights-events.md) — full Insights
  event payloads and search attribution helpers
- [references/prompt-starters.md](references/prompt-starters.md) — prompt
  starters component with streaming response parsing
- [references/agent-prompt-example.md](references/agent-prompt-example.md) —
  complete agent system prompt template
