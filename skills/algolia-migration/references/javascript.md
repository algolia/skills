# JavaScript: v4 → v5

## Install

```sh
npm install algoliasearch@5
```

## Import changes

```js
// v4
import algoliasearch from "algoliasearch";
import algoliasearch from "algoliasearch/lite";

// v5
import { algoliasearch } from "algoliasearch";
import { liteClient as algoliasearch } from "algoliasearch/lite";
```

Individual API clients (alternative):
```js
import { searchClient }    from "@algolia/client-search";
import { recommendClient } from "@algolia/recommend";
import { abtestingClient } from "@algolia/client-abtesting";
```

## `initIndex` removal

```js
// v4
const index = client.initIndex("INDEX_NAME");
const { hits } = await index.search("QUERY", { facetFilters: ["category:Book"] });

// v5
const { hits } = await client.searchSingleIndex({
  indexName: "INDEX_NAME",
  searchParams: { query: "QUERY", facetFilters: ["category:Book"] },
});
```

## Method renames

| v4 | v5 |
|----|----|
| `index.search()` | `client.searchSingleIndex()` |
| `client.multipleQueries([...])` | `client.search({ requests: [...] })` |
| `index.searchForFacetValues()` | `client.searchForFacetValues()` |
| `client.copyIndex()` / `moveIndex()` / `copyRules()` / `copySynonyms()` / `copySettings()` | `client.operationIndex()` |
| `index.exists()` | `client.indexExists({ indexName })` |
| `index.delete()` | `client.deleteIndex({ indexName })` |
| `replaceAllRules()` | `saveRules()` with `clearExistingRules: true` |
| `replaceAllSynonyms()` | `saveSynonyms()` with `replaceExistingSynonyms: true` |
| `getFrequentlyBoughtTogether()` / `getLookingSimilar()` / `getRelatedProducts()` / `getTrendingFacets()` / `getTrendingItems()` | `getRecommendations()` |
| `clearDictionaryEntries()` / `deleteDictionaryEntries()` / `replaceDictionaryEntries()` / `saveDictionaryEntries()` | `batchDictionaryEntries()` |

## Multiple index search

```js
// v4
const { results } = await client.multipleQueries([
  { indexName: "INDEX_1", query: "QUERY" },
]);

// v5
const { results } = await client.search({
  requests: [{ indexName: "INDEX_1", query: "QUERY" }],
});
```

## Indexing

```js
// v5
const { taskID } = await client.saveObject({
  indexName: "INDEX_NAME",
  body: { objectID: "1", name: "Record" },
});

await client.partialUpdateObject({
  indexName: "INDEX_NAME",
  objectID: "1",
  attributesToUpdate: { name: "Updated" },
});

await client.deleteObject({ indexName: "INDEX_NAME", objectID: "1" });
```

## Settings, synonyms, rules

```js
// v5
const settings = await client.getSettings({ indexName: "INDEX_NAME" });
await client.setSettings({
  indexName: "INDEX_NAME",
  indexSettings: { searchableAttributes: ["title"] },
});

await client.saveSynonyms({
  indexName: "INDEX_NAME",
  synonymHit: [{ objectID: "1", type: "synonym", synonyms: ["car", "auto"] }],
});
```

## `operationIndex` (copy / move)

```js
// copy
await client.operationIndex({
  indexName: "SOURCE",
  operationIndexParams: { operation: "copy", destination: "DEST" },
});

// move / rename
await client.operationIndex({
  indexName: "SOURCE",
  operationIndexParams: { operation: "move", destination: "DEST" },
});

// copy with scope
await client.operationIndex({
  indexName: "SOURCE",
  operationIndexParams: {
    operation: "copy",
    destination: "DEST",
    scope: ["rules", "settings"],
  },
});
```

## Wait pattern

```js
// v4
await index.saveObjects(records).wait();

// v5
const { taskID } = await client.saveObjects({
  indexName: "INDEX_NAME",
  objects: records,
});
await client.waitForTask({ indexName: "INDEX_NAME", taskID });
```

Three helpers: `waitForTask`, `waitForAppTask`, `waitForApiKey`.

## `replaceAllObjects`

```js
// v5 — safe option removed; scopes required
await client.replaceAllObjects({
  indexName: "INDEX_NAME",
  objects: myObjects,
  scopes: ["settings", "rules", "synonyms"],
});
```

## `saveObjects` helper changes

- `autoGenerateObjectIDIfNotExist` removed — provide `objectID` or use `chunkedBatch({ action: "addObject" })`
- New options: `waitForTasks`, `batchSize`

## Browse aggregator

```js
const objects = [];
await client.browseObjects({
  indexName: "INDEX_NAME",
  browseParams: { query: "" },
  aggregator: (response) => objects.push(...response.hits),
});
```

## Secured API key

```js
// v4 — positional args
const key = client.generateSecuredApiKey("parentApiKey", { validUntil: ... });

// v5 — object params
const key = client.generateSecuredApiKey({
  parentApiKey: "parentApiKey",
  restrictions: { validUntil: ..., restrictIndices: ["INDEX_NAME"] },
});

const remaining = client.getSecuredApiKeyRemainingValidity({
  securedApiKey: "SECURED_API_KEY",
});
```

## API key wait

```js
// v5
await client.addApiKey({ acl: ["search"] });
await client.waitForApiKey({ key: "my-api-key", operation: "add" });
```

## New in v5

**`chunkedBatch`** (was internal):
```js
await client.chunkedBatch({
  indexName: "INDEX_NAME",
  objects: myObjects,
  action: "addObject",
  waitForTasks: true,
  batchSize: 1000,
});
```

**`accountCopyIndex`** (no longer needs separate `@algolia/client-account` package — available on the `algoliasearch` meta-package client):
```js
await client.accountCopyIndex({
  sourceIndexName: "SOURCE",
  destinationAppID: "DEST_APP_ID",
  destinationApiKey: "DEST_API_KEY",
  destinationIndexName: "DEST_INDEX_NAME",
});
```

**Transformation helpers** (require `transformation: { region: "us" }` at init):
```js
const client = algoliasearch("APP_ID", "API_KEY", {
  transformation: { region: "us" },
});
await client.saveObjectsWithTransformation({ indexName: "INDEX_NAME", objects: myObjects });
await client.replaceAllObjectsWithTransformation({ indexName: "INDEX_NAME", objects: myObjects, scopes: [...] });
```
