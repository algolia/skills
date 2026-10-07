# Autocomplete Anti-patterns (InstantSearch.js)

These add to the [JS anti-patterns](../anti-patterns.md). The recommended path is the `autocomplete` widget from `instantsearch.js/es/widgets`; see [features.md](features.md). The second table applies only when the project deliberately uses the standalone `@algolia/autocomplete-js` library.

## With the `autocomplete` widget

| Anti-pattern | Why it's wrong | What to do instead |
| --- | --- | --- |
| Reaching for `@algolia/autocomplete-js` by default on a new build | Algolia's docs now prefer the InstantSearch widget, which integrates more closely with the search experience | Use `autocomplete` from `instantsearch.js/es/widgets`. Keep the standalone library for full DOM control or an existing implementation |
| Using `EXPERIMENTAL_autocomplete` on instantsearch.js 4.108.0 or later | Deprecated alias (marked `@deprecated`; only the development bundle prints the warning) | Import `autocomplete` |
| Building autocomplete with `searchBox` + `hits` and a custom dropdown | Reinvents the widget poorly and loses keyboard navigation, ARIA, detached mode and recent searches | Use the `autocomplete` widget |
| Adding a second `searchBox` over the same input as `autocomplete` | Two state owners on one input; flaky behavior | Let `autocomplete` own the input, on the same instance as the results widgets |
| Recreating the `instantsearch` instance or `searchClient` on every render | Loses the request cache, re-registers widgets and thrashes the network | Create both once at module scope and call `search.start()` once |
| Hand-deduping recent searches out of Query Suggestions | The widget already removes suggestions that match a recent search when `showRecent` and `showQuerySuggestions` are both set | Enable both options; don't filter manually |
| Looking for a `destroy()` on the widget at teardown | The widget has no separate instance; it belongs to InstantSearch | To remove only the autocomplete, pass the value `autocomplete(...)` returned to `search.removeWidgets(...)`; for full teardown, call `search.dispose()` |
| An `indices` entry with neither `getURL` nor `getQuery` | Choosing its item sets the query to `''` | Give every `indices` entry a `getURL`, a `getQuery`, or both |
| Expecting Enter to redirect to a search page | With no item highlighted, Enter only sets the query on the index the widget was added to; it doesn't call `onSelect` or `getSearchPageURL` | On pages without results widgets, implement the Enter-to-search-page behavior explicitly and test it in a browser |
| Guessing option names (`showRecent`, `showQuerySuggestions`, `indices`, `templates`) from training data | Option names and template signatures are easy to misremember | Read `node_modules/instantsearch.js/es/widgets/autocomplete/autocomplete.d.ts` and the live widget reference first |
| Styling `aa-*` classes on the widget | The widget renders `ais-Autocomplete*` classes, so `aa-*` selectors silently match nothing | Style `ais-*` classes; see [styling.md](styling.md) |

## Only if you use standalone `@algolia/autocomplete-js`

| Anti-pattern | Why it's wrong | What to do instead |
| --- | --- | --- |
| Forgetting `instance.destroy()` on SPA route change / teardown | Leaks DOM and event listeners; double-mount on hot reload causes duplicate panels | Save the `autocomplete(...)` return value and call `destroy()` at teardown |
| Recreating the `autocomplete(...)` instance on every reactive update | Tears down and rebuilds the dropdown; flicker | Mount once; update via `instance.setQuery`, `setActiveItemId`, or option closures |
| Guessing `getSources` shape from training data | The shape evolves; `getItems` return values, `templates`, plugin contracts change | Read installed `@algolia/autocomplete-js` types and the live doc before writing |
| Mixing `instantsearch({...})` widgets and `@algolia/autocomplete-js` over the same input | Two state owners on one input; flaky behavior | Pick one. For a new build, prefer the `autocomplete` widget |
| Styling `ais-*` classes when the rendered DOM is autocomplete-js (`aa-*`) | Selectors don't match; styles silently noop | Style `aa-*` classes for autocomplete-js panels |
