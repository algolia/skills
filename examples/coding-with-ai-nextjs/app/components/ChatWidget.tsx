"use client";

import { Chat } from "react-instantsearch";
import type { RecommendItemComponentProps, RecordWithObjectID } from "instantsearch-ui-components";
import { APP_ID, SEARCH_API_KEY, AGENT_ID, type ProductHit } from "../lib/algolia";
import { fetchAlgoliaToken } from "../lib/algolia-token";
import { recordSearchHit } from "../lib/insights";
import { AddToCartTool } from "./AddToCartTool";

// Product card rendered inside the chat's search-result carousel. The
// itemComponent receives the real InstantSearch props — the hit (`item`) and the
// built-in `sendEvent` helper. The queryID lives ON THE HIT (`item.__queryID`),
// so we record it here for the later add-to-cart conversion, and fire clicks
// through `sendEvent` (InstantSearch derives queryID + position from the hit).
function ChatProductCard({ item, sendEvent }: RecommendItemComponentProps<RecordWithObjectID<ProductHit>>) {
  // Remember this hit's queryID + price so trackChatAddToCart can attribute a
  // later conversion-after-search to the agent's search (see lib/insights.ts).
  recordSearchHit(item.objectID, item.__queryID, item.price);

  const trackClick = () => sendEvent("click", item, "Product Clicked in Chat");

  return (
    <div
      className="chat-hit"
      role="button"
      tabIndex={0}
      onClick={trackClick}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") trackClick();
      }}
    >
      {item.image ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={item.image} alt={item.name ?? item.objectID} className="chat-hit-image" />
      ) : null}
      <span className="chat-hit-name">{item.name ?? item.objectID}</span>
      {item.price != null ? <span className="chat-hit-price">${item.price}</span> : null}
    </div>
  );
}

export function ChatWidget() {
  return (
    <Chat
      transport={{
        api: `https://${APP_ID}.algolia.net/agent-studio/1/agents/${AGENT_ID}/completions?compatibilityMode=ai-sdk-5`,
        // compatibilityMode=ai-sdk-5 is REQUIRED when using a custom transport.
        headers: async () => {
          const token = await fetchAlgoliaToken();
          return {
            "x-algolia-application-id": APP_ID,
            "x-algolia-api-key": SEARCH_API_KEY,
            // Optional: scopes memory & conversations to the signed-in user.
            ...(token ? { "X-Algolia-Secure-User-Token": token } : {}),
          };
        },
      }}
      tools={{
        // Key MUST match the tool name configured in the Agent Studio dashboard.
        add_to_cart: { layoutComponent: AddToCartTool },
      }}
      itemComponent={ChatProductCard}
      translations={{
        prompt: {
          textareaPlaceholder: "Ask about our products…",
          disclaimer: "AI-powered assistant. Responses may not be perfect.",
        },
        header: {
          title: "Shopping assistant",
        },
      }}
    />
  );
}
