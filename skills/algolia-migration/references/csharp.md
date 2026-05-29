# Upgrade the C# API client to version 7

> Keep your C# API client up to date to benefit from improvements and bug fixes.

The latest major version of the `Algolia.Search` package is version 7.
This page helps you upgrade from version 6
and explains the breaking changes you need to address.

Algolia generates the version 7 clients from OpenAPI specifications,
which provides consistent behavior across all languages and up-to-date API coverage.
The main architectural change is the removal of the `InitIndex` pattern:
all methods are now on the `client` instance directly, with `indexName` as a parameter.

For the full list of changes, see the C# changelog.

## Update your dependencies

Update the `Algolia.Search` package to version 7:

```sh
dotnet add package Algolia.Search --version "7.*"
```

  Version 7 replaces the `Newtonsoft.Json` dependency with `System.Text.Json`.
  If your project relies on Newtonsoft-specific attributes or converters,
  see [Update the serialization library](#update-the-serialization-library) for migration guidance.

## Update imports

The package name remains `Algolia.Search`,
but several model types have been renamed.
For example, the `Query` class no longer exists.
It's replaced by `SearchParams` and `SearchParamsObject`.

```cs
// version 6
using Algolia.Search.Clients;
using Algolia.Search.Models.Search;

// version 7
using Algolia.Search.Clients;
using Algolia.Search.Models.Search;
```

The `SearchClient` class stays in the same namespace.
As you update your code, your IDE will flag missing types and suggest the correct `using` directives
for the new model classes.

## Update client initialization

Client creation is unchanged.
The constructor still accepts your application ID and API key:

```cs
// version 6
var client = new SearchClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");

// version 7
var client = new SearchClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");
```

The other major change concerns what follows initialization:
`InitIndex` no longer exists.

## Synchronous and asynchronous methods

Version 7 includes both synchronous and asynchronous variants for every API method.
Asynchronous methods have an `Async` suffix and return a `Task<T>`.
Synchronous methods keep the base name.

```cs
// Asynchronous (recommended)
var results = await client.SearchSingleIndexAsync<Hit>("INDEX_NAME", searchParams);

// Synchronous
var results = client.SearchSingleIndex<Hit>("INDEX_NAME", searchParams);
```

The code examples in this guide use the asynchronous variants.
If you prefer synchronous calls, drop the `Async` suffix and the `await` keyword.

## Remove `InitIndex`

This is the most significant change when upgrading.
Version 6 relied on an index object with methods called on it.
In version 7, all methods belong to the `client` instance,
with `indexName` as a parameter.

```cs
// version 6
var client = new SearchClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");
var index = client.InitIndex("INDEX_NAME");
var results = index.Search<Contact>(new Query("QUERY"));

// version 7
var client = new SearchClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY");
var results = await client.SearchSingleIndexAsync<Hit>(
    "INDEX_NAME",
    new SearchParams(new SearchParamsObject { Query = "QUERY" })
);
```

  If you have many files to update,
  search your codebase for `InitIndex` or `.InitIndex(` to find every place that needs changing.

## Update search calls

### Search a single index

The `index.Search()` method is now `client.SearchSingleIndexAsync()`.
Pass the index name and search parameters directly:

```cs
// version 6
var index = client.InitIndex("INDEX_NAME");
var results = await index.SearchAsync<Contact>(new Query("QUERY")
{
    FacetFilters = new List<string> { "category:Book" }
});

// version 7
var results = await client.SearchSingleIndexAsync<Hit>(
    "INDEX_NAME",
    new SearchParams(new SearchParamsObject
    {
        Query = "QUERY",
        FacetFilters = new FacetFilters(new List<string> { "category:Book" })
    })
);
```

### Search multiple indices

The `client.MultipleQueries()` method is now `client.SearchAsync()`.
Each request in the collection requires an `IndexName`:

```cs
// version 6
var results = await client.MultipleQueriesAsync<Hit>(
    new List<MultipleQueriesQuery>
    {
        new MultipleQueriesQuery { IndexName = "INDEX_1", Params = new Query("QUERY") },
        new MultipleQueriesQuery { IndexName = "INDEX_2", Params = new Query("QUERY") }
    }
);

// version 7
var results = await client.SearchAsync<Hit>(
    new SearchMethodParams
    {
        Requests = new List<SearchQuery>
        {
            new SearchQuery(new SearchForHits { IndexName = "INDEX_1", Query = "QUERY" }),
            new SearchQuery(new SearchForHits { IndexName = "INDEX_2", Query = "QUERY" })
        }
    }
);
```

### Search for facet values

The `index.SearchForFacetValues()` method becomes `client.SearchForFacetValuesAsync()`
with an `indexName` parameter:

```cs
// version 6
var index = client.InitIndex("INDEX_NAME");
var results = await index.SearchForFacetValueAsync("category", "book");

// version 7
var results = await client.SearchForFacetValuesAsync(
    "INDEX_NAME",
    "category",
    new SearchForFacetValuesRequest { FacetQuery = "book" }
);
```

## Update indexing operations

In version 7, indexing methods are on the client instead of the index object,
with `indexName` as a parameter.

### Add or replace records

```cs
// version 6
var index = client.InitIndex("INDEX_NAME");
await index.SaveObjectAsync(new { ObjectID = "1", Name = "Record" });
await index.SaveObjectsAsync(new List<object> { new { ObjectID = "1", Name = "Record" } });

// version 7
await client.SaveObjectAsync("INDEX_NAME", new { ObjectID = "1", Name = "Record" });
// SaveObjectsAsync works the same way:
// (note: pass a list of objects for the batch version)
await client.SaveObjectsAsync(
    "INDEX_NAME",
    new List<object> { new { ObjectID = "1", Name = "Record" } }
);
```

### Partially update records

```cs
// version 6
var index = client.InitIndex("INDEX_NAME");
await index.PartialUpdateObjectAsync(new { ObjectID = "1", Name = "Updated" });

// version 7
await client.PartialUpdateObjectAsync(
    "INDEX_NAME",
    "1",
    new { Name = "Updated" }
);
```

### Delete records

```cs
// version 6
var index = client.InitIndex("INDEX_NAME");
await index.DeleteObjectAsync("1");

// version 7
await client.DeleteObjectAsync("INDEX_NAME", "1");
```

## Update settings, synonyms, and rules

### Get and set settings

```cs
// version 6
var index = client.InitIndex("INDEX_NAME");
var settings = await index.GetSettingsAsync();
await index.SetSettingsAsync(new IndexSettings
{
    SearchableAttributes = new List<string> { "title", "author" }
});

// version 7
var settings = await client.GetSettingsAsync("INDEX_NAME");
await client.SetSettingsAsync(
    "INDEX_NAME",
    new IndexSettings
    {
        SearchableAttributes = new List<string> { "title", "author" }
    }
);
```

### Save synonyms and rules

```cs
// version 6
var index = client.InitIndex("INDEX_NAME");
await index.SaveSynonymsAsync(synonyms);
await index.SaveRulesAsync(rules);

// version 7
await client.SaveSynonymsAsync(
    "INDEX_NAME",
    synonyms
);
await client.SaveRulesAsync(
    "INDEX_NAME",
    rules
);
```

  In version 6, `index.ReplaceAllRules()` and `index.ReplaceAllSynonyms()` replaced all rules or synonyms.
  In version 7, use `client.SaveRulesAsync()` or `client.SaveSynonymsAsync()` with the `clearExistingRules` or `clearExistingSynonyms` parameter set to `true`.

## Update index management

The `CopyIndex`, `MoveIndex`, `CopyRules`, `CopySynonyms`, and `CopySettings`
methods are all replaced by `OperationIndexAsync`.

### Copy an index

```cs
// version 6
await client.CopyIndexAsync("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME");

// version 7
await client.OperationIndexAsync(
    "SOURCE_INDEX_NAME",
    new OperationIndexParams
    {
        Operation = OperationType.Copy,
        Destination = "DESTINATION_INDEX_NAME"
    }
);
```

### Move (rename) an index

```cs
// version 6
await client.MoveIndexAsync("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME");

// version 7
await client.OperationIndexAsync(
    "SOURCE_INDEX_NAME",
    new OperationIndexParams
    {
        Operation = OperationType.Move,
        Destination = "DESTINATION_INDEX_NAME"
    }
);
```

### Copy only rules or settings

In version 7, use the `Scope` parameter to limit the operation to specific data:

```cs
// version 7 -- copy only rules and settings from one index to another
await client.OperationIndexAsync(
    "SOURCE_INDEX_NAME",
    new OperationIndexParams
    {
        Operation = OperationType.Copy,
        Destination = "DESTINATION_INDEX_NAME",
        Scope = new List<ScopeType> { ScopeType.Rules, ScopeType.Settings }
    }
);
```

Note: the `Operation` and `Destination` parameters can also be passed via the constructor:

```cs
// version 7 (constructor form)
await client.OperationIndexAsync(
    "SOURCE_INDEX_NAME",
    new OperationIndexParams(OperationType.Copy, "DESTINATION_INDEX_NAME")
    {
        Scope = new List<ScopeType> { ScopeType.Rules, ScopeType.Settings }
    }
);
```

### Check if an index exists

In version 6, you could check if an index existed using the `Exists` method on the index object.
In version 7, use the `IndexExists` helper method on the client:

```cs
// version 6
var index = client.InitIndex("INDEX_NAME");
index.Exists();

// version 7
await client.IndexExistsAsync("INDEX_NAME");
```

## Update task handling

Version 6 supported chaining `.Wait()` on operations.
Version 7 replaces this pattern with dedicated wait helpers.

```cs
// version 6
var index = client.InitIndex("INDEX_NAME");
index.SaveObjects(records).Wait();

// version 7
await client.SaveObjectsAsync("INDEX_NAME", records, waitForTasks: true, requestOptions: null);
```

Version 7 includes three wait helpers:

* `WaitForTask`: wait until indexing operations are done.
* `WaitForAppTask`: wait for application-level tasks.
* `WaitForApiKey`: wait for API key operations.

## Update the serialization library

The `Algolia.Search` package no longer depends on `Newtonsoft.Json` for request serialization and response deserialization.
Version 7 uses .NET's official `System.Text.Json` package instead.

This is a significant change if your project relies on `Newtonsoft.Json` attributes
(such as `[JsonProperty]`) for custom serialization of your Algolia records.

If you were using the `Newtonsoft.Json` package for custom serialization,
see [Migrate from Newtonsoft.Json to System.Text.Json](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/migrate-from-newtonsoft?pivots=dotnet-9-0)
in Microsoft's documentation.

  Common attribute replacements when migrating from `Newtonsoft.Json`:

* `[JsonProperty("name")]` becomes `[JsonPropertyName("name")]`
* `[JsonIgnore]` keeps the same name but moves to the `System.Text.Json.Serialization` namespace
* Custom `JsonConverter` implementations need rewriting for `System.Text.Json`
  
## Update enumeration serialization

To keep the serialization of enumeration types consistent with previous versions of the .NET API client,
they're serialized as `int` by default.

To serialize enumeration types as strings, use the `JsonStringEnumConverter` attribute from `System.Text.Json.Serialization`:

```cs
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum MyEnum
{
    MyValue1,
    MyValue2
}

public class MyModel
{
    public MyEnum MyProperty { get; set; }
}

await client.SaveObjectAsync("INDEX_NAME", new MyModel { MyProperty = MyEnum.MyValue2 });
```

With this attribute, `MyProperty` serializes as the string `"MyValue2"` instead of the integer `1`.

## Helper method changes

The following sections document breaking changes in helper method signatures and behavior between version 6 and version 7.

### `ReplaceAllObjects`

The `safe` parameter has been removed. In version 6, `safe: true` caused the helper to wait after each step. In version 7, the helper always waits—equivalent to the previous `safe: true` behavior.

The `scopes` parameter is optional. When omitted, it defaults to all three scopes: `Settings`, `Rules`, and `Synonyms`.

```csharp
// version 6
await index.ReplaceAllObjectsAsync(objects, safe: true);

// version 7
await client.ReplaceAllObjectsAsync(
    indexName: "INDEX_NAME",
    objects: objects
);
```

### `SaveObjects`

The `autoGenerateObjectId` parameter has been removed. In version 7, every object must include an `ObjectID`. To have the API generate object IDs, use the `ChunkedBatch` helper with `Action.AddObject`.

```csharp
// version 6
await index.SaveObjectsAsync(objects, autoGenerateObjectId: true);

// version 7
// Objects must include ObjectID, or use ChunkedBatch with Action.AddObject
await client.SaveObjectsAsync(indexName: "INDEX_NAME", objects: objects);
```

### `PartialUpdateObjects`

The `createIfNotExists` parameter is now a required argument—it no longer has a default value.

```csharp
// version 6
// createIfNotExists defaulted to false
await index.PartialUpdateObjectsAsync(objects, createIfNotExists: true);

// version 7
// createIfNotExists is now required
await client.PartialUpdateObjectsAsync(
    indexName: "INDEX_NAME",
    objects: objects,
    createIfNotExists: true
);
```

### `GenerateSecuredApiKey`

The method was renamed from the plural `GenerateSecuredApiKeys` to the singular `GenerateSecuredApiKey`.

```csharp
// version 6
var key = SearchClient.GenerateSecuredApiKeys("parentApiKey", new SecuredApiKeyRestriction { ... });

// version 7
var key = SearchClient.GenerateSecuredApiKey("parentApiKey", new SecuredApiKeyRestrictions { ... });
```

### `BrowseObjects`, `BrowseRules`, `BrowseSynonyms`

These helpers no longer return iterator types (`IndexIterator<T>`, `RulesIterator`, `SynonymsIterator`). In version 7, they return `IEnumerable<T>` directly.
The index name is now a separate `string` parameter, and the params object has changed to `BrowseParamsObject`, `SearchRulesParams`, and `SearchSynonymsParams` respectively.

```csharp
// version 6
var iterator = index.Browse<MyModel>(new BrowseIndexQuery("query"));
foreach (var obj in iterator)
{
    Process(obj);
}

// version 7
var objects = (await client.BrowseObjectsAsync<MyModel>(
    "INDEX_NAME",
    new BrowseParamsObject()
)).ToList();
```

### `DeleteObjects`

Two new optional parameters are available:

* `waitForTasks` (default `false`)
* `batchSize` (default `1,000`)

```csharp
// version 6
await index.DeleteObjectsAsync(new List<string> { "id1", "id2" });

// version 7
await client.DeleteObjectsAsync(
    indexName: "INDEX_NAME",
    objectIDs: new List<string> { "id1", "id2" },
    waitForTasks: true
);
```

### `WaitForTask`

The method was renamed from `WaitTask` to `WaitForTask`. It now returns `GetTaskResponse` instead of `void`, adds explicit `maxRetries` (default `50`) and a `timeout` function (default: exponential backoff capped at 5 seconds) instead of the `timeToWait` integer.

```csharp
// version 6
// Returns void; flat timeToWait in milliseconds
await index.WaitTaskAsync(taskID, timeToWait: 100);

// version 7
// Returns GetTaskResponse; exponential backoff by default
var taskResponse = await client.WaitForTaskAsync(
    indexName: "INDEX_NAME",
    taskId: taskID,
    maxRetries: 50
);
```

### `WaitForAppTask`

This is a new helper in version 7.

```csharp
var taskResponse = await client.WaitForAppTaskAsync(taskId: taskID);
```

### `WaitForApiKey`

This is a new standalone helper in version 7.

```csharp
// Wait for a key to be created:
await client.WaitForApiKeyAsync("my-api-key", ApiKeyOperation.Add);

// Wait for a key update (pass the expected final state):
await client.WaitForApiKeyAsync(
    "my-api-key",
    ApiKeyOperation.Update,
    apiKey: new ApiKey { Acl = new List<Acl> { Acl.Search } }
);
```

### `GetSecuredApiKeyRemainingValidity`

This helper is new in version 7.

```csharp
TimeSpan remaining = client.GetSecuredApiKeyRemainingValidity(securedApiKey: key);
```

### `IndexExists`

This helper is new in version 7.

```csharp
bool exists = await client.IndexExistsAsync(indexName: "INDEX_NAME");
```

### `ChunkedBatch`

`ChunkedBatch` is now a public helper. In version 6, chunking was an internal detail of `SaveObjects`. The `waitForTasks` parameter defaults to `false` and `batchSize` defaults to `1,000`.

```csharp
var responses = await client.ChunkedBatchAsync<MyModel>(
    indexName: "INDEX_NAME",
    objects: myObjects,
    action: Action.AddObject,
    waitForTasks: true
);
```

### `CopyIndexBetweenApplications`

In version 6, `AccountClient` provided `CopyIndex<T>` and `CopyIndexAsync<T>` for copying an index between two different Algolia applications. It accepted two `ISearchIndex` objects.

In version 7, `AccountClient` is removed. You can compose existing helpers across two clients to achieve the same result.

```csharp
// version 6
var response = await AccountClient.CopyIndexAsync<MyModel>(sourceIndex, destinationIndex);

// version 7
var src = new SearchClient("SRC_APP_ID", "SRC_API_KEY");
var dst = new SearchClient("DST_APP_ID", "DST_API_KEY");

// Copy settings
var settings = await src.GetSettingsAsync("SOURCE_INDEX");
await dst.SetSettingsAsync("DEST_INDEX", settings);

// Copy rules
var rules = (await src.BrowseRulesAsync("SOURCE_INDEX", new SearchRulesParams())).ToList();
if (rules.Any())
    await dst.SaveRulesAsync("DEST_INDEX", rules);

// Copy synonyms
var synonyms = (await src.BrowseSynonymsAsync("SOURCE_INDEX", new SearchSynonymsParams())).ToList();
if (synonyms.Any())
    await dst.SaveSynonymsAsync("DEST_INDEX", synonyms);

// Copy objects
var objects = (await src.BrowseObjectsAsync<MyModel>("SOURCE_INDEX", new BrowseParamsObject())).ToList();
await dst.ReplaceAllObjectsAsync("DEST_INDEX", objects);
```

### `SaveObjectsWithTransformation`

New in version 7. Routes objects through the Algolia Push connector. Requires the transformation region to be set at client initialization.

```csharp
var responses = await client.SaveObjectsWithTransformationAsync(
    indexName: "INDEX_NAME",
    objects: myObjects,
    waitForTasks: false,
    batchSize: 1000
);
```

### `ReplaceAllObjectsWithTransformation`

New in version 7. Atomically replaces all objects via the Push connector (copy settings/rules/synonyms to a temp index → push objects → move back). Requires the transformation region to be set at client initialization.

```csharp
var response = await client.ReplaceAllObjectsWithTransformationAsync(
    indexName: "INDEX_NAME",
    objects: myObjects,
    batchSize: 1000,
    scopes: new List<ScopeType> { ScopeType.Settings, ScopeType.Rules, ScopeType.Synonyms }
);
```

### `PartialUpdateObjectsWithTransformation`

New in version 7. Routes partial updates through the Push connector. The `createIfNotExists` parameter defaults to `true`.

```csharp
var responses = await client.PartialUpdateObjectsWithTransformationAsync(
    indexName: "INDEX_NAME",
    objects: myObjects,
    createIfNotExists: false,
    waitForTasks: false,
    batchSize: 1000
);
```

## Method changes reference

The following tables list all method names that changed between version 6 and version 7.

### Search API client

| Version 6 (legacy)                          |   | Version 7 (current)                        |
| ------------------------------------------- | - | ------------------------------------------ |
| `client.AddApiKey`                          | → | `client.AddApiKey`                         |
| `client.AddApiKey.Wait`                     | → | `client.WaitForApiKey`                     |
| `DictionaryClient.ClearDictionaryEntries`   | → | `client.BatchDictionaryEntries`            |
| `client.CopyIndex`                          | → | `client.OperationIndex`                    |
| `client.CopyRules`                          | → | `client.OperationIndex`                    |
| `client.CopySynonyms`                       | → | `client.OperationIndex`                    |
| `client.DeleteApiKey`                       | → | `client.DeleteApiKey`                      |
| `DictionaryClient.DeleteDictionaryEntries`  | → | `client.BatchDictionaryEntries`            |
| `client.GenerateSecuredApiKey`              | → | `client.GenerateSecuredApiKey`             |
| `client.GetApiKey`                          | → | `client.GetApiKey`                         |
| `client.GetSecuredApiKeyRemainingValidity`  | → | `client.GetSecuredApiKeyRemainingValidity` |
| `client.ListApiKeys`                        | → | `client.ListApiKeys`                       |
| `client.ListIndices`                        | → | `client.ListIndices`                       |
| `client.MoveIndex`                          | → | `client.OperationIndex`                    |
| `client.MultipleBatch`                      | → | `client.MultipleBatch`                     |
| `client.MultipleQueries`                    | → | `client.Search`                            |
| `DictionaryClient.ReplaceDictionaryEntries` | → | `client.BatchDictionaryEntries`            |
| `client.RestoreApiKey`                      | → | `client.RestoreApiKey`                     |
| `DictionaryClient.SaveDictionaryEntries`    | → | `client.BatchDictionaryEntries`            |
| `client.UpdateApiKey`                       | → | `client.UpdateApiKey`                      |
| `index.Batch`                               | → | `client.Batch`                             |
| `index.Browse`                              | → | `client.BrowseObjects`                     |
| `index.BrowseRules`                         | → | `client.BrowseRules`                       |
| `index.BrowseSynonyms`                      | → | `client.BrowseSynonyms`                    |
| `index.ClearObjects`                        | → | `client.ClearObjects`                      |
| `index.ClearRules`                          | → | `client.ClearRules`                        |
| `index.ClearSynonyms`                       | → | `client.ClearSynonyms`                     |
| `index.CopySettings`                        | → | `client.OperationIndex`                    |
| `index.Delete`                              | → | `client.DeleteIndex`                       |
| `index.DeleteBy`                            | → | `client.DeleteBy`                          |
| `index.DeleteObject`                        | → | `client.DeleteObject`                      |
| `index.DeleteObjects`                       | → | `client.DeleteObjects`                     |
| `index.DeleteRule`                          | → | `client.DeleteRule`                        |
| `index.DeleteSynonym`                       | → | `client.DeleteSynonym`                     |
| `index.Exists`                              | → | `client.IndexExists`                       |
| `index.FindObject`                          | → | `client.SearchSingleIndex`                 |
| `index.GetObject`                           | → | `client.GetObject`                         |
| `index.GetObjects`                          | → | `client.GetObjects`                        |
| `index.GetRule`                             | → | `client.GetRule`                           |
| `index.GetSettings`                         | → | `client.GetSettings`                       |
| `index.GetSynonym`                          | → | `client.GetSynonym`                        |
| `index.GetTask`                             | → | `client.GetTask`                           |
| `index.PartialUpdateObject`                 | → | `client.PartialUpdateObject`               |
| `index.PartialUpdateObjects`                | → | `client.PartialUpdateObjects`              |
| `index.ReplaceAllObjects`                   | → | `client.ReplaceAllObjects`                 |
| `index.ReplaceAllRules`                     | → | `client.SaveRules`                         |
| `index.ReplaceAllSynonyms`                  | → | `client.SaveSynonyms`                      |
| `index.SaveObject`                          | → | `client.SaveObject`                        |
| `index.SaveObjects`                         | → | `client.SaveObjects`                       |
| `index.SaveRule`                            | → | `client.SaveRule`                          |
| `index.SaveRules`                           | → | `client.SaveRules`                         |
| `index.SaveSynonym`                         | → | `client.SaveSynonym`                       |
| `index.SaveSynonyms`                        | → | `client.SaveSynonyms`                      |
| `index.Search`                              | → | `client.SearchSingleIndex`                 |
| `index.SearchForFacetValues`                | → | `client.SearchForFacetValues`              |
| `index.SearchRules`                         | → | `client.SearchRules`                       |
| `index.SearchSynonyms`                      | → | `client.SearchSynonyms`                    |
| `index.SetSettings`                         | → | `client.SetSettings`                       |
| `index.{operation}.Wait`                    | → | `client.WaitForTask`                       |

### Recommend API client

| Version 6 (legacy)                   |   | Version 7 (current)         |
| ------------------------------------ | - | --------------------------- |
| `client.GetFrequentlyBoughtTogether` | → | `client.GetRecommendations` |
| `client.GetRecommendations`          | → | `client.GetRecommendations` |
| `client.GetRelatedProducts`          | → | `client.GetRecommendations` |
