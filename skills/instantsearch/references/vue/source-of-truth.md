# Source of Truth (Vue)

Training data is stale on prop shapes, slot names, and recently shipped widgets. Before using any widget, slot, composable, or option that is **not explicitly documented in this skill**, complete the steps below in order.

## 1. Read installed types

```bash
ls node_modules/vue-instantsearch/vue3/es/src \
   node_modules/vue-instantsearch/vue3/es/src/components \
   node_modules/vue-instantsearch/vue3/es/src/util
```

What to read, by use case:

| You need to know                              | Read                                                                              |
| --------------------------------------------- | --------------------------------------------------------------------------------- |
| `<ais-instant-search>` props                  | `node_modules/vue-instantsearch/vue3/es/src/components/InstantSearch.*`           |
| Widget props (`<ais-refinement-list>`, ...)   | `node_modules/vue-instantsearch/vue3/es/src/components/<WidgetName>.*`            |
| Slot names and slot props                     | The widget's component file (`scopedSlots` / template `<slot>` definitions)        |
| Composable return type (`createServerRootMixin`, `createWidgetMixin`) | `node_modules/vue-instantsearch/vue3/es/src/util/*` and the connector's `connect<Name>.d.ts` from `instantsearch.js` |
| Connector contract                            | `node_modules/instantsearch.js/es/connectors/<connector>/connect<Name>.d.ts`      |
| Middleware contract                           | `node_modules/instantsearch.js/es/types/middleware.d.ts`                          |
| SSR helpers                                   | `node_modules/vue-instantsearch/vue3/es/src/util/createServerRootMixin.*`         |

If files have moved between minor versions, grep:

```bash
rg -l "${SymbolName}" node_modules/vue-instantsearch
```

Vue InstantSearch has separate entry points for Vue 2 and Vue 3 (`vue-instantsearch/vue2` and `vue-instantsearch/vue3`). Confirm which one the project uses by reading `package.json` and the import path in existing setup; the slot APIs differ.

## 2. Fetch the live Algolia docs

| Topic                       | URL pattern                                                                  |
| --------------------------- | ---------------------------------------------------------------------------- |
| Widget reference            | `https://www.algolia.com/doc/api-reference/widgets/<widget-slug>/vue`        |
| Guides                      | `https://www.algolia.com/doc/guides/building-search-ui/<topic>/vue`          |
| Custom widgets              | `https://www.algolia.com/doc/guides/building-search-ui/widgets/create-your-own-widgets/vue` |
| Routing                     | `https://www.algolia.com/doc/guides/building-search-ui/going-further/routing-urls/vue` |
| SSR                         | `https://www.algolia.com/doc/guides/building-search-ui/going-further/server-side-rendering/vue` |

Widget slugs are kebab-case: `<ais-refinement-list>` -> `refinement-list`.

## 3. Grep installed CSS for class names

```bash
rg -o 'ais-[A-Za-z]+(-[a-z]+)?' node_modules/vue-instantsearch | sort -u
rg -o 'ais-[A-Za-z]+(-[a-z]+)?' node_modules/instantsearch.js | sort -u
```

`ais-*` class names are shared across React, Vue, and JS InstantSearch packages, so React's grep results often translate. Verify per-widget.

## 4. Only then write code

If any step fails, stop and ask the user. Do not guess slot names, prop shapes, or composable return values.
