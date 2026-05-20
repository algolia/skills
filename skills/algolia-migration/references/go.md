# Go: v3 → v4

## Install

```sh
go get github.com/algolia/algoliasearch-client-go/v4
```

## Import changes

```go
// v3
import "github.com/algolia/algoliasearch-client-go/v3/algolia/search"

// v4
import "github.com/algolia/algoliasearch-client-go/v4/algolia/search"
```

## Client initialization

```go
// v3 — single return value
client := search.NewClient("APP_ID", "API_KEY")

// v4 — returns (client, error); handle the error
client, err := search.NewClient("APP_ID", "API_KEY")
if err != nil {
    panic(err)
}
```

## `InitIndex` removal

```go
// v3
index := client.InitIndex("INDEX_NAME")
response, err := index.Search("QUERY", nil)

// v4 — builder pattern with typed request constructors
response, err := client.SearchSingleIndex(
    client.NewApiSearchSingleIndexRequest("INDEX_NAME").
        WithSearchParams(search.SearchParamsObjectAsSearchParams(
            search.NewEmptySearchParamsObject().SetQuery("QUERY"))))
```

## Method renames

| v3 | v4 |
|----|-----|
| `index.Search()` | `client.SearchSingleIndex()` |
| `client.MultipleQueries()` | `client.Search()` |
| `client.CopyIndex()` / `MoveIndex()` / `CopyRules()` etc. | `client.OperationIndex()` |
| `index.Exists()` | `client.IndexExists()` |
| `index.WaitTask()` | `client.WaitForTask()` |
| `AddAPIKey` / `DeleteAPIKey` / `GetAPIKey` / `UpdateAPIKey` | `AddApiKey` / `DeleteApiKey` / `GetApiKey` / `UpdateApiKey` |
| `GenerateSecuredAPIKey` | `GenerateSecuredApiKey` |
| `RestoreAPIKey` | `RestoreApiKey` |
| `index.Batch` | `client.Batch` |
| `index.BrowseObjects` | `client.BrowseObjects` |
| `index.ClearObjects` | `client.ClearObjects` |
| `index.Delete` | `client.DeleteIndex` |
| `index.DeleteObject` | `client.DeleteObject` |
| `index.GetObject` | `client.GetObject` |
| `index.PartialUpdateObject` | `client.PartialUpdateObject` |
| `index.SaveObject` | `client.SaveObject` |
| `index.SetSettings` | `client.SetSettings` |

## Multiple index search

```go
response, err := client.Search(
    client.NewApiSearchRequest(
        search.NewEmptySearchMethodParams().SetRequests(
            []search.SearchQuery{
                *search.SearchForHitsAsSearchQuery(
                    search.NewEmptySearchForHits().SetIndexName("INDEX_1").SetQuery("QUERY")),
            })))
```

## Indexing

```go
response, err := client.SaveObject(
    client.NewApiSaveObjectRequest("INDEX_NAME",
        map[string]any{"objectID": "1", "name": "Record"}))

response, err := client.PartialUpdateObject(
    client.NewApiPartialUpdateObjectRequest("INDEX_NAME", "1",
        map[string]any{"name": "Updated"}))

response, err := client.DeleteObject(
    client.NewApiDeleteObjectRequest("INDEX_NAME", "1"))
```

## Settings

```go
settings, err := client.GetSettings(
    client.NewApiGetSettingsRequest("INDEX_NAME"))

response, err := client.SetSettings(
    client.NewApiSetSettingsRequest("INDEX_NAME",
        search.NewEmptyIndexSettings().SetSearchableAttributes([]string{"title"})))
```

## `OperationIndex` (copy / move)

```go
// copy
response, err := client.OperationIndex(
    client.NewApiOperationIndexRequest("SOURCE",
        search.NewEmptyOperationIndexParams().
            SetOperation(search.OperationType("copy")).
            SetDestination("DEST")))

// move / rename
response, err := client.OperationIndex(
    client.NewApiOperationIndexRequest("SOURCE",
        search.NewEmptyOperationIndexParams().
            SetOperation(search.OperationType("move")).
            SetDestination("DEST")))
```

## Wait pattern

```go
// v3
res, err := index.SaveObject(map[string]any{"objectID": "1"})
err = index.WaitTask(res.TaskID)

// v4
response, err := client.SaveObject(
    client.NewApiSaveObjectRequest("INDEX_NAME", map[string]any{"objectID": "1"}))
resp, err := client.WaitForTask("INDEX_NAME", *response.TaskID)
```

`WaitForTask` returns `*search.GetTaskResponse` (not just `error`).

Optional controls:
```go
resp, err := client.WaitForTask("INDEX_NAME", taskID,
    search.WithWaitForTaskMaxRetries(50),
    search.WithWaitForTaskTimeout(func(count int) time.Duration {
        return min(time.Duration(count)*200*time.Millisecond, 5*time.Second)
    }))
```

## `ReplaceAllObjects`

```go
res, err := client.ReplaceAllObjects(search.ReplaceAllObjectsParams{
    IndexName: "INDEX_NAME",
    Objects:   objects,
    Scopes:    []search.ScopeType{search.SCOPETYPE_SETTINGS, search.SCOPETYPE_RULES},
})
```

## `PartialUpdateObjects` — default changed

`opt.CreateIfNotExists()` (v3 default: `false`) is now an explicit field (v4 default: `true`). Set explicitly to avoid surprises:

```go
res, err := client.PartialUpdateObjects(search.PartialUpdateObjectsParams{
    IndexName:         "INDEX_NAME",
    Objects:           objects,
    CreateIfNotExists: algoliaUtils.ToPtr(false),
})
```

## Browse aggregator

```go
// v3 — ObjectIterator
iterator, err := index.BrowseObjects(nil)

// v4 — aggregator callback
objects := []map[string]any{}
_, err := client.BrowseObjects(search.BrowseObjectsParams{
    IndexName: "INDEX_NAME",
    Aggregator: func(response *search.BrowseResponse) {
        objects = append(objects, response.Hits...)
    },
})
```

## `ChunkedBatch` (now public)

```go
res, err := client.ChunkedBatch("INDEX_NAME", objects, search.ACTION_ADD_OBJECT,
    search.WithChunkedBatchWaitForTasks(true))
```

## Secured API key

```go
key, err := client.GenerateSecuredApiKey("parentApiKey", &search.SecuredApiKeyRestrictions{
    ValidUntil:      algoliaUtils.ToPtr(int64(1893456000)),
    RestrictIndices: []string{"INDEX_NAME"},
})
```

## Cross-app copy (`AccountClient` removed)

```go
src, _ := search.NewClient("SRC_APP_ID", "SRC_API_KEY")
dst, _ := search.NewClient("DST_APP_ID", "DST_API_KEY")

settings, _ := src.GetSettings(src.NewApiGetSettingsRequest("SRC_INDEX"))
dst.SetSettings(dst.NewApiSetSettingsRequest("DST_INDEX", *settings.IndexSettings))
// repeat for rules, synonyms, then saveObjects / replaceAllObjects for records
```

## Transformation helpers (new in v4)

```go
res, err := client.SaveObjectsWithTransformation("INDEX_NAME", objects,
    search.WithChunkedBatchWaitForTasks(true))

res, err := client.ReplaceAllObjectsWithTransformation("INDEX_NAME", objects,
    search.WithReplaceAllObjectsBatchSize(1000))
```
