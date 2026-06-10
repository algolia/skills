# Source of Truth (InstantSearch.js)

Training data is stale on widget options, connector contracts, and recently shipped APIs. Before using any widget, connector, middleware, or option that is **not explicitly documented in this skill**, complete the steps below in order.

## 1. Read installed types

```bash
ls node_modules/instantsearch.js/es \
   node_modules/instantsearch.js/es/widgets \
   node_modules/instantsearch.js/es/connectors \
   node_modules/instantsearch.js/es/lib \
   node_modules/instantsearch.js/es/types
```

What to read, by use case:

| You need to know                                  | Read                                                                                       |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `instantsearch(options)` options                  | `node_modules/instantsearch.js/es/lib/InstantSearch.d.ts` (or `index.d.ts`)               |
| Widget options (`refinementList`, `pagination`, ...)| `node_modules/instantsearch.js/es/widgets/<widget>/<widget>.d.ts`                          |
| Connector contract (custom widgets)               | `node_modules/instantsearch.js/es/connectors/<connector>/connect<Name>.d.ts`              |
| Middleware contract                               | `node_modules/instantsearch.js/es/types/middleware.d.ts`                                  |
| Routing types                                     | `node_modules/instantsearch.js/es/types/router.d.ts` and `lib/routers/history.d.ts`       |
| SSR helpers                                       | `node_modules/instantsearch.js/es/lib/server/getInitialResults.d.ts`                       |

If files have moved, grep:

```bash
rg -l "${SymbolName}" node_modules/instantsearch.js
```

## 2. Fetch the live Algolia docs

| Topic                       | URL pattern                                                                  |
| --------------------------- | ---------------------------------------------------------------------------- |
| Widget reference            | `https://www.algolia.com/doc/api-reference/widgets/<widget-slug>/js`         |
| Guides                      | `https://www.algolia.com/doc/guides/building-search-ui/<topic>/js`           |
| Custom widgets              | `https://www.algolia.com/doc/guides/building-search-ui/widgets/create-your-own-widgets/js` |
| Routing                     | `https://www.algolia.com/doc/guides/building-search-ui/going-further/routing-urls/js` |
| SSR                         | `https://www.algolia.com/doc/guides/building-search-ui/going-further/server-side-rendering/js` |

Widget slugs are kebab-case: `refinementList` (the JS factory) -> `refinement-list` (the URL).

## 3. Grep installed CSS for class names

```bash
rg -o 'ais-[A-Za-z]+(-[a-z]+)?' node_modules/instantsearch.js | sort -u
```

`ais-*` class names match the React and Vue packages. Names are CamelCase; do not guess.

## 4. Only then write code

If any step fails, stop and ask the user. Do not guess widget option names, connector return values, or routing types.
