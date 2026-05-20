# Java: v3 → v4

## Dependency changes

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

// v4 — use try-with-resources; client implements Closeable
try (var client = new SearchClient("APP_ID", "API_KEY")) {
    // ...
}
```

`DefaultSearchClient.create()` factory method is removed.

## `initIndex` removal

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
| `index.search()` | `client.searchSingleIndex()` |
| `client.multipleQueries()` | `client.search()` |
| `index.searchForFacetValues()` | `client.searchForFacetValues()` |
| `index.saveObject()` | `client.saveObject("INDEX_NAME", obj)` |
| `index.partialUpdateObject()` | `client.partialUpdateObject()` |
| `index.deleteObject()` | `client.deleteObject()` |
| `index.getSettings()` | `client.getSettings("INDEX_NAME")` |
| `index.setSettings()` | `client.setSettings()` |
| `replaceAllRules()` / `replaceAllSynonyms()` | `saveRules()` / `saveSynonyms()` with `clearExisting*` |
| `copyIndex()` / `moveIndex()` / `copyRules()` etc. | `client.operationIndex()` |
| `index.exists()` | `client.indexExists("INDEX_NAME")` |
| `index.{op}.waitTask()` | `client.waitForTask()` |
| `waitTask()` | `waitForTask()` |

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

## Settings, synonyms, rules

```java
IndexSettings settings = client.getSettings("INDEX_NAME");
client.setSettings("INDEX_NAME", new IndexSettings().setSearchableAttributes(List.of("title")));

client.saveSynonyms("INDEX_NAME", synonymsList);
client.saveRules("INDEX_NAME", rulesList);
```

## `operationIndex` (copy / move)

```java
// copy
client.operationIndex("SOURCE",
    new OperationIndexParams()
        .setOperation(OperationType.COPY)
        .setDestination("DEST"));

// move / rename
client.operationIndex("SOURCE",
    new OperationIndexParams()
        .setOperation(OperationType.MOVE)
        .setDestination("DEST"));
```

## Wait pattern

```java
// v3
index.saveObject(record).waitTask();

// v4
var response = client.saveObject("INDEX_NAME", record);
client.waitForTask("INDEX_NAME", response.getTaskID());
```

`waitForTask` returns `GetTaskResponse`. Optional controls:
```java
client.waitForTask("INDEX_NAME", taskId, 50,
    retries -> Math.min(retries * 200L, 5000L));
```

Three helpers: `waitForTask`, `waitForAppTask`, `waitForApiKey`.

## `replaceAllObjects`

```java
client.replaceAllObjects(
    "INDEX_NAME",
    objects,
    1000,
    List.of(ScopeType.SETTINGS, ScopeType.RULES, ScopeType.SYNONYMS)
);
```

## Helper changes

- `saveObjects`: `autoGenerateObjectID` removed; objects must include `objectID`. Optional: `waitForTasks` (bool), `batchSize` (int)
- `partialUpdateObjects`: `createIfNotExists` required (no default)
- `browseObjects`: returns `Iterable<T>` — use a for-each loop, no aggregator callback

## Browse (Iterable pattern)

```java
for (MyObject hit : client.browseObjects("INDEX_NAME", new BrowseParamsObject(), MyObject.class)) {
    objects.add(hit);
}
```

## `chunkedBatch` (now public)

```java
List<BatchResponse> responses = client.chunkedBatch(
    "INDEX_NAME", objects, Action.ADD_OBJECT, true);
```

## Secured API key

```java
// generateSecuredAPIKey → generateSecuredApiKey
// SecuredApiKeyRestriction → SecuredApiKeyRestrictions
String key = client.generateSecuredApiKey("parentKey",
    new SecuredApiKeyRestrictions().setValidUntil(1893456000L));
```

## Cross-app copy (`AccountClient` removed)

```java
SearchClient src = new SearchClient("SRC_APP_ID", "SRC_API_KEY");
SearchClient dst = new SearchClient("DST_APP_ID", "DST_API_KEY");

IndexSettings settings = src.getSettings("SOURCE_INDEX");
dst.setSettings("DEST_INDEX", settings);
// repeat for rules, synonyms, then records via browseObjects + saveObjects
```

## Transformation helpers (new in v4)

```java
client.saveObjectsWithTransformation("INDEX_NAME", objects, true);
client.replaceAllObjectsWithTransformation("INDEX_NAME", objects);
```
