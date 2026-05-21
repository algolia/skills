# Upgrade the Swift API client to version 9

> Keep your Swift API client up to date to benefit from improvements and bug fixes.

The latest major version of the `algoliasearch-client-swift` package is version 9.
This page helps you upgrade from version 8
and explains the breaking changes you need to address.

Algolia generates the version 9 clients from OpenAPI specifications,
which provides consistent behavior across all languages and up-to-date API coverage.
The main architectural changes are:

* The `index(withName:)` pattern is removed. All methods are now on the `client` instance directly, with `indexName` as a parameter.
* Client initialization can throw, so `try` is required.
* All API calls use Swift's native `async/await` concurrency model.
* All module names are prefixed with `Algolia` (for example, `import AlgoliaSearch` instead of `import Search`).
* The client is compatible with Swift 6.

For the full list of changes, see the [Swift changelog](/doc/libraries/sdk/changelog/swift).

## Update your dependencies

### Swift Package Manager

Update your Swift Package Manager dependency to version 9.
In your `Package.swift`, change the version requirement:

```swift Swift icon=code theme={"system"}
// version 8
.package(url: "https://github.com/algolia/algoliasearch-client-swift", from: "8.0.0")

// version 9
.package(url: "https://github.com/algolia/algoliasearch-client-swift", from: "9.0.0")
```

If you're using Xcode, update the package version in **File > Swift Packages**.

### CocoaPods

If you use CocoaPods, update your `Podfile`:

```ruby Ruby icon=code theme={"system"}
# version 8
pod 'AlgoliaSearchClient', '~> 8.0'

# version 9
pod 'AlgoliaSearchClient', '~> 9.0.0'
```

<Note>
  With CocoaPods, all Algolia modules are bundled into a single `AlgoliaSearchClient` module.
  This means you use `import AlgoliaSearchClient` instead of the individual module imports
  shown in the rest of this guide.

To support CocoaPods' module flattening,
some model names are prefixed with the client name to avoid conflicts.
This applies regardless of your installation method.
The prefixed names are more verbose,
but the tradeoff is better autocompletion in IDEs and more predictable structure
that works well with AI coding assistants.
</Note>

## Update imports

Since version 9.40.0, all module names are prefixed with `Algolia` to avoid conflicts with other dependencies.
The main module changed from `AlgoliaSearchClient` to `AlgoliaSearch`:

```swift Swift icon=code theme={"system"}
// version 8
import AlgoliaSearchClient

// version 9
import AlgoliaCore
import AlgoliaSearch
```

Most version 9 code requires `AlgoliaCore` alongside the API-specific module,
since `AlgoliaCore` defines shared types such as `SearchClient` configuration and request options.

Version 9 includes dedicated modules for each API.
To access methods from a specific API,
import the corresponding module:

```swift Swift icon=code theme={"system"}
// Search API
import AlgoliaSearch
// Recommend API
import AlgoliaRecommend
// A/B testing API
import AlgoliaAbtesting
// Analytics API
import AlgoliaAnalytics
// Personalization API
import AlgoliaPersonalization
// Query Suggestions API
import AlgoliaQuerySuggestions
```

## Update client initialization

In version 9, `SearchClient` initialization can throw,
requiring the `try` keyword:

```swift Swift icon=code highlight={5} theme={"system"}
// version 8
let client = SearchClient(appID: "ALGOLIA_APPLICATION_ID", apiKey: "ALGOLIA_API_KEY")

// version 9
let client = try SearchClient(appID: "ALGOLIA_APPLICATION_ID", apiKey: "ALGOLIA_API_KEY")
```

<Note>
  The `try` keyword is required because version 9 validates
  your application ID and API key during initialization.
  If you're initializing the client inside a function that doesn't already throw,
  wrap it in a `do`/`catch` block.
</Note>

The other major change concerns what follows initialization:
`index(withName:)` no longer exists.

## Remove `index(withName:)`

This is the most significant change when upgrading.
Version 8 relied on an index object with methods called on it.
In version 9, all methods belong to the `client` instance,
with `indexName` as a parameter.

```swift Swift icon=code highlight={7-13} theme={"system"}
// version 8
let client = SearchClient(appID: "ALGOLIA_APPLICATION_ID", apiKey: "ALGOLIA_API_KEY")
let index = client.index(withName: "INDEX_NAME")
index.search(query: "QUERY")

// version 9
let client = try SearchClient(appID: "ALGOLIA_APPLICATION_ID", apiKey: "ALGOLIA_API_KEY")
try await client.searchSingleIndex(
    indexName: "INDEX_NAME",
    searchParams: SearchSearchParams.searchSearchParamsObject(
        SearchSearchParamsObject(query: "QUERY")
    )
)
```

<Tip>
  If you have many files to update,
  search your codebase for `index(withName:)` or `.index(withName:` to find every place that needs changing.
</Tip>

## Add async/await

Version 9 is built on Swift's native concurrency model.
All API calls are `async` functions that require `try await`.

In version 8, API calls rely on completion handlers:

```swift Swift icon=code theme={"system"}
// version 8 -- completion handler
let index = client.index(withName: "INDEX_NAME")
index.search(query: Query("QUERY")) { result in
    switch result {
    case .success(let response):
        print(response.hits)
    case .failure(let error):
        print(error)
    }
}

// version 9 -- async/await
let response: SearchResponse<Hit> = try await client.searchSingleIndex(
    indexName: "INDEX_NAME",
    searchParams: SearchSearchParams.searchSearchParamsObject(
        SearchSearchParamsObject(query: "QUERY")
    )
)
```

If you're calling Algolia methods from synchronous code, wrap them in a `Task`:

```swift Swift icon=code theme={"system"}
// version 9 -- calling from synchronous code
Task {
    do {
        let response: SearchResponse<Hit> = try await client.searchSingleIndex(
            indexName: "INDEX_NAME",
            searchParams: SearchSearchParams.searchSearchParamsObject(
                SearchSearchParamsObject(query: "QUERY")
            )
        )
        print(response.hits)
    } catch {
        print(error)
    }
}
```

## Update search calls

### Search a single index

The `index.search()` method is now [`client.searchSingleIndex()`](/doc/libraries/sdk/methods/search/search-single-index).
Pass the index name and search parameters as named arguments:

```swift Swift icon=code highlight={6-13} theme={"system"}
// version 8
let index = client.index(withName: "INDEX_NAME")
let result = index.search(query: "QUERY")

// version 9
let result: SearchResponse<Hit> = try await client.searchSingleIndex(
    indexName: "INDEX_NAME",
    searchParams: SearchSearchParams.searchSearchParamsObject(
        SearchSearchParamsObject(
            query: "QUERY",
            facetFilters: SearchFacetFilters.arrayOfSearchFacetFilters(
                [SearchFacetFilters.string("category:Book")]
            )
        )
    )
)
```

### Search multiple indices

The `client.multipleQueries()` method is now [`client.search()`](/doc/libraries/sdk/methods/search/search).
Each request in the array requires an `indexName`:

```swift Swift icon=code highlight={8-18} theme={"system"}
// version 8
let results = client.multipleQueries(queries: [
    IndexQuery(indexName: "INDEX_1", query: Query("QUERY")),
    IndexQuery(indexName: "INDEX_2", query: Query("QUERY")),
])

// version 9
let response: SearchResponses<Hit> = try await client.search(
    searchMethodParams: SearchMethodParams(
        requests: [
            SearchQuery.searchForHits(SearchForHits(
                indexName: "INDEX_1",
                query: "QUERY"
            )),
            SearchQuery.searchForHits(SearchForHits(
                indexName: "INDEX_2",
                query: "QUERY"
            )),
        ]
    )
)
```

### Search for facet values

The `index.searchForFacetValues()` method becomes `client.searchForFacetValues()`
with an `indexName` parameter:

```swift Swift icon=code highlight={6-10} theme={"system"}
// version 8
let index = client.index(withName: "INDEX_NAME")
let results = index.searchForFacetValues(of: "category", matching: "book")

// version 9
let results = try await client.searchForFacetValues(
    indexName: "INDEX_NAME",
    facetName: "category",
    searchForFacetValuesRequest: SearchForFacetValuesRequest(facetQuery: "book")
)
```

## Update indexing operations

In version 9, indexing methods are on the client instead of the index object,
with `indexName` as a parameter.

### Add or replace records

```swift Swift icon=code highlight={6-13} theme={"system"}
// version 8
let index = client.index(withName: "INDEX_NAME")
index.saveObject(["objectID": "1", "name": "Record"])

// version 9
let response = try await client.saveObject(
    indexName: "INDEX_NAME",
    body: [
        "objectID": "1",
        "name": "Record",
    ]
)
// saveObjects works the same way:
let response = try await client.saveObjects(
    indexName: "INDEX_NAME",
    objects: [["objectID": "1", "name": "Record"]]
)
```

### Partially update records

```swift Swift icon=code highlight={5-9} theme={"system"}
// version 8
let index = client.index(withName: "INDEX_NAME")
index.partialUpdateObject(["objectID": "1", "name": "Updated"])

// version 9
let response = try await client.partialUpdateObject(
    indexName: "INDEX_NAME",
    objectID: "1",
    attributesToUpdate: ["name": "Updated"]
)
```

### Delete records

```swift Swift icon=code highlight={5} theme={"system"}
// version 8
let index = client.index(withName: "INDEX_NAME")
index.deleteObject(withID: "1")

// version 9
let response = try await client.deleteObject(indexName: "INDEX_NAME", objectID: "1")
```

## Update settings, synonyms, and rules

### Get and set settings

```swift Swift icon=code highlight={6-12} theme={"system"}
// version 8
let index = client.index(withName: "INDEX_NAME")
let settings = index.getSettings()
index.setSettings(Settings().set(\.searchableAttributes, to: ["title", "author"]))

// version 9
let settings = try await client.getSettings(
    indexName: "INDEX_NAME"
)
try await client.setSettings(
    indexName: "INDEX_NAME",
    indexSettings: IndexSettings(searchableAttributes: ["title", "author"])
)
```

### Save synonyms and rules

```swift Swift icon=code highlight={6-13} theme={"system"}
// version 8
let index = client.index(withName: "INDEX_NAME")
index.saveSynonyms([Synonym.regular(objectID: "1", synonyms: ["car", "auto"])])
index.saveRules([Rule(objectID: "1")])

// version 9
try await client.saveSynonyms(
    indexName: "INDEX_NAME",
    synonymHit: [SynonymHit(objectID: "1", type: SynonymType.synonym, synonyms: ["car", "auto"])]
)
try await client.saveRules(
    indexName: "INDEX_NAME",
    rules: [Rule(
        objectID: "1",
        conditions: [SearchCondition(pattern: "shoes", anchoring: SearchAnchoring.contains)],
        consequence: SearchConsequence(params: SearchConsequenceParams(filters: "brand:nike"))
    )]
)
```

<Note>
  In version 8, `index.replaceAllRules()` and `index.replaceAllSynonyms()` replaced all rules or synonyms.
  In version 9, use `client.saveRules()` or `client.saveSynonyms()` with the `clearExistingRules` or `replaceExistingSynonyms` parameter set to `true`.
</Note>

## Update index management

The `copyIndex`, `moveIndex`, `copyRules`, `copySynonyms`, and `copySettings`
methods are all replaced by a single [`operationIndex`](/doc/rest-api/search/operation-index) method.

### Copy an index

```swift Swift icon=code highlight={5-10} theme={"system"}
// version 8
client.copyIndex(from: "SOURCE_INDEX_NAME", to: "DESTINATION_INDEX_NAME")

// version 9
try await client.operationIndex(
    indexName: "SOURCE_INDEX_NAME",
    operationIndexParams: OperationIndexParams(
        operation: OperationType.copy,
        destination: "DESTINATION_INDEX_NAME"
    )
)
```

### Move (rename) an index

```swift Swift icon=code highlight={5-10} theme={"system"}
// version 8
client.moveIndex(from: "SOURCE_INDEX_NAME", to: "DESTINATION_INDEX_NAME")

// version 9
try await client.operationIndex(
    indexName: "SOURCE_INDEX_NAME",
    operationIndexParams: OperationIndexParams(
        operation: OperationType.move,
        destination: "DESTINATION_INDEX_NAME"
    )
)
```

### Copy only rules or settings

In version 9, use the `scope` parameter to limit the operation to specific data:

```swift Swift icon=code theme={"system"}
// version 9 -- copy only rules and settings from one index to another
try await client.operationIndex(
    indexName: "SOURCE_INDEX_NAME",
    operationIndexParams: OperationIndexParams(
        operation: OperationType.copy,
        destination: "DESTINATION_INDEX_NAME",
        scope: [ScopeType.rules, ScopeType.settings]
    )
)
```

### Check if an index exists

In version 8, you could check if an index existed using the `exists` method on the index object.
In version 9, use the [`indexExists`](/doc/libraries/sdk/methods/search/index-exists) helper method on the client:

```swift Swift icon=code highlight={5-6} theme={"system"}
// version 8
let index = client.index(withName: "INDEX_NAME")
index.exists()

// version 9
let response = try await client.indexExists(indexName: "INDEX_NAME")
```

## Update task handling

Version 8 supported chaining `.wait()` on operations.
Version 9 replaces this pattern with dedicated wait helpers.

```swift Swift icon=code highlight={6-10} theme={"system"}
// version 8
let index = client.index(withName: "INDEX_NAME")
index.saveObjects(records).wait()

// version 9
let response = try await client.saveObjects(
    indexName: "INDEX_NAME",
    objects: records
)
try await client.waitForTask(indexName: "INDEX_NAME", taskID: Int64(response.taskID))
```

Version 9 includes three wait helpers:

* [`waitForTask`](/doc/libraries/sdk/methods/search/wait-for-task): wait until indexing operations are done.
* [`waitForAppTask`](/doc/libraries/sdk/methods/search/wait-for-app-task): wait for application-level tasks.
* [`waitForApiKey`](/doc/libraries/sdk/methods/search/wait-for-api-key): wait for API key operations.

## Helper method changes

The following sections document breaking changes in helper method signatures and behavior between version 8 and version 9.

### `replaceAllObjects`

The `safe` parameter has been removed. In version 8, `safe: true` caused the helper to wait after each step. In version 9, the helper always waits—equivalent to the previous `safe: true` behavior.

The completion-handler-based API has also been removed in favor of Swift concurrency (`async`/`await`).

```swift Swift icon=code highlight={6-11} theme={"system"}
// version 8
index.replaceAllObjects(with: objects, safe: true) { result in
    // handle result
}

// version 9
let response = try await client.replaceAllObjects(
    indexName: "INDEX_NAME",
    objects: objects,
    scopes: [.settings, .rules, .synonyms]
)
```

### `saveObjects`

The `autoGeneratingObjectID` parameter has been removed. In version 9, every object must include an `objectID`. The completion-handler-based API has also been removed in favor of Swift concurrency.

```swift Swift icon=code highlight={6-8} theme={"system"}
// version 8
index.saveObjects(objects, autoGeneratingObjectID: true) { result in
    // handle result
}

// version 9
// Objects must include objectID, or use chunkedBatch with .addObject action
let response = try await client.saveObjects(indexName: "INDEX_NAME", objects: objects)
```

### `deleteObjects`

The input type changed from `[ObjectID]` (a typed wrapper) to `[String]`. The helper moved to the client, and two new optional parameters are available: `waitForTasks` (default `false`) and `batchSize` (default `1,000`).

```swift Swift icon=code highlight={6-11} theme={"system"}
// version 8
index.deleteObjects(withIDs: [ObjectID("id1"), ObjectID("id2")]) { result in
    // handle result
}

// version 9
try await client.deleteObjects(
    indexName: "INDEX_NAME",
    objectIDs: ["id1", "id2"],
    waitForTasks: true
)
```

### `partialUpdateObjects`

The input type changed from `[(objectID: ObjectID, update: PartialUpdate)]` to `[some Encodable]`. The `createIfNotExists` default flipped from `true` (version 8) to `false` (version 9). The completion-handler API was also replaced with Swift concurrency.

```swift Swift icon=code expandable highlight={10-16} theme={"system"}
// version 8
// createIfNotExists defaulted to true
index.partialUpdateObjects(
    updates: [(ObjectID("id1"), .set(attribute: "name", value: .string("new")))],
    createIfNotExists: false
) { result in
    // handle result
}

// version 9
// createIfNotExists defaults to false — set explicitly if you relied on the old default
try await client.partialUpdateObjects(
    indexName: "INDEX_NAME",
    objects: myObjects,
    createIfNotExists: true
)
```

### `browseObjects`, `browseRules`, `browseSynonyms`

In version 8, these helpers eagerly fetched all pages and returned the full result array via a completion handler or throwing call. In version 9, they accept an `aggregator` closure invoked with each page, use Swift concurrency, and accept an optional `validate` closure to stop early.

```swift Swift icon=code expandable highlight={11-20} theme={"system"}
// version 8
index.browseObjects() { result in
    switch result {
    case .success(let responses):
        let allHits = responses.flatMap { $0.hits }
    case .failure(let error):
        // handle error
    }
}

// version 9
var objects: [Hit] = []

try await client.browseObjects(
    indexName: "INDEX_NAME",
    browseParams: BrowseParamsObject(),
    aggregator: { response in
        objects.append(contentsOf: response.hits)
    }
)
```

### `generateSecuredApiKey` and `getSecuredApiKeyRemainingValidity`

Both method names changed from `API` (all caps) to `Api` (title case) to follow Swift naming conventions.

```swift Swift icon=code highlight={7-13} theme={"system"}
// version 8
let key = SearchClient.generateSecuredAPIKey(
    withParent: "parentApiKey",
    parameters: SecuredAPIKeyRestrictions(validUntil: 1893456000)
)
let remaining = SearchClient.getSecuredAPIKeyRemainingValidity(of: key)

// version 9
let key = try SearchClient.generateSecuredApiKey(
    parentApiKey: "parentApiKey",
    restrictions: SecuredApiKeyRestrictions(validUntil: 1893456000)
)
let remaining = try SearchClient.getSecuredApiKeyRemainingValidity(for: key)
```

### `waitForTask`

The helper was renamed from `waitTask` to `waitForTask`, moved to the client, and now uses Swift concurrency. The `timeout` parameter changed from `TimeInterval?` (a maximum wall-clock limit) to a retry-count-to-delay closure (exponential backoff). An explicit `maxRetries` parameter (default `50`) was added.

```swift Swift icon=code highlight={4-9} theme={"system"}
// version 8
try index.waitTask(withID: taskID, timeout: 30)

// version 9
try await client.waitForTask(
    indexName: "INDEX_NAME",
    taskID: taskID,
    maxRetries: 50
)
```

### `waitForAppTask`

This is a new helper in version 9.

```swift Swift icon=code theme={"system"}
try await client.waitForAppTask(taskID: taskID)
```

### `waitForApiKey`

This is a new standalone helper in version 9.

```swift Swift icon=code theme={"system"}
// Wait for a key to be created:
try await client.waitForApiKey(key: "my-api-key", operation: .add)

// Wait for a key update (pass the expected final state):
try await client.waitForApiKey(
    key: "my-api-key",
    operation: .update,
    apiKey: ApiKey(acl: [.search])
)
```

### `indexExists`

This helper is new in version 9.

```swift Swift icon=code theme={"system"}
let exists = try await client.indexExists(indexName: "INDEX_NAME")
```

### `chunkedBatch`

`chunkedBatch` is now a public helper in version 9. In version 8, chunking was an internal detail of `saveObjects`. The `action` parameter defaults to `.addObject` and `waitForTasks` defaults to `false`.

```swift Swift icon=code theme={"system"}
let responses = try await client.chunkedBatch(
    indexName: "INDEX_NAME",
    objects: myObjects,
    action: .addObject,
    waitForTasks: true
)
```

### `copyIndexBetweenApplications`

In version 8, the `AccountClient` struct provided a static `copyIndex(source:destination:)` method for copying an index between two different Algolia applications.

In version 9, `AccountClient` is removed. You can compose existing helpers across two clients to achieve the same result.

```swift Swift icon=code expandable highlight={4-29} theme={"system"}
// version 8
let tasks = try AccountClient.copyIndex(source: srcIndex, destination: destIndex)

// version 9
let src = try SearchClient(appID: "SRC_APP_ID", apiKey: "SRC_API_KEY")
let dst = try SearchClient(appID: "DST_APP_ID", apiKey: "DST_API_KEY")

// Copy settings
let settings = try await src.getSettings(indexName: "SOURCE_INDEX")
try await dst.setSettings(indexName: "DEST_INDEX", indexSettings: settings)

// Copy rules
var rules: [Rule] = []
try await src.browseRules(indexName: "SOURCE_INDEX") { rules.append(contentsOf: $0.hits) }
if !rules.isEmpty {
    try await dst.saveRules(indexName: "DEST_INDEX", rules: rules)
}

// Copy synonyms
var synonyms: [SynonymHit] = []
try await src.browseSynonyms(indexName: "SOURCE_INDEX") { synonyms.append(contentsOf: $0.hits) }
if !synonyms.isEmpty {
    try await dst.saveSynonyms(indexName: "DEST_INDEX", synonyms: synonyms)
}

// Copy objects
var objects: [MyModel] = []
try await src.browseObjects(indexName: "SOURCE_INDEX") { objects.append(contentsOf: $0.hits) }
try await dst.replaceAllObjects(indexName: "DEST_INDEX", objects: objects)
```

## Method changes reference

The following tables list all method names that changed between version 8 and version 9.

### Search API client

| Version 8 (legacy)                         |   | Version 9 (current)                        |
| ------------------------------------------ | - | ------------------------------------------ |
| `client.addAPIKey`                         | → | `client.addApiKey`                         |
| `client.addAPIKey.wait`                    | → | `client.waitForApiKey`                     |
| `client.clearDictionaryEntries`            | → | `client.batchDictionaryEntries`            |
| `client.copyIndex`                         | → | `client.operationIndex`                    |
| `client.copyRules`                         | → | `client.operationIndex`                    |
| `client.copySynonyms`                      | → | `client.operationIndex`                    |
| `client.deleteAPIKey`                      | → | `client.deleteApiKey`                      |
| `client.deleteDictionaryEntries`           | → | `client.batchDictionaryEntries`            |
| `client.generateSecuredAPIKey`             | → | `client.generateSecuredApiKey`             |
| `client.getAPIKey`                         | → | `client.getApiKey`                         |
| `client.getSecuredAPIKeyRemainingValidity` | → | `client.getSecuredApiKeyRemainingValidity` |
| `client.listAPIKeys`                       | → | `client.listApiKeys`                       |
| `client.listIndices`                       | → | `client.listIndices`                       |
| `client.moveIndex`                         | → | `client.operationIndex`                    |
| `client.batch`                             | → | `client.multipleBatch`                     |
| `client.multipleQueries`                   | → | `client.search`                            |
| `client.replaceDictionaryEntries`          | → | `client.batchDictionaryEntries`            |
| `client.restoreAPIKey`                     | → | `client.restoreApiKey`                     |
| `client.saveDictionaryEntries`             | → | `client.batchDictionaryEntries`            |
| `client.updateAPIKey`                      | → | `client.updateApiKey`                      |
| `index.batch`                              | → | `client.batch`                             |
| `index.browse`                             | → | `client.browseObjects`                     |
| `index.browseRules`                        | → | `client.browseRules`                       |
| `index.browseSynonyms`                     | → | `client.browseSynonyms`                    |
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
| `index.searchForFacetValues`               | → | `client.searchForFacetValues`              |
| `index.searchRules`                        | → | `client.searchRules`                       |
| `index.searchSynonyms`                     | → | `client.searchSynonyms`                    |
| `index.setSettings`                        | → | `client.setSettings`                       |
| `index.{operation}.wait`                   | → | `client.waitForTask`                       |

### Recommend API client

| Version 8 (legacy)                   |   | Version 9 (current)         |
| ------------------------------------ | - | --------------------------- |
| `client.getFrequentlyBoughtTogether` | → | `client.getRecommendations` |
| `client.getRecommendations`          | → | `client.getRecommendations` |
| `client.getRelatedProducts`          | → | `client.getRecommendations` |