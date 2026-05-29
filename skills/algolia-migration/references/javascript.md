# Upgrade the JavaScript API client to version 5

> Keep your JavaScript API client up to date to benefit from improvements and bug fixes.

The latest major version of the `algoliasearch` package is version 5.
This page helps you upgrade from version 4
and explains the breaking changes you need to address.

Algolia generates the version 5 clients from OpenAPI specifications,
which provides consistent behavior across all languages and up-to-date API coverage.
The main architectural change is the removal of the `initIndex` pattern:
all methods are now on the `client` instance directly, with `indexName` as a parameter.

For the full list of changes, see the JavaScript changelog.

## Update your dependencies

Update the `algoliasearch` package to version 5:

```sh
npm install algoliasearch@5
```

If you're using a search-only build (lite client), the package name stays the same.
Only the import path changes (see [Update imports](#update-imports)).

## Update imports

The import style changed from a default export to a named export.

```js
// version 4
import algoliasearch from "algoliasearch";

// version 5
import { algoliasearch } from "algoliasearch";
```

If you're using the **lite client** (search only), the import also changed:

```js
// version 4
import algoliasearch from "algoliasearch/lite";

// version 5
import { liteClient as algoliasearch } from "algoliasearch/lite";
```

Version 5 also includes dedicated packages for each API.
If you only need to access methods from a specific API,
you can install and import them separately:

```js
// Search API
import { searchClient } from "@algolia/client-search";
// Recommend API
import { recommendClient } from "@algolia/recommend";
// A/B testing API
import { abtestingClient } from "@algolia/client-abtesting";
// Analytics API
import { analyticsClient } from "@algolia/client-analytics";
// Personalization API
import { personalizationClient } from "@algolia/client-personalization";
// Query Suggestions API
import { querySuggestionsClient } from "@algolia/client-query-suggestions";
```

## Update client initialization

Client creation is unchanged.
The constructor still accepts your application ID and API key:

```js
// version 4
const client = algoliasearch("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");

// version 5
const client = algoliasearch("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");
```

The other major change concerns what follows initialization:
`initIndex` no longer exists.

## Remove `initIndex`

This is the most significant change when upgrading.
Version 4 relied on an index object with methods called on it.
In version 5, all methods belong to the `client` instance,
with `indexName` as a parameter.

```js
// version 4
const client = algoliasearch("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");
const index = client.initIndex("INDEX_NAME");
const results = index.search("QUERY");

// version 5
const client = algoliasearch("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");
const results = await client.searchSingleIndex({
  indexName: "INDEX_NAME",
  searchParams: { query: "QUERY" },
});
```

  If you have many files to update,
  search your codebase for `initIndex` or `.initIndex(` to find every place that needs changing.

## Update search calls

### Search a single index

The `index.search()` method is now `client.searchSingleIndex()`.
Pass the index name and search parameters as an object:

```js
// version 4
const index = client.initIndex("INDEX_NAME");
const { hits } = await index.search("QUERY", {
  facetFilters: ["category:Book"],
});

// version 5
const { hits } = await client.searchSingleIndex({
  indexName: "INDEX_NAME",
  searchParams: {
    query: "QUERY",
    facetFilters: ["category:Book"],
  },
});
```

### Search multiple indices

The `client.multipleQueries()` method is now `client.search()`.
Each request in the array requires an `indexName`:

```js
// version 4
const { results } = await client.multipleQueries([
  { indexName: "INDEX_1", query: "QUERY" },
  { indexName: "INDEX_2", query: "QUERY" },
]);

// In version 4, you could also use:
// const { results } = await client.search([...]);
// which is equivalent to multipleQueries.

// version 5
const { results } = await client.search({
  requests: [
    { indexName: "INDEX_1", query: "QUERY" },
    { indexName: "INDEX_2", query: "QUERY" },
  ],
});
```

### Search for facet values

The `index.searchForFacetValues()` method becomes `client.searchForFacetValues()`
with an `indexName` parameter:

```js
// version 4
const index = client.initIndex("INDEX_NAME");
const results = await index.searchForFacetValues("category", "book");

// version 5
const results = await client.searchForFacetValues({
  indexName: "INDEX_NAME",
  facetName: "category",
  searchForFacetValuesRequest: { facetQuery: "book" },
});
```

## Update indexing operations

In version 5, indexing methods are on the client instead of the index object,
with `indexName` as a parameter.

### Add or replace records

```js
// version 4
const index = client.initIndex("INDEX_NAME");
await index.saveObject({ objectID: "1", name: "Record" });
await index.saveObjects([{ objectID: "1", name: "Record" }]);

// version 5
const { taskID } = await client.saveObject({
  indexName: "INDEX_NAME",
  body: { objectID: "1", name: "Record" },
});
// saveObjects works the same way:
// (note: `objects` instead of `body` for the batch version)
// saveObjects returns an array of BatchResponse — use waitForTasks or destructure the first element
await client.saveObjects({
  indexName: "INDEX_NAME",
  objects: [{ objectID: "1", name: "Record" }],
  waitForTasks: true,
});
```

### Partially update records

```js
// version 4
const index = client.initIndex("INDEX_NAME");
await index.partialUpdateObject({ objectID: "1", name: "Updated" });

// version 5
await client.partialUpdateObject({
  indexName: "INDEX_NAME",
  objectID: "1",
  attributesToUpdate: { name: "Updated" },
});
```

### Delete records

```js
// version 4
const index = client.initIndex("INDEX_NAME");
await index.deleteObject("1");

// version 5
await client.deleteObject({
  indexName: "INDEX_NAME",
  objectID: "1",
});
```

## Update settings, synonyms, and rules

### Get and set settings

```js
// version 4
const index = client.initIndex("INDEX_NAME");
const settings = await index.getSettings();
await index.setSettings({ searchableAttributes: ["title", "author"] });

// version 5
const settings = await client.getSettings({
  indexName: "INDEX_NAME",
});
await client.setSettings({
  indexName: "INDEX_NAME",
  indexSettings: { searchableAttributes: ["title", "author"] },
});
```

### Save synonyms and rules

```js
// version 4
const index = client.initIndex("INDEX_NAME");
await index.saveSynonyms([{ objectID: "1", type: "synonym", synonyms: ["car", "auto"] }]);
await index.saveRules([{ objectID: "1", conditions: [{ anchoring: "contains", pattern: "shoes" }], consequence: { params: { query: "sneakers" } } }]);

// version 5
await client.saveSynonyms({
  indexName: "INDEX_NAME",
  synonymHit: [{ objectID: "1", type: "synonym", synonyms: ["car", "auto"] }],
});
await client.saveRules({
  indexName: "INDEX_NAME",
  rules: [{ objectID: "1", conditions: [{ anchoring: "contains", pattern: "shoes" }], consequence: { params: { query: "sneakers" } } }],
});
```

  In version 4, `index.replaceAllRules()` and `index.replaceAllSynonyms()` replaced all rules or synonyms.
  In version 5, use `client.saveRules()` or `client.saveSynonyms()` with the `clearExistingRules` or `clearExistingSynonyms` parameter set to `true`.

## Update index management

The `copyIndex`, `moveIndex`, `copyRules`, `copySynonyms`, and `copySettings`
methods are all replaced by a single `operationIndex` method.

### Copy an index

```js
// version 4
await client.copyIndex("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME");

// version 5
await client.operationIndex({
  indexName: "SOURCE_INDEX_NAME",
  operationIndexParams: { operation: "copy", destination: "DESTINATION_INDEX_NAME" },
});
```

### Move (rename) an index

```js
// version 4
await client.moveIndex("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME");

// version 5
await client.operationIndex({
  indexName: "SOURCE_INDEX_NAME",
  operationIndexParams: { operation: "move", destination: "DESTINATION_INDEX_NAME" },
});
```

### Copy only rules or settings

In version 5, use the `scope` parameter to limit the operation to specific data:

```js
// version 5 -- copy only rules and settings from one index to another
await client.operationIndex({
  indexName: "SOURCE_INDEX_NAME",
  operationIndexParams: {
    operation: "copy",
    destination: "DESTINATION_INDEX_NAME",
    scope: ["rules", "settings"],
  },
});
```

### Check if an index exists

In version 4, you could check if an index existed using the `exists` method on the index object.
In version 5, use the `indexExists` helper method on the client:

```js
// version 4
const index = client.initIndex("INDEX_NAME");
await index.exists();

// version 5
await client.indexExists({ indexName: "INDEX_NAME" });
```

## Update task handling

Version 4 supported chaining `.wait()` on operations.
Version 5 replaces this pattern with dedicated wait helpers.

```js
// version 4
const index = client.initIndex("INDEX_NAME");
await index.saveObjects(records).wait();

// version 5 — saveObjects returns BatchResponse[]; use waitForTasks to block until done
await client.saveObjects({
  indexName: "INDEX_NAME",
  objects: records,
  waitForTasks: true,
});
```

Version 5 includes three wait helpers:

* `waitForTask`: wait until indexing operations are done.
* `waitForAppTask`: wait for application-level tasks.
* `waitForApiKey`: wait for API key operations.

## Helper method changes

The following sections document breaking changes in helper method signatures and behavior between version 4 and version 5.

### `replaceAllObjects`

The `safe` option has been removed. In version 4, `safe: true` caused the helper to wait after each step. In version 5, the helper always waits—equivalent to the previous `safe: true` behavior.

The `scopes` parameter is optional. When omitted, it defaults to `["settings", "rules", "synonyms"]`.

```js
// version 4
await client.replaceAllObjects({
  indexName: "INDEX_NAME",
  objects: myObjects,
  safe: true,
});

// version 5
await client.replaceAllObjects({
  indexName: "INDEX_NAME",
  objects: myObjects,
});
```

### `saveObjects`

The `autoGenerateObjectIDIfNotExist` option has been removed. In version 5, you must provide an `objectID` on every object, or use the `chunkedBatch` helper with the `action` parameter set to `addObject` if you want the API to generate object IDs.

Two new optional parameters are available:

* `waitForTasks` (waits for all indexing tasks to complete before returning, default `false`)
* `batchSize` (controls how many objects are sent per API call, default `1,000`)

```js
// version 4
await client.saveObjects({
  indexName: "INDEX_NAME",
  objects: myObjects,
  waitForTasks: false,
  autoGenerateObjectIDIfNotExist: true,
});

// version 5
// Objects must have objectID set, or use chunkedBatch with action: "addObject"
await client.saveObjects({
  indexName: "INDEX_NAME",
  objects: myObjects,
  waitForTasks: true,
  batchSize: 1000,
});
```

### `deleteObjects`

Two new optional parameters are available:

* `waitForTasks` (waits for all indexing tasks to complete before returning, default `false`)
* `batchSize` (controls how many objects are sent per API call, default `1,000`)

```js
// version 4
await client.deleteObjects({
  indexName: "INDEX_NAME",
  objectIDs: ["objectID1", "objectID2"],
});

// version 5
await client.deleteObjects({
  indexName: "INDEX_NAME",
  objectIDs: ["objectID1", "objectID2"],
  waitForTasks: true,
  batchSize: 1000,
});
```

### `partialUpdateObjects`

Two new optional parameters are available: `waitForTasks` and `batchSize`.

```js
// version 4
await client.partialUpdateObjects({
  indexName: "INDEX_NAME",
  objects: myObjects,
  createIfNotExists: true,
});

// version 5
await client.partialUpdateObjects({
  indexName: "INDEX_NAME",
  objects: myObjects,
  createIfNotExists: true,
  waitForTasks: true,
  batchSize: 1000,
});
```

### `browseObjects`, `browseRules`, `browseSynonyms`

These helpers now accept an `aggregator` callback instead of returning an iterator. The helper calls `aggregator` with each page of results as it paginates. An optional `validate` callback can be used to stop early.

```js
// version 4
const objects = [];
await client.browseObjects({
  indexName: "INDEX_NAME",
  browseParams: { query: "" },
  aggregator: (response) => objects.push(...response.hits),
});

// version 5
const objects = [];
await client.browseObjects({
  indexName: "INDEX_NAME",
  browseParams: { query: "" },
  aggregator: (response) => objects.push(...response.hits),
  // Optional: stop early when condition is met
  validate: (response) => objects.length < 500,
});
```

### `generateSecuredApiKey`

The method signature has changed from positional parameters to a single object parameter.

```js
// version 4
const key = client.generateSecuredApiKey("parentApiKey", {
  validUntil: Math.round(Date.now() / 1000) + 3600,
  restrictIndices: ["INDEX_NAME"],
});

// version 5
const key = client.generateSecuredApiKey({
  parentApiKey: "parentApiKey",
  restrictions: {
    validUntil: Math.round(Date.now() / 1000) + 3600,
    restrictIndices: ["INDEX_NAME"],
  },
});
```

### `getSecuredApiKeyRemainingValidity`

The method signature changed from a positional string argument to an object parameter.

```js
// version 4
const remaining = client.getSecuredApiKeyRemainingValidity("SECURED_API_KEY");

// version 5
const remaining = client.getSecuredApiKeyRemainingValidity({
  securedApiKey: "SECURED_API_KEY",
});
```

### `waitForTask`

The helper was renamed from `waitTask` to `waitForTask` and now takes `indexName` as an explicit parameter.

```js
// version 4
await index.waitTask(taskID);

// version 5
await client.waitForTask({ indexName: "INDEX_NAME", taskID });
```

### `waitForAppTask`

The helper was renamed from `waitAppTask` to `waitForAppTask` for consistency with `waitForTask` and `waitForApiKey`.

```js
// version 4
await client.waitAppTask({ taskID: 123 });

// version 5
await client.waitForAppTask({ taskID: 123 });
```

### `waitForApiKey`

In version 4, waiting for API key operations was done by calling `.wait()` on the `WaitablePromise` returned by `addApiKey`, `updateApiKey`, `deleteApiKey`, or `restoreApiKey`. Version 5 provides a standalone `waitForApiKey` helper.

```js
// version 4
const { wait } = await client.addApiKey({ acl: ["search"] });
await wait();

// version 5
await client.addApiKey({ acl: ["search"] });
await client.waitForApiKey({ key: "my-api-key", operation: "add" });

// For updates, pass the expected final key state:
await client.waitForApiKey({
  key: "my-api-key",
  operation: "update",
  apiKey: { acl: ["search", "browse"] },
});
```

### `indexExists`

The helper was renamed from `exists()` on the index object to `indexExists()` on the client.

```js
// version 4
const exists = await index.exists();

// version 5
const exists = await client.indexExists({ indexName: "INDEX_NAME" });
```

### `chunkedBatch`

`chunkedBatch` is now a public helper. In version 4, chunking was an internal implementation detail of `saveObjects`. The `action` parameter defaults to `"addObject"`.

```js
// version 4
// No public chunkedBatch — was internal to saveObjects

// version 5
const responses = await client.chunkedBatch({
  indexName: "INDEX_NAME",
  objects: myObjects,
  action: "addObject",
  waitForTasks: true,
  batchSize: 1000,
});
```

### `accountCopyIndex`

In version 4, `accountCopyIndex` was part of the separate `@algolia/client-account` package and accepted two initialized `SearchIndex` objects. In version 5, it's a built-in helper on the `algoliasearch` client and accepts a flat options object with string identifiers.

```js
// version 4
import { accountCopyIndex } from "@algolia/client-account";

const srcIndex = sourceClient.initIndex("SOURCE_INDEX_NAME");
const destIndex = destClient.initIndex("DEST_INDEX_NAME");

await accountCopyIndex(srcIndex, destIndex);

// version 5
const client = algoliasearch("SOURCE_APP_ID", "SOURCE_API_KEY");

await client.accountCopyIndex({
  sourceIndexName: "SOURCE_INDEX_NAME",
  destinationAppID: "DEST_APP_ID",
  destinationApiKey: "DEST_API_KEY",
  destinationIndexName: "DEST_INDEX_NAME",
  batchSize: 1000,
});
```

### `saveObjectsWithTransformation`

In version 4, this method was available on index objects via the ingestion mixin. In version 5, it's a top-level helper on the `algoliasearch` client. It routes objects through the Algolia Push connector and requires `transformation.region` to be set at client initialization.

```js
// version 4
await index.saveObjectsWithTransformation(objects, ingestionTransporter);

// version 5
const client = algoliasearch("APP_ID", "API_KEY", {
  transformation: { region: "us" },
});

await client.saveObjectsWithTransformation({
  indexName: "INDEX_NAME",
  objects: myObjects,
  waitForTasks: false,
  batchSize: 1000,
});
```

### `replaceAllObjectsWithTransformation`

New in version 5. Atomically replaces all objects via the Push connector (copy settings/rules/synonyms to a temp index → push objects → move back). Requires `transformation.region` at client initialization.

```js
const client = algoliasearch("APP_ID", "API_KEY", {
  transformation: { region: "us" },
});

await client.replaceAllObjectsWithTransformation({
  indexName: "INDEX_NAME",
  objects: myObjects,
  batchSize: 1000,
  scopes: ["settings", "rules", "synonyms"],
});
```

### `partialUpdateObjectsWithTransformation`

New in version 5. Routes partial updates through the Push connector. The `createIfNotExists` parameter defaults to `false`.

```js
await client.partialUpdateObjectsWithTransformation({
  indexName: "INDEX_NAME",
  objects: myObjects,
  createIfNotExists: false,
  waitForTasks: false,
  batchSize: 1000,
});
```

## Method changes reference

The following tables list all method names that changed between version 4 and version 5.

### Search API client

| Version 4 (legacy)                         |   | Version 5 (current)                        |
| ------------------------------------------ | - | ------------------------------------------ |
| `client.addApiKey`                         | → | `client.addApiKey`                         |
| `client.addApiKey.wait`                    | → | `client.waitForApiKey`                     |
| `client.clearDictionaryEntries`            | → | `client.batchDictionaryEntries`            |
| `client.copyIndex`                         | → | `client.operationIndex`                    |
| `client.copyRules`                         | → | `client.operationIndex`                    |
| `client.copySynonyms`                      | → | `client.operationIndex`                    |
| `client.deleteApiKey`                      | → | `client.deleteApiKey`                      |
| `client.deleteDictionaryEntries`           | → | `client.batchDictionaryEntries`            |
| `client.generateSecuredApiKey`             | → | `client.generateSecuredApiKey`             |
| `client.getApiKey`                         | → | `client.getApiKey`                         |
| `client.getSecuredApiKeyRemainingValidity` | → | `client.getSecuredApiKeyRemainingValidity` |
| `client.listApiKeys`                       | → | `client.listApiKeys`                       |
| `client.listIndices`                       | → | `client.listIndices`                       |
| `client.moveIndex`                         | → | `client.operationIndex`                    |
| `client.multipleBatch`                     | → | `client.multipleBatch`                     |
| `client.multipleQueries`                   | → | `client.search`                            |
| `client.replaceDictionaryEntries`          | → | `client.batchDictionaryEntries`            |
| `client.restoreApiKey`                     | → | `client.restoreApiKey`                     |
| `client.saveDictionaryEntries`             | → | `client.batchDictionaryEntries`            |
| `client.updateApiKey`                      | → | `client.updateApiKey`                      |
| `index.batch`                              | → | `client.batch`                             |
| `index.browseObjects`                      | → | `client.browseObjects`                     |
| `index.browseRules`                        | → | `client.browseRules`                       |
| `index.browseSynonyms`                     | → | `client.browseSynonyms`                    |
| `index.clearObjects`                       | → | `client.clearObjects`                      |
| `index.clearRules`                         | → | `client.clearRules`                        |
| `index.clearSynonyms`                      | → | `client.clearSynonyms`                     |
| `index.copySettings`                       | → | `client.operationIndex`                    |
| `index.delete`                             | → | `client.deleteIndex`                       |
| `index.deleteBy`                           | → | `client.deleteBy`                          |
| `index.deleteObject`                       | → | `client.deleteObject`                      |
| `index.deleteObjects`                      | → | `client.deleteObjects`                     |
| `index.deleteRule`                         | → | `client.deleteRule`                        |
| `index.deleteSynonym`                      | → | `client.deleteSynonym`                     |
| `index.exists`                             | → | `client.indexExists`                       |
| `index.findObject`                         | → | `client.searchSingleIndex`                 |
| `index.getObject`                          | → | `client.getObject`                         |
| `index.getObjects`                         | → | `client.getObjects`                        |
| `index.getRule`                            | → | `client.getRule`                           |
| `index.getSettings`                        | → | `client.getSettings`                       |
| `index.getSynonym`                         | → | `client.getSynonym`                        |
| `index.getTask`                            | → | `client.getTask`                           |
| `index.partialUpdateObject`                | → | `client.partialUpdateObject`               |
| `index.partialUpdateObjects`               | → | `client.partialUpdateObjects`              |
| `index.replaceAllObjects`                  | → | `client.replaceAllObjects`                 |
| `index.replaceAllRules`                    | → | `client.saveRules`                         |
| `index.replaceAllSynonyms`                 | → | `client.saveSynonyms`                      |
| `index.saveObject`                         | → | `client.saveObject`                        |
| `index.saveObjects`                        | → | `client.saveObjects`                       |
| `index.saveRule`                           | → | `client.saveRule`                          |
| `index.saveRules`                          | → | `client.saveRules`                         |
| `index.saveSynonym`                        | → | `client.saveSynonym`                       |
| `index.saveSynonyms`                       | → | `client.saveSynonyms`                      |
| `index.search`                             | → | `client.searchSingleIndex`                 |
| `index.searchForFacetValues`               | → | `client.searchForFacetValues`              |
| `index.searchRules`                        | → | `client.searchRules`                       |
| `index.searchSynonyms`                     | → | `client.searchSynonyms`                    |
| `index.setSettings`                        | → | `client.setSettings`                       |
| `index.{operation}.wait`                   | → | `client.waitForTask`                       |

### Recommend API client

| Version 4 (legacy)                   |   | Version 5 (current)         |
| ------------------------------------ | - | --------------------------- |
| `client.getFrequentlyBoughtTogether` | → | `client.getRecommendations` |
| `client.getLookingSimilar`           | → | `client.getRecommendations` |
| `client.getRecommendations`          | → | `client.getRecommendations` |
| `client.getRelatedProducts`          | → | `client.getRecommendations` |
| `client.getTrendingFacets`           | → | `client.getRecommendations` |
| `client.getTrendingItems`            | → | `client.getRecommendations` |
