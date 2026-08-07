# Coding with AI — Next.js reference app

A minimal, correct-by-construction reference app for embedding Algolia
InstantSearch and an Agent Studio chat agent in a **Next.js App Router** project.
It is the canonical thing to diff against: the patterns here are shaped for the
App Router, not ported from a Vite/SPA example.

## What it demonstrates

- Search UI (`SearchBox` + `Hits`) and a streaming `<Chat>` agent sharing one
  Algolia client and index.
- The App Router client/server split: global CSS and metadata on the server; all
  Algolia and chat UI in Client Components.
- SSR-safe InstantSearch via `<InstantSearchNext>` from
  `react-instantsearch-nextjs`.
- A server-side token endpoint that mints an HS256 JWT so the Agent Studio secret
  never reaches the browser.
- Business-events attribution done the library-idiomatic way: the search
  `queryID` is read from the hit itself (`item.__queryID`) in the chat
  `itemComponent`. Clicks fire through InstantSearch's built-in `sendEvent`;
  add-to-cart conversions look up the queryID recorded when the hit rendered.
  This avoids matching a hardcoded tool name and does not depend on the
  assistant message's `parts` (the footer component cannot access them).
- One client-side tool (`add_to_cart`) built with the `layoutComponent` pattern.

## Prerequisites

- Node.js 20 or newer.
- An Algolia application with a populated index and a **search-only** API key.
- A **published** Agent Studio agent, and its agent ID.
- The **secret key** (`sk-alg-…`) and **Key ID** from Agent Studio:
  **Settings > Authentication**.

## Setup

```bash
# 1. Configure environment
cp .env.example .env.local
#    then fill in the values in .env.local

# 2. Install and run
npm install
npm run dev
```

Open http://localhost:3000. Type a query into the search box, or open the chat
bubble and ask the agent about products.

Type-check without running the app:

```bash
npm run typecheck
```

## Environment variables

Client-side (inlined into the browser bundle — must be `NEXT_PUBLIC_*`):

| Variable | Purpose |
| --- | --- |
| `NEXT_PUBLIC_ALGOLIA_APP_ID` | Algolia application ID |
| `NEXT_PUBLIC_ALGOLIA_SEARCH_API_KEY` | Search-only API key |
| `NEXT_PUBLIC_ALGOLIA_INDEX_NAME` | Index to search (e.g. `products`) |
| `NEXT_PUBLIC_ALGOLIA_AGENT_ID` | Published Agent Studio agent ID |

Server-only (never prefix with `NEXT_PUBLIC`):

| Variable | Purpose |
| --- | --- |
| `ALGOLIA_SECRET_KEY` | Signs the user JWT — from Settings > Authentication |
| `ALGOLIA_KEY_ID` | JWT header `kid` — from the same page |

## Dashboard configuration (required)

Two things must be set up in the Agent Studio dashboard for this app to work
end to end:

1. **Define the `add_to_cart` client-side tool.** Under **Tools > Client-side
   tools**, add a function named exactly `add_to_cart` with parameters
   `productId` (string) and `quantity` (integer, nullable). The tool name must
   match the key registered on `<Chat tools={{ add_to_cart: … }}>`. In
   production set `"strict": true` — then every property must appear in
   `required`, and optional fields use the union type `["integer", "null"]`.

   ```json
   {
     "type": "function",
     "function": {
       "name": "add_to_cart",
       "description": "Adds a product to the user's shopping cart.",
       "strict": true,
       "parameters": {
         "type": "object",
         "properties": {
           "productId": { "type": "string", "description": "The Algolia objectID" },
           "quantity": { "type": ["integer", "null"], "description": "Defaults to 1" }
         },
         "required": ["productId", "quantity"],
         "additionalProperties": false
       }
     }
   }
   ```

2. **Enable memory with a non-zero retention.** Under **Customizations >
   Memory**, set data retention to 30/60/90 days (NOT 0) and require user
   authentication. Memory and conversation scoping depend on the secure user
   token minted by `app/api/auth/algolia-token/route.ts`.

## What is mocked

This is a starter, not a store. Be aware:

- **The cart is an in-memory stub** (`app/lib/cart.ts`). It is not persisted and
  not shared with any server — state is lost on refresh. Replace it with a call
  to your commerce backend.
- **The authenticated user is hardcoded** (`DEMO_USER_ID` in
  `app/lib/algolia-token.ts`, and the request body in the token route). Wire both
  to your real auth/session, and never trust a client-supplied user ID on the
  server.
- **The add-to-cart conversion price** falls back to `0.00` when the product was
  not surfaced by an agent search (so no price was captured). Resolve the
  authoritative price server-side in a real integration.
- Product-card fields (`name`, `price`, `image`, `brand`) assume a common index
  schema. Adjust `ProductHit` in `app/lib/algolia.ts` to match yours.

## File tour

```
app/
  layout.tsx                       Server Component: html shell + global CSS
  providers.tsx                    "use client": <InstantSearchNext> provider
  page.tsx                         Composes the search UI and the chat widget
  globals.css                      InstantSearch + chat CSS, plus rebrand tokens
  api/auth/algolia-token/route.ts  Route Handler: mints the HS256 user JWT
  components/
    Search.tsx                     SearchBox + Hits
    ChatWidget.tsx                 <Chat> transport, tools, attribution wiring
    AddToCartTool.tsx              add_to_cart handler (layoutComponent pattern)
  lib/
    algolia.ts                     Shared search client + config + ProductHit
    algolia-token.ts               Client helper: fetch + cache the user token
    insights.ts                    Insights events + queryID attribution from item.__queryID
    cart.ts                        In-memory cart stub
```
