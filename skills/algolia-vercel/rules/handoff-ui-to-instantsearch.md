---
title: Carry the UI Work Into InstantSearch, Don't Stop at the Query
impact: EXIT
impactDescription: ending the turn at a validated query leaves the user's actual request unfinished — but building UI nobody asked for is its own defect
tags: handoff, ui, instantsearch
---

## Carry the UI Work Into InstantSearch, Don't Stop at the Query

**This phase runs when UI was part of the ask.** "Put a search box on the products page" reaches it; "my env vars are undefined locally" does not. On a repair, the exit is the validated query plus a one-line report of what was wrong — do not volunteer a search component, and do not offer to build one at length.

When UI *was* asked for: a validated query is where *this* skill's guidance ends. It is not where the task ends. Someone who asked for a search box asked for a search box; "search is working, next you should use the instantsearch skill" hands them back their own request.

So: load `instantsearch` and keep going. It carries the current widget APIs, the framework-specific references, and the anti-patterns, which is exactly what improvising the UI gets wrong.

**Incorrect (stopping short of what was asked):**

> I've provisioned Algolia, loaded 3 example records into `example_products`, and confirmed the search returns hits. To build the search UI, you'll want to use the `instantsearch` skill next. Let me know if you need anything else!

The user asked for search in their app. Nothing was built. The turn ends with a homework assignment.

**Correct (hand the context over and continue):**

If `instantsearch` is not available in this session, say so and give the command — once:

```bash
npx skills add algolia/skills --skill instantsearch
```

Then carry the work forward with the context it needs, so it can skip its own credentials questions and go straight to the record shape:

- **Index:** `example_products` (or the existing index the validation query ran against)
- **Record shape:** `objectID`, `name`, `category`, `price` (3 example records)
- **App ID:** in `NEXT_PUBLIC_ALGOLIA_APP_ID` (merged into `.env.local`)
- **Search-only key:** in `NEXT_PUBLIC_ALGOLIA_SEARCH_API_KEY` — the browser-safe one
- **Write key:** `ALGOLIA_WRITE_API_KEY`, server-side only, not for the UI

Pass the variable names, not the values. The UI reads them through `process.env`; nothing needs a key pasted into the transcript.

There is nothing wrong with the markup InstantSearch produces for a first pass:

```jsx
<InstantSearch searchClient={client} indexName="example_products">
  <SearchBox />
  <Hits hitComponent={({ hit }) => <div>{hit.name}</div>} />
</InstantSearch>
```

That is a reasonable starting point — but write it from the `instantsearch` guidance and the installed package version, not from memory, and let that skill drive provider placement, routing, SSR, and styling.

Two things to say once the UI exists: the index holds **example data** under a name the user can delete, and the deployed app only sees the new environment variables after its next deployment.

Other exits from this phase:

| The user wants                                      | Skill                        | Install                                                      |
| --------------------------------------------------- | ---------------------------- | ------------------------------------------------------------ |
| Real records, settings, synonyms, rules, API keys   | `algolia-cli`                | `npx skills add algolia/skills --skill algolia-cli`          |
| Their site crawled into the index                   | `algolia-crawler`            | `npx skills add algolia/skills --skill algolia-crawler`      |
| A full implementation plan                          | `algolia-discovery-planning` | `npx skills add algolia/skills --skill algolia-discovery-planning` |
| Read-only search and analytics                      | `algolia-mcp`                | `npx skills add algolia/skills --skill algolia-mcp`          |

If the Vercel integration enabled the Crawler (`-m crawler=true`), say which index it populates and that its records arrive on its own schedule — do not wait on it to validate this phase.

## Sources

- `vercel integration guide algolia --framework nextjs` — points at InstantSearch for the UI layer
- https://www.algolia.com/doc/guides/building-search-ui/what-is-instantsearch/react/
