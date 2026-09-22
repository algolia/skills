---
title: Validate With a Query, and Claim Only What It Showed
impact: MEDIUM
impactDescription: an exit-zero command proves nothing, and a query that reaches an empty index proves access rather than working search — so the setup can be reported as done while the user's search still returns nothing
tags: validation, search, verification
---

## Validate With a Query, and Claim Only What It Showed

"The import command succeeded" and "search works" are different claims. Indexing is asynchronous, and the key that worked for the import is not the key the app will carry. Validate with the **search-only key** — `ALGOLIA_API_KEY` set to it deliberately, not left over from a write step. A query that only works with the write key means the app fails the moment it ships.

This phase is **read-only**. Query the index already chosen for this setup — the user's existing index, or the demo index if one was seeded; do not import a demo index to give yourself something to query. A search-only key is not guaranteed to carry the `listIndexes` ACL, so do not make listing a prerequisite for querying.

**Incorrect (treating a clean exit as proof):**

```bash
algolia objects import example_products -F example.ndjson
echo "Search is set up ✅"
```

No query ran, no key was tested, and without `-w` the import may not have finished.

**Correct:**

```bash
algolia search example_products -o json                      # general request: what is in there at all?
algolia search example_products --query "headphones" -o json # then a term you expect to match
```

### Say what the response actually showed

Read `nbHits` against the number of records you expect, and match the claim to it:

| Result | What you may claim |
| --- | --- |
| `nbHits` ≥ 1 and the hits are the expected records | This CLI query, with the search-only key, returned those records from that index. The app's own search is a separate check |
| The request **succeeded** with `nbHits` = 0 on an index that exists | The app ID, the search key and index access are good — nothing matched. Not "search works" |
| `nbHits` = 0 on an index you just seeded with `-w` | Something is wrong: wrong application, wrong index name, or a term absent from the data |
| The request **failed** | Nothing is proven, including access. Read the error before retrying |

A zero-hit response only demonstrates access when the request itself succeeded — an index-not-found error is not a zero-hit result. On a repair, the second row is a pass: the credentials were the problem and the query shows they are fixed. Do not seed records to turn a 0 into a 1.

Report the actual numbers — index name, `nbHits`, one matched record — and keep the claim to the CLI query that produced them. Do not describe the deployed application as working on the strength of a local query; that is a different verification, and running it is the user's call.

## Sources

- `algolia search --help` (Algolia CLI 1.17.0) — `--query`, `--hitsPerPage`, `-o/--output`, `--responseFields`
- `algolia objects import --help` (Algolia CLI 1.17.0) — `-w` waits for the operation to complete
- <https://www.algolia.com/doc/guides/security/api-keys/> — API key ACLs and per-index restrictions
