# Styling InstantSearch.js Widgets

Style widgets by writing CSS targeting `ais-*` selectors in the project's global stylesheet. Use the project's design tokens. The class-name vocabulary matches React InstantSearch and Vue InstantSearch (all three packages share the rendering layer).

## Finding class names

```bash
rg -o 'ais-[A-Za-z]+(-[a-z]+)?' node_modules/instantsearch.js | sort -u
```

Names are CamelCase (e.g., `ais-Pagination-list`). Do not guess.

## Per-widget overrides via `cssClasses`

InstantSearch.js widgets accept a `cssClasses` option that adds custom classes alongside the defaults. Use it when the project has a CSS architecture (BEM, utility-first) that wants its own selectors:

```ts
refinementList({
  container: "#brand",
  attribute: "brand",
  cssClasses: {
    list: "my-refinement-list",
    item: "my-refinement-list__item",
  },
});
```

Read the widget's `.d.ts` for the keys accepted in `cssClasses`. They differ per widget.

## Per-widget overrides via `templates`

Widgets accept a `templates` option for custom HTML rendering. Templates can be strings, functions returning HTML strings, or `html` tagged-template helpers. When you replace a template, the inner DOM is yours; outer `ais-*` classes still apply for layout selectors.

```ts
hits({
  container: "#hits",
  templates: {
    item: (hit, { html, components }) =>
      html`<article><h3>${components.Highlight({ hit, attribute: "name" })}</h3></article>`,
  },
});
```

The `html` and `components` helpers come from the template render context. Read the widget's type for the exact signature in the installed version.

## Tailwind v4

`ais-*` classes are rendered at runtime. Place their CSS outside any `@layer` directive to avoid Tailwind v4 purging.

## Pattern-specific styling

This skill covers autocomplete only at the pattern level. For other patterns, run the source-of-truth check.
