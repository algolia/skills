# Upgrade the Java API client to version 4

> Keep your Java API client up to date to benefit from improvements and bug fixes.

The latest major version of the `algoliasearch` package is version 4.
This page helps you upgrade from version 3
and explains the breaking changes you need to address.

Algolia generates the version 4 clients from OpenAPI specifications,
which provides consistent behavior across all languages and up-to-date API coverage.
The main architectural change is the removal of the `initIndex` pattern:
all methods are now on the `client` instance directly, with `indexName` as a parameter.

For the full list of changes, see the Java changelog.

## Update your dependencies

Version 4 consolidates the separate `algoliasearch-core` and HTTP client packages
into a single `algoliasearch` artifact.
You no longer need `algoliasearch-apache` or `algoliasearch-java-net`.

### Maven

Replace your Algolia dependencies in `pom.xml`:

```xml
<!-- version 3 -->
<dependency>
  <groupId>com.algolia</groupId>
  <artifactId>algoliasearch-core</artifactId>
</dependency>
<dependency>
  <groupId>com.algolia</groupId>
  <artifactId>algoliasearch-apache</artifactId>
</dependency>

<!-- version 4 -->
<dependency>
  <groupId>com.algolia</groupId>
  <artifactId>algoliasearch</artifactId>
</dependency>
```

### Gradle

Update your `build.gradle` file:

```groovy
// version 3
implementation 'com.algolia:algoliasearch-core:VERSION'
implementation 'com.algolia:algoliasearch-apache:VERSION'

// version 4
implementation 'com.algolia:algoliasearch:VERSION'
```

Find the latest version on [Maven Central](https://central.sonatype.com/artifact/com.algolia/algoliasearch).

## Update imports

The package structure changed.
Client classes moved from `com.algolia.search` to `com.algolia.api`,
and model classes moved to `com.algolia.model.search`.

```java
// version 3
import com.algolia.search.DefaultSearchClient;
import com.algolia.search.SearchClient;
import com.algolia.search.SearchIndex;
import com.algolia.search.models.indexing.Query;
import com.algolia.search.models.indexing.SearchResult;

// version 4
import com.algolia.api.SearchClient;
import com.algolia.model.search.*;
```

Version 4 also includes dedicated client classes for each API:

```java
// Search API
import com.algolia.api.SearchClient;
// Recommend API
import com.algolia.api.RecommendClient;
// A/B testing API
import com.algolia.api.AbtestingClient;
// Analytics API
import com.algolia.api.AnalyticsClient;
// Personalization API
import com.algolia.api.PersonalizationClient;
// Query Suggestions API
import com.algolia.api.QuerySuggestionsClient;
```

## Update client initialization

In version 3, the `DefaultSearchClient.create()` factory method created the client.
Version 4 removes this factory. Use the `SearchClient` constructor instead.

```java
// version 3
SearchClient client = DefaultSearchClient.create("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");

// version 4
var client = new SearchClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");
```

The version 4 client implements `Closeable`.
Use try-with-resources to ensure the client is properly closed:

```java
// version 4 (recommended)
try (var client = new SearchClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")) {
    // use client
}
```

## Understand the new API surface

Version 4 introduces two major changes to the API surface:

* **No more `initIndex`.**
  In version 3, the client created a typed `SearchIndex<T>` object with methods called on it.
  In version 4, the `SearchIndex` class is gone.
  All methods belong to the `client` instance,
  with `indexName` as a parameter.
* **Generic type parameter moves to each method call.**
  In version 3, you set the result type once on `initIndex("INDEX", Record.class)`.
  In version 4, you pass the target class (for example, `Hit.class`) as the last argument
  to each method that returns typed results,
  such as `searchSingleIndex` or `getObject`.

```java
// version 3
SearchClient client = DefaultSearchClient.create("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");
SearchIndex<Record> index = client.initIndex("INDEX_NAME", Record.class);
index.search(new Query("QUERY"));

// version 4
var client = new SearchClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");
client.searchSingleIndex(
    "INDEX_NAME",
    new SearchParamsObject().setQuery("QUERY"),
    Hit.class
);
```

  If you have many files to update,
  search your codebase for `initIndex` or `.initIndex(` to find every place that needs changing.

## Update search calls

### Search a single index

The `index.search()` method is now `client.searchSingleIndex()`.
Pass the index name, a `SearchParamsObject`, and the target class:

```java
// version 3
SearchIndex<Record> index = client.initIndex("INDEX_NAME", Record.class);
SearchResult<Record> results = index.search(new Query("QUERY"));

// version 4
var results = client.searchSingleIndex(
    "INDEX_NAME",
    new SearchParamsObject().setQuery("QUERY"),
    Hit.class
);
```

### Search multiple indices

The `client.multipleQueries()` method is now `client.search()`.
Each request in the list requires an `indexName`:

```java
// version 3
client.multipleQueries(Arrays.asList(
    new IndexQuery("INDEX_1", new Query("QUERY")),
    new IndexQuery("INDEX_2", new Query("QUERY"))
));

// version 4
var results = client.search(
    new SearchMethodParams().setRequests(Arrays.asList(
        new SearchForHits().setIndexName("INDEX_1").setQuery("QUERY"),
        new SearchForHits().setIndexName("INDEX_2").setQuery("QUERY")
    )),
    Hit.class
);
```

### Search for facet values

The `index.searchForFacetValues()` method becomes `client.searchForFacetValues()`
with an `indexName` parameter:

```java
// version 3
SearchIndex<Record> index = client.initIndex("INDEX_NAME", Record.class);
index.searchForFacetValues("category", "book", new Query());

// version 4
var results = client.searchForFacetValues(
    "INDEX_NAME",
    "category",
    new SearchForFacetValuesRequest().setFacetQuery("book")
);
```

## Update indexing operations

In version 4, indexing methods are on the client instead of the index object,
with `indexName` as a parameter.

### Add or replace records

```java
// version 3
SearchIndex<Record> index = client.initIndex("INDEX_NAME", Record.class);
index.saveObject(record);
index.saveObjects(records);

// version 4
client.saveObject("INDEX_NAME", record);
// saveObjects works the same way:
client.saveObjects("INDEX_NAME", records);
```

### Partially update records

```java
// version 3
SearchIndex<Record> index = client.initIndex("INDEX_NAME", Record.class);
index.partialUpdateObject(new Record().setObjectID("1").setName("Updated"));

// version 4
client.partialUpdateObject(
    "INDEX_NAME",
    "1",
    Map.of("name", "Updated")
);
```

### Delete records

```java
// version 3
SearchIndex<Record> index = client.initIndex("INDEX_NAME", Record.class);
index.deleteObject("1");

// version 4
client.deleteObject("INDEX_NAME", "1");
```

## Update settings, synonyms, and rules

### Get and set settings

```java
// version 3
SearchIndex<Record> index = client.initIndex("INDEX_NAME", Record.class);
IndexSettings settings = index.getSettings();
index.setSettings(new IndexSettings().setSearchableAttributes(Arrays.asList("title", "author")));

// version 4
SettingsResponse settings = client.getSettings("INDEX_NAME");
client.setSettings(
    "INDEX_NAME",
    new IndexSettings().setSearchableAttributes(Arrays.asList("title", "author"))
);
```

### Save synonyms and rules

```java
// version 3
SearchIndex<Record> index = client.initIndex("INDEX_NAME", Record.class);
index.saveSynonyms(synonymsList);
index.saveRules(rulesList);

// version 4
client.saveSynonyms("INDEX_NAME", synonymsList);
client.saveRules("INDEX_NAME", rulesList);
```

  In version 3, `index.replaceAllRules()` and `index.replaceAllSynonyms()` replaced all rules or synonyms.
  In version 4, use `client.saveRules()` or `client.saveSynonyms()` with the `clearExistingRules` or `clearExistingSynonyms` parameter set to `true`.

## Update index management

The `copyIndex`, `moveIndex`, `copyRules`, `copySynonyms`, and `copySettings`
methods are all replaced by a single `operationIndex` method.

### Copy an index

```java
// version 3
client.copyIndex("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME");

// version 4
client.operationIndex(
    "SOURCE_INDEX_NAME",
    new OperationIndexParams().setOperation(OperationType.COPY).setDestination("DESTINATION_INDEX_NAME")
);
```

### Move (rename) an index

```java
// version 3
client.moveIndex("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME");

// version 4
client.operationIndex(
    "SOURCE_INDEX_NAME",
    new OperationIndexParams().setOperation(OperationType.MOVE).setDestination("DESTINATION_INDEX_NAME")
);
```

### Copy only rules or settings

In version 4, use the `scope` parameter to limit the operation to specific data:

```java
// version 4: copy only rules and settings from one index to another
client.operationIndex(
    "SOURCE_INDEX_NAME",
    new OperationIndexParams()
        .setOperation(OperationType.COPY)
        .setDestination("DESTINATION_INDEX_NAME")
        .setScope(Arrays.asList(ScopeType.RULES, ScopeType.SETTINGS))
);
```

### Check if an index exists

In version 3, you could check if an index existed using the `exists` method on the index object.
In version 4, use the `indexExists` helper method on the client:

```java
// version 3
SearchIndex<Record> index = client.initIndex("INDEX_NAME", Record.class);
index.exists();

// version 4
client.indexExists("INDEX_NAME");
```

## Update task handling

Version 3 supported chaining `.waitTask()` on operations.
Version 4 replaces this pattern with dedicated wait helpers.

```java
// version 3
SearchIndex<Record> index = client.initIndex("INDEX_NAME", Record.class);
index.saveObject(record).waitTask();

// version 4
var response = client.saveObject("INDEX_NAME", record);
client.waitForTask("INDEX_NAME", response.getTaskID());
```

Version 4 includes three wait helpers:

* `waitForTask`: wait until indexing operations are done.
* `waitForAppTask`: wait for application-level tasks.
* `waitForApiKey`: wait for API key operations.

## Helper method changes

The following sections document breaking changes in helper method signatures and behavior between version 3 and version 4.

### `replaceAllObjects`

The `safe` parameter has been removed. In version 3, passing `safe = true` caused the helper to wait after each step. In version 4, the helper always waits—equivalent to the previous `safe = true` behavior.

The `scopes` parameter is optional. When omitted, it defaults to all three: `SETTINGS`, `RULES`, and `SYNONYMS`.

```java
// version 3
index.replaceAllObjects(objects, true);

// version 4
client.replaceAllObjects("INDEX_NAME", objects);
```

### `saveObjects`

The `autoGenerateObjectID` parameter has been removed. In version 4, every object must include an `objectID`. To have the API generate object IDs, use `chunkedBatch` with `Action.ADD_OBJECT`. Two new optional parameters are available:

* `waitForTasks` (default `false`)
* `batchSize` (default `1,000`)

```java
// version 3
index.saveObjects(objects, true);

// version 4
// Objects must include objectID, or use chunkedBatch with Action.ADD_OBJECT
client.saveObjects("INDEX_NAME", objects);

// With wait:
client.saveObjects("INDEX_NAME", objects, true, null);
```

### `deleteObjects`

Two new optional parameters are available:

* `waitForTasks` (default `false`)
* `batchSize` (default `1,000`)

```java
// version 3
index.deleteObjects(Arrays.asList("id1", "id2"));

// version 4
client.deleteObjects("INDEX_NAME", Arrays.asList("id1", "id2"));

// With wait:
client.deleteObjects("INDEX_NAME", Arrays.asList("id1", "id2"), true, null);
```

### `partialUpdateObjects`

The `createIfNotExists` parameter is now required—the overload without it has been removed (it previously defaulted to `false`).

```java
// version 3
// createIfNotExists defaulted to false when omitted
index.partialUpdateObjects(objects);
index.partialUpdateObjects(objects, true);

// version 4
// createIfNotExists is now required
client.partialUpdateObjects("INDEX_NAME", objects, true);
```

### `browseObjects`, `browseRules`, `browseSynonyms`

These helpers no longer return iterable types (`IndexIterable`, `RulesIterable`, `SynonymsIterable`). In version 4, they return a lazy `Iterable<T>` that you can iterate or stream directly.

```java
// version 3
for (MyObject obj : index.browseObjects(new BrowseIndexQuery("query"))) {
    process(obj);
}

// version 4
List<MyObject> objects = new ArrayList<>();
client.browseObjects("INDEX_NAME", new BrowseParamsObject(), MyObject.class)
    .forEach(objects::add);
```

### `waitForTask`

The helper was renamed from `waitTask` to `waitForTask`. It now returns `GetTaskResponse` instead of `void`, and the `timeToWait` millisecond parameter is replaced by `maxRetries` (default `50`) and a `timeout` function (default: exponential backoff capped at 5 seconds).

```java
// version 3
// Returns void; flat timeToWait in milliseconds
index.waitTask(taskId, 100L);

// version 4
// Returns GetTaskResponse; exponential backoff by default
GetTaskResponse response = client.waitForTask("INDEX_NAME", taskId);

// With explicit retry controls:
client.waitForTask("INDEX_NAME", taskId, 50,
    retries -> Math.min(retries * 200, 5000));
```

### `waitForAppTask`

This is a new helper in version 4.

```java
GetTaskResponse response = client.waitForAppTask(taskId);
```

### `waitForApiKey`

This is a new standalone helper in version 4.

```java
// Wait for a key to be created:
client.waitForApiKey("my-api-key", ApiKeyOperation.ADD);

// Wait for a key update (pass the expected final state):
client.waitForApiKey("my-api-key", ApiKeyOperation.UPDATE,
    new ApiKey().setAcl(Arrays.asList(Acl.SEARCH)));
```

### `generateSecuredApiKey`

The method was renamed from `generateSecuredAPIKey` to `generateSecuredApiKey` (camelCase normalization). The parameter type also changed from `SecuredApiKeyRestriction` (singular) to `SecuredApiKeyRestrictions` (plural).

```java
// version 3
String key = client.generateSecuredAPIKey("parentApiKey",
    new SecuredApiKeyRestriction().setValidUntil(1893456000L));

// version 4
String key = client.generateSecuredApiKey("parentApiKey",
    new SecuredApiKeyRestrictions().setValidUntil(1893456000L));
```

### `getSecuredApiKeyRemainingValidity`

The parameter was renamed from `securedAPIKey` to `securedApiKey` (camelCase normalization).

```java
// version 3
Duration remaining = client.getSecuredApiKeyRemainingValidity(securedAPIKey);

// version 4
Duration remaining = client.getSecuredApiKeyRemainingValidity(securedApiKey);
```

### `indexExists`

This helper is new in version 4.

```java
boolean exists = client.indexExists("INDEX_NAME");
```

### `chunkedBatch`

`chunkedBatch` is now a public helper. In version 3, chunking was an internal detail of `saveObjects`.

```java
List<BatchResponse> responses = client.chunkedBatch(
    "INDEX_NAME", objects, Action.ADD_OBJECT, true);
```

### `copyIndexBetweenApplications`

In version 3, the static `AccountClient` class provided `copyIndex` and `copyIndexAsync` for copying an index between two Algolia applications. It accepted two typed `SearchIndex<T>` objects.

In version 4, `AccountClient` is removed. You can compose existing helpers across two clients to achieve the same result.

```java
// version 3
MultiResponse response = AccountClient.copyIndex(sourceIndex, destinationIndex);

// version 4
SearchClient src = new SearchClient("SRC_APP_ID", "SRC_API_KEY");
SearchClient dst = new SearchClient("DST_APP_ID", "DST_API_KEY");

// Copy settings
SettingsResponse settingsResp = src.getSettings("SOURCE_INDEX");
IndexSettings indexSettings = new ObjectMapper().convertValue(settingsResp, IndexSettings.class);
dst.setSettings("DEST_INDEX", indexSettings);

// Copy rules
List<Rule> rules = new ArrayList<>();
src.browseRules("SOURCE_INDEX").forEach(rules::add);
if (!rules.isEmpty()) dst.saveRules("DEST_INDEX", rules);

// Copy synonyms
List<SynonymHit> synonyms = new ArrayList<>();
src.browseSynonyms("SOURCE_INDEX").forEach(synonyms::add);
if (!synonyms.isEmpty()) dst.saveSynonyms("DEST_INDEX", synonyms);

// Copy objects
List<MyModel> objects = new ArrayList<>();
src.browseObjects("SOURCE_INDEX", MyModel.class).forEach(objects::add);
dst.replaceAllObjects("DEST_INDEX", objects);
```

### `saveObjectsWithTransformation`

New in version 4. Routes objects through the Algolia Push connector. Requires the transformation region to be set at client initialization.

```java
List<WatchResponse> responses = client.saveObjectsWithTransformation(
    "INDEX_NAME", objects, true);
```

### `replaceAllObjectsWithTransformation`

New in version 4. Atomically replaces all objects via the Push connector (copy settings/rules/synonyms to a temp index → push objects → move back). Requires the transformation region to be set at client initialization.

```java
ReplaceAllObjectsWithTransformationResponse response =
    client.replaceAllObjectsWithTransformation("INDEX_NAME", objects, 1000,
        Arrays.asList(ScopeType.SETTINGS, ScopeType.RULES, ScopeType.SYNONYMS));
```

### `partialUpdateObjectsWithTransformation`

New in version 4. Routes partial updates through the Push connector. The `createIfNotExists` parameter defaults to `false`.

```java
List<WatchResponse> responses =
    client.partialUpdateObjectsWithTransformation(
        "INDEX_NAME", objects, false, false, 1000);
```

## Method changes reference

The following tables list all method names that changed between version 3 and version 4.

### Search API client

| Version 3 (legacy)                         |   | Version 4 (current)                        |
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

| Version 3 (legacy)                   |   | Version 4 (current)         |
| ------------------------------------ | - | --------------------------- |
| `client.getFrequentlyBoughtTogether` | → | `client.getRecommendations` |
| `client.getRecommendations`          | → | `client.getRecommendations` |
| `client.getRelatedProducts`          | → | `client.getRecommendations` |
