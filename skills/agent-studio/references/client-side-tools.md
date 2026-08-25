# Client-Side Tools — Full Reference

Client-side tools let the agent trigger actions in your frontend (fetch user
data, update UI, add to cart, etc.). They follow the OpenAI Function Calling
spec. You define the tool schema in the Agent Studio dashboard and register a
handler on the `<Chat>` component in your React app.

## The `layoutComponent` pattern (IMPORTANT)

Use `layoutComponent` (NOT `onToolCall`) for async client-side tools. The
`onToolCall` callback executes during the library's stream-processing phase,
which can deadlock the internal `SerialJobExecutor` when combined with async
work. `layoutComponent` defers execution to React's render cycle and avoids the
deadlock.

```tsx
function MyToolHandler({
  message,
  addToolResult,
}: {
  message: { state: string };
  addToolResult: (params: { output: unknown }) => void;
  [key: string]: unknown;
}) {
  const fetchedRef = useRef(false);

  useEffect(() => {
    // Only execute when the tool is ready for input and hasn't run yet
    if (message.state !== "input-available" || fetchedRef.current) return;
    fetchedRef.current = true;

    // Do your async work here
    fetchSomeData()
      .then((data) => addToolResult({ output: data }))
      .catch((err) => addToolResult({ output: { error: err.message } }));
  }, [message.state, addToolResult]);

  // Render UI, or return an empty fragment for invisible tools
  return <></>;
}

// Register on the Chat component
<Chat
  tools={{
    my_tool_name: { layoutComponent: MyToolHandler },
  }}
/>;
```

**Key rules:**

- The component receives `message` (with `state`), `addToolResult`,
  `indexUiState`, and `setIndexUiState`.
- Check `message.state === "input-available"` before executing.
- Use `useRef` to prevent duplicate executions.
- Always call `addToolResult` (even on error) so the agent can continue.
- Tool keys must match the tool name configured in Agent Studio.

## Tool definition in Agent Studio

Register the tool in the Agent Studio dashboard under
**Tools > Client-side tools**.

Tool with no parameters (e.g. read the current user's data):

```json
{
  "type": "function",
  "function": {
    "name": "get_user_orders",
    "description": "Retrieves the user's order history with IDs, statuses, totals, dates, and item details.",
    "strict": true,
    "parameters": {
      "type": "object",
      "properties": {},
      "required": [],
      "additionalProperties": false
    }
  }
}
```

Tool with parameters:

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
        "productId": {
          "type": "string",
          "description": "The Algolia objectID of the product to add"
        },
        "quantity": {
          "type": ["integer", "null"],
          "description": "Number of items to add (defaults to 1)"
        }
      },
      "required": ["productId", "quantity"],
      "additionalProperties": false
    }
  }
}
```

Set `"strict": true` in production for reliable schema adherence. With strict
mode, ALL properties must appear in the `required` array, and optional fields
must use the union type `["type", "null"]` (as `quantity` does above).
