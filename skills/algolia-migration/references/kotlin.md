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
import com.algolia.search.model.ObjectID
import com.algolia.search.dsl.query
import com.algolia.search.dsl.settings

// v3
import com.algolia.client.api.SearchClient
import com.algolia.client.model.search.*
```

## Client initialization

```kotlin
// v2
val client = ClientSearch(
    ApplicationID("APP_ID"),
    APIKey("API_KEY")
)

// v3 — class renamed; plain strings
val client = SearchClient(
    appId = "APP_ID",
    apiKey = "API_KEY"
)
```

## `initIndex` removal

```kotlin
// v2
val index = client.initIndex(IndexName("INDEX_NAME"))
index.search(Query("QUERY"))

// v3
client.searchSingleIndex(
    indexName = "INDEX_NAME",
    searchParamsObject = SearchParamsObject(query = "QUERY")
)
```

## DSL replacement

v3 uses plain data classes instead of DSL builders:

```kotlin
// v2 — query DSL
val query = query {
    attributesToRetrieve { +"color"; +"category" }
    filters { and { facet("color", "red") } }
}

// v3 — data class + filter string
val params = SearchParamsObject(
    query = "QUERY",
    attributesToRetrieve = listOf("color", "category"),
    filters = "color:red"
)
```

```kotlin
// v2 — settings DSL
val settings = settings { searchableAttributes { +"title"; +"author" } }

// v3 — data class
val settings = IndexSettings(
    searchableAttributes = listOf("title", "author")
)
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
| `client.copyIndex()` / `moveIndex()` | `client.operationIndex()` |
| `index.exists()` | `client.indexExists(indexName)` |
| `index.waitTask()` | `client.waitForTask(indexName, taskID)` |
| `ClientAccount.copyIndex()` | compose across two clients manually |
| `generateAPIKey` | `generateSecuredApiKey` |
| `getSecuredApiKeyRemainingValidity` (on client) | `securedApiKeyRemainingValidity` (top-level function) |

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
// objectID is now a plain String, not ObjectID()
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

## `replaceAllObjects`

```kotlin
// v3 — serializer dropped; objects as List<JsonObject>; scopes required
client.replaceAllObjects(
    indexName = "INDEX_NAME",
    objects = myObjects.map { Json.encodeToJsonElement(it).jsonObject },
    scopes = listOf(ScopeType.Settings, ScopeType.Rules, ScopeType.Synonyms)
)
```

## `saveObjects` / `deleteObjects`

```kotlin
// v3 — serializer dropped; waitForTasks available
client.saveObjects(
    indexName = "INDEX_NAME",
    objects = myObjects.map { Json.encodeToJsonElement(it).jsonObject },
    waitForTasks = true
)

client.deleteObjects(
    indexName = "INDEX_NAME",
    objectIDs = listOf("id1", "id2"),
    waitForTasks = true
)
```

## `partialUpdateObjects` — `createIfNotExists` required

```kotlin
// v2 defaulted to true; v3 requires explicit value
client.partialUpdateObjects(
    indexName = "INDEX_NAME",
    objects = myObjects.map { Json.encodeToJsonElement(it).jsonObject },
    createIfNotExists = true
)
```

## Browse aggregator

```kotlin
val hits = mutableListOf<JsonObject>()
client.browseObjects(
    indexName = "INDEX_NAME",
    params = BrowseParamsObject(),
    aggregator = { response -> hits.addAll(response.hits) }
)
```

## Secured API key

```kotlin
// v2
val key: APIKey = client.generateAPIKey(
    parentApiKey = APIKey("parentApiKey"),
    restriction = SecuredAPIKeyRestriction(validUntil = 1893456000)
)

// v3 — returns plain String
val key: String = client.generateSecuredApiKey(
    parentApiKey = "parentApiKey",
    restrictions = SecuredApiKeyRestrictions(validUntil = 1893456000)
)

// remaining validity is now a top-level function
val remaining: Duration = securedApiKeyRemainingValidity("my-key")
```

## Cross-app copy (`ClientAccount` removed)

```kotlin
val src = SearchClient("SRC_APP_ID", "SRC_API_KEY")
val dst = SearchClient("DST_APP_ID", "DST_API_KEY")

val settings = src.getSettings(indexName = "SOURCE_INDEX")
dst.setSettings(indexName = "DEST_INDEX", indexSettings = settings)

val rules = mutableListOf<Rule>()
src.browseRules(indexName = "SOURCE_INDEX", searchRulesParams = SearchRulesParams(),
    aggregator = { rules.addAll(it.hits) })
if (rules.isNotEmpty()) dst.saveRules(indexName = "DEST_INDEX", rules = rules)
// repeat for synonyms and objects
```
