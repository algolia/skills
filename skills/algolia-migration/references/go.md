# Upgrade the Go API client to version 4

> Keep your Go API client up to date to benefit from improvements and bug fixes.

The latest major version of the `algoliasearch-client-go` package is version 4.
This page helps you upgrade from version 3
and explains the breaking changes you need to address.

Algolia generates the version 4 clients from OpenAPI specifications,
which provides consistent behavior across all languages and up-to-date API coverage.
The main architectural change is the removal of the `InitIndex` pattern:
all methods are now on the `client` instance directly, with `indexName` as a parameter.

For the full list of changes, see the [Go changelog](/doc/libraries/sdk/changelog/go).

## Update your dependencies

Update the `algoliasearch-client-go` package to version 4:

```sh Command line icon=square-terminal theme={"system"}
go get github.com/algolia/algoliasearch-client-go/v4
```

## Update imports

The import path changed from `v3` to `v4`:

```go Go icon=code theme={"system"}
// version 3
import "github.com/algolia/algoliasearch-client-go/v3/algolia/search"

// version 4
import "github.com/algolia/algoliasearch-client-go/v4/algolia/search"
```

## Update client initialization

In version 3, `NewClient` returned a client directly.
In version 4, it returns a `(client, error)` pair, so you need to handle the error:

```go Go icon=code highlight={6-9} theme={"system"}
// version 3
client := search.NewClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")

// version 4
client, err := search.NewClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")
if err != nil {
  panic(err)
}
```

## Understand the new API surface

Version 4 introduces two major changes to the API surface:

* **No more `InitIndex`.**
  Version 3 relied on an index object with methods called on it.
  In version 4, all methods belong to the `client` instance,
  with `indexName` as a parameter.
* **Builder pattern for requests.**
  Version 4 introduces typed request builders (`NewApi*Request` constructors)
  with `With*` methods for optional parameters.

The builder pattern is more verbose than version 3's flat function signatures.
The tradeoff is strong typing, better IDE autocompletion,
and predictable structure that works well with AI coding assistants.

```go Go icon=code highlight={7-14} theme={"system"}
// version 3
client := search.NewClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")
index := client.InitIndex("INDEX_NAME")
index.Search("QUERY")

// version 4
client, err := search.NewClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")
if err != nil {
  panic(err)
}
response, err := client.SearchSingleIndex(client.NewApiSearchSingleIndexRequest(
  "INDEX_NAME").WithSearchParams(
    search.SearchParamsObjectAsSearchParams(
      search.NewEmptySearchParamsObject().SetQuery("QUERY"))))
```

<Tip>
  If you have many files to update,
  search your codebase for `InitIndex` or `.InitIndex(` to find every place that needs changing.
</Tip>

## Update search calls

### Search a single index

The `index.Search()` method is now [`client.SearchSingleIndex()`](/doc/libraries/sdk/methods/search/search-single-index).
Build the request with `NewApiSearchSingleIndexRequest` and attach search parameters with `WithSearchParams`:

```go Go icon=code highlight={7-11} theme={"system"}
// version 3
index := client.InitIndex("INDEX_NAME")
res, err := index.Search("QUERY", opt.Filters("category:Book"))

// version 4
response, err := client.SearchSingleIndex(client.NewApiSearchSingleIndexRequest(
  "INDEX_NAME").WithSearchParams(
    search.SearchParamsObjectAsSearchParams(
      search.NewEmptySearchParamsObject().
        SetQuery("QUERY").
        SetFacetFilters(search.ArrayOfFacetFiltersAsFacetFilters([]search.FacetFilters{*search.StringAsFacetFilters("category:Book")})))))
```

### Search multiple indices

The `client.MultipleQueries()` method is now [`client.Search()`](/doc/libraries/sdk/methods/search/search).
Each query in the request requires an `IndexName`:

```go Go icon=code highlight={8-14} theme={"system"}
// version 3
res, err := client.MultipleQueries([]search.IndexedQuery{
  {IndexName: "INDEX_1", Params: search.Params{Query: search.Query("QUERY")}},
  {IndexName: "INDEX_2", Params: search.Params{Query: search.Query("QUERY")}},
})

// version 4
response, err := client.Search(client.NewApiSearchRequest(
  search.NewEmptySearchMethodParams().SetRequests(
    []search.SearchQuery{
      *search.SearchForHitsAsSearchQuery(
        search.NewEmptySearchForHits().SetIndexName("INDEX_1").SetQuery("QUERY")),
      *search.SearchForHitsAsSearchQuery(
        search.NewEmptySearchForHits().SetIndexName("INDEX_2").SetQuery("QUERY")),
    })))
```

### Search for facet values

The `index.SearchForFacetValues()` method becomes `client.SearchForFacetValues()`
with an `indexName` parameter:

```go Go icon=code highlight={5-7} theme={"system"}
// version 3
index := client.InitIndex("INDEX_NAME")
res, err := index.SearchForFacetValues("category", "book", nil)

// version 4
response, err := client.SearchForFacetValues(client.NewApiSearchForFacetValuesRequest(
  "INDEX_NAME", "category"))
```

## Update indexing operations

In version 4, indexing methods are on the client instead of the index object,
with `indexName` as a parameter.

### Add or replace records

```go Go icon=code highlight={6-11} theme={"system"}
// version 3
index := client.InitIndex("INDEX_NAME")
res, err := index.SaveObject(map[string]any{"objectID": "1", "name": "Record"})

// version 4
response, err := client.SaveObject(client.NewApiSaveObjectRequest(
  "INDEX_NAME",
  map[string]any{
    "objectID": "1",
    "name":     "Record",
  }))
```

### Partially update records

```go Go icon=code highlight={5-7} theme={"system"}
// version 3
index := client.InitIndex("INDEX_NAME")
res, err := index.PartialUpdateObject(map[string]any{"objectID": "1", "name": "Updated"})

// version 4
response, err := client.PartialUpdateObject(client.NewApiPartialUpdateObjectRequest(
  "INDEX_NAME", "1", map[string]any{"name": "Updated"}))
```

### Delete records

```go Go icon=code highlight={5-7} theme={"system"}
// version 3
index := client.InitIndex("INDEX_NAME")
res, err := index.DeleteObject("1")

// version 4
response, err := client.DeleteObject(client.NewApiDeleteObjectRequest(
  "INDEX_NAME", "1"))
```

## Update settings, synonyms, and rules

### Get and set settings

```go Go icon=code highlight={7-14} theme={"system"}
// version 3
index := client.InitIndex("INDEX_NAME")
settings, err := index.GetSettings()
index.SetSettings(search.Settings{SearchableAttributes: opt.SearchableAttributes("title", "author")})

// version 4
settingsResponse, err := client.GetSettings(client.NewApiGetSettingsRequest(
  "INDEX_NAME"))

setResponse, err := client.SetSettings(client.NewApiSetSettingsRequest(
  "INDEX_NAME",
  search.NewEmptyIndexSettings().
    SetSearchableAttributes([]string{"title", "author"})))
```

### Save synonyms and rules

```go Go icon=code highlight={7-19} theme={"system"}
// version 3
index := client.InitIndex("INDEX_NAME")
index.SaveSynonyms([]search.Synonym{{ObjectID: "1", Type: search.RegularSynonymType, Synonyms: []string{"car", "auto"}}})
index.SaveRules([]search.Rule{{ObjectID: "1", Conditions: []search.RuleCondition{{Anchoring: search.Contains, Pattern: "shoes"}}, Consequence: search.RuleConsequence{Params: &search.RuleParams{Query: search.NewRuleQueryObject(search.RuleQueryObjectParams{Edits: []search.QueryEdit{{Type: search.Remove, Delete: "shoes", Insert: "sneakers"}}})}}}})

// version 4
synonymResponse, err := client.SaveSynonyms(client.NewApiSaveSynonymsRequest(
  "INDEX_NAME",
  []search.SynonymHit{
    *search.NewEmptySynonymHit().SetObjectID("1").
      SetType(search.SynonymType("synonym")).
      SetSynonyms([]string{"car", "auto"}),
  }))

rulesResponse, err := client.SaveRules(client.NewApiSaveRulesRequest(
  "INDEX_NAME",
  []search.Rule{
    *search.NewEmptyRule().SetObjectID("1").
      SetConditions([]search.Condition{
        *search.NewEmptyCondition().SetPattern("shoes").SetAnchoring(search.Anchoring("contains")),
      }).
      SetConsequence(search.NewEmptyConsequence().SetParams(
        search.NewEmptyConsequenceParams().SetFilters("brand:sneakers"))),
  }))
```

<Note>
  In version 3, `index.ReplaceAllRules()` and `index.ReplaceAllSynonyms()` replaced all rules or synonyms.
  In version 4, use `client.SaveRules()` or `client.SaveSynonyms()` with the `WithClearExistingRules(true)` or `WithReplaceExistingSynonyms(true)` option on the request builder.
</Note>

## Update index management

The `CopyIndex`, `MoveIndex`, `CopyRules`, `CopySynonyms`, and `CopySettings`
methods are all replaced by a single [`OperationIndex`](/doc/rest-api/search/operation-index) method.

### Copy an index

```go Go icon=code highlight={5-8} theme={"system"}
// version 3
client.CopyIndex("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME")

// version 4
response, err := client.OperationIndex(client.NewApiOperationIndexRequest(
  "SOURCE_INDEX_NAME",
  search.NewEmptyOperationIndexParams().
    SetOperation(search.OperationType("copy")).
    SetDestination("DESTINATION_INDEX_NAME")))
```

### Move (rename) an index

```go Go icon=code highlight={5-8} theme={"system"}
// version 3
client.MoveIndex("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME")

// version 4
response, err := client.OperationIndex(client.NewApiOperationIndexRequest(
  "SOURCE_INDEX_NAME",
  search.NewEmptyOperationIndexParams().
    SetOperation(search.OperationType("move")).
    SetDestination("DESTINATION_INDEX_NAME")))
```

### Copy only rules or settings

In version 4, use the `SetScope` parameter to limit the operation to specific data:

```go Go icon=code theme={"system"}
// version 4 -- copy only rules and settings from one index to another
response, err := client.OperationIndex(client.NewApiOperationIndexRequest(
  "SOURCE_INDEX_NAME",
  search.NewEmptyOperationIndexParams().
    SetOperation(search.OperationType("copy")).
    SetDestination("DESTINATION_INDEX_NAME").
    SetScope([]search.ScopeType{
      search.ScopeType("rules"),
      search.ScopeType("settings"),
    })))
```

### Check if an index exists

In version 3, you could check if an index existed using the `Exists` method on the index object.
In version 4, use the [`IndexExists`](/doc/libraries/sdk/methods/search/index-exists) helper method on the client:

```go Go icon=code highlight={5-6} theme={"system"}
// version 3
index := client.InitIndex("INDEX_NAME")
ok, err := index.Exists()

// version 4
response, err := client.IndexExists("INDEX_NAME")
```

## Update task handling

Version 3 supported chaining `.Wait()` on operations.
Version 4 replaces this pattern with dedicated wait helpers.

```go Go icon=code highlight={6-8} theme={"system"}
// version 3
index := client.InitIndex("INDEX_NAME")
res, err := index.SaveObjects(records)
res.Wait()

// version 4
response, err := client.SaveObjects("INDEX_NAME", records)
client.WaitForTask("INDEX_NAME", *response[0].TaskID)
```

Version 4 includes three wait helpers:

* [`WaitForTask`](/doc/libraries/sdk/methods/search/wait-for-task): wait until indexing operations are done.
* [`WaitForAppTask`](/doc/libraries/sdk/methods/search/wait-for-app-task): wait for application-level tasks.
* [`WaitForApiKey`](/doc/libraries/sdk/methods/search/wait-for-api-key): wait for API key operations.

## Helper method changes

The following sections document breaking changes in helper method signatures and behavior between version 3 and version 4.

### `ReplaceAllObjects`

The `opt.Safe()` functional option has been removed. In version 3, passing `opt.Safe(true)` caused the helper to wait after each step. In version 4, the helper always waits—equivalent to the previous `opt.Safe(true)` behavior.

```go Go icon=code highlight={4-9} theme={"system"}
// version 3
res, err := index.ReplaceAllObjects(objects, opt.Safe(true))

// version 4
res, err := client.ReplaceAllObjects(search.ReplaceAllObjectsParams{
    IndexName: "INDEX_NAME",
    Objects:   objects,
    Scopes:    []search.ScopeType{search.SCOPETYPE_SETTINGS, search.SCOPETYPE_RULES, search.SCOPETYPE_SYNONYMS},
})
```

### `SaveObjects`

The `opt.AutoGenerateObjectIDIfNotExist()` functional option has been removed. In version 4, every object must include an `ObjectID`. To have the API generate object IDs, use `ChunkedBatch` with `search.ACTION_ADD_OBJECT`.

```go Go icon=code highlight={4-9} theme={"system"}
// version 3
res, err := index.SaveObjects(objects, opt.AutoGenerateObjectIDIfNotExist(true))

// version 4
// Objects must include ObjectID, or use ChunkedBatch with ACTION_ADD_OBJECT
res, err := client.SaveObjects(search.SaveObjectsParams{
    IndexName: "INDEX_NAME",
    Objects:   objects,
})
```

### `PartialUpdateObjects`

The `opt.CreateIfNotExists()` functional option has been replaced with an explicit field on the params struct. The default also changed: in version 3 it defaulted to `false` (used `partialUpdateObjectNoCreate`); in version 4 it defaults to `true`.

```go Go icon=code highlight={5-11} theme={"system"}
// version 3
// Default: createIfNotExists = false
res, err := index.PartialUpdateObjects(objects, opt.CreateIfNotExists(true))

// version 4
// Default: createIfNotExists = true
res, err := client.PartialUpdateObjects(search.PartialUpdateObjectsParams{
    IndexName:         "INDEX_NAME",
    Objects:           objects,
    CreateIfNotExists: algoliaUtils.ToPtr(false), // explicitly set false to match old default
})
```

### `BrowseObjects`, `BrowseRules`, `BrowseSynonyms`

The `ObjectIterator`, `RuleIterator`, and `SynonymIterator` types have been removed. These helpers now use an `Aggregator` callback that is called with each page of results.

```go Go icon=code expandable highlight={9-19} theme={"system"}
// version 3
it, err := index.BrowseObjects()
for {
    obj, err := it.Next()
    if err == io.EOF {
        break
    }
    process(obj)
}

// version 4
objects := []map[string]any{}

_, err := client.BrowseObjects(search.BrowseObjectsParams{
    IndexName: "INDEX_NAME",
    Aggregator: func(response *search.BrowseResponse) {
        objects = append(objects, response.Hits...)
    },
})
```

### `DeleteObjects`

Two new optional parameters are available:

* `WithWaitForTasks(bool)` (default `false`)
* `WithBatchSize(int)` (default `1,000`)

```go Go icon=code highlight={4-7} theme={"system"}
// version 3
res, err := index.DeleteObjects([]string{"id1", "id2"})

// version 4
res, err := client.DeleteObjects("INDEX_NAME", []string{"id1", "id2"},
    search.WithDeleteObjectsWaitForTasks(true),
)
```

### `WaitForTask`

The helper was renamed from `WaitTask` to `WaitForTask`, moved to the client, and now returns `*GetTaskResponse` instead of `error`. The `timeToWait` config option is replaced by explicit `WithMaxRetries` and `WithTimeout` options—the default timeout uses exponential backoff capped at 5 seconds.

```go Go icon=code highlight={4-13} theme={"system"}
// version 3
err := index.WaitTask(taskID)

// version 4
resp, err := client.WaitForTask("INDEX_NAME", taskID)

// With explicit retry controls:
resp, err := client.WaitForTask("INDEX_NAME", taskID,
    search.WithWaitForTaskMaxRetries(50),
    search.WithWaitForTaskTimeout(func(count int) time.Duration {
        return min(time.Duration(count)*200*time.Millisecond, 5*time.Second)
    }),
)
```

### `WaitForAppTask`

This is a new helper in version 4.

```go Go icon=code theme={"system"}
resp, err := client.WaitForAppTask(taskID)
```

### `WaitForApiKey`

This is a new standalone helper in version 4. In version 3, waiting for API key operations required polling `GetAPIKey` manually.

```go Go icon=code theme={"system"}
// Wait for a key to be created:
resp, err := client.WaitForApiKey("my-api-key", search.APIKEYOPERATION_ADD, nil)

// Wait for a key update (pass the expected final state):
apiKey := &search.ApiKey{Acl: []search.Acl{search.ACL_SEARCH}}
resp, err := client.WaitForApiKey("my-api-key", search.APIKEYOPERATION_UPDATE,
    search.WithWaitForApiKeyApiKey(apiKey),
)
```

### `IndexExists`

The helper was renamed from `Exists()` on the index object to `IndexExists()` on the client.

```go Go icon=code highlight={4-5} theme={"system"}
// version 3
exists, err := index.Exists()

// version 4
exists, err := client.IndexExists("INDEX_NAME")
```

### `GenerateSecuredApiKey`

The function moved from a package-level function to a method on the client and was renamed from `GenerateSecuredAPIKey` to `GenerateSecuredApiKey`. The restrictions are now a single typed struct instead of variadic functional options.

```go Go icon=code highlight={7-11} theme={"system"}
// version 3
key, err := search.GenerateSecuredAPIKey("parentApiKey",
    opt.ValidUntil(1893456000),
    opt.RestrictIndices("INDEX_NAME"),
)

// version 4
key, err := client.GenerateSecuredApiKey("parentApiKey", &search.SecuredApiKeyRestrictions{
    ValidUntil:      algoliaUtils.ToPtr(int64(1893456000)),
    RestrictIndices: []string{"INDEX_NAME"},
})
```

### `GetSecuredApiKeyRemainingValidity`

The method was renamed from `GetSecuredAPIKeyRemainingValidity` to `GetSecuredApiKeyRemainingValidity`. The variadic options parameter has been removed.

```go Go icon=code highlight={4-5} theme={"system"}
// version 3
duration, err := client.GetSecuredAPIKeyRemainingValidity(key)

// version 4
duration, err := client.GetSecuredApiKeyRemainingValidity(key)
```

### `ChunkedBatch`

`ChunkedBatch` is now a public helper. In version 3, chunking was an internal detail of `SaveObjects`. The `action` parameter is required.

```go Go icon=code theme={"system"}
res, err := client.ChunkedBatch("INDEX_NAME", objects, search.ACTION_ADD_OBJECT,
    search.WithChunkedBatchWaitForTasks(true),
    search.WithChunkedBatchBatchSize(1000),
)
```

### `CopyIndexBetweenApplications`

In version 3, the `Account` type provided a `CopyIndex` method for copying an index between two different Algolia applications. It accepted two `*Index` values, each carrying its own app credentials.

In version 4, the `Account` type is removed. You can compose existing helpers across two clients to achieve the same result.

```go Go icon=code expandable highlight={5-49} theme={"system"}
// version 3
account := search.NewAccount(srcClient, destClient)
_, err := account.CopyIndex(srcIndex, destIndex)

// version 4
ctx := context.Background()
src, _ := search.NewClient("SRC_APP_ID", "SRC_API_KEY")
dst, _ := search.NewClient("DST_APP_ID", "DST_API_KEY")

// Copy settings
settings, _ := src.GetSettings(ctx, "SOURCE_INDEX")
dst.SetSettings(ctx, "DEST_INDEX", *settings)

// Copy rules
var rules []search.Rule
src.BrowseRules("SOURCE_INDEX", search.SearchRulesParams{},
    search.WithAggregator(func(res any, err error) {
        if r, ok := res.(*search.SearchRulesResponse); ok {
            rules = append(rules, r.Hits...)
        }
    }),
)
if len(rules) > 0 {
    dst.SaveRules(ctx, "DEST_INDEX", rules)
}

// Copy synonyms
var synonyms []search.SynonymHit
src.BrowseSynonyms("SOURCE_INDEX", search.SearchSynonymsParams{},
    search.WithAggregator(func(res any, err error) {
        if r, ok := res.(*search.SearchSynonymsResponse); ok {
            synonyms = append(synonyms, r.Hits...)
        }
    }),
)
if len(synonyms) > 0 {
    dst.SaveSynonyms(ctx, "DEST_INDEX", synonyms)
}

// Copy objects
var objects []map[string]any
src.BrowseObjects("SOURCE_INDEX", search.BrowseParamsObject{},
    search.WithAggregator(func(res any, err error) {
        if r, ok := res.(*search.BrowseResponse); ok {
            objects = append(objects, r.Hits...)
        }
    }),
)
dst.ReplaceAllObjects("DEST_INDEX", objects)
```

### `SaveObjectsWithTransformation`

New in version 4. Routes objects through the Algolia Push connector. Requires the `IngestionTransporter` to be configured at client initialization via a region.

```go Go icon=code theme={"system"}
res, err := client.SaveObjectsWithTransformation("INDEX_NAME", objects,
    search.WithChunkedBatchWaitForTasks(true),
    search.WithChunkedBatchBatchSize(1000),
)
```

### `ReplaceAllObjectsWithTransformation`

New in version 4. Atomically replaces all objects via the Push connector (copy settings/rules/synonyms to a temp index → push objects → move back). Requires the `IngestionTransporter` to be configured at client initialization.

```go Go icon=code theme={"system"}
res, err := client.ReplaceAllObjectsWithTransformation("INDEX_NAME", objects,
    search.WithReplaceAllObjectsBatchSize(1000),
    search.WithReplaceAllObjectsScopes([]search.ScopeType{
        search.SCOPETYPE_SETTINGS,
        search.SCOPETYPE_RULES,
        search.SCOPETYPE_SYNONYMS,
    }),
)
```

### `PartialUpdateObjectsWithTransformation`

New in version 4. Routes partial updates through the Push connector. The `createIfNotExists` option defaults to `false`.

```go Go icon=code theme={"system"}
res, err := client.PartialUpdateObjectsWithTransformation("INDEX_NAME", objects,
    search.WithPartialUpdateObjectsCreateIfNotExists(false),
    search.WithChunkedBatchWaitForTasks(false),
    search.WithChunkedBatchBatchSize(1000),
)
```

## Method changes reference

The following tables list all method names that changed between version 3 and version 4.

### Search API client

| Version 3 (legacy)                         |   | Version 4 (current)                        |
| ------------------------------------------ | - | ------------------------------------------ |
| `client.AddAPIKey`                         | → | `client.AddApiKey`                         |
| `client.AddAPIKey.wait`                    | → | `client.WaitForApiKey`                     |
| `client.ClearDictionaryEntries`            | → | `client.BatchDictionaryEntries`            |
| `client.CopyIndex`                         | → | `client.OperationIndex`                    |
| `client.CopyRules`                         | → | `client.OperationIndex`                    |
| `client.CopySynonyms`                      | → | `client.OperationIndex`                    |
| `client.DeleteAPIKey`                      | → | `client.DeleteApiKey`                      |
| `client.DeleteDictionaryEntries`           | → | `client.BatchDictionaryEntries`            |
| `client.GenerateSecuredAPIKey`             | → | `client.GenerateSecuredApiKey`             |
| `client.GetAPIKey`                         | → | `client.GetApiKey`                         |
| `client.GetSecuredAPIKeyRemainingValidity` | → | `client.GetSecuredApiKeyRemainingValidity` |
| `client.ListAPIKeys`                       | → | `client.ListApiKeys`                       |
| `client.ListIndices`                       | → | `client.ListIndices`                       |
| `client.MoveIndex`                         | → | `client.OperationIndex`                    |
| `client.MultipleBatch`                     | → | `client.MultipleBatch`                     |
| `client.MultipleQueries`                   | → | `client.Search`                            |
| `client.ReplaceDictionaryEntries`          | → | `client.BatchDictionaryEntries`            |
| `client.RestoreAPIKey`                     | → | `client.RestoreApiKey`                     |
| `client.SaveDictionaryEntries`             | → | `client.BatchDictionaryEntries`            |
| `client.UpdateAPIKey`                      | → | `client.UpdateApiKey`                      |
| `index.Batch`                              | → | `client.Batch`                             |
| `index.BrowseObjects`                      | → | `client.BrowseObjects`                     |
| `index.BrowseRules`                        | → | `client.BrowseRules`                       |
| `index.BrowseSynonyms`                     | → | `client.BrowseSynonyms`                    |
| `index.ClearObjects`                       | → | `client.ClearObjects`                      |
| `index.ClearRules`                         | → | `client.ClearRules`                        |
| `index.ClearSynonyms`                      | → | `client.ClearSynonyms`                     |
| `index.CopySettings`                       | → | `client.OperationIndex`                    |
| `index.Delete`                             | → | `client.DeleteIndex`                       |
| `index.DeleteBy`                           | → | `client.DeleteBy`                          |
| `index.DeleteObject`                       | → | `client.DeleteObject`                      |
| `index.DeleteObjects`                      | → | `client.DeleteObjects`                     |
| `index.DeleteRule`                         | → | `client.DeleteRule`                        |
| `index.DeleteSynonym`                      | → | `client.DeleteSynonym`                     |
| `index.Exists`                             | → | `client.IndexExists`                       |
| `index.FindObject`                         | → | `client.SearchSingleIndex`                 |
| `index.GetObject`                          | → | `client.GetObject`                         |
| `index.GetObjects`                         | → | `client.GetObjects`                        |
| `index.GetRule`                            | → | `client.GetRule`                           |
| `index.GetSettings`                        | → | `client.GetSettings`                       |
| `index.GetSynonym`                         | → | `client.GetSynonym`                        |
| `index.GetStatus`                          | → | `client.GetTask`                           |
| `index.PartialUpdateObject`                | → | `client.PartialUpdateObject`               |
| `index.PartialUpdateObjects`               | → | `client.PartialUpdateObjects`              |
| `index.ReplaceAllObjects`                  | → | `client.ReplaceAllObjects`                 |
| `index.ReplaceAllRules`                    | → | `client.SaveRules`                         |
| `index.ReplaceAllSynonyms`                 | → | `client.SaveSynonyms`                      |
| `index.SaveObject`                         | → | `client.SaveObject`                        |
| `index.SaveObjects`                        | → | `client.SaveObjects`                       |
| `index.SaveRule`                           | → | `client.SaveRule`                          |
| `index.SaveRules`                          | → | `client.SaveRules`                         |
| `index.SaveSynonym`                        | → | `client.SaveSynonym`                       |
| `index.SaveSynonyms`                       | → | `client.SaveSynonyms`                      |
| `index.Search`                             | → | `client.SearchSingleIndex`                 |
| `index.SearchForFacetValues`               | → | `client.SearchForFacetValues`              |
| `index.SearchRules`                        | → | `client.SearchRules`                       |
| `index.SearchSynonyms`                     | → | `client.SearchSynonyms`                    |
| `index.SetSettings`                        | → | `client.SetSettings`                       |
| `index.{operation}.wait`                   | → | `client.WaitForTask`                       |

### Recommend API client

| Version 3 (legacy)                   |   | Version 4 (current)         |
| ------------------------------------ | - | --------------------------- |
| `client.GetFrequentlyBoughtTogether` | → | `client.GetRecommendations` |
| `client.GetRecommendations`          | → | `client.GetRecommendations` |
| `client.GetRelatedProducts`          | → | `client.GetRecommendations` |