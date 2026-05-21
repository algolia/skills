# Go: v3 → v4

## Install

```sh
go get github.com/algolia/algoliasearch-client-go/v4
```

## Import changes

Change `v3` to `v4` in every import path:

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

// v4 — returns (client, error)
client, err := search.NewClient("APP_ID", "API_KEY")
if err != nil {
    panic(err)
}
```

## Remove `InitIndex`

```go
// v3
index := client.InitIndex("INDEX_NAME")
index.Search("QUERY")

// v4 — builder pattern
client, err := search.NewClient("APP_ID", "API_KEY")
if err != nil {
    panic(err)
}
response, err := client.SearchSingleIndex(
    client.NewApiSearchSingleIndexRequest("INDEX_NAME").
        WithSearchParams(search.SearchParamsObjectAsSearchParams(
            search.NewEmptySearchParamsObject().SetQuery("QUERY"))))
```

## Method renames

| v3 | v4 |
|----|----|
| `index.Search()` | `client.SearchSingleIndex()` |
| `client.MultipleQueries()` | `client.Search()` |
| `client.CopyIndex()` / `MoveIndex()` / `CopyRules()` / `CopySynonyms()` | `client.OperationIndex()` |
| `index.Exists()` | `client.IndexExists()` |
| `index.WaitTask()` | `client.WaitForTask()` |
| `client.AddAPIKey` / `DeleteAPIKey` / `GetAPIKey` / `UpdateAPIKey` | `AddApiKey` / `DeleteApiKey` / `GetApiKey` / `UpdateApiKey` |
| `client.GenerateSecuredAPIKey` | `client.GenerateSecuredApiKey` |
| `client.GetSecuredAPIKeyRemainingValidity` | `client.GetSecuredApiKeyRemainingValidity` |
| `client.RestoreAPIKey` | `client.RestoreApiKey` |
| `client.ListAPIKeys` | `client.ListApiKeys` |
| `client.ClearDictionaryEntries` | `client.BatchDictionaryEntries` |
| `index.Batch` | `client.Batch` |
| `index.BrowseObjects` / `BrowseRules` / `BrowseSynonyms` | `client.BrowseObjects` / `BrowseRules` / `BrowseSynonyms` |
| `index.Delete` | `client.DeleteIndex` |
| `index.FindObject` | `client.SearchSingleIndex` |

## Search single index

```go
// v3
res, err := index.Search("QUERY", opt.Filters("category:Book"))

// v4
response, err := client.SearchSingleIndex(
    client.NewApiSearchSingleIndexRequest("INDEX_NAME").
        WithSearchParams(search.SearchParamsObjectAsSearchParams(
            search.NewEmptySearchParamsObject().
                SetQuery("QUERY").
                SetFacetFilters(search.ArrayOfFacetFiltersAsFacetFilters(
                    []search.FacetFilters{
                        *search.StringAsFacetFilters("category:Book"),
                    })))))
```

## Search multiple indices

```go
// v3 MultipleQueries → v4 Search
response, err := client.Search(
    client.NewApiSearchRequest(
        search.NewEmptySearchMethodParams().SetRequests(
            []search.SearchQuery{
                *search.SearchForHitsAsSearchQuery(
                    search.NewEmptySearchForHits().SetIndexName("INDEX_1").SetQuery("QUERY")),
                *search.SearchForHitsAsSearchQuery(
                    search.NewEmptySearchForHits().SetIndexName("INDEX_2").SetQuery("QUERY")),
            })))
```

## Indexing

```go
// SaveObject
response, err := client.SaveObject(
    client.NewApiSaveObjectRequest("INDEX_NAME",
        map[string]any{"objectID": "1", "name": "Record"}))

// PartialUpdateObject
response, err := client.PartialUpdateObject(
    client.NewApiPartialUpdateObjectRequest("INDEX_NAME", "1",
        map[string]any{"name": "Updated"}))

// DeleteObject
response, err := client.DeleteObject(
    client.NewApiDeleteObjectRequest("INDEX_NAME", "1"))
```

## Settings

```go
settingsResponse, err := client.GetSettings(
    client.NewApiGetSettingsRequest("INDEX_NAME"))

setResponse, err := client.SetSettings(
    client.NewApiSetSettingsRequest("INDEX_NAME",
        search.NewEmptyIndexSettings().SetSearchableAttributes([]string{"title", "author"})))
```

## `OperationIndex` (copy / move)

```go
// copy
response, err := client.OperationIndex(
    client.NewApiOperationIndexRequest("SOURCE",
        search.NewEmptyOperationIndexParams().
            SetOperation(search.OperationType("copy")).
            SetDestination("DEST")))

// move
response, err := client.OperationIndex(
    client.NewApiOperationIndexRequest("SOURCE",
        search.NewEmptyOperationIndexParams().
            SetOperation(search.OperationType("move")).
            SetDestination("DEST")))

// copy with scope
response, err := client.OperationIndex(
    client.NewApiOperationIndexRequest("SOURCE",
        search.NewEmptyOperationIndexParams().
            SetOperation(search.OperationType("copy")).
            SetDestination("DEST").
            SetScope([]search.ScopeType{
                search.ScopeType("rules"),
                search.ScopeType("settings"),
            })))

// IndexExists
response, err := client.IndexExists("INDEX_NAME")
```

## Task handling

```go
// v3
res, err := index.SaveObjects(records)
res.Wait()

// v4 — SaveObjects returns array of responses
response, err := client.SaveObjects("INDEX_NAME", records)
client.WaitForTask("INDEX_NAME", *response[0].TaskID)

// WaitForTask with controls
resp, err := client.WaitForTask("INDEX_NAME", taskID,
    search.WithWaitForTaskMaxRetries(50),
    search.WithWaitForTaskTimeout(func(count int) time.Duration {
        return min(time.Duration(count)*200*time.Millisecond, 5*time.Second)
    }))

// WaitForAppTask (new in v4)
resp, err := client.WaitForAppTask(taskID)

// WaitForApiKey (new in v4)
resp, err := client.WaitForApiKey("my-api-key", search.APIKEYOPERATION_ADD, nil)
resp, err := client.WaitForApiKey("my-api-key", search.APIKEYOPERATION_UPDATE,
    search.WithWaitForApiKeyApiKey(&search.ApiKey{Acl: []search.Acl{search.ACL_SEARCH}}))
```

`WaitForTask` is renamed from `WaitTask` and returns `*search.GetTaskResponse`.

## Helper method changes

### `ReplaceAllObjects`

Safe copy removed; always waits. Pass a struct:

```go
res, err := client.ReplaceAllObjects(search.ReplaceAllObjectsParams{
    IndexName: "INDEX_NAME",
    Objects:   objects,
    Scopes: []search.ScopeType{
        search.SCOPETYPE_SETTINGS,
        search.SCOPETYPE_RULES,
        search.SCOPETYPE_SYNONYMS,
    },
})
```

### `SaveObjects`

`AutoGenerateObjectIDIfNotExist` removed. Every object must have `objectID`, or use `ChunkedBatch` with `ACTION_ADD_OBJECT`:

```go
res, err := client.SaveObjects(search.SaveObjectsParams{
    IndexName: "INDEX_NAME",
    Objects:   objects,
})
```

### `PartialUpdateObjects`

`opt.CreateIfNotExists` replaced with explicit struct field. Default changed from `false` to `true` — set explicitly:

```go
res, err := client.PartialUpdateObjects(search.PartialUpdateObjectsParams{
    IndexName:         "INDEX_NAME",
    Objects:           objects,
    CreateIfNotExists: algoliaUtils.ToPtr(false),
})
```

### `DeleteObjects`

New `WithDeleteObjectsWaitForTasks` option:

```go
res, err := client.DeleteObjects("INDEX_NAME", []string{"id1", "id2"},
    search.WithDeleteObjectsWaitForTasks(true))
```

### `BrowseObjects` / `BrowseRules` / `BrowseSynonyms`

Iterators removed. Use an `Aggregator` callback:

```go
objects := []map[string]any{}
_, err := client.BrowseObjects(search.BrowseObjectsParams{
    IndexName: "INDEX_NAME",
    Aggregator: func(response *search.BrowseResponse) {
        objects = append(objects, response.Hits...)
    },
})
```

### `GenerateSecuredApiKey`

Moved to a client method; renamed from `GenerateSecuredAPIKey`:

```go
key, err := client.GenerateSecuredApiKey("parentApiKey", &search.SecuredApiKeyRestrictions{
    ValidUntil:      algoliaUtils.ToPtr(int64(1893456000)),
    RestrictIndices: []string{"INDEX_NAME"},
})
```

### `GetSecuredApiKeyRemainingValidity`

Renamed from `GetSecuredAPIKeyRemainingValidity`:

```go
duration, err := client.GetSecuredApiKeyRemainingValidity(key)
```

### `ChunkedBatch` (now public)

```go
res, err := client.ChunkedBatch("INDEX_NAME", objects, search.ACTION_ADD_OBJECT,
    search.WithChunkedBatchWaitForTasks(true),
    search.WithChunkedBatchBatchSize(1000))
```

### Cross-app copy (`AccountClient` removed)

Compose manually across two client instances:

```go
src, _ := search.NewClient("SRC_APP_ID", "SRC_API_KEY")
dst, _ := search.NewClient("DST_APP_ID", "DST_API_KEY")

settings, _ := src.GetSettings(src.NewApiGetSettingsRequest("SRC_INDEX"))
dst.SetSettings(dst.NewApiSetSettingsRequest("DST_INDEX", *settings))
// browse rules, synonyms, objects via BrowseObjects with aggregator,
// then SaveRules / SaveSynonyms / ReplaceAllObjects
```

### Transformation helpers (new in v4)

Require `IngestionTransporter` region to be set.

```go
// SaveObjectsWithTransformation
res, err := client.SaveObjectsWithTransformation("INDEX_NAME", objects,
    search.WithChunkedBatchWaitForTasks(true),
    search.WithChunkedBatchBatchSize(1000))

// ReplaceAllObjectsWithTransformation
res, err := client.ReplaceAllObjectsWithTransformation("INDEX_NAME", objects,
    search.WithReplaceAllObjectsBatchSize(1000),
    search.WithReplaceAllObjectsScopes([]search.ScopeType{
        search.SCOPETYPE_SETTINGS,
        search.SCOPETYPE_RULES,
        search.SCOPETYPE_SYNONYMS,
    }))

// PartialUpdateObjectsWithTransformation (createIfNotExists defaults false)
res, err := client.PartialUpdateObjectsWithTransformation("INDEX_NAME", objects,
    search.WithPartialUpdateObjectsCreateIfNotExists(false),
    search.WithChunkedBatchWaitForTasks(false),
    search.WithChunkedBatchBatchSize(1000))
```

## Method changes reference

Full rename table (PascalCase):

| v3 | v4 |
|----|----|
| `client.AddAPIKey` + `.wait` | `client.AddApiKey` + `client.WaitForApiKey` |
| `client.ClearDictionaryEntries` | `client.BatchDictionaryEntries` |
| `client.CopyIndex` / `CopyRules` / `CopySynonyms` / `MoveIndex` | `client.OperationIndex` |
| `client.DeleteAPIKey` | `client.DeleteApiKey` |
| `client.GenerateSecuredAPIKey` | `client.GenerateSecuredApiKey` |
| `client.GetAPIKey` | `client.GetApiKey` |
| `client.GetSecuredAPIKeyRemainingValidity` | `client.GetSecuredApiKeyRemainingValidity` |
| `client.ListAPIKeys` | `client.ListApiKeys` |
| `client.MultipleBatch` | `client.MultipleBatch` |
| `client.MultipleQueries` | `client.Search` |
| `client.RestoreAPIKey` | `client.RestoreApiKey` |
| `client.UpdateAPIKey` | `client.UpdateApiKey` |
| `index.Batch` | `client.Batch` |
| `index.BrowseObjects` / `BrowseRules` / `BrowseSynonyms` | `client.BrowseObjects` / `BrowseRules` / `BrowseSynonyms` |
| `index.ClearObjects` / `ClearRules` / `ClearSynonyms` | `client.ClearObjects` / `ClearRules` / `ClearSynonyms` |
| `index.CopySettings` | `client.OperationIndex` |
| `index.Delete` | `client.DeleteIndex` |
| `index.DeleteBy` | `client.DeleteBy` |
| `index.DeleteObject` / `DeleteObjects` / `DeleteRule` / `DeleteSynonym` | `client.DeleteObject` / `DeleteObjects` / `DeleteRule` / `DeleteSynonym` |
| `index.Exists` | `client.IndexExists` |
| `index.FindObject` | `client.SearchSingleIndex` |
| `index.GetObject` / `GetObjects` / `GetRule` / `GetSettings` / `GetSynonym` / `GetStatus` | `client.GetObject` / `GetObjects` / `GetRule` / `GetSettings` / `GetSynonym` / `GetTask` |
| `index.PartialUpdateObject` / `PartialUpdateObjects` | `client.PartialUpdateObject` / `PartialUpdateObjects` |
| `index.ReplaceAllObjects` / `ReplaceAllRules` / `ReplaceAllSynonyms` | `client.ReplaceAllObjects` / `client.SaveRules` (with `WithClearExistingRules(true)`) / `client.SaveSynonyms` (with `WithReplaceExistingSynonyms(true)`) |
| `index.SaveObject` / `SaveObjects` / `SaveRule` / `SaveRules` / `SaveSynonym` / `SaveSynonyms` | `client.SaveObject` / `SaveObjects` / `SaveRule` / `SaveRules` / `SaveSynonym` / `SaveSynonyms` |
| `index.Search` | `client.SearchSingleIndex` |
| `index.SearchForFacetValues` / `SearchRules` / `SearchSynonyms` | `client.SearchForFacetValues` / `SearchRules` / `SearchSynonyms` |
| `index.SetSettings` | `client.SetSettings` |
| `index.{operation}.wait` | `client.WaitForTask` |

### Recommend API renames

| v3 | v4 |
|----|----|
| `client.GetFrequentlyBoughtTogether` | `client.GetRecommendations` |
| `client.GetRelatedProducts` | `client.GetRecommendations` |
