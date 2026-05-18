# Autocomplete Styling (Vue)

Because the recommended path uses `@algolia/autocomplete-js`, styling targets `aa-*` classes (the autocomplete-js vocabulary), not `ais-*`. Verify by grepping:

```bash
rg -o 'aa-[A-Za-z]+' node_modules/@algolia/autocomplete-js | sort -u
rg -o 'aa-[A-Za-z]+' node_modules/@algolia/autocomplete-theme-classic | sort -u
```

Common targets: `aa-Autocomplete`, `aa-Form`, `aa-Input`, `aa-Panel`, `aa-PanelLayout`, `aa-Source`, `aa-SourceHeader`, `aa-Item`, `aa-ItemContent`. Names occasionally evolve; always grep first.

## Starting point: classic theme

Importing `@algolia/autocomplete-theme-classic` in the Vue component gives you a baseline. Override on top with the project's tokens; do not duplicate the theme.

## Layout invariants (for a custom theme)

- Panel positioned relative to the input; the library handles this when `container` is correct.
- Panel constrained with `max-height` and `overflow-y: auto` to prevent viewport overflow.
- Hover and keyboard-selected states styled on `aa-Item[aria-selected="true"]` so pointer and keyboard users see the same active item.

## Mobile / detached behavior

`@algolia/autocomplete-js` supports a detached mode via the `detachedMediaQuery` option (string media query). Set it to match the project's mobile breakpoint, then style the detached overlay:

```bash
rg -o 'aa-Detached[A-Za-z]*' node_modules/@algolia/autocomplete-js | sort -u
```

The shape mirrors the React InstantSearch detached overlay (full-screen container, sticky form area, scrollable panel). Reuse the structural rules from the [React autocomplete styling guide](../../react/autocomplete/styling.md), substituting `aa-*` selectors for `ais-Autocomplete*` selectors.

## Tailwind v4

Same rule as the rest of the skill: `aa-*` and `ais-*` classes are rendered at runtime. Place their CSS outside any `@layer` directive.
