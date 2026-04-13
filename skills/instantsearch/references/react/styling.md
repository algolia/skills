# Styling InstantSearch Widgets

Style widgets by writing CSS targeting `ais-*` selectors in the project's global stylesheet. Use the project's design tokens, colors, spacing, and typography.

## Finding class names

Grep `node_modules/react-instantsearch` for `ais-` to find the class names the widget renders. The naming convention is CamelCase (e.g., `ais-AutocompletePanel`, not `ais-Autocomplete-panel`). Do not guess.

## Tailwind v4

`ais-*` classes are rendered at runtime and won't be found in source templates. Tailwind v4 purges styles inside `@layer` directives for unknown classes, so place `ais-*` styles **outside of any `@layer`** in the global CSS file.

## Pattern-specific styling

Each pattern (e.g., autocomplete) has its own styling reference with specific CSS requirements. Always check the pattern's styling guide after following these steps.
