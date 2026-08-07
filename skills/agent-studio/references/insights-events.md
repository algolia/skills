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
client-side search to read a `queryID` from. Instead, `react-instantsearch`
stamps a per-query token onto every hit it renders in the chat carousel: the
`queryID` lives on the hit itself as `item.__queryID`. The chat's
`itemComponent` receives the real InstantSearch props — the hit (`item`) and a
built-in `sendEvent` helper — so both clicks and conversions attribute
themselves from the hit. Do not read the assistant message's streamed `parts`
and do not match on a tool name: the search tool is renameable per agent
(`algolia_search_index`, a custom name, or an MCP-suffixed variant), and the
chat's message-footer component in this version of `react-instantsearch`
receives no message, so it cannot read the results at all. The hit is the
reliable, library-idiomatic source.

Agent Studio runs the agent's searches with click analytics enabled and tags
them with `alg#agent-studio`, so click and conversion events that carry this
`queryID` roll up as the agent's search-driven analytics: click-through rate,
conversion rate, and revenue.

### Clicks: fire the built-in `sendEvent`

For a click on a product card, call the `sendEvent` helper the `itemComponent`
receives. InstantSearch derives the `queryID` and 1-based position from the hit,
so there is no manual `pushEvents` call for clicks.

```tsx
// components/ChatWidget.tsx — product card rendered in the chat carousel.
function ChatProductCard({ item, sendEvent }) {
  // Record this hit's queryID + price so a later add-to-cart can attribute
  // itself to the agent's search (see recordSearchHit below).
  recordSearchHit(item.objectID, item.__queryID, item.price);

  return (
    <div onClick={() => sendEvent("click", item, "Product Clicked in Chat")}>
      {item.name} — ${item.price}
    </div>
  );
}
```

### Conversions: look up the recorded `queryID`

Add-to-cart and purchase are triggered by a client-side tool, not by a hit
click, so they cannot use `sendEvent`. Record `objectID -> { queryID, price }`
as each card renders, then look it up on the conversion and send a
conversion-after-search event carrying that `queryID`. A conversion event needs
no `positions`.

```typescript
// lib/insights.ts — remember each hit, then attribute the conversion.
const queryIdByObjectID = new Map<string, { queryID?: string; price?: string }>();

export function recordSearchHit(objectID: string, queryID?: string, price?: number | string) {
  queryIdByObjectID.set(objectID, {
    queryID,
    price: price != null ? String(price) : undefined,
  });
}

export function trackChatAddToCart(objectID: string, quantity = 1) {
  const ctx = queryIdByObjectID.get(objectID);
  const price = ctx?.price ?? "0.00";

  client.pushEvents({ events: [{
    eventType: "conversion",
    eventSubtype: "addToCart",
    eventName: "Added to Cart from Chat",
    index: indexName,
    userToken: getUserToken(),
    objectIDs: [objectID],
    // Attach the queryID only when the product came from an agent search.
    ...(ctx?.queryID ? { queryID: ctx.queryID } : {}),
    objectData: [{ price, quantity, ...(ctx?.queryID ? { queryID: ctx.queryID } : {}) }],
    currency: "USD",
  }]});
}
```

Wire `recordSearchHit` and the `sendEvent` click into the chat's `itemComponent`
(the product card), and `trackChatAddToCart` into your add-to-cart handler or
client-side tool. Without the `queryID`, the events are still recorded, but they
do not count as click-after-search or conversion-after-search, so the agent's
contribution to click-through, conversion, and revenue is lost.

For a complete working example, see `examples/coding-with-ai-nextjs`.

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
