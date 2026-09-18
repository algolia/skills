---
title: Import Example Data Additively, Into a New Index
impact: HIGH
impactDescription: clearing or reusing an existing index to make room for demo data can destroy real records, and demo data is usually not wanted at all
tags: data, import, safety
---

## Import Example Data Additively, Into a New Index

**First: does this phase apply at all?** Seed example data only when the search the user asked for has nothing to run against *and* they want a demo index. Skip it when:

- an index with records already exists. Query that one — `algolia indices list -o json` answers whether there is anything to search.
- the user asked to import *their* data. That is `algolia-cli`, not a demo index.
- the request is a repair — the credentials were the problem, so validate read-only against an index the application already has.

A freshly provisioned application being empty is not, on its own, a reason to write to it. Seeding "to be thorough" leaves a stray index on someone's application — so list the indices, read the answer off that, and offer the demo index rather than creating it unasked.

When it does apply, it must not be able to damage anything. Reaching for `indices clear` or `indices delete` to get a clean slate is what turns a demo import into data loss — and the same code path runs when the application turns out not to be fresh.

**Incorrect (destructive prep, reused index name):**

```bash
algolia indices clear products -y            # wipes whatever was there
algolia objects import products -F demo.ndjson
```

`products` is the name a real catalog will want. Clearing it is unrecoverable without a backup, and there is no reason to touch it to demonstrate search.

**Correct (new name, additive import).** Credentials are already configured for the Algolia CLI — see `credentials-write-key-never-reaches-the-browser` — with `ALGOLIA_API_KEY` holding the **write** key for this step:

```bash
algolia indices list -o json                                     # is there anything already?
algolia objects import example_products -F example.ndjson -w     # -F takes the user's file, or one you wrote
```

Read that listing before importing: if `example_products` is already there, it is someone else's index, so pick a demo name that is not in the list (`example_products_demo`, a suffix of your choosing) and import into that instead. The import is additive — it will merge into whatever it lands on.

`example.ndjson` is either a file the user already has or one you create first — the import does not invent it. ndjson means one JSON object per line, never a JSON array:

```
{"objectID":"1","name":"Wireless Headphones","category":"Audio","price":129}
{"objectID":"2","name":"Mechanical Keyboard","category":"Input","price":89}
```

- **`-w`** waits for indexing to finish. Without it the validation query can race the import and return zero hits.
- **`objectID`** makes a re-import an upsert instead of a duplicate. Include it, or pass `-a` to have IDs generated — but then a rerun duplicates.
- **No `-y`** exists on `objects import`: it is non-interactive by design. That flag belongs to destructive commands, which this phase does not run.
- **Say what you made.** Tell the user the index name and that it holds example data, so they know what to delete later.

## Sources

- `algolia objects import --help` (Algolia CLI 1.17.0) — ndjson requirement, `-F`, `-w`, `-a`; no `-y` flag
- `algolia indices clear --help` (Algolia CLI 1.17.0) — `-y/--confirm` exists here, which is the point
