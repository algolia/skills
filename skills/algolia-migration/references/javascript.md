# JavaScript: v4 → v5

## Install

```sh
npm install algoliasearch@5
```

## Import changes

```js
// v4 — default export
import algoliasearch from "algoliasearch";
import algoliasearch from "algoliasearch/lite";

// v5 — named export
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

The most significant change: `initIndex` is removed. All methods that previously lived on the index object are now on the client and require `indexName`.

```js
// v4
const index = client.initIndex("INDEX_NAME");
const results = await index.search("QUERY");

// v5
const results = await client.searchSingleIndex({
  indexName: "INDEX_NAME",
  searchParams: { query: "QUERY" },
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
| `index.replaceAllRules()` | `client.saveRules()` with `clearExistingRules: true` |
| `index.replaceAllSynonyms()` | `client.saveSynonyms()` with `clearExistingSynonyms: true` |
| `client.waitAppTask()` | `client.waitForAppTask()` |
| `client.clearDictionaryEntries()` / `deleteDictionaryEntries()` / `replaceDictionaryEntries()` / `saveDictionaryEntries()` | `client.batchDictionaryEntries()` |

## Search single index

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

## Search for facet values

```js
// v4
const results = await index.searchForFacetValues("category", "book");

// v5
const results = await client.searchForFacetValues({
  indexName: "INDEX_NAME",
  facetName: "category",
  searchForFacetValuesRequest: { facetQuery: "book" },
});
```

## Indexing

All indexing methods now require `indexName` directly on the client.

```js
// saveObject
const { taskID } = await client.saveObject({
  indexName: "INDEX_NAME",
  body: { objectID: "1", name: "Record" },
});

// saveObjects (note: objects, not body, for batch)
const { taskID } = await client.saveObjects({
  indexName: "INDEX_NAME",
  objects: [{ objectID: "1", name: "Record" }],
});

// partialUpdateObject
await client.partialUpdateObject({
  indexName: "INDEX_NAME",
  objectID: "1",
  attributesToUpdate: { name: "Updated" },
});

// deleteObject
await client.deleteObject({ indexName: "INDEX_NAME", objectID: "1" });
```

## Settings, synonyms, rules

```js
// getSettings / setSettings
const settings = await client.getSettings({ indexName: "INDEX_NAME" });
await client.setSettings({
  indexName: "INDEX_NAME",
  indexSettings: { searchableAttributes: ["title", "author"] },
});

// saveSynonyms
await client.saveSynonyms({
  indexName: "INDEX_NAME",
  synonymHit: [{ objectID: "1", type: "synonym", synonyms: ["car", "auto"] }],
});

// saveRules
await client.saveRules({
  indexName: "INDEX_NAME",
  rules: [{ objectID: "1", conditions: [...], consequence: {...} }],
});

// replaceAllRules → saveRules with clearExistingRules
await client.saveRules({ indexName: "INDEX_NAME", rules: [...], clearExistingRules: true });

// replaceAllSynonyms → saveSynonyms with clearExistingSynonyms
await client.saveSynonyms({ indexName: "INDEX_NAME", synonymHit: [...], clearExistingSynonyms: true });
```

## `operationIndex` (copy / move)

```js
// copy
await client.operationIndex({
  indexName: "SOURCE_INDEX_NAME",
  operationIndexParams: { operation: "copy", destination: "DESTINATION_INDEX_NAME" },
});

// move / rename
await client.operationIndex({
  indexName: "SOURCE_INDEX_NAME",
  operationIndexParams: { operation: "move", destination: "DESTINATION_INDEX_NAME" },
});

// copy with scope
await client.operationIndex({
  indexName: "SOURCE_INDEX_NAME",
  operationIndexParams: {
    operation: "copy",
    destination: "DESTINATION_INDEX_NAME",
    scope: ["rules", "settings"],
  },
});

// check if index exists
await client.indexExists({ indexName: "INDEX_NAME" });
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

```js
// waitForApiKey — add
await client.addApiKey({ acl: ["search"] });
await client.waitForApiKey({ key: "my-api-key", operation: "add" });

// waitForApiKey — update (pass expected final state)
await client.waitForApiKey({
  key: "my-api-key",
  operation: "update",
  apiKey: { acl: ["search", "browse"] },
});

// waitForAppTask (was waitAppTask in v4)
await client.waitForAppTask({ taskID: 123 });
```

## `replaceAllObjects`

```js
// v5 — safe option removed; scopes required
await client.replaceAllObjects({
  indexName: "INDEX_NAME",
  objects: myObjects,
  scopes: ["settings", "rules", "synonyms"],
});
```

## Helper method changes

- **`saveObjects`**: `autoGenerateObjectIDIfNotExist` removed — provide `objectID` or use `chunkedBatch({ action: "addObject" })`; new `waitForTasks` and `batchSize` options
- **`deleteObjects`**: new `waitForTasks` and `batchSize` options
- **`partialUpdateObjects`**: new `waitForTasks` and `batchSize` options

## Browse aggregator

```js
const objects = [];
await client.browseObjects({
  indexName: "INDEX_NAME",
  browseParams: { query: "" },
  aggregator: (response) => objects.push(...response.hits),
  validate: (response) => objects.length < 500,
});
```

## Secured API key

```js
// v4 — positional args
const key = client.generateSecuredApiKey("parentApiKey", {
  validUntil: 1893456000,
  restrictIndices: ["INDEX_NAME"],
});

// v5 — object params
const key = client.generateSecuredApiKey({
  parentApiKey: "parentApiKey",
  restrictions: { validUntil: 1893456000, restrictIndices: ["INDEX_NAME"] },
});

// getSecuredApiKeyRemainingValidity — positional → object
const remaining = client.getSecuredApiKeyRemainingValidity({
  securedApiKey: "SECURED_API_KEY",
});
```

## New in v5

**`chunkedBatch`** (was internal):
```js
const responses = await client.chunkedBatch({
  indexName: "INDEX_NAME",
  objects: myObjects,
  action: "addObject",
  waitForTasks: true,
  batchSize: 1000,
});
```

**`accountCopyIndex`** (no longer needs separate `@algolia/client-account` package — available on the `algoliasearch` meta-package):
```js
await client.accountCopyIndex({
  sourceIndexName: "SOURCE",
  destinationAppID: "DEST_APP_ID",
  destinationApiKey: "DEST_API_KEY",
  destinationIndexName: "DEST_INDEX_NAME",
  batchSize: 1000,
});
```

**Transformation helpers** (require `transformation: { region: "us" }` at init):
```js
const client = algoliasearch("APP_ID", "API_KEY", {
  transformation: { region: "us" },
});

await client.saveObjectsWithTransformation({
  indexName: "INDEX_NAME",
  objects: myObjects,
  waitForTasks: false,
  batchSize: 1000,
});

await client.replaceAllObjectsWithTransformation({
  indexName: "INDEX_NAME",
  objects: myObjects,
  batchSize: 1000,
  scopes: ["settings", "rules", "synonyms"],
});

await client.partialUpdateObjectsWithTransformation({
  indexName: "INDEX_NAME",
  objects: myObjects,
  createIfNotExists: false,
  waitForTasks: false,
  batchSize: 1000,
});
```

## Method changes reference

Full rename table from v4 to v5:

| v4 | v5 |
|----|----|
| `client.addApiKey({}).wait()` | `client.waitForApiKey()` |
| `client.clearDictionaryEntries()` | `client.batchDictionaryEntries()` |
| `client.copyIndex()` | `client.operationIndex()` |
| `client.copyRules()` | `client.operationIndex()` |
| `client.copySynonyms()` | `client.operationIndex()` |
| `client.deleteApiKey()` | `client.deleteApiKey()` |
| `client.deleteDictionaryEntries()` | `client.batchDictionaryEntries()` |
| `client.generateSecuredApiKey()` | `client.generateSecuredApiKey()` (object params) |
| `client.getSecuredApiKeyRemainingValidity()` | `client.getSecuredApiKeyRemainingValidity()` (object params) |
| `client.listApiKeys()` | `client.listApiKeys()` |
| `client.listIndices()` | `client.listIndices()` |
| `client.moveIndex()` | `client.operationIndex()` |
| `client.multipleBatch()` | `client.multipleBatch()` |
| `client.multipleQueries()` | `client.search()` |
| `client.replaceDictionaryEntries()` | `client.batchDictionaryEntries()` |
| `client.restoreApiKey()` | `client.restoreApiKey()` |
| `client.saveDictionaryEntries()` | `client.batchDictionaryEntries()` |
| `client.updateApiKey()` | `client.updateApiKey()` |
| `client.waitAppTask()` | `client.waitForAppTask()` |
| `index.batch()` | `client.batch()` |
| `index.browseObjects()` | `client.browseObjects()` |
| `index.browseRules()` | `client.browseRules()` |
| `index.browseSynonyms()` | `client.browseSynonyms()` |
| `index.clearObjects()` | `client.clearObjects()` |
| `index.clearRules()` | `client.clearRules()` |
| `index.clearSynonyms()` | `client.clearSynonyms()` |
| `index.copySettings()` | `client.operationIndex()` |
| `index.delete()` | `client.deleteIndex()` |
| `index.deleteBy()` | `client.deleteBy()` |
| `index.deleteObject()` | `client.deleteObject()` |
| `index.deleteObjects()` | `client.deleteObjects()` |
| `index.deleteRule()` | `client.deleteRule()` |
| `index.deleteSynonym()` | `client.deleteSynonym()` |
| `index.exists()` | `client.indexExists()` |
| `index.findObject()` | `client.searchSingleIndex()` |
| `index.getObject()` | `client.getObject()` |
| `index.getObjects()` | `client.getObjects()` |
| `index.getRule()` | `client.getRule()` |
| `index.getSettings()` | `client.getSettings()` |
| `index.getSynonym()` | `client.getSynonym()` |
| `index.getTask()` | `client.getTask()` |
| `index.partialUpdateObject()` | `client.partialUpdateObject()` |
| `index.partialUpdateObjects()` | `client.partialUpdateObjects()` |
| `index.replaceAllObjects()` | `client.replaceAllObjects()` |
| `index.replaceAllRules()` | `client.saveRules()` (with `clearExistingRules: true`) |
| `index.replaceAllSynonyms()` | `client.saveSynonyms()` (with `clearExistingSynonyms: true`) |
| `index.saveObject()` | `client.saveObject()` |
| `index.saveObjects()` | `client.saveObjects()` |
| `index.saveRule()` | `client.saveRule()` |
| `index.saveRules()` | `client.saveRules()` |
| `index.saveSynonym()` | `client.saveSynonym()` |
| `index.saveSynonyms()` | `client.saveSynonyms()` |
| `index.search()` | `client.searchSingleIndex()` |
| `index.searchForFacetValues()` | `client.searchForFacetValues()` |
| `index.searchRules()` | `client.searchRules()` |
| `index.searchSynonyms()` | `client.searchSynonyms()` |
| `index.setSettings()` | `client.setSettings()` |
| `index.{operation}.wait()` | `client.waitForTask()` |

Recommend API renames:

| v4 | v5 |
|----|----|
| `client.getFrequentlyBoughtTogether()` | `client.getRecommendations()` |
| `client.getLookingSimilar()` | `client.getRecommendations()` |
| `client.getRelatedProducts()` | `client.getRecommendations()` |
| `client.getTrendingFacets()` | `client.getRecommendations()` |
| `client.getTrendingItems()` | `client.getRecommendations()` |
