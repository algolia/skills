# Upgrade the Kotlin API client to version 3

> Keep your Kotlin API client up to date to benefit from improvements and bug fixes.

The latest major version of the `algoliasearch-client-kotlin` package is version 3.
This page helps you upgrade from version 2
and explains the breaking changes you need to address.

Algolia generates the version 3 clients from OpenAPI specifications,
which provides consistent behavior across all languages and up-to-date API coverage.
The main architectural changes are the removal of the `initIndex` pattern
and the Kotlin DSL:
all methods are now on the `client` instance directly, with `indexName` as a parameter,
and parameters use typed data classes instead of DSL builders.

For the full list of changes, see the [Kotlin changelog](/doc/libraries/sdk/changelog/kotlin).

## Update your dependencies

Update the `algoliasearch-client-kotlin` dependency to version 3 in your build file:

```groovy build.gradle icon=braces theme={"system"}
// version 2
implementation("com.algolia:algoliasearch-client-kotlin:2.x.x")

// version 3
implementation("com.algolia:algoliasearch-client-kotlin:3.+")
```

## Update imports

The package structure changed from `com.algolia.search` to `com.algolia.client`.
Type wrapper classes like `ApplicationID`, `APIKey`, `IndexName`, and `ObjectID` no longer exist.

```kotlin Kotlin icon=code theme={"system"}
// version 2
import com.algolia.search.client.ClientSearch
import com.algolia.search.model.ApplicationID
import com.algolia.search.model.APIKey
import com.algolia.search.model.IndexName
import com.algolia.search.model.ObjectID
import com.algolia.search.model.search.Query
import com.algolia.search.dsl.query
import com.algolia.search.dsl.settings

// version 3
import com.algolia.client.api.SearchClient
import com.algolia.client.model.search.*
```

Version 3 also includes dedicated packages for each API.
If you only need methods from a specific API,
you can import them separately:

```kotlin Kotlin icon=code theme={"system"}
// Search API
import com.algolia.client.api.SearchClient
// Recommend API
import com.algolia.client.api.RecommendClient
// A/B testing API
import com.algolia.client.api.AbtestingClient
// Analytics API
import com.algolia.client.api.AnalyticsClient
// Personalization API
import com.algolia.client.api.PersonalizationClient
// Query Suggestions API
import com.algolia.client.api.QuerySuggestionsClient
```

## Update client initialization

Version 3 renames `ClientSearch` to `SearchClient`.
It also removes the `ApplicationID` and `APIKey` type wrappers. Pass plain strings instead.

```kotlin Kotlin icon=code highlight={7-10} theme={"system"}
// version 2
val client = ClientSearch(
    ApplicationID("ALGOLIA_APPLICATION_ID"),
    APIKey("ALGOLIA_API_KEY")
)

// version 3
val client = SearchClient(
    appId = "ALGOLIA_APPLICATION_ID",
    apiKey = "ALGOLIA_API_KEY"
)
```

The other major change concerns what follows initialization:
`initIndex` no longer exists.

## Remove `initIndex`

This is the most significant structural change when upgrading.
Version 2 relied on an index object with methods called on it.
In version 3, all methods belong to the `client` instance,
with `indexName` as a parameter.

```kotlin Kotlin icon=code highlight={10-14} theme={"system"}
// version 2
val client = ClientSearch(
    ApplicationID("ALGOLIA_APPLICATION_ID"),
    APIKey("ALGOLIA_API_KEY")
)
val index = client.initIndex(IndexName("INDEX_NAME"))
index.search(Query("QUERY"))

// version 3
val client = SearchClient(
    appId = "ALGOLIA_APPLICATION_ID",
    apiKey = "ALGOLIA_API_KEY"
)
client.searchSingleIndex(
    indexName = "INDEX_NAME",
    searchParamsObject = SearchParamsObject(query = "QUERY")
)
```

<Tip>
  If you have many files to update,
  search your codebase for `initIndex` or `IndexName(` to find every place that needs changing.
</Tip>

## Replace the domain-specific language

Version 2 of the Kotlin client included a domain-specific language (DSL)
for building queries, settings, and filters.
Version 3 removes this DSL.
Replace all DSL builder blocks with typed data class constructors and named parameters.

### Query parameters

```kotlin Kotlin icon=code highlight={8-11} theme={"system"}
// version 2
val query = query {
    attributesToRetrieve {
        +"color"
        +"category"
    }
}

// version 3
val params = SearchParamsObject(
    query = "QUERY",
    attributesToRetrieve = listOf("color", "category")
)
```

### Settings

```kotlin Kotlin icon=code highlight={7-9} theme={"system"}
// version 2
val settings = settings {
    searchableAttributes {
        +"title"
        +"author"
    }
}

// version 3
val settings = IndexSettings(
    searchableAttributes = listOf("title", "author")
)
```

### Filters

```kotlin Kotlin icon=code highlight={11-14} theme={"system"}
// version 2
val query = query {
    filters {
        and {
            facet("color", "red")
            facet("category", "shirt")
        }
    }
}

// version 3
val params = SearchParamsObject(
    query = "QUERY",
    filters = "color:red AND category:shirt"
)
```

<Tip>
  If you used the DSL extensively,
  search your codebase for `query {`, `settings {`, and `filters {`
  to find every block that needs rewriting.
</Tip>

## Update search calls

### Search a single index

The `index.search()` method is now [`client.searchSingleIndex()`](/doc/libraries/sdk/methods/search/search-single-index).
Pass the index name and search parameters using named arguments:

```kotlin Kotlin icon=code highlight={7-12} theme={"system"}
// version 2
val index = client.initIndex(IndexName("INDEX_NAME"))
val results = index.search(Query("QUERY").apply {
    facetFilters = listOf(listOf("category:Book"))
})

// version 3
val results = client.searchSingleIndex(
    indexName = "INDEX_NAME",
    searchParamsObject = SearchParamsObject(
        query = "QUERY",
        filters = "category:Book"
    )
)
```

### Search multiple indices

The `client.multipleQueries()` method is now [`client.search()`](/doc/libraries/sdk/methods/search/search).
Each request in the list requires an `indexName`:

```kotlin Kotlin icon=code highlight={9-17} theme={"system"}
// version 2
val results = client.multipleQueries(
    listOf(
        IndexQuery(IndexName("INDEX_1"), Query("QUERY")),
        IndexQuery(IndexName("INDEX_2"), Query("QUERY"))
    )
)

// version 3
val results = client.search(
    searchMethodParams = SearchMethodParams(
        requests = listOf(
            SearchForHits(indexName = "INDEX_1", query = "QUERY"),
            SearchForHits(indexName = "INDEX_2", query = "QUERY")
        )
    )
)
```

### Search for facet values

The `index.searchForFacets()` method becomes `client.searchForFacetValues()`
with an `indexName` parameter:

```kotlin Kotlin icon=code highlight={5-9} theme={"system"}
// version 2
val index = client.initIndex(IndexName("INDEX_NAME"))
val results = index.searchForFacets(Attribute("category"), "book")

// version 3
val results = client.searchForFacetValues(
    indexName = "INDEX_NAME",
    facetName = "category",
    searchForFacetValuesRequest = SearchForFacetValuesRequest(facetQuery = "book")
)
```

## Update indexing operations

In version 3, indexing methods are on the client instead of the index object,
with `indexName` as a parameter.
Version 3 replaces type wrappers like `ObjectID("id")` with plain strings.

### Add or replace records

```kotlin Kotlin icon=code highlight={8-13} theme={"system"}
// version 2
val index = client.initIndex(IndexName("INDEX_NAME"))
index.saveObject(buildJsonObject {
    put("objectID", "1")
    put("name", "Record")
})

// version 3
client.saveObject(
    indexName = "INDEX_NAME",
    body = buildJsonObject {
        put("objectID", "1")
        put("name", "Record")
    }
)
```

### Partially update records

```kotlin Kotlin icon=code highlight={8-12} theme={"system"}
// version 2
val index = client.initIndex(IndexName("INDEX_NAME"))
index.partialUpdateObject(buildJsonObject {
    put("objectID", "1")
    put("name", "Updated")
})

// version 3
client.partialUpdateObject(
    indexName = "INDEX_NAME",
    objectID = "1",
    attributesToUpdate = buildJsonObject { put("name", "Updated") }
)
```

### Delete records

```kotlin Kotlin icon=code highlight={5-8} theme={"system"}
// version 2
val index = client.initIndex(IndexName("INDEX_NAME"))
index.deleteObject(ObjectID("1"))

// version 3
client.deleteObject(
    indexName = "INDEX_NAME",
    objectID = "1"
)
```

## Update settings, synonyms, and rules

### Get and set settings

```kotlin Kotlin icon=code highlight={7-14} theme={"system"}
// version 2
val index = client.initIndex(IndexName("INDEX_NAME"))
val settings = index.getSettings()
index.setSettings(settings { searchableAttributes { +"title"; +"author" } })

// version 3
val settings = client.getSettings(
    indexName = "INDEX_NAME"
)
client.setSettings(
    indexName = "INDEX_NAME",
    indexSettings = IndexSettings(
        searchableAttributes = listOf("title", "author")
    )
)
```

### Save synonyms and rules

```kotlin Kotlin icon=code highlight={6-12} theme={"system"}
// version 2
val index = client.initIndex(IndexName("INDEX_NAME"))
index.saveSynonyms(
    listOf(SynonymMultiWay(ObjectID("1"), listOf("car", "auto")))
)

// version 3
client.saveSynonyms(
    indexName = "INDEX_NAME",
    synonymHit = listOf(
        SynonymHit(
            objectID = "1",
            type = SynonymType.entries.first { it.value == "synonym" },
            synonyms = listOf("car", "auto")
        )
    )
)
```

<Note>
  In version 2, `index.replaceAllRules()` and `index.replaceAllSynonyms()` replaced all rules or synonyms.
  In version 3, use `client.saveRules()` or `client.saveSynonyms()` with the `clearExistingRules` or `clearExistingSynonyms` parameter set to `true`.
</Note>

## Update index management

The `copyIndex`, `moveIndex`, `copyRules`, `copySynonyms`, and `copySettings`
methods are all replaced by a single [`operationIndex`](/doc/rest-api/search/operation-index) method.

### Copy an index

```kotlin Kotlin icon=code highlight={5-11} theme={"system"}
// version 2
client.copyIndex(IndexName("SOURCE_INDEX_NAME"), IndexName("DESTINATION_INDEX_NAME"))

// version 3
client.operationIndex(
    indexName = "SOURCE_INDEX_NAME",
    operationIndexParams = OperationIndexParams(
        operation = OperationType.entries.first { it.value == "copy" },
        destination = "DESTINATION_INDEX_NAME"
    )
)
```

### Move (rename) an index

```kotlin Kotlin icon=code highlight={5-11} theme={"system"}
// version 2
client.moveIndex(IndexName("SOURCE_INDEX_NAME"), IndexName("DESTINATION_INDEX_NAME"))

// version 3
client.operationIndex(
    indexName = "SOURCE_INDEX_NAME",
    operationIndexParams = OperationIndexParams(
        operation = OperationType.entries.first { it.value == "move" },
        destination = "DESTINATION_INDEX_NAME"
    )
)
```

### Copy only rules or settings

In version 3, use the `scope` parameter to limit the operation to specific data:

```kotlin Kotlin icon=code theme={"system"}
// version 3: copy only rules and settings from one index to another
client.operationIndex(
    indexName = "SOURCE_INDEX_NAME",
    operationIndexParams = OperationIndexParams(
        operation = OperationType.entries.first { it.value == "copy" },
        destination = "DESTINATION_INDEX_NAME",
        scope = listOf(
            ScopeType.entries.first { it.value == "rules" },
            ScopeType.entries.first { it.value == "settings" }
        )
    )
)
```

### Check if an index exists

In version 2, you could check if an index existed using the `exists` method on the index object.
In version 3, use the [`indexExists`](/doc/libraries/sdk/methods/search/index-exists) helper method on the client:

```kotlin Kotlin icon=code highlight={5-6} theme={"system"}
// version 2
val index = client.initIndex(IndexName("INDEX_NAME"))
index.exists()

// version 3
client.indexExists(indexName = "INDEX_NAME")
```

## Update task handling

Version 2 supported chaining `.wait()` on operations.
Version 3 replaces this pattern with dedicated wait helpers.

```kotlin Kotlin icon=code highlight={6-10} theme={"system"}
// version 2
val index = client.initIndex(IndexName("INDEX_NAME"))
index.apply {
    saveObjects(Contact.serializer(), records).wait()
}

// version 3
val response = client.saveObject(
    indexName = "INDEX_NAME",
    body = record
)
client.waitForTask(indexName = "INDEX_NAME", taskID = response.taskID)
```

Version 3 includes three wait helpers:

* [`waitForTask`](/doc/libraries/sdk/methods/search/wait-for-task): wait until indexing operations are done.
* [`waitForAppTask`](/doc/libraries/sdk/methods/search/wait-for-app-task): wait for application-level tasks.
* [`waitForApiKey`](/doc/libraries/sdk/methods/search/wait-for-api-key): wait for API key operations.

## Helper method changes

The following sections document breaking changes in helper method signatures and behavior between version 2 and version 3.

### `generateSecuredApiKey`

The method was renamed from `generateAPIKey` to `generateSecuredApiKey`. The input type also changed from `APIKey` wrapper to `String`, and the return type changed from `APIKey` to `String`.

```kotlin Kotlin icon=code highlight={7-11} theme={"system"}
// version 2
val key: APIKey = client.generateAPIKey(
    parentApiKey = APIKey("parentApiKey"),
    restriction = SecuredAPIKeyRestriction(validUntil = 1893456000)
)

// version 3
val key: String = client.generateSecuredApiKey(
    parentApiKey = "parentApiKey",
    restrictions = SecuredApiKeyRestrictions(validUntil = 1893456000)
)
```

### `securedApiKeyRemainingValidity`

The function was renamed and its return type changed from `Long` (milliseconds) to `Duration`. In version 3 it is a **top-level function**, not a method on the client.

```kotlin Kotlin icon=code highlight={4-6} theme={"system"}
// version 2
val remainingMs: Long = client.getSecuredApiKeyRemainingValidity(APIKey("my-key"))

// version 3
// Top-level function — not called on the client
val remaining: Duration = securedApiKeyRemainingValidity("my-key")
```

### `replaceAllObjects`

This helper moved from the `Index` object to `SearchClient`. The `KSerializer<T>` requirement was removed—objects are now passed as `List<JsonObject>`. New `batchSize` (default `1,000`) and `scopes` parameters were added, and the return type changed from `List<TaskIndex>` to `ReplaceAllObjectsResponse`.

```kotlin Kotlin icon=code highlight={7-12} theme={"system"}
// version 2
val tasks: List<TaskIndex> = index.replaceAllObjects(
    serializer = MyObject.serializer(),
    records = myObjects
)

// version 3
val response: ReplaceAllObjectsResponse = client.replaceAllObjects(
    indexName = "INDEX_NAME",
    objects = myObjects.map { Json.encodeToJsonElement(it).jsonObject },
    scopes = listOf(ScopeType.Settings, ScopeType.Rules, ScopeType.Synonyms)
)
```

### `saveObjects`

This helper moved from the `Index` object to `SearchClient`. The `KSerializer<T>` requirement was removed. Two new optional parameters are available:

* `waitForTasks` (default `false`)
* `batchSize` (default `1,000`)

```kotlin Kotlin icon=code highlight={7-12} theme={"system"}
// version 2
val response = index.saveObjects(
    serializer = MyObject.serializer(),
    records = myObjects
)

// version 3
val responses = client.saveObjects(
    indexName = "INDEX_NAME",
    objects = myObjects.map { Json.encodeToJsonElement(it).jsonObject },
    waitForTasks = true
)
```

### `deleteObjects`

This helper moved from the `Index` object to `SearchClient`. Two new optional parameters are available:

* `waitForTasks` (default `false`)
* `batchSize` (default `1,000`)

```kotlin Kotlin icon=code highlight={4-9} theme={"system"}
// version 2
val response = index.deleteObjects(objectIDs = listOf(ObjectID("id1"), ObjectID("id2")))

// version 3
val responses = client.deleteObjects(
    indexName = "INDEX_NAME",
    objectIDs = listOf("id1", "id2"),
    waitForTasks = true
)
```

### `partialUpdateObjects`

This helper moved from the `Index` object to `SearchClient`. The `createIfNotExists` parameter is now required—in version 2 it defaulted to `true`. The input type changed from `List<Pair<ObjectID, Partial>>` to `List<JsonObject>`.

```kotlin Kotlin icon=code highlight={7-13} theme={"system"}
// version 2
// createIfNotExists defaulted to true
val response = index.partialUpdateObjects(
    partials = listOf(ObjectID("id1") to Partial.attribute("name", JsonPrimitive("new")))
)

// version 3
// createIfNotExists is now required — no default
val responses = client.partialUpdateObjects(
    indexName = "INDEX_NAME",
    objects = myObjects.map { Json.encodeToJsonElement(it).jsonObject },
    createIfNotExists = true
)
```

### `browseObjects`, `browseRules`, `browseSynonyms`

These helpers moved from the `Index` object to `SearchClient`. The input type changed from `Query`/`RuleQuery`/`SynonymQuery` to `BrowseParamsObject`/`SearchRulesParams`/`SearchSynonymsParams`. They now use an `aggregator` callback instead of returning a list, and accept an optional `validate` callback to stop early.

```kotlin Kotlin icon=code highlight={5-12} theme={"system"}
// version 2
val results: List<ResponseSearch> = index.browseObjects(query = Query())
results.forEach { process(it) }

// version 3
val hits = mutableListOf<JsonObject>()

client.browseObjects(
    indexName = "INDEX_NAME",
    params = BrowseParamsObject(),
    aggregator = { response -> hits.addAll(response.hits) }
)
```

### `waitForTask`

The helper was renamed from `waitTask` to `waitForTask`. The `timeout` parameter type changed from `Long?` (milliseconds cap) to `Duration` (default `Duration.INFINITE`). Explicit `maxRetries` (default `50`), `initialDelay` (default `200ms`), and `maxDelay` (default `5s`) parameters were added. The return type changed from `TaskStatus` to `GetTaskResponse`.

```kotlin Kotlin icon=code highlight={4-8} theme={"system"}
// version 2
val status: TaskStatus = index.waitTask(taskID = TaskID(123))

// version 3
val response: GetTaskResponse = client.waitForTask(
    indexName = "INDEX_NAME",
    taskID = 123L
)
```

### `waitForAppTask`

This is a new helper in version 3.

```kotlin Kotlin icon=code theme={"system"}
val response = client.waitForAppTask(taskID = 123L)
```

### `waitForApiKey`

This is a new standalone helper in version 3. In version 2, waiting for API key operations required polling manually.

```kotlin Kotlin icon=code theme={"system"}
// Wait for a key to be created:
client.waitForApiKey(key = "my-api-key", operation = ApiKeyOperation.Add)

// Wait for a key update (pass the expected final state):
client.waitForApiKey(
    key = "my-api-key",
    operation = ApiKeyOperation.Update,
    apiKey = ApiKey(acl = listOf(Acl.Search))
)
```

### `indexExists`

The helper was renamed from `exists()` on the `Index` object to `indexExists()` on the client.

```kotlin Kotlin icon=code highlight={4-5} theme={"system"}
// version 2
val exists: Boolean = index.exists()

// version 3
val exists: Boolean = client.indexExists(indexName = "INDEX_NAME")
```

### `chunkedBatch`

`chunkedBatch` is now a public helper in version 3. The `waitForTasks` parameter is required and must be passed explicitly.

```kotlin Kotlin icon=code theme={"system"}
val responses = client.chunkedBatch(
    indexName = "INDEX_NAME",
    objects = myObjects.map { Json.encodeToJsonElement(it).jsonObject },
    action = Action.AddObject,
    waitForTasks = true  // required, no default
)
```

### `copyIndexBetweenApplications`

In version 2, the `ClientAccount` singleton provided a `copyIndex(source, destination)` suspend function for copying an index between two different Algolia applications.

In version 3, `ClientAccount` is removed. You can compose existing helpers across two clients to achieve the same result.

```kotlin Kotlin icon=code expandable highlight={4-25} theme={"system"}
// version 2
val tasks = ClientAccount.copyIndex(sourceIndex, destinationIndex)

// version 3
val src = SearchClient("SRC_APP_ID", "SRC_API_KEY")
val dst = SearchClient("DST_APP_ID", "DST_API_KEY")

// Copy settings
val settings = src.getSettings(indexName = "SOURCE_INDEX")
dst.setSettings(indexName = "DEST_INDEX", indexSettings = settings)

// Copy rules
val rules = mutableListOf<Rule>()
src.browseRules(indexName = "SOURCE_INDEX", searchRulesParams = SearchRulesParams(), aggregator = { rules.addAll(it.hits) })
if (rules.isNotEmpty()) dst.saveRules(indexName = "DEST_INDEX", rules = rules)

// Copy synonyms
val synonyms = mutableListOf<SynonymHit>()
src.browseSynonyms(indexName = "SOURCE_INDEX", searchSynonymsParams = SearchSynonymsParams(), aggregator = { synonyms.addAll(it.hits) })
if (synonyms.isNotEmpty()) dst.saveSynonyms(indexName = "DEST_INDEX", synonyms = synonyms)

// Copy objects
val objects = mutableListOf<JsonObject>()
src.browseObjects(indexName = "SOURCE_INDEX", params = BrowseParamsObject(), aggregator = { objects.addAll(it.hits) })
dst.replaceAllObjects(indexName = "DEST_INDEX", objects = objects)
```

## Method changes reference

The following tables list all method names that changed between version 2 and version 3.

### Search API client

| Version 2 (legacy)                         |   | Version 3 (current)                        |
| ------------------------------------------ | - | ------------------------------------------ |
| `client.addAPIKey`                         | → | `client.addApiKey`                         |
| `client.addAPIKey.wait`                    | → | `client.waitForApiKey`                     |
| `client.clearDictionaryEntries`            | → | `client.batchDictionaryEntries`            |
| `client.copyIndex`                         | → | `client.operationIndex`                    |
| `client.copyRules`                         | → | `client.operationIndex`                    |
| `client.copySynonyms`                      | → | `client.operationIndex`                    |
| `client.deleteAPIKey`                      | → | `client.deleteApiKey`                      |
| `client.deleteDictionaryEntries`           | → | `client.batchDictionaryEntries`            |
| `client.generateAPIKey`                    | → | `client.generateSecuredApiKey`             |
| `client.getAPIKey`                         | → | `client.getApiKey`                         |
| `client.getSecuredAPIKeyRemainingValidity` | → | `client.getSecuredApiKeyRemainingValidity` |
| `client.listAPIKeys`                       | → | `client.listApiKeys`                       |
| `client.listIndices`                       | → | `client.listIndices`                       |
| `client.moveIndex`                         | → | `client.operationIndex`                    |
| `client.multipleBatchObjects`              | → | `client.multipleBatch`                     |
| `client.multipleQueries`                   | → | `client.search`                            |
| `client.replaceDictionaryEntries`          | → | `client.batchDictionaryEntries`            |
| `client.restoreAPIKey`                     | → | `client.restoreApiKey`                     |
| `client.saveDictionaryEntries`             | → | `client.batchDictionaryEntries`            |
| `client.updateAPIKey`                      | → | `client.updateApiKey`                      |
| `index.batch`                              | → | `client.batch`                             |
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
| `index.searchForFacets`                    | → | `client.searchForFacetValues`              |
| `index.searchRules`                        | → | `client.searchRules`                       |
| `index.searchSynonyms`                     | → | `client.searchSynonyms`                    |
| `index.setSettings`                        | → | `client.setSettings`                       |
| `index.{operation}.wait`                   | → | `client.waitForTask`                       |

### Recommend API client

| Version 2 (legacy)                   |   | Version 3 (current)         |
| ------------------------------------ | - | --------------------------- |
| `client.getFrequentlyBoughtTogether` | → | `client.getRecommendations` |
| `client.getRecommendations`          | → | `client.getRecommendations` |
| `client.getRelatedProducts`          | → | `client.getRecommendations` |