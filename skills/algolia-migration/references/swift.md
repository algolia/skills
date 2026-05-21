# Swift: v8 → v9

## Install

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

```swift
// v8
import AlgoliaSearchClient

// v9 — dedicated modules per API
import AlgoliaCore
import AlgoliaSearch

// Other API clients
import AlgoliaRecommend
import AlgoliaAbtesting
import AlgoliaAnalytics
```

## Client initialization

v9 initialization can throw — add `try`. All API calls are now `async` and require `try await`. Wrap in `Task {}` when calling from synchronous code.

```swift
// v8
let client = SearchClient(appID: "ID", apiKey: "KEY")

// v9
let client = try SearchClient(appID: "ID", apiKey: "KEY")
```

## Remove `index(withName:)`

```swift
// v8
let index = client.index(withName: "INDEX_NAME")
index.search(query: "QUERY")

// v9 — completion handlers replaced by async/await
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
| `client.multipleQueries()` | `client.search()` |
| `index.search()` | `client.searchSingleIndex("INDEX_NAME", ...)` |
| `index.searchForFacetValues()` | `client.searchForFacetValues("INDEX_NAME", ...)` |
| `index.exists()` | `client.indexExists(indexName:)` |
| `index.replaceAllRules()` | `client.saveRules()` with `clearExistingRules` |
| `index.replaceAllSynonyms()` | `client.saveSynonyms()` with `clearExistingSynonyms` |
| `client.copyIndex()` / `moveIndex()` | `client.operationIndex()` |
| `index.waitTask()` | `client.waitForTask()` |
| `generateSecuredAPIKey()` | `generateSecuredApiKey()` |
| `addAPIKey()` / `deleteAPIKey()` | `addApiKey()` / `deleteApiKey()` |

## Multiple index search

```swift
let response: SearchResponses<Hit> = try await client.search(
    searchMethodParams: SearchMethodParams(requests: [
        SearchQuery.searchForHits(SearchForHits(indexName: "INDEX_1", query: "QUERY")),
        SearchQuery.searchForHits(SearchForHits(indexName: "INDEX_2", query: "QUERY")),
    ])
)
```

## Indexing

```swift
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
try await client.operationIndex(indexName: "SOURCE",
    operationIndexParams: OperationIndexParams(operation: OperationType.copy, destination: "DEST"))

// move
try await client.operationIndex(indexName: "SOURCE",
    operationIndexParams: OperationIndexParams(operation: OperationType.move, destination: "DEST"))

// copy with scope
try await client.operationIndex(indexName: "SOURCE",
    operationIndexParams: OperationIndexParams(operation: OperationType.copy, destination: "DEST",
        scope: [ScopeType.rules, ScopeType.settings]))

// check if index exists (new in v9)
let response = try await client.indexExists(indexName: "INDEX_NAME")
```

## Wait pattern

```swift
// v8 — completion handler with manual polling
index.saveObject(record) { result in ... }

// v9
let response = try await client.saveObjects(indexName: "INDEX_NAME", objects: records)
try await client.waitForTask(indexName: "INDEX_NAME", taskID: Int64(response.taskID))

// new helpers
try await client.waitForAppTask(taskID: taskID)
try await client.waitForApiKey(key: "my-api-key", operation: .add)
try await client.waitForApiKey(key: "my-api-key", operation: .update,
    apiKey: ApiKey(acl: [.search]))
```

## Helper method changes

- **`replaceAllObjects`**: `safe` removed; scopes required:
```swift
let response = try await client.replaceAllObjects(
    indexName: "INDEX_NAME", objects: objects, scopes: [.settings, .rules, .synonyms])
```
- **`saveObjects`**: `autoGeneratingObjectID` removed; use `chunkedBatch` with `.addObject` for auto-ID; new `waitForTasks` and `batchSize`:
```swift
try await client.saveObjects(indexName: "INDEX_NAME", objects: objects)
try await client.saveObjects(indexName: "INDEX_NAME", objects: objects, waitForTasks: true)
```
- **`deleteObjects`**: input changed from `[ObjectID]` to `[String]`; new `waitForTasks` and `batchSize`:
```swift
try await client.deleteObjects(indexName: "INDEX_NAME", objectIDs: ["id1", "id2"], waitForTasks: true)
```
- **`partialUpdateObjects`**: `createIfNotExists` default changed from `true` (v8) to `false` (v9) — must now be explicit:
```swift
try await client.partialUpdateObjects(indexName: "INDEX_NAME", objects: myObjects, createIfNotExists: true)
```
- **`browseObjects` / `browseRules` / `browseSynonyms`**: completion handlers replaced by aggregator closure:
```swift
// v8 — completion handler
index.browseObjects() { result in switch result { ... } }

// v9 — aggregator closure
var objects: [Hit] = []
try await client.browseObjects(
    indexName: "INDEX_NAME",
    browseParams: BrowseParamsObject(),
    aggregator: { response in objects.append(contentsOf: response.hits) }
)
```
- **`generateSecuredApiKey` / `getSecuredApiKeyRemainingValidity`**: renamed from `APIKey` (all caps) to `ApiKey` (title case); external parameter labels changed:
```swift
// v8
let key = SearchClient.generateSecuredAPIKey(withParent: "parentApiKey", parameters: ...)
let remaining = SearchClient.getSecuredAPIKeyRemainingValidity(of: key)

// v9
let key = try SearchClient.generateSecuredApiKey(
    parentApiKey: "parentApiKey",
    restrictions: SecuredApiKeyRestrictions(validUntil: 1893456000))
let remaining = try SearchClient.getSecuredApiKeyRemainingValidity(for: key)
```
- **`chunkedBatch`** (now public):
```swift
try await client.chunkedBatch(
    indexName: "INDEX_NAME", objects: myObjects, action: .addObject, waitForTasks: true)
```

## Cross-app copy (`AccountClient` removed)

```swift
let src = try SearchClient(appID: "SRC_APP_ID", apiKey: "SRC_API_KEY")
let dst = try SearchClient(appID: "DST_APP_ID", apiKey: "DST_API_KEY")

let settings = try await src.getSettings(indexName: "SOURCE_INDEX")
try await dst.setSettings(indexName: "DEST_INDEX", indexSettings: settings)

var rules: [Rule] = []
try await src.browseRules(indexName: "SOURCE_INDEX") { rules.append(contentsOf: $0.hits) }
if !rules.isEmpty { try await dst.saveRules(indexName: "DEST_INDEX", rules: rules) }

// repeat for synonyms, then browseObjects + replaceAllObjects
```

## Method changes reference

| v8 | v9 |
|----|----|
| `client.multipleQueries()` | `client.search()` |
| `client.copyIndex()` | `client.operationIndex()` |
| `client.moveIndex()` | `client.operationIndex()` |
| `client.generateSecuredAPIKey()` | `client.generateSecuredApiKey()` |
| `client.addAPIKey()` | `client.addApiKey()` |
| `client.deleteAPIKey()` | `client.deleteApiKey()` |
| `index.batch()` | `client.batch(indexName:, ...)` |
| `index.browseObjects()` | `client.browseObjects(indexName:, ..., aggregator:)` |
| `index.browseRules()` | `client.browseRules(indexName:, ...)` |
| `index.browseSynonyms()` | `client.browseSynonyms(indexName:, ...)` |
| `index.clearObjects()` | `client.clearObjects(indexName:)` |
| `index.clearRules()` | `client.clearRules(indexName:)` |
| `index.clearSynonyms()` | `client.clearSynonyms(indexName:)` |
| `index.delete()` | `client.deleteIndex(indexName:)` |
| `index.deleteBy()` | `client.deleteBy(indexName:, ...)` |
| `index.deleteObject()` | `client.deleteObject(indexName:, objectID:)` |
| `index.deleteObjects()` | `client.deleteObjects(indexName:, objectIDs:)` |
| `index.deleteRule()` | `client.deleteRule(indexName:, ruleID:)` |
| `index.deleteSynonym()` | `client.deleteSynonym(indexName:, objectID:)` |
| `index.exists()` | `client.indexExists(indexName:)` |
| `index.getObject()` | `client.getObject(indexName:, objectID:)` |
| `index.getObjects()` | `client.getObjects(...)` |
| `index.getRule()` | `client.getRule(indexName:, ruleID:)` |
| `index.getSettings()` | `client.getSettings(indexName:)` |
| `index.getSynonym()` | `client.getSynonym(indexName:, objectID:)` |
| `index.getTask()` | `client.getTask(indexName:, taskID:)` |
| `index.partialUpdateObject()` | `client.partialUpdateObject(indexName:, objectID:, ...)` |
| `index.partialUpdateObjects()` | `client.partialUpdateObjects(indexName:, ...)` |
| `index.replaceAllObjects()` | `client.replaceAllObjects(indexName:, objects:, scopes:)` |
| `index.replaceAllRules()` | `client.saveRules(indexName:, rules:)` |
| `index.replaceAllSynonyms()` | `client.saveSynonyms(indexName:, synonymHit:)` |
| `index.saveObject()` | `client.saveObject(indexName:, body:)` |
| `index.saveObjects()` | `client.saveObjects(indexName:, objects:)` |
| `index.saveRule()` | `client.saveRule(indexName:, ...)` |
| `index.saveRules()` | `client.saveRules(indexName:, rules:)` |
| `index.saveSynonym()` | `client.saveSynonym(indexName:, ...)` |
| `index.saveSynonyms()` | `client.saveSynonyms(indexName:, synonymHit:)` |
| `index.search()` | `client.searchSingleIndex(indexName:, searchParams:)` |
| `index.searchForFacetValues()` | `client.searchForFacetValues(indexName:, ...)` |
| `index.searchRules()` | `client.searchRules(indexName:, ...)` |
| `index.searchSynonyms()` | `client.searchSynonyms(indexName:, ...)` |
| `index.setSettings()` | `client.setSettings(indexName:, indexSettings:)` |
| `index.waitTask()` | `client.waitForTask(indexName:, taskID:)` |

Recommend API renames:

| v8 | v9 |
|----|----|
| `recommend.getFrequentlyBoughtTogether()` | `recommend.getRecommendations()` |
| `recommend.getRelatedProducts()` | `recommend.getRecommendations()` |
