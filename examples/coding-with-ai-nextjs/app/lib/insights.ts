"use client";

import { insightsClient } from "algoliasearch";
import { APP_ID, SEARCH_API_KEY, INDEX_NAME } from "./algolia";

// In algoliasearch v5, Insights is its own client (the search client has no
// pushEvents). We reuse the same app ID + search key.
const insights = insightsClient(APP_ID, SEARCH_API_KEY);

// --------------------------------------------------------------------------
// User token
// --------------------------------------------------------------------------
let authenticatedToken: string | null = null;

/** Call on login/logout to switch between the user ID and the anon token. */
export function setInsightsUserToken(userId: string | null): void {
  authenticatedToken = userId;
}

function getOrCreateAnonToken(): string {
  let token = localStorage.getItem("algolia_anon_token");
  if (!token) {
    token = `anon-${crypto.randomUUID()}`;
    localStorage.setItem("algolia_anon_token", token);
  }
  return token;
}

function getUserToken(): string {
  return authenticatedToken ?? getOrCreateAnonToken();
}

// --------------------------------------------------------------------------
// Chat search attribution (the corrected pattern)
// --------------------------------------------------------------------------
//
// The agent runs its searches server-side, so there is no client-side search to
// read a queryID from. But InstantSearch stamps a per-query `__queryID` onto
// every hit it renders in the chat carousel. So the queryID comes from THE HIT
// ITSELF (`item.__queryID`), recorded by the chat `itemComponent` when the card
// renders — see components/ChatWidget.tsx.
//
// This is why we do NOT key off a hardcoded tool name (the search tool is
// renameable per agent — `algolia_search_index`, a custom name, or an
// MCP-suffixed variant), and NOT off the assistant message's streamed `parts`:
// the `assistantMessageFooterComponent` in this version of react-instantsearch
// is typed `() => Element` and receives no props, so it cannot read the message
// at all. The hit is the reliable, library-idiomatic source.
//
// Clicks go straight through InstantSearch's `sendEvent` helper in the
// itemComponent (it derives queryID/position from the hit), so there is no click
// tracker here. This module only needs to remember each hit's queryID + price so
// the add-to-cart conversion (fired later, from the tool handler) can attribute
// itself to the agent's search.

// objectID -> { queryID, price } captured from the hits the agent surfaced.
const queryIdByObjectID = new Map<string, { queryID?: string; price?: string }>();

/** Record a hit's queryID + price so a later conversion can be attributed. */
export function recordSearchHit(objectID: string, queryID?: string, price?: number | string): void {
  queryIdByObjectID.set(objectID, {
    queryID,
    price: price != null ? String(price) : undefined,
  });
}

/** Add-to-cart attributed to the agent's search (conversion-after-search). */
export function trackChatAddToCart(objectID: string, quantity = 1): void {
  const ctx = queryIdByObjectID.get(objectID);
  const userToken = getUserToken();
  // Prefer the price captured from the agent's search hits. A real store would
  // resolve the authoritative price server-side; this keeps the event valid.
  const price = ctx?.price ?? "0.00";

  if (ctx?.queryID) {
    // Conversion-after-search: attach the queryID. No `positions` needed for a
    // conversion event.
    void insights.pushEvents({
      events: [
        {
          eventType: "conversion",
          eventSubtype: "addToCart",
          eventName: "Added to Cart from Chat",
          index: INDEX_NAME,
          userToken,
          objectIDs: [objectID],
          queryID: ctx.queryID,
          objectData: [{ price, quantity, queryID: ctx.queryID }],
          currency: "USD",
        },
      ],
    });
  } else {
    // No queryID for this product (it was not surfaced by an agent search):
    // record a plain, unattributed addToCart conversion.
    void insights.pushEvents({
      events: [
        {
          eventType: "conversion",
          eventSubtype: "addToCart",
          eventName: "Added to Cart from Chat",
          index: INDEX_NAME,
          userToken,
          objectIDs: [objectID],
          objectData: [{ price, quantity }],
          currency: "USD",
        },
      ],
    });
  }
}
