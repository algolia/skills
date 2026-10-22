# Autocomplete (InstantSearch.js)

InstantSearch.js ships an **`autocomplete` widget**, exported from `instantsearch.js/es/widgets`. It is the recommended path for new builds. Algolia's Autocomplete docs say: "Prefer using the Autocomplete widget from InstantSearch instead of the standalone Autocomplete library."

**Versions:**
- **4.82.0** introduced the widget as `EXPERIMENTAL_autocomplete`.
- **4.108.0** made it stable as `autocomplete`.

`EXPERIMENTAL_autocomplete` remains as a deprecated alias. It is marked `@deprecated`, and its message, "EXPERIMENTAL_autocomplete is no longer experimental. Please use autocomplete instead.", is printed only by the development bundle. If the installed version is older than 4.108.0, prefer upgrading over using the experimental name.

The standalone library, `@algolia/autocomplete-js`, is **not** deprecated. It is still the right choice when the project:
- needs full control of the rendered DOM;
- needs sources that aren't Algolia indices, such as static links, user actions or other APIs;
- or already has a working autocomplete-js implementation.

See [Standalone alternative](#standalone-alternative-algoliaautocomplete-js) below.

Before implementing, run the [Source-of-truth check](../source-of-truth.md). Read `node_modules/instantsearch.js/es/widgets/autocomplete/autocomplete.d.ts` and the live widget reference, and confirm the options below against them.

## Recommended path: the `autocomplete` widget

The widget is an ordinary InstantSearch widget:

1. Install `instantsearch.js`, `algoliasearch` v5, and `instantsearch.css` for the theme.
2. Create the `searchClient` and the `instantsearch` instance once, at module scope.
3. Add `autocomplete({ container, ... })` with `search.addWidgets([...])`.
4. Call `search.start()` once.

```ts
import instantsearch from "instantsearch.js";
import { autocomplete } from "instantsearch.js/es/widgets";
import { liteClient as algoliasearch } from "algoliasearch/lite";
import "instantsearch.css/themes/satellite.css";

const searchClient = algoliasearch(process.env.ALGOLIA_APP_ID!, process.env.ALGOLIA_API_KEY!);

const search = instantsearch({ indexName: "YOUR_INDEX", searchClient });

search.addWidgets([
  autocomplete({
    container: "#autocomplete",
    placeholder: "Search...",
    showRecent: true,
    showQuerySuggestions: { indexName: "YOUR_QUERY_SUGGESTIONS_INDEX" },
    // On pages without results widgets, send chosen suggestions to the search route:
    // getSearchPageURL: (uiState) => `/search?query=${encodeURIComponent(uiState.query ?? "")}`,
    indices: [
      {
        indexName: "YOUR_INDEX",
        searchParameters: { hitsPerPage: 4 },
        getURL: (item) => `/products/${item.objectID}`,
        templates: {
          header: (_, { html }) => html`<span>Products</span>`,
          item: ({ item }, { html, components }) =>
            html`<${components.Highlight} hit=${item} attribute="name" />`,
        },
      },
    ],
  }),
]);

search.start();
```

Query Suggestions has no `getURL` here. Choosing a suggestion then sets the query in place, or goes through `getSearchPageURL`; see `onSelect` below. This example has no results widgets, so as written, choosing a suggestion or recent search only fills the input. On a page without a results page, set `getSearchPageURL` (the commented line) to the project's real search route. Only add `showQuerySuggestions.getURL` if the project has a search route that reads the query from the URL you build.

### What the options do

This list is not exhaustive. `autocomplete.d.ts` also covers prompt suggestions (`showPromptSuggestions`, which needs a chat widget), `aiMode`, `transformItems`, `translations`, `escapeHTML` and composition `feeds`.

**Rendering**

- **`container`**: where the widget renders. Pass an empty element, as a selector or a node. The widget renders its own input, an ARIA combobox with keyboard navigation, and its own panel. Don't pass an existing `<input>`.
- **`placeholder`**: the input's placeholder text.

**Sections**

- **`showQuerySuggestions`**: a Query Suggestions section, `{ indexName, getURL?, templates?, searchParameters?, cssClasses? }`. No plugin is needed. It shows 3 suggestions unless `searchParameters.hitsPerPage` says otherwise.
- **`showRecent`**: recent searches, saved in `localStorage`.
  - Pass `true` for the defaults (key `autocomplete-recent-searches`), or `{ storageKey?, templates?, cssClasses? }`.
  - The panel shows at most five, filtered to the saved searches that contain the text typed so far. The match is a case-sensitive substring.
- **Dedupe**: when `showRecent` and `showQuerySuggestions` are both set, the widget drops any suggestion whose text exactly matches a recent search currently shown. Don't hand-roll this.
- **`indices`**: one entry per results section: `{ indexName, searchParameters?, getURL?, getQuery?, onSelect?, templates?: { header, item, noResults }, cssClasses? }`.
  - **`getURL: (item) => string`**: where the item links to.
  - **`getQuery: (item) => string`**: the query to set when the item is chosen and has no URL. Without either, choosing the item sets the query to `''`. Give every `indices` entry a `getURL` or a `getQuery`.
- **`searchParameters`** (widget level): sent with every section's request, Query Suggestions included. It defaults to `{ hitsPerPage: 5 }`. A section's own `searchParameters` overrides it. Query Suggestions keep their own default of `hitsPerPage: 3`.

**Layout**

- **`templates.panel`**: controls the panel layout and the order of sections. It receives `({ elements, indices }, { html })`. `elements.recent`, `elements.suggestions` and `elements[indexName]` are the rendered sections.
  - Without it, the order is recent searches, then Query Suggestions, then each entry in `indices`. Prompt suggestions come last, if enabled.
- **`detachedMediaQuery`**: full-screen detached mode on small screens. The default is `"(max-width: 680px)"`, and `""` disables it.

**Selection**

- **`onSelect`**: overrides what happens when an item is chosen. By default:
  - If the item has a URL from `getURL`, the widget navigates to it.
  - Otherwise, if the index the widget was added to has no `hits` or `infiniteHits` widget and `getSearchPageURL` is set, it navigates to `getSearchPageURL(...)`. That function is called with the index's current UI state plus the chosen `query`.
  - Otherwise, it sets the query on the index the widget was added to, so results on that index update in place. It also saves the query as a recent search.
- **`getSearchPageURL`**: `(nextUiState) => string`, used by the default `onSelect` above.
- **Pressing Enter with no item highlighted** sets the query on the index the widget was added to. It does not call `onSelect` or `getSearchPageURL`. On a page without results widgets, such as a header on a product page, nothing navigates. If Enter must redirect to a search page, implement that explicitly and test it in a browser.

**Behavior**

- **`requiresSearch`**: set to `false` when the widget is the only widget on the page. The main search request is then skipped.
- **`autofocus`**: focuses the input and opens the panel on load.
- **Deferred queries**: the widget registers and queries its indices only when the input is first focused, so it sends no autocomplete requests at page load. (`autofocus` focuses it on load.) The main search request still runs unless `requiresSearch` is `false`. The panel opens on focus.
- **Empty panel**: the panel is hidden when every section, recent searches included, is empty, and no `noResults` template (on any section) and no `templates.panel` is set.

### Lifecycle

The widget belongs to the InstantSearch instance; there is no separate autocomplete instance to destroy. `autocomplete(...)` returns an array of widgets.
- **Remove only the autocomplete:** keep that return value and pass it to `search.removeWidgets(...)`. The other widgets stay mounted.
- **Full teardown:** on an SPA route change, call `search.dispose()`, which "Removes all widgets without triggering a search afterwards."

### Autocomplete and a results page together

When the page also has a results page, add `autocomplete` to the **same** `instantsearch` instance as the results widgets. Don't add a second `searchBox` over the same input.

The widget runs its own queries in an isolated index, so typing doesn't change the results. The results update when the query is set on the shared instance:
- by pressing Enter;
- by choosing a recent search;
- by choosing a suggestion, or an `indices` item that has a `getQuery` and no URL.

## Standalone alternative: `@algolia/autocomplete-js`

Use the standalone library only when the project needs full control of the rendered DOM, needs non-Algolia sources, or already runs autocomplete-js. Its rules differ from the widget's:

- Call `autocomplete({ container, getSources, ... })` from `@algolia/autocomplete-js` once. Keep the returned instance, and call `instance.destroy()` at teardown.
- Configure sources with `getSources` and plugins (`@algolia/autocomplete-plugin-query-suggestions`, `@algolia/autocomplete-plugin-recent-searches`).
- Style `aa-*` classes, not `ais-*`. See [styling.md](styling.md).
- Don't mix it with InstantSearch widgets over the same input.

Before scaffolding, confirm its options shape (`getSources`, `templates`, `plugins`) and the `algoliasearch` v5 `search` method against the installed types and the live docs.

## Not autocomplete: the `searchBox` widget

If the user wants a search input on a results page without a dropdown of suggestions, use the `searchBox` widget. Don't build an autocomplete out of `searchBox` + `hits`.

## Live docs

- Autocomplete widget (InstantSearch.js): `https://www.algolia.com/doc/api-reference/widgets/autocomplete/js`
- Which library to use: `https://www.algolia.com/doc/ui-libraries/autocomplete/introduction/what-is-autocomplete`
- Standalone autocomplete-js API reference: `https://www.algolia.com/doc/ui-libraries/autocomplete/api-reference/autocomplete-js`
