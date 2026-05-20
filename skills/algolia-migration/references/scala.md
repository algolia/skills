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

## Import changes

```scala
// v1
import algolia.AlgoliaClient
import algolia.AlgoliaDsl._

// v2
import algoliasearch.api.SearchClient
```

## Client initialization

```scala
// v1
val client = new AlgoliaClient("APP_ID", "API_KEY")

// v2
val client = SearchClient(appId = "APP_ID", apiKey = "API_KEY")
```

## DSL removal — the major change

v1 used an `execute { ... }` DSL for all operations. v2 replaces every DSL block with direct method calls and named parameters.

## Search

```scala
// v1
client.execute { search into "INDEX_NAME" query Query(query = Some("QUERY")) }

// v2
client.searchSingleIndex(
  indexName = "INDEX_NAME",
  searchParams = Some(SearchParamsObject(query = Some("QUERY")))
)
```

## Indexing

```scala
// v1 — single
client.execute { index into "INDEX_NAME" `object` Record("name", "1") }

// v2 — single
client.saveObject(
  indexName = "INDEX_NAME",
  body = JObject(List(JField("objectID", JString("1")), JField("name", JString("Record"))))
)

// v1 — batch
client.execute { index into "INDEX_NAME" objects Seq(Record("name", "1")) }

// v2 — batch
client.saveObjects(indexName = "INDEX_NAME", objects = Seq(...))
```

## Delete

```scala
// v1
client.execute { delete from "INDEX_NAME" objectId "1" }

// v2
client.deleteObject(indexName = "INDEX_NAME", objectID = "1")
```

## Settings

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

// v2 — explicit wait helpers; all operations return Future[...]
result.flatMap { r =>
  client.waitForTask(indexName = "INDEX_NAME", taskID = r.taskID)
}
```

New wait helpers: `waitForTask`, `waitForAppTask`, `waitForApiKey`.

## New helpers in v2

| Helper | Description |
|--------|-------------|
| `replaceAllObjects` | Atomically replaces all objects |
| `saveObjects` | Batches automatically |
| `deleteObjects` | Batches automatically |
| `browseObjects` | Aggregator callback |
| `browseRules` | Aggregator callback |
| `browseSynonyms` | Aggregator callback |
| `indexExists` | Returns `Future[Boolean]` |
| `generateSecuredApiKey` | Instance method with typed `restrictions` |

## Gotchas

- No separate `initIndex` step — pass `indexName` to every method
- All methods return `Future[...]`; use `flatMap` / `for`-comprehension or `Await` for blocking
- Response objects contain raw JSON; parse with json4s or similar
- DSL expressions like `search into`, `index into`, `delete from` must all be replaced with direct method calls
