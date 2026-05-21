# Java: v3 → v4

## Dependencies

**Maven — replace two artifacts with one:**
```xml
<!-- Remove -->
<dependency>
  <groupId>com.algolia</groupId>
  <artifactId>algoliasearch-core</artifactId>
</dependency>
<dependency>
  <groupId>com.algolia</groupId>
  <artifactId>algoliasearch-apache</artifactId>
</dependency>

<!-- Add -->
<dependency>
  <groupId>com.algolia</groupId>
  <artifactId>algoliasearch</artifactId>
  <version>VERSION</version>
</dependency>
```

**Gradle:**
```groovy
implementation 'com.algolia:algoliasearch:VERSION'
```

## Import changes

```java
// v3
import com.algolia.search.DefaultSearchClient;
import com.algolia.search.SearchClient;
import com.algolia.search.SearchIndex;

// v4
import com.algolia.api.SearchClient;
import com.algolia.api.RecommendClient;
import com.algolia.api.AbtestingClient;
import com.algolia.model.search.*;
```

## Client initialization

```java
// v3
SearchClient client = DefaultSearchClient.create("APP_ID", "API_KEY");

// v4 — DefaultSearchClient.create() removed; client implements Closeable
try (var client = new SearchClient("APP_ID", "API_KEY")) {
    // ...
}
```

## Remove `initIndex`

```java
// v3
SearchIndex<Record> index = client.initIndex("INDEX_NAME", Record.class);
index.search(new Query("QUERY"));

// v4 — generic type passed per-method, not at init
var results = client.searchSingleIndex(
    "INDEX_NAME",
    new SearchParamsObject().setQuery("QUERY"),
    Hit.class
);
```

## Method renames

| v3 | v4 |
|----|----|
| `DefaultSearchClient.create()` | `new SearchClient()` |
| `client.multipleQueries()` | `client.search()` |
| `index.search()` | `client.searchSingleIndex("INDEX_NAME", ...)` |
| `index.exists()` | `client.indexExists("INDEX_NAME")` |
| `index.replaceAllRules()` | `client.saveRules()` with `clearExistingRules` |
| `index.replaceAllSynonyms()` | `client.saveSynonyms()` with `clearExistingSynonyms` |
| `copyIndex()` / `moveIndex()` | `client.operationIndex()` |
| `index.{op}.waitTask()` | `client.waitForTask()` |
| `waitTask()` | `waitForTask()` |
| `generateSecuredAPIKey()` | `generateSecuredApiKey()` |

## Multiple index search

```java
var results = client.search(
    new SearchMethodParams().setRequests(Arrays.asList(
        new SearchForHits().setIndexName("INDEX_1").setQuery("QUERY"),
        new SearchForHits().setIndexName("INDEX_2").setQuery("QUERY")
    )),
    Hit.class
);
```

## Indexing

```java
client.saveObject("INDEX_NAME", record);
client.partialUpdateObject("INDEX_NAME", "1", Map.of("name", "Updated"));
client.deleteObject("INDEX_NAME", "1");
```

## `operationIndex` (copy / move)

```java
// copy
client.operationIndex("SOURCE",
    new OperationIndexParams().setOperation(OperationType.COPY).setDestination("DEST"));

// move
client.operationIndex("SOURCE",
    new OperationIndexParams().setOperation(OperationType.MOVE).setDestination("DEST"));

// copy with scope
client.operationIndex("SOURCE",
    new OperationIndexParams().setOperation(OperationType.COPY).setDestination("DEST")
        .setScope(Arrays.asList(ScopeType.RULES, ScopeType.SETTINGS)));

// check if index exists (new in v4)
client.indexExists("INDEX_NAME");
```

## Wait pattern

```java
// v3
index.saveObject(record).waitTask();

// v4
var response = client.saveObject("INDEX_NAME", record);
client.waitForTask("INDEX_NAME", response.getTaskID());

// with controls
client.waitForTask("INDEX_NAME", taskId, 50, retries -> Math.min(retries * 200L, 5000L));

// new helpers
client.waitForAppTask(taskId);
client.waitForApiKey("my-api-key", ApiKeyOperation.ADD);
client.waitForApiKey("my-api-key", ApiKeyOperation.UPDATE,
    new ApiKey().setAcl(Arrays.asList(Acl.SEARCH)));
```

## Helper method changes

- **`replaceAllObjects`**: `safe` removed; uses `ReplaceAllObjectsParams` builder:
```java
client.replaceAllObjects(new ReplaceAllObjectsParams()
    .setIndexName("INDEX_NAME").setObjects(objects)
    .setScopes(Arrays.asList(ScopeType.SETTINGS, ScopeType.RULES, ScopeType.SYNONYMS)));
```
- **`saveObjects`**: `autoGenerateObjectID` removed; objects must include `objectID`; new optional `waitForTasks` and `batchSize`:
```java
client.saveObjects("INDEX_NAME", objects);
client.saveObjects("INDEX_NAME", objects, true); // wait for tasks
```
- **`partialUpdateObjects`**: `createIfNotExists` required (no default):
```java
client.partialUpdateObjects("INDEX_NAME", objects, true);
```
- **`deleteObjects`**: new `waitForTasks` and `batchSize`:
```java
client.deleteObjects("INDEX_NAME", Arrays.asList("id1", "id2"));
client.deleteObjects("INDEX_NAME", Arrays.asList("id1", "id2"), true); // wait
```
- **`browseObjects` / `browseRules` / `browseSynonyms`**: iterable types removed; use aggregator callback:
```java
// v3 — for-each
for (MyObject obj : index.browseObjects(new BrowseIndexQuery("query"))) { process(obj); }

// v4 — aggregator callback
List<Object> objects = new ArrayList<>();
client.browseObjects("INDEX_NAME", new BrowseParamsObject(), MyObject.class,
    response -> objects.addAll(response.getHits()));
```
- **`generateSecuredApiKey`**: renamed from `generateSecuredAPIKey`; `SecuredApiKeyRestriction` → `SecuredApiKeyRestrictions` (plural):
```java
String key = client.generateSecuredApiKey("parentKey",
    new SecuredApiKeyRestrictions().setValidUntil(1893456000L));
```
- **`chunkedBatch`** (now public):
```java
client.chunkedBatch("INDEX_NAME", objects, Action.ADD_OBJECT, true);
```

## Cross-app copy (`AccountClient` removed)

```java
SearchClient src = new SearchClient("SRC_APP_ID", "SRC_API_KEY");
SearchClient dst = new SearchClient("DST_APP_ID", "DST_API_KEY");

IndexSettings settings = src.getSettings("SOURCE_INDEX");
dst.setSettings("DEST_INDEX", settings);

List<Rule> rules = new ArrayList<>();
src.browseRules("SOURCE_INDEX", Rule.class, r -> rules.addAll(r.getHits()));
if (!rules.isEmpty()) dst.saveRules("DEST_INDEX", rules);

// repeat for synonyms, then browseObjects + replaceAllObjects
```

## Transformation helpers (new in v4)

```java
client.saveObjectsWithTransformation("INDEX_NAME", objects, true);
client.replaceAllObjectsWithTransformation("INDEX_NAME", objects);
client.partialUpdateObjectsWithTransformation("INDEX_NAME", objects, true);
```

## Method changes reference

| v3 | v4 |
|----|----|
| `DefaultSearchClient.create()` | `new SearchClient("APP_ID", "API_KEY")` |
| `client.multipleQueries()` | `client.search()` |
| `client.copyIndex()` | `client.operationIndex()` |
| `client.moveIndex()` | `client.operationIndex()` |
| `client.generateSecuredAPIKey()` | `client.generateSecuredApiKey()` |
| `index.batch()` | `client.batch("INDEX_NAME", ...)` |
| `index.browseObjects()` | `client.browseObjects("INDEX_NAME", ..., aggregator)` |
| `index.browseRules()` | `client.browseRules("INDEX_NAME", ...)` |
| `index.browseSynonyms()` | `client.browseSynonyms("INDEX_NAME", ...)` |
| `index.clearObjects()` | `client.clearObjects("INDEX_NAME")` |
| `index.clearRules()` | `client.clearRules("INDEX_NAME")` |
| `index.clearSynonyms()` | `client.clearSynonyms("INDEX_NAME")` |
| `index.delete()` | `client.deleteIndex("INDEX_NAME")` |
| `index.deleteBy()` | `client.deleteBy("INDEX_NAME", ...)` |
| `index.deleteObject()` | `client.deleteObject("INDEX_NAME", id)` |
| `index.deleteObjects()` | `client.deleteObjects("INDEX_NAME", ids)` |
| `index.deleteRule()` | `client.deleteRule("INDEX_NAME", id)` |
| `index.deleteSynonym()` | `client.deleteSynonym("INDEX_NAME", id)` |
| `index.exists()` | `client.indexExists("INDEX_NAME")` |
| `index.getObject()` | `client.getObject("INDEX_NAME", id, ...)` |
| `index.getObjects()` | `client.getObjects(...)` |
| `index.getRule()` | `client.getRule("INDEX_NAME", id)` |
| `index.getSettings()` | `client.getSettings("INDEX_NAME")` |
| `index.getSynonym()` | `client.getSynonym("INDEX_NAME", id)` |
| `index.getTask()` | `client.getTask("INDEX_NAME", taskId)` |
| `index.partialUpdateObject()` | `client.partialUpdateObject("INDEX_NAME", ...)` |
| `index.partialUpdateObjects()` | `client.partialUpdateObjects("INDEX_NAME", ...)` |
| `index.replaceAllObjects()` | `client.replaceAllObjects(...)` |
| `index.replaceAllRules()` | `client.saveRules("INDEX_NAME", rules)` |
| `index.replaceAllSynonyms()` | `client.saveSynonyms("INDEX_NAME", synonyms)` |
| `index.saveObject()` | `client.saveObject("INDEX_NAME", obj)` |
| `index.saveObjects()` | `client.saveObjects("INDEX_NAME", objs)` |
| `index.saveRule()` | `client.saveRule("INDEX_NAME", ...)` |
| `index.saveRules()` | `client.saveRules("INDEX_NAME", rules)` |
| `index.saveSynonym()` | `client.saveSynonym("INDEX_NAME", ...)` |
| `index.saveSynonyms()` | `client.saveSynonyms("INDEX_NAME", synonyms)` |
| `index.search()` | `client.searchSingleIndex("INDEX_NAME", ...)` |
| `index.searchForFacetValues()` | `client.searchForFacetValues("INDEX_NAME", ...)` |
| `index.searchRules()` | `client.searchRules("INDEX_NAME", ...)` |
| `index.searchSynonyms()` | `client.searchSynonyms("INDEX_NAME", ...)` |
| `index.setSettings()` | `client.setSettings("INDEX_NAME", ...)` |
| `index.{op}.waitTask()` | `client.waitForTask("INDEX_NAME", taskId)` |

Recommend API renames:

| v3 | v4 |
|----|----|
| `recommend.getFrequentlyBoughtTogether()` | `recommend.getRecommendations()` |
| `recommend.getRelatedProducts()` | `recommend.getRecommendations()` |
