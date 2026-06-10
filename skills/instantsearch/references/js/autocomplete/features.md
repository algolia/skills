# Autocomplete (InstantSearch.js)

InstantSearch.js does not ship a dedicated autocomplete widget. The recommended path is **`@algolia/autocomplete-js`**, which is a separate UI library that integrates with `algoliasearch` v5. This is **not** an anti-pattern in vanilla JS (it is in React).

Before implementing, run the [Source-of-truth check](../source-of-truth.md) and confirm the recommended path against the live docs.

## Recommended path: `@algolia/autocomplete-js`

The pattern is:

1. Install `@algolia/autocomplete-js` and `algoliasearch` v5.
2. Create or pick a host element (selector or DOM node).
3. Call `autocomplete({ container, ... })` once.
4. Configure `getSources` to query the same Algolia index used elsewhere; reuse the module-level `searchClient`.

```ts
import { autocomplete } from "@algolia/autocomplete-js";
import { liteClient as algoliasearch } from "algoliasearch/lite";
import "@algolia/autocomplete-theme-classic";

const searchClient = algoliasearch(process.env.ALGOLIA_APP_ID!, process.env.ALGOLIA_API_KEY!);

const instance = autocomplete({
  container: "#autocomplete",
  placeholder: "Search...",
  getSources: () => [
    {
      sourceId: "products",
      getItems: ({ query }) =>
        searchClient.search({
          requests: [{ indexName: "YOUR_INDEX", query, hitsPerPage: 5 }],
        }).then((res) => res.results[0].hits),
      getItemUrl: ({ item }) => `/products/${item.objectID}`,
      templates: {
        item: ({ item, html }) => html`<a href="/products/${item.objectID}">${item.name}</a>`,
      },
    },
  ],
});
```

Confirm the `autocomplete` options shape (`getSources`, `templates`, `plugins`) and the `algoliasearch` v5 `search` method against installed types and the live docs before scaffolding. Both have evolved.

When the page is destroyed (SPA route change, panel teardown), call `instance.destroy()` to release listeners.

## Alternative: `searchBox` widget for non-autocomplete inputs

If the user wants a search input on a results page (no dropdown of suggestions), use the `searchBox` widget from `instantsearch.js/es/widgets`. This is not autocomplete; it's the search input for an InstantSearch widget tree. Don't confuse the two.

## Multiple sources, recent searches, query suggestions

Same building blocks as the React autocomplete: query suggestions index, recent-searches plugin, multi-source `getSources` array. Read `https://www.algolia.com/doc/ui-libraries/autocomplete/api-reference/autocomplete-js` for the up-to-date plugin and source APIs.

## Live docs

- Autocomplete-js getting started: `https://www.algolia.com/doc/ui-libraries/autocomplete/introduction/getting-started`
- API reference: `https://www.algolia.com/doc/ui-libraries/autocomplete/api-reference/autocomplete-js`
