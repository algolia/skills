# Custom Widgets (React)

This file is for the cases the built-in widgets genuinely cannot do. Most "custom widget" instincts are wrong: a built-in widget plus `classNames` plus a small `transformItems` callback covers the large majority of real designs.

## Decide first: do you actually need a custom widget?

Walk this checklist before reaching for `useConnector` / `useXxx`. If any of these resolves the problem, do not write a custom widget.

- Is the issue purely visual? Use the widget's `classNames` prop and write `ais-*` CSS. See [styling.md](styling.md).
- Do you need to filter, reorder, or annotate items? Use the widget's `transformItems` (most refinement widgets accept it). Read the widget's `.d.ts` for the exact signature.
- Do you need a different DOM wrapper? Use the widget's `classNames` plus normal CSS, or wrap the widget in your own component. The widget's children DOM is supported via class targeting.
- Do you need a non-default rendering for `Hits` items only? Use `<Hits>`'s `hitComponent` / `itemComponent` prop. Don't reach for `useHits` for this.
- Do you need to render a refinement widget you've never used before? Run the [Source-of-truth check](source-of-truth.md) first; most "missing" features are existing props you didn't know about.

If none of the above applies, you have a real custom-widget case. Continue.

## When custom widgets are justified

- Genuinely custom interaction (e.g., a 2D color/refinement picker, a map-based geo refiner, a slider that snaps to non-numeric values).
- Composite UI that needs state from multiple connectors at once and where rendering them as separate widgets would split the layout.
- Headless contexts (e.g., rendering refinements inside a third-party component library that takes data, not children).
- Programmatic search-state inspection that has no widget equivalent (read-only `useInstantSearch()` is the answer here, not a new widget).

## The contract

There are two paths. Pick based on the API surface available.

### Path A: `useXxx` hook (preferred when one exists)

`react-instantsearch` ships a hook for every connector: `useSearchBox`, `useHits`, `useRefinementList`, `useHierarchicalMenu`, `useRange`, `usePagination`, `useSortBy`, `useStats`, `useToggleRefinement`, `useCurrentRefinements`, `useClearRefinements`, `useConfigure`, `useInstantSearch`, and so on.

Workflow:

1. Read the hook's `.d.ts` from `node_modules/react-instantsearch/dist/es/connectors/use<Name>.d.ts` to learn the **arguments** (connector params) and the **return type** (renderState).
2. Call the hook inside a component nested under `<InstantSearch>` / `<InstantSearchNext>`.
3. Render whatever you want from the returned state. Forward `classNames`, refs, accessibility attributes manually if you want them.

Do **not** assume field names. The return type is the source of truth. Names like `items`, `refine`, `currentRefinement`, `canRefine`, `isShowingMore`, `toggleShowMore` exist on some connectors and not others.

### Path B: `useConnector(connector, params)` (when there is no React hook)

Use this when you need a connector exposed by `instantsearch.js` that does not yet have a dedicated React hook, or when you are wrapping a custom connector you wrote yourself.

```ts
import { useConnector } from "react-instantsearch";
import connectFoo from "instantsearch.js/es/connectors/foo/connectFoo";
import type {
  FooConnectorParams,
  FooWidgetDescription,
} from "instantsearch.js/es/connectors/foo/connectFoo";

export function useFoo(params: FooConnectorParams) {
  return useConnector<FooConnectorParams, FooWidgetDescription>(connectFoo, params);
}
```

The two type parameters come from the connector's `.d.ts`. Read that file before writing the wrapper. The shape returned is the connector's renderState type, minus the lifecycle plumbing (`init`, `render`, etc., are handled by `useConnector`).

For the official guide, read `https://www.algolia.com/doc/guides/building-search-ui/widgets/create-your-own-widgets/react`.

## Common pitfalls

- **Stale state in event handlers.** Refinement callbacks (`refine`) returned from a hook are stable across renders, but values you destructure (`currentRefinement`, `items`) are not. Read them inside the handler or via a ref if you need the latest.
- **Re-render storms.** A custom widget that calls `refine` on every keystroke without debouncing will trigger a search per keystroke. For typed inputs, debounce or use `<SearchBox>`'s `queryHook` prop.
- **Lost accessibility.** Built-in widgets render correct ARIA semantics. Custom widgets do not. Add `role`, `aria-*`, keyboard handlers explicitly.
- **Multiple instances of the same connector with conflicting params.** Calling `useRefinementList({ attribute: "brand", limit: 10 })` and `useRefinementList({ attribute: "brand", limit: 20 })` in two components creates two virtual widgets that will fight. Use one source of truth, or accept that only the first registered params win.
- **Reading `useInstantSearch().renderState` for a connector you didn't mount.** `renderState` only contains entries for connectors actually mounted in the tree (via widgets or hooks). If your connector isn't mounted, the renderState entry will be missing. Mount the hook (even in a hidden component) or use the connector directly.

## Do not

- Do not re-implement `<Pagination>`, `<RefinementList>`, `<SortBy>`, `<HierarchicalMenu>`, `<RangeInput>`, `<CurrentRefinements>`, or `<ClearRefinements>` from `useHits` + `useState`. Each has a dedicated hook with the right state.
- Do not subclass or extend the InstantSearch widgets. They are not designed for inheritance.
- Do not reach into `instantsearch.js`'s internals from a React component. Stay at the connector / hook layer.
