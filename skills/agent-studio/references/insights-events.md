# Algolia Insights Events — Full Reference

Track user behavior to power Algolia analytics and AI Personalization. Events
are sent with the lite client's `pushEvents` method.

## Setup

```typescript
import { liteClient as algoliasearch } from "algoliasearch/lite";
const client = algoliasearch(appId, apiKey);
```

## User token management

Use a stable random token for anonymous users, and switch to the authenticated
user ID once the user logs in.

```typescript
// Anonymous users: stable random token in localStorage
function getOrCreateAnonToken(): string {
  let token = localStorage.getItem("algolia_anon_token");
  if (!token) {
    token = `anon-${crypto.randomUUID()}`;
    localStorage.setItem("algolia_anon_token", token);
  }
  return token;
}

// On login: switch to authenticated user ID
let authenticatedToken: string | null = null;
function setInsightsUserToken(userId: string | null) {
  authenticatedToken = userId;
}
function getUserToken(): string {
  return authenticatedToken ?? getOrCreateAnonToken();
}
```

## Event types

```typescript
// View events
client.pushEvents({ events: [{
  eventType: "view",
  eventName: "Product Viewed",
  index: indexName,
  userToken: getUserToken(),
  objectIDs: [objectID],
}]});

// Click after search (requires queryID from the search response)
client.pushEvents({ events: [{
  eventType: "click",
  eventName: "Product Clicked after Search",
  index: indexName,
  userToken: getUserToken(),
  objectIDs: [objectID],
  positions: [position], // 1-based position in search results
  queryID: queryID,
}]});

// Add to cart (conversion with revenue)
client.pushEvents({ events: [{
  eventType: "conversion",
  eventSubtype: "addToCart",
  eventName: "Product Added to Cart",
  index: indexName,
  userToken: getUserToken(),
  objectIDs: [objectID],
  objectData: [{ price: "29.99", quantity: 1 }],
  currency: "USD",
}]});

// Purchase (conversion with revenue)
client.pushEvents({ events: [{
  eventType: "conversion",
  eventSubtype: "purchase",
  eventName: "Products Purchased",
  index: indexName,
  userToken: getUserToken(),
  objectIDs: objectIDs,
  objectData: items.map((i) => ({ price: i.price.toFixed(2), quantity: i.quantity })),
  currency: "USD",
}]});
```

## Attribute chat events to the agent's search

In the chat flow the agent runs its searches server-side, so there is no
client-side search to read a `queryID` from. Instead, every `algolia_search`
tool result streamed to the client includes the `queryID` of the search the
agent ran, alongside the `hits` it returned. Agent Studio runs these searches
with click analytics enabled and tags them with `alg#agent-studio`, so click
and conversion events that carry this `queryID` roll up as the agent's
search-driven analytics: click-through rate, conversion rate, and revenue.

Build a lookup from the streamed search tool results, then include the
`queryID` (and the 1-based `position` for clicks) in the events you send for
products the agent surfaced.

```typescript
type ChatSearchContext = { queryID: string; position: number };

// Index { queryID, position } per objectID from the agent's algolia_search
// tool results in an assistant message's parts. AI SDK v5 tool parts carry the
// tool output; the search tool returns { hits, queryID }.
function indexChatSearchResults(parts: any[], map: Map<string, ChatSearchContext>) {
  for (const part of parts) {
    const output = part?.output ?? part?.result;
    if (!output?.queryID || !Array.isArray(output?.hits)) continue;
    output.hits.forEach((hit: { objectID: string }, i: number) => {
      map.set(hit.objectID, { queryID: output.queryID, position: i + 1 });
    });
  }
}
```

```typescript
// Click on a product the agent surfaced (click-after-search)
function trackChatClick(objectID: string, ctx: ChatSearchContext) {
  client.pushEvents({ events: [{
    eventType: "click",
    eventName: "Product Clicked in Chat",
    index: indexName,
    userToken: getUserToken(),
    objectIDs: [objectID],
    positions: [ctx.position],
    queryID: ctx.queryID,
  }]});
}

// Add to cart attributed to the agent's search (conversion-after-search)
function trackChatAddToCart(objectID: string, price: string, ctx?: ChatSearchContext) {
  client.pushEvents({ events: [{
    eventType: "conversion",
    eventSubtype: "addToCart",
    eventName: "Added to Cart from Chat",
    index: indexName,
    userToken: getUserToken(),
    objectIDs: [objectID],
    ...(ctx ? { queryID: ctx.queryID } : {}),
    objectData: [{ price, quantity: 1, ...(ctx ? { queryID: ctx.queryID } : {}) }],
    currency: "USD",
  }]});
}
```

Wire `trackChatClick` into the chat's `itemComponent` (the product card) and
`trackChatAddToCart` into your add-to-cart handler or client-side tool. Without
the `queryID`, the events are still recorded, but they do not count as
click-after-search or conversion-after-search, so the agent's contribution to
click-through, conversion, and revenue is lost.

## Search-context attribution

For products opened from a client-side InstantSearch results page (not the
chat), connect clicks and conversions back to the search query that originated
them: store the search context (queryID + position) when a product is clicked
from search results, then retrieve it on the product page.

```typescript
// On search result click
function storeSearchContext(ctx: { queryID: string; position: number; objectID: string }) {
  sessionStorage.setItem(`search_ctx_${ctx.objectID}`, JSON.stringify(ctx));
}

// On product page load
function consumeSearchContext(objectID: string) {
  const key = `search_ctx_${objectID}`;
  const raw = sessionStorage.getItem(key);
  if (!raw) return null;
  sessionStorage.removeItem(key);
  return JSON.parse(raw);
}
```
