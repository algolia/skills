# Middleware (React)

Middleware is a low-level extension point on the InstantSearch instance. It is the right tool for a narrow set of cross-cutting concerns and the wrong tool for almost everything else. Read this before reaching for `addMiddlewares` or the `middleware` prop.

## When to use middleware

Use middleware only when **all** of these are true:

- The behavior is cross-cutting (touches every search, every state change, or the whole lifecycle), not a single widget concern.
- It cannot be expressed via `<Configure>`, `routing`, a widget prop, or `useInstantSearch()` in a small component.
- It needs to observe (and optionally react to) state changes, not just render.

Legitimate examples:

- **Custom analytics tagging** beyond what `insights={true}` covers (e.g., funnel events, A/B exposure, custom event names).
- **Syncing search state to a non-URL store** (e.g., a session-only Zustand store, a server-side log, a parent app's state machine).
- **Custom URL parameters** that `routing.stateMapping` cannot express (rare; try `stateMapping` first).
- **Instrumentation** for debugging (logging every state transition during development).

## When NOT to use middleware

The most common middleware misuses:

- **URL sync.** Use `routing` (or `routing={{ router, stateMapping }}`). Middleware that writes to `window.location` will fight `routing`.
- **Default refinements / default query.** Use `<Configure>` for index params (`filters`, `query`, `hitsPerPage`) or the refinement widget's default-selection prop. Do not push state via middleware on init.
- **Reacting to a single widget's state.** Use the widget's hook (`useRefinementList`, `useSortBy`) inside a small component. Middleware is too coarse.
- **Triggering side effects on hit clicks.** That is a render-time concern. Use the click handler in your `hitComponent` and call `sendEvent` from `useInsights()` if needed.
- **Replacing `routing` because the URL format isn't what you want.** Customize via `routing.stateMapping` first; that's exactly what it's for.

## Contract

Read the live, version-correct contract from the installed types: `node_modules/instantsearch.js/es/types/middleware.d.ts`. The signature is stable across recent releases but field names occasionally evolve, so check before writing one.

The shape is roughly:

```ts
type Middleware = (options: { instantSearchInstance: InstantSearch }) => {
  subscribe?: () => void;
  started?: () => void;
  unsubscribe?: () => void;
  onStateChange?: (params: { uiState: UiState }) => void;
};
```

Hook semantics:

- `subscribe` runs once when the middleware is registered. Set up listeners here.
- `started` runs after the InstantSearch instance starts. Safe to read `instantSearchInstance.status`.
- `onStateChange` runs on every UI-state transition. Keep it cheap. This is hot.
- `unsubscribe` runs when the middleware is removed or the instance is disposed. Clean up.

## Registering middleware in React

Use the `middleware` prop on `<InstantSearch>` / `<InstantSearchNext>`, or `useInstantSearch().addMiddlewares(...)` from a child component. Read the props type to confirm the exact name and accepted shape (an array of middleware factories) for the installed version.

When using `useInstantSearch().addMiddlewares` inside a component, return the unsubscribe function from `useEffect` to avoid duplicate registrations on rerenders.

## Pitfalls

- **Stale `uiState` reads.** `onStateChange` receives the current `uiState` as its argument. Do not read `instantSearchInstance.getUiState()` inside; the argument is what you want.
- **Synchronous heavy work in `onStateChange`.** Every refinement, query keystroke, and pagination click triggers it. Debounce or schedule with `queueMicrotask` for non-urgent work.
- **Middleware that mutates `uiState`.** Middleware is observational by default. To affect search, call `instantSearchInstance.setUiState(...)` or use widgets/hooks. Do not mutate the argument.
- **Middleware order.** Middleware runs in registration order. If two middlewares race on the same external store, the later registration wins per cycle. Keep them independent.
- **Forgetting `unsubscribe`.** Long-lived listeners (window events, intervals, store subscriptions) will leak across remounts if you do not return them in `unsubscribe`.

## Doc reference

For the canonical, version-correct guide, fetch `https://www.algolia.com/doc/api-reference/widgets/middleware/react`. Confirm any prop or method name there before shipping.
