---
title: Validate With a Query That Returns Hits
impact: REQUIRED
impactDescription: an exit-zero command proves nothing; only nbHits proves search works
tags: validation, search, verification
---

## Validate With a Query That Returns Hits

"The import command succeeded" and "search works" are different claims. Indexing is asynchronous, and the key that worked for the import is not the key the browser will use.

Validate with the **search-only key**. That is the credential the deployed app carries, so it is the one worth proving. A query that only works with the write key means the app will fail the moment it ships.

This phase is **read-only**, and on a repair it is the whole job: the credentials were the problem, so query an index the application already has and stop. Take the name from `algolia indices list` — do not import a demo index to give yourself something to query, and do not write anything to prove a read works.

**Incorrect (treating a clean exit as proof):**

```bash
algolia objects import example_products -F example.ndjson
echo "Search is set up ✅"
```

No query ran, no key was tested, and without `-w` the import may not even have finished.

**Correct (empty-query count, then a real term):**

`$ALGOLIA_VERCEL_SKILL_DIR` is the absolute path of the directory holding this skill's `SKILL.md` — wherever it is installed, not a repo-relative `skills/…` path. `$STAGING` is the env file from the credentials phase. `example_products` is the seeded index on a new setup; on a repair, substitute the existing index name.

```bash
# 1. Is anything in the index at all?
node "$ALGOLIA_VERCEL_SKILL_DIR/scripts/with-algolia-env.mjs" "$STAGING" ALGOLIA_SEARCH_API_KEY -- \
  algolia search example_products --query "" --hitsPerPage 3 --output json

# 2. Does a real term from the data match?
node "$ALGOLIA_VERCEL_SKILL_DIR/scripts/with-algolia-env.mjs" "$STAGING" ALGOLIA_SEARCH_API_KEY -- \
  algolia search example_products --query "headphones" --output json
```

The helper parses the pulled file and sets the credentials for that one command, so the search-only key is genuinely what was used — not whatever an earlier `export` left in the shell.

Read `nbHits` from the response. The phase passes only when the term query returns `nbHits` ≥ 1 **and** the hits are the records you imported.

If it does not pass, read what actually came back rather than retrying:

| What you got                                                   | Where to look                                                                 |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `Index example_products does not exist` (or a 404)             | The index name is wrong, or the import never ran — `algolia indices list`       |
| Empty query returns 0 hits on an index that exists             | The import is still in flight (it was run without `-w`), or it wrote to a different application — check the app ID the import used |
| Empty query has hits, the term query does not                  | The term is not in the data; pick one from the records you imported             |
| `Invalid Application-ID or API key`                            | App ID and key are from different applications, or a key was pasted into the wrong variable |
| `Method not allowed with this API key` / `Index not allowed with this API key` | The key's ACLs or its index restrictions do not cover this operation — inspect the key rather than assuming it is the wrong one |
| The write key works and the search key does not                 | Could be any of: the search key was never injected (`vercel env ls`), the resource is connected with a `--prefix` so the name differs, or the search key is restricted to other indices. Check which before concluding. |

Report the actual numbers — index name, `nbHits`, one matched record. Do not describe the *deployed* application as working on the strength of a local query: Vercel applies environment variables at build time, so the browser sees them only after the next deployment, and triggering one is the user's call.

Never claim an end-to-end verification you did not run.

## Sources

- `algolia search --help` (Algolia CLI 1.17.0) — `--query`, `--hitsPerPage`, `-o/--output`, `--responseFields`
- `algolia objects import --help` (Algolia CLI 1.17.0) — `-w` waits for the operation to complete
- https://www.algolia.com/doc/guides/security/api-keys/ — API key ACLs and per-index restrictions
- `vercel integration guide algolia --framework nextjs` — env vars are applied at build time; redeploy to pick them up
