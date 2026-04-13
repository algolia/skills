# Anti-patterns

These apply across **all** React InstantSearch patterns. They supplement the technology rules. If something is already covered there, it's not repeated here.

If you catch yourself doing any of these, stop and reconsider:

| Anti-pattern                                                                               | Why it's wrong                                                         | What to do instead                                                                 |
| ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Using `<InstantSearch>` in a Next.js App Router project                                    | Missing SSR/RSC integration                                            | Use `<InstantSearchNext>` from `react-instantsearch-nextjs`                        |
| Using `react-instantsearch-router-nextjs` with App Router                                  | Requires Pages Router's `singletonRouter`                              | Use the `routing` prop on `<InstantSearchNext>` directly                           |
| Building search with `algoliasearch` client directly                                       | Bypasses the widget tree and state management                          | Use InstantSearch widgets                                                          |
| Hardcoding an index name like `instant_search`                                             | Likely a demo index from training data                                 | Ask the user                                                                       |
| Styling widgets with arbitrary selectors (tag names, positional selectors, generated classes) | Brittle, breaks on updates                                             | Write CSS targeting `ais-*` selectors. See the styling guide                       |
| Guessing `ais-*` class names without checking                                              | Names are CamelCase and easy to get wrong. Broken styles with no error | Grep `node_modules/react-instantsearch` for actual class names before writing CSS  |
