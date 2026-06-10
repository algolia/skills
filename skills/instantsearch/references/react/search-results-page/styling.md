# Search Results Page Styling

This covers results-page-specific layout. For the general approach, see the [styling guide](../styling.md). Always grep `node_modules` for actual `ais-*` class names before writing CSS; do not guess.

## Page-level layout

A typical results page has three regions: a header (search box, stats, sort), a refinements panel (sidebar on desktop, drawer on mobile), and a results column (hits + pagination). Use the host site's grid/flex tokens; the InstantSearch widgets do not impose a layout.

What matters at the layout level:

- The **refinements panel** should not collapse or overflow when refinement lists grow. Set a `max-height` with `overflow-y: auto` per panel section, and a sticky header above each panel.
- The **results column** should reserve a minimum height so a transition from "many results" to "few results" doesn't shift content.
- The **search box** should keep a visible focus state and match the autocomplete input from the rest of the site.

## Refinement panel

Each refinement widget renders a labeled list. Common targets:

- `ais-RefinementList` (root), `ais-RefinementList-list`, `ais-RefinementList-item`, `ais-RefinementList-label`, `ais-RefinementList-checkbox`, `ais-RefinementList-labelText`, `ais-RefinementList-count`, `ais-RefinementList-showMore`.
- `ais-HierarchicalMenu` follows the same shape, with nested `ais-HierarchicalMenu-list` for child levels.
- `ais-CurrentRefinements` renders chips: `ais-CurrentRefinements-list`, `ais-CurrentRefinements-item`, `ais-CurrentRefinements-label`, `ais-CurrentRefinements-category`, `ais-CurrentRefinements-categoryLabel`, `ais-CurrentRefinements-delete`.
- `ais-ClearRefinements-button`.

Verify all of these against the installed source before writing CSS. Names occasionally change.

Common rules:

- Hide the count when zero (`ais-RefinementList-count` with conditional styling) only if the design demands it.
- Style `:hover`, `:focus-visible`, and the checked state on `ais-RefinementList-checkbox` consistently.
- Reserve right padding on items so long labels do not collide with the count.

## Hits grid

`<Hits>` renders an `ais-Hits` root, an `ais-Hits-list`, and `ais-Hits-item` per hit. The list is a `<ol>` by default; style it with grid or flex on the host site's tokens. The hit component you provide is rendered inside `ais-Hits-item`; its inner DOM is yours.

For consistent height, set a fixed image aspect ratio on the hit image and clamp text lines (`-webkit-line-clamp` or the host's utility) on titles and descriptions.

## Pagination

`ais-Pagination`, `ais-Pagination-list`, `ais-Pagination-item`, `ais-Pagination-link`, plus modifier classes (`ais-Pagination-item--selected`, `ais-Pagination-item--disabled`, `ais-Pagination-item--firstPage`, `ais-Pagination-item--lastPage`, `ais-Pagination-item--previousPage`, `ais-Pagination-item--nextPage`, `ais-Pagination-item--page`).

Style the modifier classes explicitly. The `--selected` state must be visually distinct from hover.

## Mobile refinements drawer

The widgets do not ship a drawer. Common pattern:

1. Render the refinements panel inside a `<dialog>` or a custom modal component the project already has.
2. Toggle it via a "Filters" button shown only at the mobile breakpoint.
3. Inside the drawer, render the same refinement widgets you render on desktop. Do not duplicate `<InstantSearch>` providers.

If the project already has a drawer/sheet component, use it. Do not introduce a new modal pattern just for refinements.

## Sort and HitsPerPage

`ais-SortBy` and `ais-HitsPerPage` render a `<select>` plus optional label classes. Match the host site's form-control styling. If the design uses a custom dropdown menu (button + menu), use the corresponding hook (`useSortBy`, `useHitsPerPage`) and your menu component. See [custom-widgets.md](../custom-widgets.md).

## Tailwind v4 reminder

`ais-*` classes are not in source files; place their CSS outside any `@layer` directive. See [styling.md](../styling.md) for the full rule.

## Verification

Test at three states:

1. Empty query (no refinements, all hits visible).
2. Query with results (refinements collapsed/expanded, pagination visible).
3. Query with zero results (no-results component, refinements still navigable).

Do this at desktop and mobile breakpoints. Broken refinement layout often only shows up after several refinements are selected.
