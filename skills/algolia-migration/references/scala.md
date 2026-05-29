# Upgrade the Scala API client to version 2

> Keep your Scala API client up to date to benefit from improvements and bug fixes.

The latest major version of the `algoliasearch-scala` package is version 2.
This page helps you upgrade from version 1
and explains the breaking changes you need to address.

Algolia generates the version 2 client from OpenAPI specifications,
which provides consistent behavior across all languages and up-to-date API coverage.
The main architectural change is the **removal of the domain-specific language (DSL)**.
Instead of writing expressions like `client.execute { search into "index" query "q" }` (version 1), you call methods directly on the `SearchClient` instance, passing named parameters.

For the full list of changes, see the Scala changelog.

## Update your dependencies

Update the `algoliasearch-scala` package to version 2.

With **`sbt`**, update the version range in your `build.sbt` file:

```txt
// version 1
libraryDependencies += "com.algolia" %% "algoliasearch-scala" % "[1,)"

// version 2
libraryDependencies += "com.algolia" %% "algoliasearch-client-scala" % "[2,)"
```

With **Maven**, update the version in your `pom.xml` file:

```xml
<!-- version 1 -->
<dependency>
    <groupId>com.algolia</groupId>
    <artifactId>algoliasearch-scala_2.13</artifactId>
    <version>[1,)</version>
</dependency>

<!-- version 2 -->
<dependency>
    <groupId>com.algolia</groupId>
    <artifactId>algoliasearch-client-scala_2.13</artifactId>
    <version>[2,)</version>
</dependency>
```

The version 2 client is cross-published for **Scala 2.13** and **Scala 3**.
`sbt` resolves the correct artifact automatically based on your `scalaVersion`.
If you use Maven, replace `_2.13` with `_3` in the `artifactId` for Scala 3 projects.

## Update imports

The package namespace changed from `algolia` to `algoliasearch`.
Version 2 also includes dedicated imports for each API.

```scala
// version 1
import algolia.AlgoliaClient
import algolia.AlgoliaDsl._
import algolia.objects.Query

// version 2
import algoliasearch.api.SearchClient
```

Version 2 includes separate client classes for each API.
If you only need a specific API, import the corresponding client:

```scala
// Search API
import algoliasearch.api.SearchClient
// Recommend API
import algoliasearch.api.RecommendClient
// A/B testing API
import algoliasearch.api.AbtestingClient
// Analytics API
import algoliasearch.api.AnalyticsClient
// Ingestion API
import algoliasearch.api.IngestionClient
// Insights API
import algoliasearch.api.InsightsClient
// Monitoring API
import algoliasearch.api.MonitoringClient
// Personalization API
import algoliasearch.api.PersonalizationClient
// Query Suggestions API
import algoliasearch.api.QuerySuggestionsClient
// Usage API
import algoliasearch.api.UsageClient
```

## Update client initialization

The client class was renamed from `AlgoliaClient` to `SearchClient`,
and you no longer use the `new` keyword.

```scala
// version 1
val client = new AlgoliaClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")

// version 2
val client = SearchClient(appId = "ALGOLIA_APPLICATION_ID", apiKey = "ALGOLIA_API_KEY")
```

Unlike other language clients, version 1 of the Scala client didn't have a separate `initIndex` step.
The DSL handled index references inline, embedding the index name into expressions like `search into "index"`.
In version 2, you pass `indexName` as a named parameter to every method. There's no index object and no DSL expression.

## Remove the domain-specific language

This is the most significant change when upgrading the Scala client.
Version 1 provided a domain-specific language (DSL) through `algolia.AlgoliaDsl._`
that let you write expressive, English-like code inside `client.execute { ... }` blocks.
**Version 2 removes the DSL entirely.**

Every `client.execute { ... }` call must be replaced with a direct method call on the client.
Here are the most common DSL patterns and their replacements:

### Search

```scala
// version 1
val future: Future[Search] =
    client.execute {
        search into "INDEX_NAME" query Query(query = Some("QUERY"))
    }

// version 2
val response: Future[SearchResponse] =
  client.searchSingleIndex(
    indexName = "INDEX_NAME",
    searchParams = Some(
      SearchParamsObject(query = Some("QUERY"))
    )
  )
```

### Index an object

```scala
// version 1
client.execute {
    index into "INDEX_NAME" `object` Contact("Jimmie", "Barninger", 93, "California Paint")
}

// version 2
val response: Future[SaveObjectResponse] =
  client.saveObject(
    indexName = "INDEX_NAME",
    body = JObject(
      List(
        JField("name", JString("Jimmie")),
        JField("company", JString("California Paint")),
        JField("objectID", JString("1"))
      )
    )
  )
```

### Parse results

```scala
// version 1 (case class deserialization via json4s)
val future: Future[Seq[Contact]] =
    client
        .execute { search into "index" query "a" }
        .map { search => search.as[Contact] }

// version 2
// The response contains raw JSON. Parse with json4s or your preferred library.
val response: Future[SearchResponse] =
  client.searchSingleIndex(
    indexName = "INDEX_NAME",
    searchParams = Some(
      SearchParamsObject(query = Some("a"))
    )
  )
```

  Search your codebase for `client.execute`, `AlgoliaDsl`, and `import algolia.` to find every place that needs changing.

## Update search calls

### Search a single index

The DSL `search into` expression is now `client.searchSingleIndex()`.
Pass the index name and search parameters as named arguments:

```scala
// version 1
val results = client.execute {
    search into "INDEX_NAME" query Query(
      query = Some("QUERY"),
      facetFilters = Some(Seq("category:Book"))
    )
}

// version 2
val results: Future[SearchResponse] =
  client.searchSingleIndex(
    indexName = "INDEX_NAME",
    searchParams = Some(
      SearchParamsObject(
        query = Some("QUERY"),
        facetFilters = Some(Seq(MixedSearchFilters(Seq("category:Book"))))
      )
    )
  )
```

### Search multiple indices

The `multiQueries` DSL is now `client.search()`.
Each request in the list requires an `indexName`:

```scala
// version 1
val results = client.execute {
    multiQueries(
      Seq(search into "INDEX_1" query "QUERY", search into "INDEX_2" query "QUERY")
    )
}

// version 2
val results: Future[SearchResponses] =
  client.search(
    searchMethodParams = SearchMethodParams(
      requests = Seq(
        SearchForHits(indexName = "INDEX_1", query = Some("QUERY")),
        SearchForHits(indexName = "INDEX_2", query = Some("QUERY"))
      )
    )
  )
```

### Search for facet values

The `search facet` DSL is now on the client
and requires `indexName` and `facetName` parameters:

```scala
// version 1
client.execute { search facet "category" into "INDEX_NAME" query "book" }

// version 2
val results: Future[SearchForFacetValuesResponse] =
  client.searchForFacetValues(
    indexName = "INDEX_NAME",
    facetName = "category",
    searchForFacetValuesRequest = Some(
      SearchForFacetValuesRequest(facetQuery = Some("book"))
    )
  )
```

## Update indexing operations

In version 2, indexing methods are direct client method calls
with `indexName` as a parameter.

### Add or replace records

```scala
// version 1
client.execute {
    index into "INDEX_NAME" `object` Record("Record", "1")
}
client.execute {
    index into "INDEX_NAME" objects Seq(Record("Record", "1"))
}

// version 2 (single record)
val result: Future[SaveObjectResponse] =
  client.saveObject(
    indexName = "INDEX_NAME",
    body = JObject(List(JField("objectID", JString("1")), JField("name", JString("Record"))))
  )
// version 2 (batch)
val result: Future[Seq[BatchResponse]] =
  client.saveObjects(
    indexName = "INDEX_NAME",
    objects = Seq(
      JObject(List(JField("objectID", JString("1")), JField("name", JString("Record"))))
    )
  )
```

### Partially update records

```scala
// version 1
client.execute { partialUpdate from "INDEX_NAME" `object` ("1", JObject()) }

// version 2
val result: Future[UpdatedAtWithObjectIDResponse] =
  client.partialUpdateObject(
    indexName = "INDEX_NAME",
    objectID = "1",
    attributesToUpdate = JObject(List(JField("name", JString("Updated"))))
  )
```

### Delete records

```scala
// version 1
client.execute { delete from "INDEX_NAME" objectId "1" }

// version 2
val result: Future[DeletedAtResponse] =
  client.deleteObject(
    indexName = "INDEX_NAME",
    objectID = "1"
  )
```

## Update settings, synonyms, and rules

### Get and set settings

```scala
// version 1
client.execute { settings of "INDEX_NAME" }
client.execute {
    setSettings of "INDEX_NAME" `with` Settings(searchableAttributes = Some(Seq("title", "author")))
}

// version 2
val settings: Future[SettingsResponse] =
  client.getSettings(
    indexName = "INDEX_NAME"
  )
val updated: Future[UpdatedAtResponse] =
  client.setSettings(
    indexName = "INDEX_NAME",
    indexSettings = IndexSettings(
      searchableAttributes = Some(Seq("title", "author"))
    )
  )
```

### Save synonyms and rules

Many synonym and rule operations weren't available in version 1 of the Scala client.
Version 2 includes full coverage of the API, including `saveSynonyms`, `saveRules`, and `replaceAllObjects`.

```scala
// version 2 -- save synonyms
val result: Future[UpdatedAtResponse] =
  client.saveSynonyms(
    indexName = "INDEX_NAME",
    synonymHit = Seq(
      SynonymHit(
        objectID = "1",
        `type` = SynonymType.withName("synonym"),
        synonyms = Some(Seq("car", "auto"))
      )
    ),
    replaceExistingSynonyms = Some(true)
  )
```

```scala
// version 2 -- save rules
val result: Future[UpdatedAtResponse] =
  client.saveRules(
    indexName = "INDEX_NAME",
    rules = Seq(
      Rule(
        objectID = "1",
        conditions = Some(Seq(
          Condition(
            pattern = Some("shoes"),
            anchoring = Some(Anchoring.withName("contains"))
          )
        )),
        consequence = Consequence(
          params = Some(ConsequenceParams(query = Some("sneakers")))
        )
      )
    ),
    clearExistingRules = Some(true)
  )
```

  In version 1, `replaceAllRules` and `replaceAllSynonyms` weren't available in the Scala client.
  In version 2, use `client.saveRules()` with `clearExistingRules = Some(true)` or `client.saveSynonyms()` with `replaceExistingSynonyms = Some(true)` to replace all rules or synonyms.

## Update index management

The `copy index` and `move index` DSL commands
are replaced by a single `operationIndex` method.

### Copy an index

```scala
// version 1
client.execute { copy index "SOURCE_INDEX_NAME" to "DESTINATION_INDEX_NAME" }

// version 2
val result: Future[UpdatedAtResponse] =
  client.operationIndex(
    indexName = "SOURCE_INDEX_NAME",
    operationIndexParams = OperationIndexParams(
      operation = OperationType.withName("copy"),
      destination = "DESTINATION_INDEX_NAME"
    )
  )
```

### Move (rename) an index

```scala
// version 1
client.execute { move index "SOURCE_INDEX_NAME" to "DESTINATION_INDEX_NAME" }

// version 2
val result: Future[UpdatedAtResponse] =
  client.operationIndex(
    indexName = "SOURCE_INDEX_NAME",
    operationIndexParams = OperationIndexParams(
      operation = OperationType.withName("move"),
      destination = "DESTINATION_INDEX_NAME"
    )
  )
```

### Copy only rules or settings

In version 2, use the `scope` parameter to limit the operation to specific data:

```scala
// version 2 -- copy only rules and settings from one index to another
val result: Future[UpdatedAtResponse] =
  client.operationIndex(
    indexName = "SOURCE_INDEX_NAME",
    operationIndexParams = OperationIndexParams(
      operation = OperationType.withName("copy"),
      destination = "DESTINATION_INDEX_NAME",
      scope = Some(Seq(ScopeType.withName("rules"), ScopeType.withName("settings")))
    )
  )
```

### Check if an index exists

Version 2 introduces the `indexExists` helper method to check if an index exists.
This method wasn't available in version 1.

```scala
// version 2
val exists: Future[Boolean] = client.indexExists(indexName = "INDEX_NAME")
```

## Update task handling

Version 1 relied on calling `.wait()` on `Future` results or `Await.ready`.
Version 2 replaces this pattern with dedicated wait helpers.
Since all methods return `Future[...]`, you can chain `waitForTask` with a `flatMap`:

```scala
// version 1
val indexing = client.execute {
    index into "INDEX_NAME" `object` Record("test", "1")
}
Await.ready(indexing, Duration.Inf)

// version 2
val result: Future[SaveObjectResponse] =
  client.saveObject(
    indexName = "INDEX_NAME",
    body = JObject(List(JField("objectID", JString("1")), JField("name", JString("test"))))
  )
val waited: Future[GetTaskResponse] =
  result.flatMap { r =>
    client.waitForTask(
      indexName = "INDEX_NAME",
      taskID = r.taskID
    )
  }
```

Version 2 includes three wait helpers:

* `waitForTask`: wait until indexing operations are done.
* `waitForAppTask`: wait for application-level tasks.
* `waitForApiKey`: wait for API key operations.

## Helper method changes

The following sections document breaking changes in helper method signatures and behavior between version 1 and version 2.

### `generateSecuredApiKey`

The method was previously available through the version 1 DSL as a static utility. In version 2, it is an instance method on the client.

```scala
// version 1
val key = client.generateSecuredAPIKey(
  parentApiKey = "parentApiKey",
  params = Map("validUntil" -> 1893456000)
)

// version 2
val key = client.generateSecuredApiKey(
  parentApiKey = "parentApiKey",
  restrictions = SecuredApiKeyRestrictions(validUntil = Some(1893456000))
)
```

### `replaceAllObjects`

New in version 2. Atomically replaces all objects in an index by copying it, batch-saving new objects, then moving the copy back. `batchSize` defaults to `1,000` and `scopes` defaults to `["settings", "rules", "synonyms"]`.

```scala
val response = client.replaceAllObjects(
  indexName = "INDEX_NAME",
  objects = myObjects,
  batchSize = 1000,
  scopes = Seq(ScopeType.Settings, ScopeType.Rules, ScopeType.Synonyms)
)
```

### `saveObjects`

New in version 2. Sends objects in chunks. `waitForTasks` defaults to `false` and `batchSize` defaults to `1,000`.

```scala
val responses = client.saveObjects(
  indexName = "INDEX_NAME",
  objects = myObjects,
  waitForTasks = true,
  batchSize = 1000
)
```

### `deleteObjects`

New in version 2. Deletes objects by ID in chunks. `waitForTasks` defaults to `false` and `batchSize` defaults to `1,000`.

```scala
val responses = client.deleteObjects(
  indexName = "INDEX_NAME",
  objectIDs = Seq("id1", "id2"),
  waitForTasks = true
)
```

### `partialUpdateObjects`

New in version 2. `createIfNotExists` defaults to `false`.

```scala
val responses = client.partialUpdateObjects(
  indexName = "INDEX_NAME",
  objects = myObjects,
  createIfNotExists = true
)
```

### `browseObjects`, `browseRules`, `browseSynonyms`

New in version 2. Each helper accepts an `aggregator` callback invoked with every page, and an optional `validate` callback to stop early.

```scala
val hits = scala.collection.mutable.ListBuffer.empty[JsonObject]

client.browseObjects(
  indexName = "INDEX_NAME",
  browseParams = BrowseParamsObject(),
  aggregator = response => hits ++= response.hits
)
```

### `waitForTask`

New in version 2. Polls until an indexing task reaches the `published` state. `maxRetries` defaults to `50`.

```scala
val response = client.waitForTask(
  indexName = "INDEX_NAME",
  taskID = taskId
)
```

### `waitForAppTask`

New in version 2. Polls until an application-level task completes.

```scala
val response = client.waitForAppTask(taskID = taskId)
```

### `waitForApiKey`

New in version 2. Polls until an API key operation (`add`, `update`, or `delete`) has propagated.

```scala
// Wait for a key to be created:
client.waitForApiKey(key = "my-api-key", operation = ApiKeyOperation.Add)

// Wait for a key update (pass the expected final state):
client.waitForApiKey(
  key = "my-api-key",
  operation = ApiKeyOperation.Update,
  apiKey = Some(ApiKey(acl = Seq(Acl.Search)))
)
```

### `indexExists`

New in version 2. Returns `true` if the index exists.

```scala
val exists: Future[Boolean] = client.indexExists(indexName = "INDEX_NAME")
```

### `chunkedBatch`

New in version 2. Sends objects in chunks with a specified action. `waitForTasks` is required with no default.

```scala
val responses = client.chunkedBatch(
  indexName = "INDEX_NAME",
  objects = myObjects,
  action = Action.AddObject,
  waitForTasks = true,
  batchSize = 1000
)
```

### `getSecuredApiKeyRemainingValidity`

New in version 2. Returns the time remaining until a secured API key expires, based on its embedded `validUntil` parameter.

```scala
val remaining: Duration = client.getSecuredApiKeyRemainingValidity(
  securedApiKey = myKey
)
```

### `accountCopyIndex`

There is no built-in cross-application copy helper in the Scala client, but you can compose existing helpers across two clients to achieve the same result.

```scala
val src = SearchClient(appId = "SRC_APP_ID", apiKey = "SRC_API_KEY")
val dst = SearchClient(appId = "DST_APP_ID", apiKey = "DST_API_KEY")

val rules    = scala.collection.mutable.Buffer.empty[Rule]
val synonyms = scala.collection.mutable.Buffer.empty[SynonymHit]
val objects  = scala.collection.mutable.Buffer.empty[Any]

for {
  // Copy settings
  settings <- src.getSettings("SOURCE_INDEX")
  _ <- dst.setSettings("DEST_INDEX", settings)

  // Copy rules
  _ <- src.browseRules("SOURCE_INDEX", SearchRulesParams(), aggregator = r => rules ++= r.hits)
  _ <- if (rules.nonEmpty) dst.saveRules("DEST_INDEX", rules.toList) else Future.unit

  // Copy synonyms
  _ <- src.browseSynonyms("SOURCE_INDEX", SearchSynonymsParams(), aggregator = r => synonyms ++= r.hits)
  _ <- if (synonyms.nonEmpty) dst.saveSynonyms("DEST_INDEX", synonyms.toList) else Future.unit

  // Copy objects
  _ <- src.browseObjects("SOURCE_INDEX", BrowseParamsObject(), aggregator = r => objects ++= r.hits)
  _ <- dst.replaceAllObjects("DEST_INDEX", objects.toList)
} yield ()
```

## Method changes reference

The following tables list all method names that changed between version 1 and version 2.

### Search API client

| Version 1 (legacy)      |   | Version 2 (current)             |
| ----------------------- | - | ------------------------------- |
| `add key`               | → | `client.addApiKey`              |
| `clear dictionary`      | → | `client.batchDictionaryEntries` |
| `copy index`            | → | `client.operationIndex`         |
| `not available`         | → | `client.operationIndex`         |
| `not available`         | → | `client.operationIndex`         |
| `delete key`            | → | `client.deleteApiKey`           |
| `delete dictionary`     | → | `client.batchDictionaryEntries` |
| `get key`               | → | `client.getApiKey`              |
| `list keys`             | → | `client.listApiKeys`            |
| `list indices`          | → | `client.listIndices`            |
| `move index`            | → | `client.operationIndex`         |
| `multipleBatch`         | → | `client.multipleBatch`          |
| `multiQueries`          | → | `client.search`                 |
| `replace dictionary`    | → | `client.batchDictionaryEntries` |
| `restore key`           | → | `client.restoreApiKey`          |
| `save dictionary`       | → | `client.batchDictionaryEntries` |
| `update key`            | → | `client.updateApiKey`           |
| `index.batch`           | → | `client.batch`                  |
| `clear index`           | → | `client.clearObjects`           |
| `clear rules`           | → | `client.clearRules`             |
| `clear synonyms`        | → | `client.clearSynonyms`          |
| `not available`         | → | `client.operationIndex`         |
| `delete`                | → | `client.deleteIndex`            |
| `delete by`             | → | `client.deleteBy`               |
| `deleteObject`          | → | `client.deleteObject`           |
| `delete objectIds`      | → | `client.deleteObjects`          |
| `delete rule`           | → | `client.deleteRule`             |
| `delete synonym`        | → | `client.deleteSynonym`          |
| `not available`         | → | `client.indexExists`            |
| `helper.findObject`     | → | `client.searchSingleIndex`      |
| `getObject`             | → | `client.getObject`              |
| `get objectIds`         | → | `client.getObjects`             |
| `get rule`              | → | `client.getRule`                |
| `settings of`           | → | `client.getSettings`            |
| `get synonym`           | → | `client.getSynonym`             |
| `index.getTask`         | → | `client.getTask`                |
| `partialUpdateObject`   | → | `client.partialUpdateObject`    |
| `partialUpdate objects` | → | `client.partialUpdateObjects`   |
| `not available`         | → | `client.replaceAllObjects`      |
| `not available`         | → | `client.saveRules`              |
| `not available`         | → | `client.saveSynonyms`           |
| `saveObject`            | → | `client.saveObject`             |
| `index objects`         | → | `client.saveObjects`            |
| `save rule`             | → | `client.saveRule`               |
| `saveRules`             | → | `client.saveRules`              |
| `save synonym`          | → | `client.saveSynonym`            |
| `save synonyms`         | → | `client.saveSynonyms`           |
| `search`                | → | `client.searchSingleIndex`      |
| `search facet`          | → | `client.searchForFacetValues`   |
| `search rules`          | → | `client.searchRules`            |
| `search synonyms`       | → | `client.searchSynonyms`         |
| `setSettings of`        | → | `client.setSettings`            |
| `{operation}.wait`      | → | `client.waitForTask`            |

### Recommend API client

| Version 1 (legacy)             |   | Version 2 (current)         |
| ------------------------------ | - | --------------------------- |
| `get frequentlyBoughtTogether` | → | `client.getRecommendations` |
| `get recommendations`          | → | `client.getRecommendations` |
| `get relatedProducts`          | → | `client.getRecommendations` |
