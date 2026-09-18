---
title: Import Example Data Additively, Into a New Index
impact: HIGH
impactDescription: clearing or reusing an existing index to make room for demo data can destroy real records, and demo data is usually not wanted at all
tags: data, import, safety
---

## Import Example Data Additively, Into a New Index

**First: does this phase apply at all?** Seed example data only when the search the user asked for has nothing to run against, *and* they want a demo index. Skip it when:

- the request is a **repair** — the credentials never reached the machine, and the fix is the credentials phase. Validate read-only against an index the application already has (`algolia indices list`).
- an index with records already exists and the user pointed at it. Query that one.
- the user asked to import *their* data. That is `algolia-cli`, not a demo index.

A freshly provisioned application being empty is not, on its own, a reason to write to it. Seeding "to be thorough" leaves a stray `example_products` index on someone's application and bills its records. If it is unclear whether there is data to search, list the indices and read the answer off that; if there is none, offer the demo index rather than creating it unasked.

When it does apply: example data exists to prove the pipeline works, and it must not be able to damage anything. The same code path runs when the application turns out not to be fresh — a reconnected resource, a shared team application, a rerun. Reaching for `indices clear` or `indices delete` to get a clean slate is what turns a demo import into data loss.

**Incorrect (destructive prep, reused index name):**

```bash
algolia indices clear products -y            # wipes whatever was there
algolia objects import products -F demo.ndjson
```

`products` is the name a real catalog will want. Clearing it is unrecoverable without a backup, and there is no reason to touch it to demonstrate search.

**Correct (new name, additive import, credentials bridged inside `vercel env run`):**

The `sh -eu -c` block is the one from `credentials-run-with-vercel-env` — single-quoted, so the expansions happen in the child after `env run` has injected the variables. `-e development` is the environment the resource was connected with.

```bash
# 1. Does any index already hold records? That answer decides whether to run step 3 at all.
vercel env run -e development --scope acme-team -- sh -eu -c '
: "${ALGOLIA_APP_ID:?not injected — check: vercel env ls}"
: "${ALGOLIA_WRITE_API_KEY:?not injected — check: vercel env ls}"
export ALGOLIA_APPLICATION_ID="$ALGOLIA_APP_ID"
export ALGOLIA_API_KEY="$ALGOLIA_WRITE_API_KEY"
exec "$@"
' algolia-env algolia indices list

# 2. Write ndjson — one JSON object per line, NOT a JSON array
cat > example.ndjson <<'EOF'
{"objectID":"1","name":"Wireless Headphones","category":"Audio","price":129}
{"objectID":"2","name":"Mechanical Keyboard","category":"Input","price":89}
{"objectID":"3","name":"27-inch Monitor","category":"Displays","price":329}
EOF

# 3. Import into a name that cannot collide with real data
vercel env run -e development --scope acme-team -- sh -eu -c '
: "${ALGOLIA_APP_ID:?not injected — check: vercel env ls}"
: "${ALGOLIA_WRITE_API_KEY:?not injected — check: vercel env ls}"
export ALGOLIA_APPLICATION_ID="$ALGOLIA_APP_ID"
export ALGOLIA_API_KEY="$ALGOLIA_WRITE_API_KEY"
exec "$@"
' algolia-env algolia objects import example_products -F example.ndjson -w
```

Details that bite:

- **ndjson, not JSON.** `objects import` takes one object per line. A `[...]` array fails.
- **`-w`** waits for indexing to finish. Without it the validation query can run against an index that has not caught up and return zero hits.
- **`objectID`** is what makes a re-import an upsert instead of a duplicate. Include it, or pass `-a` to have the CLI generate IDs — but then a rerun creates duplicates.
- **No `-y` needed**, and none exists: `objects import` is non-interactive by design. Reach for `-y` only on genuinely destructive commands, which this phase should not be running.

Tell the user the index name you created and that it is example data, so they know what to delete later.

## Sources

- `algolia objects import --help` (Algolia CLI 1.17.0) — ndjson requirement, `-F`, `-w`, `-a`; no `-y` flag
- `algolia indices clear --help` (Algolia CLI 1.17.0) — `-y/--confirm` exists here, which is the point
- `algolia-cli` skill — credential precedence (env vars > flags > profile), ndjson conventions
