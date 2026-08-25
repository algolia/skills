# UI Library Selector

This reference is intentionally a living selector, not a copied docs dump. Use official docs for current APIs, install commands, imports, and version-specific behavior.

## Current Docs Index

Algolia exposes an LLM-friendly docs index:

- https://www.algolia.com/doc/llms.txt

Check this first when docs paths or names might have changed.

## Library Choice

### Full Search Or Browse UI

Use InstantSearch when building:

- Search results pages.
- Category or browse pages.
- Faceted navigation.
- Sort-by and replica-backed sort.
- Pagination or infinite hits.
- Current refinements.
- URL-synced search state.
- Search UI that needs click/conversion events.

Official docs:

- InstantSearch.js overview: https://www.algolia.com/doc/guides/building-search-ui/what-is-instantsearch/js
- InstantSearch.js install: https://www.algolia.com/doc/guides/building-search-ui/installation/js
- React InstantSearch install: https://www.algolia.com/doc/guides/building-search-ui/installation/react
- Vue InstantSearch install: https://www.algolia.com/doc/guides/building-search-ui/installation/vue
- Angular getting started (InstantSearch.js in Angular): https://www.algolia.com/doc/guides/building-search-ui/getting-started/angular

Angular note: `angular-instantsearch` is formally **deprecated** by Algolia — the npm
package carries a deprecation notice, its docs moved under `/doc/deprecated/`, and Algolia
has said it will not ship an Angular replacement. There is no successor package. For
Angular apps, use InstantSearch.js with connectors inside Angular services and components,
per the Angular getting-started guide above. Treat existing Angular InstantSearch code as a
migration candidate, not a target for new work. Migration guide:
https://www.algolia.com/blog/algolia/migrating-from-angular-instantsearch/

Caution when checking status: Algolia's marketing pages under `/developers` and `/products`
still present Angular as an available, maintained flavor. Confirm library status from npm
and `algolia.com/doc`, not from marketing pages.

Never recommend `react-instantsearch-dom` or `react-instantsearch-hooks-web`. Both are
deprecated in favour of `react-instantsearch`; npm redirects them and they stopped
receiving releases.
- InstantSearch events: https://www.algolia.com/doc/guides/building-search-ui/events/js
- React InstantSearch events: https://www.algolia.com/doc/guides/building-search-ui/events/react
- Vue InstantSearch events: https://www.algolia.com/doc/guides/building-search-ui/events/vue

### React And Next.js

Use React InstantSearch (`react-instantsearch`) for React apps. For Next.js or SSR, verify
current Next.js/SSR docs before coding.

Next.js App Router needs the dedicated `react-instantsearch-nextjs` package: swap
`<InstantSearch>` for `<InstantSearchNext>` (same props), keep the search component in its
own file rather than `page.tsx`, and mark it `"use client"`. Plain `react-instantsearch` is
not App-Router-SSR-ready on its own, and there is no React-Server-Component-native
InstantSearch — the widgets are client components by design. On the Pages Router the older
`getServerState` flow still applies.

Algolia documents a backend-search pattern (a custom `searchClient` proxying through your
own server) for security, SEO, or data-enrichment needs, but explicitly recommends
frontend search for latency and availability. There is no official guidance to drop
InstantSearch in favour of calling the API client directly.

Official docs:

- React InstantSearch getting started: https://www.algolia.com/doc/guides/building-search-ui/getting-started/react
- React routing: https://www.algolia.com/doc/guides/building-search-ui/going-further/routing-urls/react
- React SSR: https://www.algolia.com/doc/guides/building-search-ui/going-further/server-side-rendering/react
- React secured API keys: https://www.algolia.com/doc/guides/building-search-ui/going-further/api-keys-security/react
- InstantSearchNext API reference: https://www.algolia.com/doc/api-reference/widgets/instantsearch-next/react
- createInstantSearchRouterNext API reference: https://www.algolia.com/doc/api-reference/widgets/instantsearch-next-router/react

### Autocomplete And Typeahead

Use Autocomplete when the primary interaction is typing into a search box and showing suggestions before a full result page.

Good fits:

- Query suggestions.
- Recent searches.
- Popular searches.
- Product/content/category suggestions.
- Federated autocomplete.
- InstantSearch handoff from an input.
- Documentation/site search patterns.

Official docs:

- Autocomplete overview: https://www.algolia.com/doc/ui-libraries/autocomplete/introduction/what-is-autocomplete
- Autocomplete API reference: https://www.algolia.com/doc/api-reference/widgets/autocomplete/react
- InstantSearch autocomplete pattern JS: https://www.algolia.com/doc/guides/building-search-ui/ui-and-ux-patterns/autocomplete/js
- InstantSearch autocomplete pattern React: https://www.algolia.com/doc/guides/building-search-ui/ui-and-ux-patterns/autocomplete/react
- InstantSearch autocomplete pattern Vue: https://www.algolia.com/doc/guides/building-search-ui/ui-and-ux-patterns/autocomplete/vue

### Mobile And Native

Use native/mobile UI libraries when building mobile app search surfaces rather than forcing web InstantSearch patterns into native UI.

Official docs:

- InstantSearch Android API reference: https://www.algolia.com/doc/api-reference/widgets/android
- InstantSearch iOS API reference: https://www.algolia.com/doc/api-reference/widgets/ios
- Algolia for Flutter (Flutter Helper) API reference: https://www.algolia.com/doc/api-reference/widgets/flutter
- Android install: https://www.algolia.com/doc/guides/building-search-ui/installation/android
- iOS install: https://www.algolia.com/doc/guides/building-search-ui/installation/ios
- Flutter install: https://www.algolia.com/doc/guides/building-search-ui/installation/flutter
- Android events: https://www.algolia.com/doc/guides/building-search-ui/events/android
- iOS events: https://www.algolia.com/doc/guides/building-search-ui/events/ios
- Flutter events: https://www.algolia.com/doc/guides/building-search-ui/events/flutter

Flutter is not an InstantSearch flavor. `algolia_helper_flutter` supplies business-logic
helpers only, with no UI widgets — plan to build the UI yourself.

### Lower-Code And Newer Options

Check these before assuming a hand-built InstantSearch UI is the only path. Confirm current
status in official docs before recommending either, and do not make them the default.

- **Algolia SiteSearch** — a registry of copy-in components built on top of React
  InstantSearch, plus an Ask AI surface. Useful when the team wants a fast, good-looking
  starting point in React and is willing to own the copied code. Algolia labels it **beta**,
  and it has pinned older React InstantSearch versions in the past, so verify what it
  installs before committing. Docs: https://sitesearch.algolia.com/docs
- **Algolia Experiences** (`algolia-experiences`) — build the experience in the dashboard and
  embed it with a script tag and an experience ID. This is the genuine no-developer tier;
  reach for it when nobody will own frontend code.

Also relevant when scoping: **Compositions** change how queries are issued and carry hard
constraints — the `index` widget is unsupported and Composition calls cannot be mixed with
Search/Recommend calls on the same page. Verify current Composition docs before designing a
UI around it. DocSearch has moved well past v3, so confirm the current major before quoting
setup steps for documentation search.

There is no official Algolia web-components, Svelte, Astro, or Angular library. If a team
asks for one, the answer is InstantSearch.js with connectors.

## Selection Heuristics

- If the user needs search results plus facets, choose InstantSearch for the app framework.
- If the user needs suggestions while typing, choose Autocomplete and optionally integrate it with InstantSearch.
- If both are needed, use Autocomplete for entry and InstantSearch for results; define handoff behavior explicitly.
- If the app is server-rendered, verify SSR and routing docs before implementation.
- If the app must protect restricted records, review secured API key docs and index filters before exposing UI.
- If the search UI will drive analytics, personalization, Recommend, NeuralSearch evaluation, or Agent Studio feedback, wire events deliberately.

## QA Checklist

- Query, clear query, and no-query behavior.
- Filters, facets, sort, pagination or infinite hits.
- URL routing and browser back/forward when required.
- Empty, loading, and error states.
- Mobile filter/sort and autocomplete behavior.
- Keyboard navigation and accessible labels.
- Click/conversion events with queryID/objectID/position/userToken.
- Secured API keys and hidden filters for restricted content.
- Search request volume and performance.
- SSR hydration and route restoration when applicable.

## Related Skills

- `$algolia-instantsearch-ui`: full results and browse UI implementation.
- `$algolia-autocomplete`: typeahead and query suggestion implementation.
- `$algolia-events-insights`: event attribution and analytics.
- `$algolia-release-qa`: launch validation.
