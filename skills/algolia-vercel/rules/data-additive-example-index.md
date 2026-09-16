---
title: Import Example Data Additively, Into a New Index
impact: CONDITIONAL
impactDescription: clearing or reusing an index to make room for demo data destroys real records — and on a repair there is no reason to write at all
tags: data, import, safety
---

## Import Example Data Additively, Into a New Index

**First: does this phase apply at all?** Seed data only when the search the user asked for has nothing to run against. Skip it when:

- the request is a **repair** — the resource exists, the credentials never reached the machine, and the fix is the pull and the merge. Validate read-only against an index the application already has (`algolia indices list`).
- an index with records already exists and the user pointed at it. Query that one.
- the user asked to import *their* data. That is `algolia-cli`, not a demo index.

Seeding "to be thorough" on a repair leaves a stray `example_products` index on someone's application and bills its records. If it is genuinely unclear whether there is data to search, list the indices first and read the answer off that.

When it does apply: example data exists to prove the pipeline works, and it must not be able to damage anything.

A freshly provisioned application is empty, so this looks risk-free — but the same code path runs when the application turns out not to be fresh (a reconnected resource, a shared team application, a rerun). Reaching for `indices clear` or `indices delete` to get a clean slate is what turns a demo import into data loss.

**Incorrect (destructive prep, reused index name):**

```bash
algolia indices clear products -y            # wipes whatever was there
algolia objects import products -F demo.ndjson
```

`products` is the name a real catalog will want. Clearing it is unrecoverable without a backup, and there is no reason to touch it to demonstrate search.

**Correct (new name, additive import, explicit credentials):**

`$ALGOLIA_VERCEL_SKILL_DIR` is the absolute path of the directory containing this skill's `SKILL.md`, wherever it is installed — never a repo-relative `skills/…` path. `$STAGING` is the env file from the credentials phase. Both are set once; the working directory stays on the app.

```bash
# 1. Confirm the index name is unused — and whether any index already holds records,
#    which is the signal to skip this phase. Credentials come from the staged file,
#    parsed — see credentials-pull-without-clobbering.
node "$ALGOLIA_VERCEL_SKILL_DIR/scripts/with-algolia-env.mjs" "$STAGING" ALGOLIA_WRITE_API_KEY -- \
  algolia indices list

# 2. Write ndjson — one JSON object per line, NOT a JSON array
cat > example.ndjson <<'EOF'
{"objectID":"1","name":"Wireless Headphones","category":"Audio","price":129}
{"objectID":"2","name":"Mechanical Keyboard","category":"Input","price":89}
{"objectID":"3","name":"27-inch Monitor","category":"Displays","price":329}
EOF

# 3. Import into a name that cannot collide with real data
node "$ALGOLIA_VERCEL_SKILL_DIR/scripts/with-algolia-env.mjs" "$STAGING" ALGOLIA_WRITE_API_KEY -- \
  algolia objects import example_products -F example.ndjson -w
```

Details that bite:

- **ndjson, not JSON.** `objects import` takes one object per line. A `[...]` array fails.
- **`-w`** waits for indexing to finish. Without it the validation query in the next phase can run against an index that has not caught up and return zero hits.
- **`objectID`** is what makes a re-import an upsert instead of a duplicate. Include it, or pass `-a` to have the CLI generate IDs — but then a rerun creates duplicates.
- **No `-y` needed**, and none exists: `objects import` is non-interactive by design. Reach for `-y` only on genuinely destructive commands, which this phase should not be running.
- **Credentials from the pulled file.** `vercel env pull` writes a file and loads nothing; `$ALGOLIA_WRITE_API_KEY` is empty in the shell right after it. The helper parses that file and sets `ALGOLIA_APPLICATION_ID` / `ALGOLIA_API_KEY` for the child command, which the Algolia CLI reads ahead of flags and profiles — so no `algolia auth login` and no profile.

Tell the user the index name you created and that it is example data, so they know what to delete later.

## Sources

- `algolia objects import --help` (Algolia CLI 1.17.0) — ndjson requirement, `-F`, `-w`, `-a`; no `-y` flag
- `algolia indices clear --help` (Algolia CLI 1.17.0) — `-y/--confirm` exists here, which is the point
- `algolia-cli` skill — credential precedence (env vars > flags > profile), ndjson conventions
