# Kotlin: v2 → v3

## Dependency

```groovy
// v2
implementation("com.algolia:algoliasearch-client-kotlin:2.x.x")

// v3
implementation("com.algolia:algoliasearch-client-kotlin:3.+")
```

## Import changes

Package moved from `com.algolia.search` to `com.algolia.client`. Type wrappers (`ApplicationID`, `APIKey`, `IndexName`, `ObjectID`) are eliminated — use plain strings.

```kotlin
// v2 (removed)
import com.algolia.search.model.ApplicationID
import com.algolia.search.model.APIKey
import com.algolia.search.model.IndexName
import com.algolia.search.dsl.query
import com.algolia.search.dsl.settings

// v3
import com.algolia.client.api.SearchClient
import com.algolia.client.model.search.*
```

## Client initialization

`ClientSearch` is renamed to `SearchClient`:

```kotlin
// v2
val client = ClientSearch(ApplicationID("APP_ID"), APIKey("API_KEY"))

// v3
val client = SearchClient(appId = "APP_ID", apiKey = "API_KEY")
```

## Remove `initIndex`

v3 has no index object. Pass `indexName` to every client method. The query DSL is also removed — use typed data classes:

```kotlin
// v2
val index = client.initIndex(IndexName("INDEX_NAME"))
index.search(query { query = "QUERY" })

// v3
client.searchSingleIndex(
    indexName = "INDEX_NAME",
    searchParamsObject = SearchParamsObject(query = "QUERY")
)
```

DSL replacement examples:

```kotlin
// v2 — query DSL
val query = query {
    attributesToRetrieve { +"color" }
    filters { and { facet("color", "red") } }
}

// v3 — data class + filter string
val params = SearchParamsObject(
    query = "QUERY",
    attributesToRetrieve = listOf("color"),
    filters = "color:red"
)

// v2 — settings DSL
val settings = settings { searchableAttributes { +"title"; +"author" } }

// v3 — data class
val settings = IndexSettings(searchableAttributes = listOf("title", "author"))
```

## Method renames

| v2 | v3 |
|----|----|
| `index.search()` | `client.searchSingleIndex()` |
| `client.multipleQueries()` | `client.search()` |
| `index.searchForFacets()` | `client.searchForFacetValues()` |
| `index.saveObject()` | `client.saveObject(indexName, body)` |
| `index.partialUpdateObject()` | `client.partialUpdateObject(indexName, objectID, attrs)` |
| `index.deleteObject()` | `client.deleteObject(indexName, objectID)` |
| `index.replaceAllRules()` | `client.saveRules()` |
| `index.replaceAllSynonyms()` | `client.saveSynonyms()` |
| `client.copyIndex()` / `moveIndex()` | `client.operationIndex()` |
| `index.exists()` | `client.indexExists(indexName)` |
| `index.waitTask()` | `client.waitForTask(indexName, taskID)` |
| `ClientAccount.copyIndex()` | compose across two clients manually |
| `generateAPIKey` | `generateSecuredApiKey` |
| `getSecuredApiKeyRemainingValidity` (on client) | `securedApiKeyRemainingValidity` (top-level fn) |

## Multiple index search

```kotlin
val results = client.search(
    searchMethodParams = SearchMethodParams(
        requests = listOf(
            SearchForHits(indexName = "INDEX_1", query = "QUERY"),
            SearchForHits(indexName = "INDEX_2", query = "QUERY")
        )
    )
)
```

## Indexing

```kotlin
// objectID is a plain String, not ObjectID()
client.saveObject(
    indexName = "INDEX_NAME",
    body = buildJsonObject { put("objectID", "1"); put("name", "Record") }
)

client.partialUpdateObject(
    indexName = "INDEX_NAME",
    objectID = "1",
    attributesToUpdate = buildJsonObject { put("name", "Updated") }
)

client.deleteObject(indexName = "INDEX_NAME", objectID = "1")
```

## `operationIndex` (copy / move)

```kotlin
client.operationIndex(
    indexName = "SOURCE",
    operationIndexParams = OperationIndexParams(
        operation = OperationType.entries.first { it.value == "copy" },
        destination = "DEST"
    )
)
```

## Wait pattern

```kotlin
// v2
index.saveObjects(Contact.serializer(), records).wait()

// v3
val response = client.saveObject(indexName = "INDEX_NAME", body = record)
client.waitForTask(indexName = "INDEX_NAME", taskID = response.taskID)
```

`taskID` is a `Long`, not the v2 `TaskID` wrapper type.

## Helper method changes

**`replaceAllObjects`** — serializer dropped; objects as `List<JsonObject>`; `scopes` required:

```kotlin
client.replaceAllObjects(
    indexName = "INDEX_NAME",
    objects = myObjects.map { Json.encodeToJsonElement(it).jsonObject },
    scopes = listOf(ScopeType.Settings, ScopeType.Rules, ScopeType.Synonyms)
)
```

**`saveObjects` / `deleteObjects`** — serializer dropped; `waitForTasks` available:

```kotlin
client.saveObjects(
    indexName = "INDEX_NAME",
    objects = myObjects.map { Json.encodeToJsonElement(it).jsonObject },
    waitForTasks = true
)
client.deleteObjects(indexName = "INDEX_NAME", objectIDs = listOf("id1", "id2"), waitForTasks = true)
```

**`partialUpdateObjects`** — `createIfNotExists` is now required (no default):

```kotlin
client.partialUpdateObjects(
    indexName = "INDEX_NAME",
    objects = myObjects.map { Json.encodeToJsonElement(it).jsonObject },
    createIfNotExists = true
)
```

**`browseObjects`** — uses aggregator callback; `browseRules`/`browseSynonyms` have no dedicated extension helpers in v3 — paginate via `searchRules`/`searchSynonyms`:

```kotlin
val hits = mutableListOf<JsonObject>()
client.browseObjects(
    indexName = "INDEX_NAME",
    params = BrowseParamsObject(),
    aggregator = { response -> hits.addAll(response.hits) }
)
```

**`generateSecuredApiKey`** — returns plain `String`, not `APIKey`:

```kotlin
// v2
val key: APIKey = client.generateAPIKey(
    parentApiKey = APIKey("parentApiKey"),
    restriction = SecuredAPIKeyRestriction(validUntil = 1893456000)
)

// v3
val key: String = client.generateSecuredApiKey(
    parentApiKey = "parentApiKey",
    restrictions = SecuredApiKeyRestrictions(validUntil = 1893456000)
)

// remaining validity is now a top-level function
val remaining: Duration = securedApiKeyRemainingValidity("my-key")
```

## Method changes reference

| v2 | v3 |
|----|----|
| `ClientSearch(ApplicationID, APIKey)` | `SearchClient(appId, apiKey)` |
| `client.initIndex()` | removed — pass `indexName` to each method |
| `index.search()` | `client.searchSingleIndex()` |
| `client.multipleQueries()` | `client.search()` |
| `index.searchForFacets()` | `client.searchForFacetValues()` |
| `index.saveObject()` | `client.saveObject(indexName, body)` |
| `index.saveObjects(serializer, objects)` | `client.saveObjects(indexName, objects)` |
| `index.partialUpdateObject()` | `client.partialUpdateObject()` |
| `index.partialUpdateObjects()` | `client.partialUpdateObjects(createIfNotExists = ...)` |
| `index.deleteObject()` | `client.deleteObject()` |
| `index.deleteObjects()` | `client.deleteObjects()` |
| `index.replaceAllObjects(serializer, objects)` | `client.replaceAllObjects(objects, scopes)` |
| `index.replaceAllRules()` | `client.saveRules()` |
| `index.replaceAllSynonyms()` | `client.saveSynonyms()` |
| `index.getSettings()` | `client.getSettings()` |
| `index.setSettings()` | `client.setSettings()` |
| `index.searchRules()` | `client.searchRules()` |
| `index.searchSynonyms()` | `client.searchSynonyms()` |
| `index.exists()` | `client.indexExists()` |
| `index.waitTask(TaskID)` | `client.waitForTask(indexName, taskID: Long)` |
| `client.copyIndex()` / `moveIndex()` | `client.operationIndex()` |
| `ClientAccount.copyIndex()` | compose manually across two `SearchClient` instances |
| `generateAPIKey` | `generateSecuredApiKey` (returns `String`) |
| `getSecuredApiKeyRemainingValidity` (client method) | `securedApiKeyRemainingValidity` (top-level fn) |
