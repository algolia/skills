"use client";

import { useEffect, useRef } from "react";
import { addToCart } from "../lib/cart";
import { trackChatAddToCart } from "../lib/insights";

// Client-side tool handler for the `add_to_cart` tool defined in the Agent
// Studio dashboard. It uses the `layoutComponent` pattern (NOT `onToolCall`):
// onToolCall runs during the library's stream-processing phase and can deadlock
// the internal SerialJobExecutor with async work, whereas layoutComponent defers
// execution to React's render cycle.

// Match the library's ClientSideToolComponentProps, where `input` is `unknown`.
// Narrow it at runtime inside the effect rather than in the prop type.
type AddToCartMessage = {
  state: string;
  input?: unknown;
  // The Chat widget passes additional fields we don't need here.
  [key: string]: unknown;
};

export function AddToCartTool({
  message,
  addToolResult,
}: {
  message: AddToCartMessage;
  addToolResult: (params: { output: unknown }) => void;
  [key: string]: unknown;
}) {
  // Guard against duplicate executions across re-renders.
  const handledRef = useRef(false);

  useEffect(() => {
    if (message.state !== "input-available" || handledRef.current) return;
    handledRef.current = true;

    try {
      const input = message.input as { productId?: string; quantity?: number | null } | undefined;
      const productId = input?.productId;
      const quantity = input?.quantity ?? 1;

      if (!productId) {
        // Always call addToolResult, even on failure, so the agent can continue.
        addToolResult({ output: { error: "Missing productId" } });
        return;
      }

      const line = addToCart(productId, quantity);
      // Conversion-after-search: attributed to the agent's search when we have a
      // queryID for this product (see lib/insights.ts).
      trackChatAddToCart(productId, quantity);

      addToolResult({
        output: { success: true, productId, quantity: line.quantity },
      });
    } catch (err) {
      addToolResult({
        output: { error: err instanceof Error ? err.message : "Add to cart failed" },
      });
    }
  }, [message.state, message.input, addToolResult]);

  // Invisible tool: render an empty fragment (the component must return an
  // Element, not null, per ClientSideToolComponent).
  return <></>;
}
