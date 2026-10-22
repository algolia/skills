# Autocomplete Styling (InstantSearch.js)

## The `autocomplete` widget (recommended path)

The widget renders InstantSearch's own `ais-Autocomplete*` classes, not `aa-*`. Always grep the installed package for the real names before writing CSS:

```bash
rg -oh 'ais-Autocomplete[A-Za-z-]*' node_modules/instantsearch.js/es node_modules/instantsearch-ui-components/dist/es | sort -u
```

Grep both packages. The shared autocomplete components, including the panel, form, input, index lists and detached parts, live in `instantsearch-ui-components`. Grepping `instantsearch.js` alone misses most class names.

Examples include `ais-AutocompletePanel`, `ais-AutocompleteRecentSearches` and `ais-AutocompleteBackButton`. Names can evolve, so grep first.

To add your own class names, use the `cssClasses` option on each section: `indices[]`, `showRecent` and `showQuerySuggestions`. At the widget level, only `cssClasses.root` takes effect in instantsearch.js 4.119.0, so style the other parts with the `ais-Autocomplete*` selectors.

### Starting point: an InstantSearch theme

The `instantsearch.css` satellite theme (`instantsearch.css/themes/satellite.css`) includes the autocomplete component styles. Import it as a baseline, then override on top with the project's tokens rather than duplicating the theme.

### Mobile / detached behavior

The widget switches to a full-screen detached overlay when `detachedMediaQuery` matches. The default is `"(max-width: 680px)"`. Set it to the project's mobile breakpoint, or to `""` to disable it. The structure matches React InstantSearch's detached overlay, and the `ais-Autocomplete*` selectors are the same, so reuse the rules from the [React autocomplete styling guide](../../react/autocomplete/styling.md).

## Standalone `@algolia/autocomplete-js`

This section applies only if the project uses the standalone library. It renders `aa-*` classes:

```bash
rg -o 'aa-[A-Za-z]+' node_modules/@algolia/autocomplete-js | sort -u
rg -o 'aa-[A-Za-z]+' node_modules/@algolia/autocomplete-theme-classic | sort -u
```

Common targets: `aa-Autocomplete`, `aa-Form`, `aa-Input`, `aa-Panel`, `aa-PanelLayout`, `aa-Source`, `aa-SourceHeader`, `aa-Item`, `aa-ItemContent`, `aa-DetachedOverlay`, `aa-DetachedFormContainer` and `aa-DetachedContainer`. `@algolia/autocomplete-theme-classic` gives a baseline, and `detachedMediaQuery` controls detached mode here too.

## Layout invariants (either library)

- Constrain the panel with `max-height` and `overflow-y: auto` to avoid viewport overflow.
- Style hover and keyboard-selected items the same, so pointer and keyboard users see the same active item. Grep for the selected-state attribute or class the library renders.

## Tailwind v4

`ais-*` and `aa-*` classes are rendered at runtime. Place their CSS outside any `@layer` directive.
