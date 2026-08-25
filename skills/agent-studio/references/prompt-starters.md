# Prompt Starters — Full Implementation

Generate personalized AI conversation starters on product pages using a dedicated Agent Studio agent.

## Architecture

- A **separate agent** (with its own `VITE_ALGOLIA_PROMPT_STARTERS_AGENT_ID`) generates starters
- The agent is called directly via the API (not through the Chat widget)
- A `display_prompt_starters` client-side tool forces structured output
- The streamed response is parsed for the tool call arguments
- Starters are rendered as buttons that open the main chat with context

## Component

```tsx
import { useEffect, useState } from "react";
import { fetchAlgoliaToken } from "../../lib/apiClient";
import { useChatActions } from "../../context/ChatContext";

const agentId = import.meta.env.VITE_ALGOLIA_PROMPT_STARTERS_AGENT_ID;
const appId = import.meta.env.VITE_ALGOLIA_APP_ID;
const apiKey = import.meta.env.VITE_ALGOLIA_SEARCH_API_KEY;

interface Props {
  product: {
    objectID: string;
    name: string;
    price: number;
    brand?: string;
    category?: string;
    description?: string;
    rating?: number;
  };
}

export default function PromptStarters({ product }: Props) {
  const [starters, setStarters] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const { sendWithContext } = useChatActions();

  useEffect(() => {
    if (!agentId || !appId || !apiKey) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchStarters() {
      const token = await fetchAlgoliaToken();
      if (cancelled) return;

      // Build product context string
      const productContext = [
        `Product: "${product.name}"`,
        `Price: $${product.price.toFixed(2)}`,
        product.brand ? `Brand: ${product.brand}` : "",
        product.category ? `Category: ${product.category}` : "",
        product.description ? `Description: ${product.description}` : "",
        product.rating != null ? `Rating: ${product.rating.toFixed(1)}/5` : "",
      ]
        .filter(Boolean)
        .join(". ");

      try {
        const url = `https://${appId}.algolia.net/agent-studio/1/agents/${agentId}/completions?compatibilityMode=ai-sdk-5`;
        const headers: Record<string, string> = {
          "Content-Type": "application/json",
          "x-algolia-application-id": appId!,
          "x-algolia-api-Key": apiKey!,
        };
        if (token) {
          headers["X-Algolia-Secure-User-Token"] = token;
        }

        const res = await fetch(url, {
          method: "POST",
          headers,
          body: JSON.stringify({
            id: crypto.randomUUID(),
            messages: [
              {
                role: "user",
                parts: [{ type: "text", text: productContext }],
              },
            ],
            // Define a client-side tool to force structured output
            tools: [
              {
                type: "function",
                name: "display_prompt_starters",
                description:
                  "Display personalized prompt starter suggestions on the product page to engage the user into a conversation.",
                parameters: {
                  type: "object",
                  properties: {
                    starters: {
                      type: "array",
                      description:
                        "Exactly 3 prompt starter questions tailored to the product and user context.",
                      items: {
                        type: "string",
                        description:
                          "A short, natural question the user might ask about the product. Max 140 characters.",
                      },
                      minItems: 3,
                      maxItems: 3,
                    },
                  },
                  required: ["starters"],
                  additionalProperties: false,
                },
              },
            ],
            // Force the agent to use this tool
            toolChoice: {
              type: "function",
              name: "display_prompt_starters",
            },
          }),
        });

        if (!res.ok || !res.body) {
          setLoading(false);
          return;
        }

        const text = await res.text();
        const parsed = parseStarters(text);
        if (!cancelled && parsed.length > 0) {
          setStarters(parsed);
        }
      } catch {
        // Non-critical — just don't show starters
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchStarters();
    return () => {
      cancelled = true;
    };
  }, [product.objectID]);

  function handleClick(starter: string) {
    const ctx = `The user is viewing product "${product.name}" (ID: ${product.objectID}, price: $${product.price.toFixed(2)}${product.brand ? `, brand: ${product.brand}` : ""}${product.category ? `, category: ${product.category}` : ""}). Answer their question about this product.`;
    sendWithContext(ctx, starter);
  }

  if (loading || starters.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mt-4">
      {starters.map((s) => (
        <button
          key={s}
          onClick={() => handleClick(s)}
          className="px-3 py-2 text-sm border rounded-lg hover:bg-gray-50 transition-colors"
        >
          {s}
        </button>
      ))}
    </div>
  );
}
```

## Parsing the Streamed Response

The AI SDK 5 stream sends newline-delimited `data: {JSON}` events. The tool arguments come through as:
- `tool-input-delta` events (incremental chunks)
- `tool-input-available` event (complete parsed input)

```typescript
function parseStarters(raw: string): string[] {
  let toolArgs = "";

  for (const line of raw.split("\n")) {
    if (!line.startsWith("data: ")) continue;
    const payload = line.slice(6);
    try {
      const obj = JSON.parse(payload);

      // Best case: complete input available
      if (
        obj.type === "tool-input-available" &&
        obj.toolName === "display_prompt_starters" &&
        Array.isArray(obj.input?.starters)
      ) {
        return obj.input.starters;
      }

      // Accumulate deltas as fallback
      if (
        obj.type === "tool-input-delta" &&
        typeof obj.inputTextDelta === "string"
      ) {
        toolArgs += obj.inputTextDelta;
      }
    } catch {
      // Not JSON, skip
    }
  }

  // Try parsing accumulated args
  if (toolArgs) {
    try {
      const parsed = JSON.parse(toolArgs);
      if (Array.isArray(parsed.starters)) {
        return parsed.starters;
      }
    } catch {
      // ignore
    }
  }

  return [];
}
```

## Agent Setup for Prompt Starters

Create a separate agent in Agent Studio with:
- **System prompt**: "Generate exactly 3 short, natural questions a shopper might ask about the given product. Questions should be engaging and help the user start a conversation."
- **Tool**: Add the `display_prompt_starters` tool definition (same as above)
- **No search tools needed** — this agent just generates questions based on the product context
