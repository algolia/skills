# Swift: v8 → v9

## Package manager

**Swift Package Manager:**
```swift
// v8
.package(url: "https://github.com/algolia/algoliasearch-client-swift", from: "8.0.0")

// v9
.package(url: "https://github.com/algolia/algoliasearch-client-swift", from: "9.0.0")
```

**CocoaPods:**
```ruby
# v8
pod 'AlgoliaSearchClient', '~> 8.0'

# v9
pod 'AlgoliaSearchClient', '~> 9.0.0'
```

## Import changes

Module names now use `Algolia` prefix. Dedicated modules per API:

```swift
// v8
import AlgoliaSearchClient

// v9
import AlgoliaCore
import AlgoliaSearch

// Other API clients
import AlgoliaRecommend
import AlgoliaAbtesting
import AlgoliaAnalytics
```

## Client initialization

v9 initialization can throw — add `try`:

```swift
// v8
let client = SearchClient(appID: "ID", apiKey: "KEY")

// v9
let client = try SearchClient(appID: "ID", apiKey: "KEY")
```

## `index(withName:)` removal

```swift
// v8
let index = client.index(withName: "INDEX_NAME")
index.search(query: "QUERY")

// v9 — async/await required for all API calls
let response: SearchResponse<Hit> = try await client.searchSingleIndex(
    indexName: "INDEX_NAME",
    searchParams: SearchSearchParams.searchSearchParamsObject(
        SearchSearchParamsObject(query: "QUERY")
    )
)
```

## Async/await — completion handlers removed

All API calls in v9 are `async` functions that require `try await`:

```swift
// v8 — completion handler
index.search(query: Query("QUERY")) { result in
    switch result {
    case .success(let response): print(response.hits)
    case .failure(let error): print(error)
    }
}

// v9 — async/await
let response: SearchResponse<Hit> = try await client.searchSingleIndex(
    indexName: "INDEX_NAME",
    searchParams: SearchSearchParams.searchSearchParamsObject(
        SearchSearchParamsObject(query: "QUERY")
    )
)
```

## Method renames

| v8 | v9 |
|----|-----|
| `index.search()` | `client.searchSingleIndex()` |
| `client.multipleQueries()` | `client.search()` |
| `index.searchForFacetValues()` | `client.searchForFacetValues()` |
| `client.generateSecuredAPIKey()` | `client.generateSecuredApiKey()` |
| `client.copyIndex()` / `moveIndex()` | `client.operationIndex()` |
| `index.exists()` | `client.indexExists()` |
| `index.waitTask()` | `client.waitForTask()` |

## Indexing

```swift
// v9
let response = try await client.saveObject(
    indexName: "INDEX_NAME",
    body: ["objectID": "1", "name": "Record"]
)

try await client.partialUpdateObject(
    indexName: "INDEX_NAME",
    objectID: "1",
    attributesToUpdate: ["name": "Updated"]
)

try await client.deleteObject(indexName: "INDEX_NAME", objectID: "1")
```

## `operationIndex` (copy / move)

```swift
// copy
try await client.operationIndex(
    indexName: "SOURCE",
    operationIndexParams: OperationIndexParams(operation: .copy, destination: "DEST")
)

// move / rename
try await client.operationIndex(
    indexName: "SOURCE",
    operationIndexParams: OperationIndexParams(operation: .move, destination: "DEST")
)
```

## Wait pattern

```swift
// v8
index.saveObject(record) { result in ... }  // manual polling

// v9
let response = try await client.saveObject(indexName: "INDEX_NAME", body: record)
try await client.waitForTask(indexName: "INDEX_NAME", taskID: response.taskID)
```

Three helpers: `waitForTask`, `waitForAppTask`, `waitForApiKey`.

## `replaceAllObjects`

```swift
// v9 — safe removed; scopes required
try await client.replaceAllObjects(
    indexName: "INDEX_NAME",
    objects: myObjects,
    scopes: [.settings, .rules, .synonyms]
)
```

## `saveObjects` helper

```swift
// Save multiple objects with built-in task waiting
try await client.saveObjects(
    indexName: "INDEX_NAME",
    objects: myObjects,
    waitForTasks: true
)
```

## Browse aggregator

```swift
var objects: [MyModel] = []
try await client.browseObjects(
    indexName: "INDEX_NAME",
    browseParams: BrowseParamsObject(),
    aggregator: { response in
        objects.append(contentsOf: response.hits)
    }
)
```
