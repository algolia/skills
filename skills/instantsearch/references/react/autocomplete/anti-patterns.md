# Autocomplete-specific Anti-patterns

These are in addition to the [anti-patterns](../anti-patterns.md).

| Anti-pattern | Why it's wrong | What to do instead |
|---|---|---|
| Installing `@algolia/autocomplete-js` | A separate standalone library. It isn't deprecated, but in React InstantSearch the widget is the maintained autocomplete path | Use the React InstantSearch autocomplete widget |
| Importing `EXPERIMENTAL_Autocomplete` on react-instantsearch 7.41.0 or later | Deprecated alias (marked `@deprecated`; the npm builds don't print a warning) | Import `Autocomplete` |
| Using `useHits` + `useSearchBox` to build autocomplete from scratch | Overengineered, misses built-in features | Use the autocomplete widget |
