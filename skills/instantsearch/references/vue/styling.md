# Styling Vue InstantSearch Widgets

Style widgets by writing CSS targeting `ais-*` selectors in the project's global stylesheet. Use the project's design tokens, colors, spacing, and typography. The class-name vocabulary is the same as React InstantSearch and InstantSearch.js because all three packages share `instantsearch.js`'s rendering layer.

## Finding class names

```bash
rg -o 'ais-[A-Za-z]+(-[a-z]+)?' node_modules/vue-instantsearch | sort -u
rg -o 'ais-[A-Za-z]+(-[a-z]+)?' node_modules/instantsearch.js | sort -u
```

Names are CamelCase (e.g., `ais-RefinementList-list`). Do not guess.

## Tailwind v4

`ais-*` classes are rendered at runtime and are not in source templates. Tailwind v4 purges unknown classes inside `@layer` directives, so place `ais-*` styles **outside any `@layer`** in the global CSS file.

## Slot-based styling

Vue InstantSearch widgets expose scoped slots that let you replace the rendered DOM. When you override a slot, the `ais-*` classes are no longer applied; you own the markup and the CSS. Pick one approach per widget:

- Default rendering with `ais-*` CSS targeting (preferred when the structure works).
- Slot override with custom DOM and your own classes (when the structure must change).

Do not mix: do not write CSS for `ais-*` classes that no longer render because you overrode the slot.

## Pattern-specific styling

Each pattern has its own styling reference. Phase 2 in this skill covers autocomplete only; for other patterns, run the source-of-truth check and consult the live Algolia docs.
