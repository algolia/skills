# C#: v6 → v7

## Install

```sh
dotnet add package Algolia.Search --version "7.*"
```

**Critical:** v7 replaces `Newtonsoft.Json` with `System.Text.Json`. All custom serialization must be updated.

## Serialization migration (Newtonsoft → System.Text.Json)

```csharp
// v6 (Newtonsoft.Json)
[JsonProperty("name")]
public string Name { get; set; }

[JsonIgnore]
public string Internal { get; set; }

// v7 (System.Text.Json — same attribute names, different namespace)
[JsonPropertyName("name")]
public string Name { get; set; }

[JsonIgnore]
public string Internal { get; set; }
```

Enums default to serializing as `int` in v7. For string serialization:
```csharp
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum MyEnum { MyValue1, MyValue2 }
```

Custom converters (`JsonConverter<T>` subclasses) must be rewritten for `System.Text.Json`.

## Client initialization

Client init is unchanged. Both sync and async methods are available; async (`Async` suffix, returns `Task<T>`) is recommended.

```csharp
var client = new SearchClient("APP_ID", "API_KEY");
```

`Query` class is removed — use `SearchParamsObject` inside `SearchParams`.

## Remove `InitIndex`

```csharp
// v6
var index = client.InitIndex("INDEX_NAME");
var results = index.Search<Contact>(new Query("QUERY"));

// v7
var results = await client.SearchSingleIndexAsync<Hit>(
    "INDEX_NAME",
    new SearchParams(new SearchParamsObject { Query = "QUERY" })
);
```

## Method renames

| v6 | v7 |
|----|----|
| `client.MultipleQueries()` | `client.SearchAsync()` |
| `index.Search()` | `client.SearchSingleIndexAsync("INDEX_NAME", ...)` |
| `index.SearchForFacetValues()` | `client.SearchForFacetValuesAsync("INDEX_NAME", ...)` |
| `index.Exists()` | `client.IndexExistsAsync("INDEX_NAME")` |
| `index.ReplaceAllRules()` | `client.SaveRulesAsync()` with `clearExistingRules` |
| `index.ReplaceAllSynonyms()` | `client.SaveSynonymsAsync()` with `clearExistingSynonyms` |
| `client.CopyIndex()` / `MoveIndex()` | `client.OperationIndexAsync()` |
| `.Wait()` chaining | `client.WaitForTaskAsync("INDEX_NAME", taskID)` |
| `GenerateSecuredApiKeys` (plural) | `GenerateSecuredApiKey` (singular) |

## Multiple index search

```csharp
var results = await client.SearchAsync<Hit>(new SearchMethodParams {
    Requests = new List<SearchQuery> {
        new SearchQuery(new SearchForHits { IndexName = "INDEX_1", Query = "QUERY" }),
        new SearchQuery(new SearchForHits { IndexName = "INDEX_2", Query = "QUERY" })
    }
});
```

## Indexing

```csharp
await client.SaveObjectAsync("INDEX_NAME", new { ObjectID = "1", Name = "Record" });
await client.PartialUpdateObjectAsync("INDEX_NAME", "1", new { Name = "Updated" });
await client.DeleteObjectAsync("INDEX_NAME", "1");
```

## `OperationIndexAsync` (copy / move)

```csharp
// copy
await client.OperationIndexAsync("SOURCE",
    new OperationIndexParams { Operation = OperationType.Copy, Destination = "DEST" });

// move
await client.OperationIndexAsync("SOURCE",
    new OperationIndexParams { Operation = OperationType.Move, Destination = "DEST" });

// copy with scope
await client.OperationIndexAsync("SOURCE", new OperationIndexParams {
    Operation = OperationType.Copy, Destination = "DEST",
    Scope = new List<ScopeType> { ScopeType.Rules, ScopeType.Settings }
});

// check if index exists (new in v7)
bool exists = await client.IndexExistsAsync("INDEX_NAME");
```

## Wait pattern

```csharp
// v6
index.SaveObjects(records).Wait();

// v7
var response = await client.SaveObjectsAsync("INDEX_NAME", records);
await client.WaitForTaskAsync("INDEX_NAME", response.TaskID);

// new helpers
await client.WaitForAppTaskAsync(taskId: taskID);
await client.WaitForApiKeyAsync("my-api-key", ApiKeyOperation.Add);
await client.WaitForApiKeyAsync("my-api-key", ApiKeyOperation.Update,
    apiKey: new ApiKey { Acl = new List<Acl> { Acl.Search } });
```

## Helper method changes

- **`ReplaceAllObjectsAsync`**: `safe` removed; scopes required:
```csharp
await client.ReplaceAllObjectsAsync(indexName: "INDEX_NAME", objects: objects,
    scopes: new List<ScopeType> { ScopeType.Settings, ScopeType.Rules, ScopeType.Synonyms });
```
- **`SaveObjectsAsync`**: `autoGenerateObjectId` removed; objects must include `ObjectID`; use `ChunkedBatchAsync` with `Action.AddObject` for auto-ID
- **`PartialUpdateObjectsAsync`**: `createIfNotExists` required (no default)
- **`DeleteObjectsAsync`**: new `waitForTasks` and `batchSize` params
- **`BrowseObjectsAsync` / `BrowseRulesAsync` / `BrowseSynonymsAsync`**: no longer return iterators; accept an aggregator action:
```csharp
// v6 — iterator
var iterator = index.Browse<MyModel>(new BrowseIndexQuery("query"));
foreach (var obj in iterator) { Process(obj); }

// v7 — aggregator action
var objects = new List<MyModel>();
await client.BrowseObjectsAsync<MyModel>(
    new BrowseObjectsParams { IndexName = "INDEX_NAME" },
    response => objects.AddRange(response.Hits));
```
- **`GenerateSecuredApiKey`**: renamed from `GenerateSecuredApiKeys` (plural → singular)
- **`GetSecuredApiKeyRemainingValidity`** (new):
```csharp
TimeSpan remaining = client.GetSecuredApiKeyRemainingValidity(securedApiKey: key);
```
- **`ChunkedBatchAsync`** (now public):
```csharp
var responses = await client.ChunkedBatchAsync<MyModel>(
    indexName: "INDEX_NAME", objects: myObjects, action: Action.AddObject, waitForTasks: true);
```

## Cross-app copy (`AccountClient` removed)

```csharp
var src = new SearchClient("SRC_APP_ID", "SRC_API_KEY");
var dst = new SearchClient("DST_APP_ID", "DST_API_KEY");

var settings = await src.GetSettingsAsync("SOURCE_INDEX");
await dst.SetSettingsAsync("DEST_INDEX", settings);

var rules = new List<Rule>();
await src.BrowseRulesAsync("SOURCE_INDEX", r => rules.AddRange(r.Hits));
if (rules.Any()) await dst.SaveRulesAsync("DEST_INDEX", rules);

// repeat for synonyms, then BrowseObjectsAsync + ReplaceAllObjectsAsync
```

## Transformation helpers (new in v7)

```csharp
await client.SaveObjectsWithTransformationAsync("INDEX_NAME", objects);
await client.ReplaceAllObjectsWithTransformationAsync("INDEX_NAME", objects);
await client.PartialUpdateObjectsWithTransformationAsync("INDEX_NAME", objects);
```

## Method changes reference

| v6 | v7 |
|----|----|
| `client.MultipleQueries()` | `client.SearchAsync()` |
| `client.CopyIndex()` | `client.OperationIndexAsync()` |
| `client.MoveIndex()` | `client.OperationIndexAsync()` |
| `client.GenerateSecuredApiKeys()` | `client.GenerateSecuredApiKey()` |
| `index.Batch()` | `client.BatchAsync("INDEX_NAME", ...)` |
| `index.Browse()` | `client.BrowseObjectsAsync("INDEX_NAME", ..., aggregator)` |
| `index.BrowseRules()` | `client.BrowseRulesAsync("INDEX_NAME", ...)` |
| `index.BrowseSynonyms()` | `client.BrowseSynonymsAsync("INDEX_NAME", ...)` |
| `index.ClearObjects()` | `client.ClearObjectsAsync("INDEX_NAME")` |
| `index.ClearRules()` | `client.ClearRulesAsync("INDEX_NAME")` |
| `index.ClearSynonyms()` | `client.ClearSynonymsAsync("INDEX_NAME")` |
| `index.Delete()` | `client.DeleteIndexAsync("INDEX_NAME")` |
| `index.DeleteBy()` | `client.DeleteByAsync("INDEX_NAME", ...)` |
| `index.DeleteObject()` | `client.DeleteObjectAsync("INDEX_NAME", id)` |
| `index.DeleteObjects()` | `client.DeleteObjectsAsync("INDEX_NAME", ids)` |
| `index.DeleteRule()` | `client.DeleteRuleAsync("INDEX_NAME", id)` |
| `index.DeleteSynonym()` | `client.DeleteSynonymAsync("INDEX_NAME", id)` |
| `index.Exists()` | `client.IndexExistsAsync("INDEX_NAME")` |
| `index.GetObject()` | `client.GetObjectAsync("INDEX_NAME", id)` |
| `index.GetObjects()` | `client.GetObjectsAsync(...)` |
| `index.GetRule()` | `client.GetRuleAsync("INDEX_NAME", id)` |
| `index.GetSettings()` | `client.GetSettingsAsync("INDEX_NAME")` |
| `index.GetSynonym()` | `client.GetSynonymAsync("INDEX_NAME", id)` |
| `index.GetTask()` | `client.GetTaskAsync("INDEX_NAME", taskId)` |
| `index.PartialUpdateObject()` | `client.PartialUpdateObjectAsync("INDEX_NAME", ...)` |
| `index.PartialUpdateObjects()` | `client.PartialUpdateObjectsAsync("INDEX_NAME", ...)` |
| `index.ReplaceAllObjects()` | `client.ReplaceAllObjectsAsync(...)` |
| `index.ReplaceAllRules()` | `client.SaveRulesAsync("INDEX_NAME", rules)` |
| `index.ReplaceAllSynonyms()` | `client.SaveSynonymsAsync("INDEX_NAME", synonyms)` |
| `index.SaveObject()` | `client.SaveObjectAsync("INDEX_NAME", obj)` |
| `index.SaveObjects()` | `client.SaveObjectsAsync("INDEX_NAME", objs)` |
| `index.SaveRule()` | `client.SaveRuleAsync("INDEX_NAME", ...)` |
| `index.SaveRules()` | `client.SaveRulesAsync("INDEX_NAME", rules)` |
| `index.SaveSynonym()` | `client.SaveSynonymAsync("INDEX_NAME", ...)` |
| `index.SaveSynonyms()` | `client.SaveSynonymsAsync("INDEX_NAME", synonyms)` |
| `index.Search()` | `client.SearchSingleIndexAsync("INDEX_NAME", ...)` |
| `index.SearchForFacetValues()` | `client.SearchForFacetValuesAsync("INDEX_NAME", ...)` |
| `index.SearchRules()` | `client.SearchRulesAsync("INDEX_NAME", ...)` |
| `index.SearchSynonyms()` | `client.SearchSynonymsAsync("INDEX_NAME", ...)` |
| `index.SetSettings()` | `client.SetSettingsAsync("INDEX_NAME", ...)` |
| `index.{op}.Wait()` | `client.WaitForTaskAsync("INDEX_NAME", taskId)` |

Recommend API renames:

| v6 | v7 |
|----|----|
| `recommend.GetFrequentlyBoughtTogether()` | `recommend.GetRecommendations()` |
| `recommend.GetRelatedProducts()` | `recommend.GetRecommendations()` |
