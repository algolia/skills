---
title: Validate With a Query, and Claim Only What It Showed
impact: MEDIUM
impactDescription: an exit-zero command proves nothing, and a query that reaches an empty index proves access rather than working search — so the setup can be reported as done while the user's search still returns nothing
tags: validation, search, verification
---

## Validate With a Query, and Claim Only What It Showed

"The import command succeeded" and "search works" are different claims. Indexing is asynchronous, and the key that worked for the import is not the key the browser will use.

Validate with the **search-only key**. That is the credential the deployed app carries, so it is the one worth proving. A query that only works with the write key means the app will fail the moment it ships.

This phase is **read-only**. On a repair it is the whole job: query an index the application already has, take the name from `algolia indices list`, and stop. Do not import a demo index to give yourself something to query.

**Incorrect (treating a clean exit as proof):**

```bash
algolia objects import example_products -F example.ndjson
echo "Search is set up ✅"
```

No query ran, no key was tested, and without `-w` the import may not even have finished.

**Correct (search key, bridged inside `vercel env run`):**

Same single-quoted block as `credentials-run-with-vercel-env`, with `ALGOLIA_SEARCH_API_KEY` in place of the write key. `example_products` is the seeded index on a new setup; on a repair, substitute the existing index name.

```bash
vercel env run -e development --scope acme-team -- sh -eu -c '
: "${ALGOLIA_APP_ID:?not injected — check: vercel env ls}"
: "${ALGOLIA_SEARCH_API_KEY:?not injected — check: vercel env ls}"
export ALGOLIA_APPLICATION_ID="$ALGOLIA_APP_ID"
export ALGOLIA_API_KEY="$ALGOLIA_SEARCH_API_KEY"
exec "$@"
' algolia-env algolia search example_products --query "headphones" --output json
```

Naming the key variable explicitly inside the block is what makes the *search-only* slot deliberate, rather than inheriting whatever an earlier `export ALGOLIA_API_KEY=…` left behind. It does not guarantee the value came from Vercel: a stale `ALGOLIA_SEARCH_API_KEY` in your shell or a local `.env` file still wins over the fetched one — see `credentials-run-with-vercel-env`.

### Say what the response actually showed

Read `nbHits`, and match the claim to it:

| Result | What you may claim |
| --- | --- |
| Term query returns `nbHits` ≥ 1 and the hits are the expected records | This CLI query, with the search-only key, returned those records from that index. Verifying the app's own search — in the UI, or on the deployed site — is a separate step |
| Query succeeds with `nbHits` = 0 against an index that exists | The app ID, the search key and index access are good — the index has nothing matching. Not "search works" |
| Query succeeds with `nbHits` = 0 against an index you just seeded with `-w` | Something is wrong: wrong application, wrong index name, or a term absent from the data |

On a **new setup with seeded data**, the phase passes only on the first row. On a **repair**, the second row is a pass: the credentials were the problem and the query shows they are fixed. Report it as that, and do not seed records to turn a 0 into a 1.

If it does not pass, read what came back rather than retrying:

| What you got                                                   | Where to look                                                                 |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `Index example_products does not exist` (or a 404)             | The index name is wrong, or the import never ran — `algolia indices list`       |
| Empty query returns 0 hits on an index that exists             | The import is still in flight (run without `-w`), or it wrote to a different application — check the app ID the import used |
| Empty query has hits, the term query does not                  | The term is not in the data; pick one from the records                          |
| `Invalid Application-ID or API key`                            | App ID and key are from different applications, or a key was pasted into the wrong variable |
| `Method not allowed with this API key` / `Index not allowed with this API key` | The key's ACLs or its index restrictions do not cover this operation — inspect the key rather than assuming it is the wrong one |
| The write key works and the search key does not                 | Could be any of: the search key was never injected (`vercel env ls`), the resource is connected with a `--prefix` so the name differs, or the search key is restricted to other indices. Check which before concluding. |

Report the actual numbers — index name, `nbHits`, one matched record — and keep the claim to the CLI query that produced them. Do not describe the *deployed* application as working on the strength of a local query: the browser-public variables are embedded into the client bundle at build time, so a deployed site serves whatever its last build baked in until it is rebuilt, and triggering that is the user's call.

Never claim an end-to-end verification you did not run.

## Sources

- `algolia search --help` (Algolia CLI 1.17.0) — `--query`, `--hitsPerPage`, `-o/--output`, `--responseFields`
- `algolia objects import --help` (Algolia CLI 1.17.0) — `-w` waits for the operation to complete
- https://www.algolia.com/doc/guides/security/api-keys/ — API key ACLs and per-index restrictions
- `vercel integration guide algolia --framework nextjs` — env vars are applied at build time; redeploy to pick them up
