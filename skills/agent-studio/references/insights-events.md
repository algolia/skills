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

## Search-context attribution

To connect clicks and conversions back to the search query that originated
them, store the search context (queryID + position) when a product is clicked
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
