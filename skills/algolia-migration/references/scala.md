# Scala: v1 → v2

## Dependency

**sbt:**
```scala
// v1
libraryDependencies += "com.algolia" %% "algoliasearch-scala" % "[1,)"

// v2
libraryDependencies += "com.algolia" %% "algoliasearch-client-scala" % "[2,)"
```

**Maven:**
```xml
<!-- v1 -->
<artifactId>algoliasearch-scala_2.13</artifactId>
<version>[1,)</version>

<!-- v2 -->
<artifactId>algoliasearch-client-scala_2.13</artifactId>
<version>[2,)</version>
```

Supports Scala 2.13 and Scala 3.

## Import changes

```scala
// v1
import algolia.AlgoliaClient
import algolia.AlgoliaDsl._

// v2
import algoliasearch.api.SearchClient
```

## Client initialization

v1 used the `new` keyword; v2 uses a factory method:

```scala
// v1
val client = new AlgoliaClient("APP_ID", "API_KEY")

// v2
val client = SearchClient(appId = "APP_ID", apiKey = "API_KEY")
```

## Remove `initIndex`

There is no `initIndex` step. Pass `indexName` directly to every method call.

## Method renames

| v1 | v2 |
|----|----|
| `execute { search into }` | `client.searchSingleIndex()` |
| `execute { index into ... objects }` | `client.saveObjects()` |
| `execute { index into ... object }` | `client.saveObject()` |
| `execute { delete from }` | `client.deleteObject()` |
| `execute { settings of }` | `client.getSettings()` |
| `execute { setSettings of }` | `client.setSettings()` |
| `execute { copy index }` | `client.operationIndex()` |
| `execute { move index }` | `client.operationIndex()` |

## DSL removal — the major change

v1 used an `execute { ... }` DSL for all operations. v2 replaces every DSL block with direct method calls and named parameters.

**Search:**
```scala
// v1
client.execute { search into "INDEX_NAME" query Query(query = Some("QUERY")) }

// v2
client.searchSingleIndex(
  indexName = "INDEX_NAME",
  searchParams = Some(SearchParamsObject(query = Some("QUERY")))
)
```

**Indexing:**
```scala
// v1 — single
client.execute { index into "INDEX_NAME" `object` Record("name", "1") }
// v1 — batch
client.execute { index into "INDEX_NAME" objects Seq(Record("name", "1")) }

// v2 — single
client.saveObject(indexName = "INDEX_NAME", body = JObject(...))
// v2 — batch
client.saveObjects(indexName = "INDEX_NAME", objects = Seq(...))
```

**Delete:**
```scala
// v1
client.execute { delete from "INDEX_NAME" objectId "1" }

// v2
client.deleteObject(indexName = "INDEX_NAME", objectID = "1")
```

**Settings:**
```scala
// v1
client.execute { settings of "INDEX_NAME" }
client.execute { setSettings of "INDEX_NAME" `with` Settings(...) }

// v2
client.getSettings(indexName = "INDEX_NAME")
client.setSettings(indexName = "INDEX_NAME", indexSettings = IndexSettings(...))
```

## `operationIndex` (copy / move)

```scala
// v1
client.execute { copy index "SOURCE" to "DEST" }
client.execute { move index "SOURCE" to "DEST" }

// v2
client.operationIndex(
  indexName = "SOURCE",
  operationIndexParams = OperationIndexParams(
    operation = OperationType.withName("copy"),
    destination = "DEST"
  )
)
```

## Task handling

```scala
// v1 — blocking wait
Await.ready(indexing, Duration.Inf)

// v2 — explicit wait helpers; all methods return Future[...]
result.flatMap { r =>
  client.waitForTask(indexName = "INDEX_NAME", taskID = r.taskID)
}
```

New wait helpers in v2: `waitForTask`, `waitForAppTask`, `waitForApiKey`.

## Helper method changes

New helpers added in v2 that have no v1 equivalent:

| Helper | Notes |
|--------|-------|
| `indexExists` | Returns `Future[Boolean]` |
| `replaceAllObjects` | Atomically replaces all objects |
| `saveObjects` | Batches automatically |
| `deleteObjects` | Batches automatically |
| `browseObjects` | Aggregator callback: `BrowseResponse => Unit` |
| `browseRules` | Aggregator callback |
| `browseSynonyms` | Aggregator callback |
| `generateSecuredApiKey` | Instance method with typed `restrictions` |
| `getSecuredApiKeyRemainingValidity` | New helper |

**`browseObjects` example:**
```scala
val hits = scala.collection.mutable.ListBuffer.empty[JObject]
client.browseObjects(
  indexName = "INDEX_NAME",
  aggregator = response => hits.addAll(response.hits)
)
```

## Method changes reference

| v1 DSL | v2 |
|--------|----|
| `execute { search into "I" query Q }` | `client.searchSingleIndex(indexName, searchParams)` |
| `execute { index into "I" objects Seq(...) }` | `client.saveObjects(indexName, objects)` |
| `execute { index into "I" object r }` | `client.saveObject(indexName, body)` |
| `execute { delete from "I" objectId "1" }` | `client.deleteObject(indexName, objectID)` |
| `execute { settings of "I" }` | `client.getSettings(indexName)` |
| `execute { setSettings of "I" with S }` | `client.setSettings(indexName, indexSettings)` |
| `execute { copy index "S" to "D" }` | `client.operationIndex(indexName, OperationIndexParams(...))` |
| `execute { move index "S" to "D" }` | `client.operationIndex(indexName, OperationIndexParams(...))` |
| `Await.ready(op, Duration.Inf)` | `client.waitForTask(indexName, taskID)` |
| n/a | `client.indexExists(indexName)` |
| n/a | `client.replaceAllObjects(indexName, objects)` |
| n/a | `client.browseObjects(indexName, aggregator)` |
| n/a | `client.browseRules(indexName, aggregator)` |
| n/a | `client.browseSynonyms(indexName, aggregator)` |
| n/a | `client.generateSecuredApiKey(parentApiKey, restrictions)` |
