# Autocomplete-specific Anti-patterns

These are in addition to the [anti-patterns](../anti-patterns.md).

| Anti-pattern | Why it's wrong | What to do instead |
|---|---|---|
| Installing `@algolia/autocomplete-js` | Legacy standalone library, not the maintained path | Use the React InstantSearch autocomplete widget |
| Using `useHits` + `useSearchBox` to build autocomplete from scratch | Overengineered, misses built-in features | Use the autocomplete widget |
