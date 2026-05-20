# Source of Truth (React)

Training data is stale and frequently wrong on prop shapes, renderState fields, future flags, and recently shipped widgets. Before using any widget, hook, connector, prop, middleware, or future flag that is **not explicitly documented in this skill**, complete the steps below in order. Do not skip and do not reorder.

## 1. Read installed types

The installed `react-instantsearch` types are the canonical source. They match the version actually running in the project, so they cannot drift.

```bash
ls node_modules/react-instantsearch/dist/es/index.d.ts \
   node_modules/react-instantsearch/dist/es/widgets \
   node_modules/react-instantsearch/dist/es/connectors \
   node_modules/react-instantsearch/dist/es/lib
```

What to read, by use case:

| You need to know                                  | Read                                                                                       |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `<InstantSearch>` / `<InstantSearchNext>` props   | `node_modules/react-instantsearch/dist/es/index.d.ts` (`InstantSearchProps`)               |
| Widget props (`<RefinementList>`, `<SortBy>`, ...) | `node_modules/react-instantsearch/dist/es/widgets/<WidgetName>.d.ts`                       |
| Hook return type / renderState                    | `node_modules/react-instantsearch/dist/es/connectors/use<ConnectorName>.d.ts`              |
| `useConnector` contract                           | `node_modules/react-instantsearch-core/dist/es/lib/useConnector.d.ts`                      |
| Connector contract (for custom widgets)           | `node_modules/instantsearch.js/es/connectors/<connector>/connect<Name>.d.ts`               |
| `future.*` flags                                  | `InstantSearchProps['future']` in `index.d.ts`, then the connected `InstantSearchOptions`  |
| Middleware contract                               | `node_modules/instantsearch.js/es/types/middleware.d.ts`                                   |
| SSR helpers                                       | `node_modules/react-instantsearch/dist/es/server/getServerState.d.ts` and `InstantSearchSSRProvider.d.ts` |

For Next.js App Router, also read `node_modules/react-instantsearch-nextjs/dist/es/InstantSearchNext.d.ts` for the props that differ from `<InstantSearch>`.

If a file path above does not match the installed package layout (the package may move things between minor versions), grep the package root:

```bash
rg -l "interface ${SymbolName}" node_modules/react-instantsearch
rg -l "type ${SymbolName}" node_modules/react-instantsearch
```

Read the type definition **before** writing the prop. Do not copy a prop from training data and assume it still exists.

## 2. Fetch the live Algolia docs

Live docs cover behavior, defaults, and recently shipped widgets that may not be in your training data. Use the canonical URL patterns:

| Topic                         | URL pattern                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------------ |
| Widget reference              | `https://www.algolia.com/doc/api-reference/widgets/<widget-slug>/react.md`                       |
| Hook / connector reference    | `https://www.algolia.com/doc/api-reference/widgets/<widget-slug>/react.md#hook`                  |
| Guides (concepts, patterns)   | `https://www.algolia.com/doc/guides/building-search-ui/<topic>/react.md`                         |
| Custom widgets                | `https://www.algolia.com/doc/guides/building-search-ui/widgets/create-your-own-widgets/react.md` |
| Routing                       | `https://www.algolia.com/doc/guides/building-search-ui/going-further/routing-urls/react.md`      |
| SSR                           | `https://www.algolia.com/doc/guides/building-search-ui/going-further/server-side-rendering/react.md` |
| Upgrade guides / future flags | `https://www.algolia.com/doc/guides/building-search-ui/upgrade-guides/react.md`                  |

Append `.md` to the URL so the agent fetches the markdown source instead of the rendered HTML page (saves tokens, no layout chrome).

The widget slug is the kebab-case form of the widget name: `<RefinementList>` -> `refinement-list`, `<HierarchicalMenu>` -> `hierarchical-menu`, `<CurrentRefinements>` -> `current-refinements`.

If the URL 404s, search `site:algolia.com/doc <widget>` as a fallback. Do not invent URLs.

## 3. Grep installed source for class names

For `ais-*` CSS class names you intend to style, follow [styling.md](styling.md). The same rule applies here: grep installed source, never guess.

## 4. Only then write code

If any step fails (offline, 404, missing types, ambiguous results), **stop and ask the user**. Do not guess prop names, renderState shapes, connector contracts, or future flag defaults. The cost of a wrong guess is silent runtime breakage, which is worse than a clarifying question.

When you do write the code, leave a brief comment above non-obvious props pointing to the type or doc URL you sourced them from, so reviewers can verify. Do not narrate the code, but do annotate provenance for anything beyond the documented baked patterns.
