# Search Results Page (React)

A search results page is the page users land on after submitting a query (from autocomplete, a header search box, or a deep link). It typically combines: a search input, a hits list, pagination, refinements (facets), sort, stats, and a no-results state. It is also the natural home for faceted search.

This file scaffolds the structural skeleton. **Prop details and any prop you have not used before must come from the [Source-of-truth check](../source-of-truth.md), not from this file.**

## Discovery (in addition to SKILL.md Discover step)

Confirm before scaffolding:

- **Route**: which URL renders this page? Verify it actually reads query params and renders dynamic results (not a static listing).
- **Refinement attributes**: which record fields should become facets? They must be in the index's `attributesForFaceting`. If the user is unsure, ask before adding refinement widgets to avoid a "facet is not configured" error at runtime.
- **Sort replicas**: does the index have replicas (e.g., `<index>_price_asc`, `<index>_price_desc`)? If yes, ask the user to confirm the replica names and labels for the sort dropdown. If no, do not add `<SortBy>` (or ask whether they want to set replicas up via the `algolia-cli` skill first).
- **Pagination vs. infinite scroll**: ask the user. Both are supported. Pagination is the default for shareable URLs; infinite scroll is common for catalog-style UX.
- **Empty/error states**: what should the page show when there are no hits, no query, or the network fails? Ask if not obvious from the design.
- **Mobile refinements**: how should refinements appear on mobile? Common pattern: drawer or modal, opened by a "Filters" button. Ask if the design isn't explicit.

## Canonical widget tree

This is the structural skeleton. Wire props from types and live docs.

```tsx
import {
  Configure,
  CurrentRefinements,
  ClearRefinements,
  HierarchicalMenu,
  Hits,
  HitsPerPage,
  Pagination,
  RangeInput,
  RefinementList,
  SearchBox,
  SortBy,
  Stats,
  ToggleRefinement,
  useInstantSearch,
} from "react-instantsearch";

function SearchResultsPage() {
  return (
    <>
      <Configure
        hitsPerPage={20}
        attributesToHighlight={["name", "brand"]}
        attributesToSnippet={["description:30"]}
      />
      <header>
        <SearchBox />
        <Stats />
        <HitsPerPage items={[/* read SortBy/HitsPerPage type for shape */]} />
        <SortBy items={[/* { label, value } pairs; value is the replica index name */]} />
      </header>

      <aside aria-label="Refinements">
        <CurrentRefinements />
        <ClearRefinements />
        <RefinementList attribute="brand" />
        <HierarchicalMenu attributes={["categories.lvl0", "categories.lvl1", "categories.lvl2"]} />
        <RangeInput attribute="price" />
        <ToggleRefinement attribute="free_shipping" label="Free shipping" />
      </aside>

      <main>
        <NoResultsBoundary fallback={<NoResults />}>
          <Hits hitComponent={Hit} />
          <Pagination />
        </NoResultsBoundary>
      </main>
    </>
  );
}

function NoResultsBoundary({ children, fallback }: { children: React.ReactNode; fallback: React.ReactNode }) {
  const { results } = useInstantSearch();
  if (!results.__isArtificial && results.nbHits === 0) {
    return <>{fallback}</>;
  }
  return <>{children}</>;
}

function NoResults() {
  const { indexUiState } = useInstantSearch();
  return <div>No results for &quot;{indexUiState.query}&quot;.</div>;
}

function Hit({ hit }: { hit: Record<string, unknown> & { objectID: string } }) {
  // Render with <Highlight attribute="name" hit={hit} /> per technology-rules.md
  return null;
}
```

The `<NoResultsBoundary>` shape is the version-stable pattern from the official guide. Confirm `useInstantSearch` return fields against installed types before destructuring.

## Refinement widgets: which one when

| Use case                              | Widget                                  | Notes                                                                                                |
| ------------------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Multi-select categorical filter       | `<RefinementList attribute="brand" />`  | For long lists, look up `searchable`, `searchablePlaceholder`, `limit`, `showMore`, `showMoreLimit`. |
| Single-select categorical filter      | `<Menu attribute="brand" />`            | Mutually exclusive selection. Often used with `transformItems` for ordering.                         |
| Hierarchical / nested categories      | `<HierarchicalMenu attributes={[...]} />` | Requires `lvl0/lvl1/lvl2` attributes in the records. Read the guide.                                  |
| Numeric range with input fields       | `<RangeInput attribute="price" />`      | Numeric attribute. Two inputs (min/max).                                                             |
| Numeric range with a slider           | (no built-in)                           | Use `useRange` and your component library's slider. Read [custom-widgets.md](../custom-widgets.md).  |
| Boolean toggle (free shipping, etc.)  | `<ToggleRefinement attribute="..." />`  | Toggles a single facet value on/off.                                                                 |
| Active-filter chips                   | `<CurrentRefinements />`                | Renders all active refinements as removable chips. Useful at the top of results.                     |
| Clear-all button                      | `<ClearRefinements />`                  | Pairs with `<CurrentRefinements />`. Look up `excludedAttributes` to keep some refinements pinned.   |

For every prop beyond `attribute` / `attributes`, **read the widget's `.d.ts`** before writing. Names and accepted shapes change across versions.

## Pagination vs. infinite scroll

Two mutually exclusive options:

- `<Pagination />`: shareable URL state per page. Default for results pages.
- `<InfiniteHits />`: replaces both `<Hits>` and `<Pagination>`. Loads more on scroll or on a "Load more" button. Read `<InfiniteHits>`'s `.d.ts` for `showPrevious`, `translations`, and how it interacts with `routing`.

Do not combine both.

## Sort

`<SortBy items={...} />` switches the active index between the primary and its replicas. The replicas must already exist on the Algolia side; this widget only chooses among them.

```tsx
<SortBy
  items={[
    { label: "Featured", value: "products" },
    { label: "Price (low to high)", value: "products_price_asc" },
    { label: "Price (high to low)", value: "products_price_desc" },
  ]}
/>
```

If replicas don't exist, do not fabricate them. Tell the user they need to be created first (point them to the `algolia-cli` skill).

## URL state, sharing, deep linking

`routing={true}` on the provider already syncs SearchBox query, refinements, page, and sort to the URL. Verify by changing a refinement and reloading; state should persist.

For custom URL formats (e.g., `/search/brand/nike` rather than `?brand=nike`), pass `routing={{ router, stateMapping }}` and read both types. This is non-trivial; consult the live [Routing guide](https://www.algolia.com/doc/guides/building-search-ui/going-further/routing-urls/react) before scaffolding.

## Multi-index results pages

If the page shows results from more than one index (e.g., products + articles), nest `<Index indexName="...">` blocks. Each index gets its own `<Configure>`, refinements, hits, and pagination, scoped to that index.

```tsx
<InstantSearch searchClient={searchClient} indexName="products" routing insights>
  <Configure hitsPerPage={20} />
  <SearchBox />

  <Index indexName="products">
    <Configure hitsPerPage={20} />
    <Hits hitComponent={ProductHit} />
    <Pagination />
  </Index>

  <Index indexName="articles">
    <Configure hitsPerPage={5} />
    <Hits hitComponent={ArticleHit} />
  </Index>
</InstantSearch>
```

Refinement widgets target the **enclosing index**. Putting `<RefinementList attribute="brand">` outside any `<Index>` refines the root index; putting it inside `<Index indexName="products">` refines only that one.

## Features checklist

Consider each. Include when the index and use case support it:

- [ ] `<Configure>` sets `hitsPerPage`, `attributesToHighlight`, `attributesToSnippet`
- [ ] `<SearchBox>` (or wired to autocomplete that submits here)
- [ ] `<Stats>` for "X results in Y ms"
- [ ] `<Hits>` (or `<InfiniteHits>`) with a typed `hitComponent` using `<Highlight>` / `<Snippet>`
- [ ] `<Pagination>` (or `<InfiniteHits>`, not both)
- [ ] `<CurrentRefinements>` + `<ClearRefinements>`
- [ ] One or more refinement widgets matching the index's `attributesForFaceting`
- [ ] `<SortBy>` if replicas exist
- [ ] `<HitsPerPage>` if the design needs it
- [ ] No-results boundary with a helpful message
- [ ] Mobile refinement drawer / modal
- [ ] `routing={true}` and `insights={true}` on the provider
- [ ] SSR if the framework supports it (see [ssr.md](../ssr.md))

For pattern-specific styling, see [styling.md](styling.md). For pattern-specific anti-patterns, see [anti-patterns.md](anti-patterns.md).
