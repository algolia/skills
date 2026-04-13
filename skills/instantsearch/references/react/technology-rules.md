# Technology Rules (hard rules, no exceptions)

These rules apply to **all** React InstantSearch patterns, not just autocomplete.

## Always

- If `react-instantsearch` and `algoliasearch` are not already installed, install the latest versions and **wait for the install to complete** before proceeding. If using Next.js App Router, also install `react-instantsearch-nextjs`. Use the same package manager as the rest of the project (npm, yarn, pnpm, bun, etc.). If the project uses a CDN (e.g., jsDelivr with script tags), follow that pattern instead. Do not read types or import from packages until the install has finished. Do not fetch types from the web (unpkg, GitHub, etc.).
- Use `react-instantsearch` v7. Import from `react-instantsearch`, never from `react-instantsearch-dom`. **If using Next.js App Router**, use `InstantSearchNext` from `react-instantsearch-nextjs` instead of `<InstantSearch>`. The props are the same.
- **Place the `<InstantSearch>` (or `<InstantSearchNext>`) provider high in the component tree**. At the layout level, not wrapping a single widget. Other widgets (search results, facets, etc.) will need to be nested inside it later. Decouple the provider from any specific widget.
- Use `algoliasearch` v5 (the latest) to create the search client. Do not use older v4/v3 patterns. If already installed, check `package.json` for the version. The API changed between v4 and v5. If not installed, install the latest version. For web applications, prefer the lite client for a smaller bundle: `import { liteClient as algoliasearch } from "algoliasearch/lite";`
- **Declare the search client outside of React components.** The client's reference must remain stable to preserve its internal cache. Do not inline `algoliasearch(...)` inside the `searchClient` prop, and do not create it inside a component with `useCallback` or `useMemo` unless there is no alternative.
- Use `<Highlight>` on all displayed text attributes. Never render raw attribute strings. Use `<Snippet>` instead of `<Highlight>` for long text attributes (descriptions, body content) to avoid rendering full-length highlighted text. Always set `attributesToHighlight` and `attributesToSnippet` at query time to match the attributes you display. Do not rely on index settings, which may not be configured. For InstantSearch widgets, set them in `<Configure>`. For autocomplete, set them per index source in its search parameters.
- Use `<Configure>` to set `hitsPerPage` and any other index parameters.
- Prefer built-in widgets with CSS class names over custom connectors/hooks when the widget can achieve the desired result. Connectors add complexity. Use them only when a built-in widget genuinely cannot do what's needed.
- **Follow the [styling guide](styling.md) for all widget styling.** Write CSS targeting `ais-*` selectors. Grep for actual class names before writing CSS.
- Set `insights={true}` on the `<InstantSearch>` wrapper to enable click analytics via Algolia Insights.
- **Set up routing** so the search state is reflected in the URL. Search result URLs must be shareable and bookmarkable. Enable routing by passing `routing` or `routing={true}` on the `<InstantSearch>` (or `<InstantSearchNext>`) wrapper. For further customization, pass an object to `routing` where `router` accepts the same options as `history`, and `stateMapping` accepts the same options as in `InstantSearch`. Read the type definitions for full configuration options.

## Never

- **Never use v6 APIs.** Do not import from `react-instantsearch-dom`, do not use class-based connectors, do not use `connectSearchBox` or similar v6 patterns.
- **Never guess credentials or index names.** Always ask the user. Never silently use a public demo index.
- **Never start coding before completing discovery.** You need credentials, schema understanding, rendering preferences, and project design context first.
- **Never overuse connectors.** If you're reaching for `useSearchBox`, `useHits`, `useRefinementList` etc., first check whether the built-in widget with a `classNames` prop achieves the same result. Custom hooks/connectors are for genuinely custom rendering that widgets cannot handle.
