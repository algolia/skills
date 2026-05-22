---
name: algolia-migration
description: >-
  Migrate existing Algolia API client code to a newer major version.
  Triggers on: upgrading algoliasearch, moving from initIndex to client methods,
  fixing "initIndex is not a function", updating imports after a version bump,
  handling breaking changes from v3→v4 or v4→v5, replacing .wait() chaining,
  or any mention of "migrate Algolia client", "upgrade Algolia SDK", or a
  specific old-to-new version (e.g. "Python v3 to v4", "JS v4 to v5").
  Covers JavaScript, Python, Go, PHP, Java, C#, Ruby, Kotlin, Scala, Swift. Dart is a new client, doesn't need migration and is therefore excluded from the scope of this skill.
  Do NOT use for new project setup (use algolia-cli or algolia-mcp instead),
  InstantSearch / frontend frameworks, analytics queries, or recommendations.
license: MIT
metadata:
  author: algolia
  version: "1.0"
---

# Algolia API Client Migration

> This skill covers **API client upgrades** (backend and frontend search-only builds).
> For frontend search UI, see **instantsearch**. For index operations, see **algolia-cli**.

## Supported migrations

| Language   | Migration    | Reference |
|------------|--------------|-----------|
| JavaScript | v4 → v5      | [references/javascript.md](references/javascript.md) |
| Python     | v3 → v4      | [references/python.md](references/python.md) |
| Go         | v3 → v4      | [references/go.md](references/go.md) |
| PHP        | v3 → v4      | [references/php.md](references/php.md) |
| Java       | v3 → v4      | [references/java.md](references/java.md) |
| C#         | v6 → v7      | [references/csharp.md](references/csharp.md) |
| Ruby       | v2 → v3      | [references/ruby.md](references/ruby.md) |
| Kotlin     | v2 → v3      | [references/kotlin.md](references/kotlin.md) |
| Scala      | v1 → v2      | [references/scala.md](references/scala.md) |
| Swift      | v8 → v9      | [references/swift.md](references/swift.md) |
| Dart       | new client   | Unsupported |

Open the matching reference file before writing any migration code.

## Universal breaking changes

Every language migration shares the same set of architectural shifts. Understand these first; the reference files add language-specific syntax on top.

### 1. `initIndex` is gone

The index object pattern is eliminated in every language. All methods moved to the **client** with `indexName` as an explicit parameter.

**The fix:** remove `initIndex` / `init_index` / `index(withName:)`, call the method on the client, pass `indexName`.

**Grep to find all affected call sites:**
```
grep -r "initIndex\|init_index\|InitIndex\|index(withName" .
```

### 2. `.wait()` chaining is gone

Chained `.wait()` / `!` bang methods on task responses are replaced by dedicated wait helpers.

| Old | New |
|-----|-----|
| `index.saveObjects(records).wait()` | `client.waitForTask(indexName, taskID)` |
| `index.save_objects!(objects)` (Ruby) | `client.save_objects(index_name, objects, true)` |

Three helpers available in every language: `waitForTask`, `waitForAppTask`, `waitForApiKey`.

### 3. `copyIndex` / `moveIndex` → `operationIndex`

All index copy and move operations, including scoped copies (`copyRules`, `copySettings`, `copySynonyms`), consolidate into a single `operationIndex` call with `operation: "copy"` or `"move"` and an optional `scope` array.

### 4. `objectID` is required in `saveObjects`

`autoGenerateObjectIDIfNotExist` is removed. Every object passed to `saveObjects` must include an explicit `objectID`. To let the API generate IDs, use `chunkedBatch` with `action: addObject`.

### 5. `replaceAllObjects` requires explicit `scopes`

The `safe` option is removed. Pass `scopes: ["settings", "rules", "synonyms"]` explicitly (or whichever subset you want to carry over).

### 6. Browse helpers change pattern

The old iterator/chained patterns are gone. The new pattern **varies by language** — check the reference file:

- **Aggregator callback** (JS, Python, Go, Ruby, Kotlin, Scala, Swift, C#, Java): pass an `aggregator` function that receives each page response
- **Iterable / foreach** (PHP): the method returns `ObjectIterator` — iterate with a for-each loop

### 7. `AccountClient` is gone

Cross-application index copies now require composing helpers across two client instances manually: get settings from source, set on destination; browse + save for rules, synonyms, and objects.

### 8. Dedicated clients per API

Each API now has its own client class. If the code previously imported one monolithic client, update imports for `RecommendClient`, `AnalyticsClient`, `AbtestingClient`, etc.

## Migration workflow

1. **Detect language and version** from the project's package manifest (`package.json`, `go.mod`, `composer.json`, `pom.xml`, `Gemfile`, etc.).
2. **Open the matching reference file** from the table above.
3. **Grep for `initIndex`** (and language equivalents) to enumerate all call sites.
4. **Update the install / dependency** first so the compiler/runtime flags all remaining issues.
5. **Apply universal changes** (sections above) before language-specific ones.
6. **Replace wait patterns** — search for `.wait()`, `waitTask`, `wait_task`, bang methods.
7. **Verify** by running the existing test suite or a minimal integration test.

## Direct Invocation

If the skill doesn't trigger automatically, invoke it directly:

- **`/algolia-migration`** — Load the full skill for any Algolia client upgrade task

This is useful when the request is brief (e.g., "update my Algolia imports") and the skill might not auto-trigger.

## Reference Docs

- [references/javascript.md](references/javascript.md) — JavaScript v4 → v5
- [references/python.md](references/python.md) — Python v3 → v4
- [references/go.md](references/go.md) — Go v3 → v4
- [references/php.md](references/php.md) — PHP v3 → v4
- [references/java.md](references/java.md) — Java v3 → v4
- [references/csharp.md](references/csharp.md) — C# v6 → v7
- [references/ruby.md](references/ruby.md) — Ruby v2 → v3
- [references/kotlin.md](references/kotlin.md) — Kotlin v2 → v3
- [references/scala.md](references/scala.md) — Scala v1 → v2
- [references/swift.md](references/swift.md) — Swift v8 → v9
- [references/dart.md](references/dart.md) — Dart (new client)
