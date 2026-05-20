# C#: v6 → v7

## Package update

```sh
dotnet add package Algolia.Search --version "7.*"
```

**Critical:** v7 replaces `Newtonsoft.Json` with `System.Text.Json`. Any custom serialization attributes must be updated.

## Serialization migration (Newtonsoft → System.Text.Json)

```csharp
// v6 (Newtonsoft.Json)
[JsonProperty("name")]
public string Name { get; set; }

[JsonIgnore]
public string Internal { get; set; }

// v7 (System.Text.Json)
[JsonPropertyName("name")]
public string Name { get; set; }

[JsonIgnore]   // same name, different namespace
public string Internal { get; set; }
```

Enums default to serializing as `int` in v7. To serialize as strings:
```csharp
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum MyEnum { MyValue1, MyValue2 }
```

Custom converters (e.g. `JsonConverter<T>` subclasses) must be rewritten for `System.Text.Json`.

## `InitIndex` removal

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

`Query` class is removed — use `SearchParamsObject` inside `SearchParams`.

## Async pattern

All methods exist in both forms. Async is recommended:
```csharp
// async
var results = await client.SearchSingleIndexAsync<Hit>("INDEX_NAME", searchParams);

// sync
var results = client.SearchSingleIndex<Hit>("INDEX_NAME", searchParams);
```

## Method renames

| v6 | v7 |
|----|----|
| `index.Search()` | `client.SearchSingleIndexAsync()` |
| `client.MultipleQueries()` | `client.SearchAsync()` |
| `index.SearchForFacetValues()` | `client.SearchForFacetValuesAsync()` |
| `index.SaveObject()` | `client.SaveObjectAsync("INDEX_NAME", obj)` |
| `index.PartialUpdateObject()` | `client.PartialUpdateObjectAsync("INDEX_NAME", id, obj)` |
| `index.DeleteObject()` | `client.DeleteObjectAsync("INDEX_NAME", id)` |
| `index.GetSettings()` | `client.GetSettingsAsync("INDEX_NAME")` |
| `index.SaveRules()` | `client.SaveRulesAsync("INDEX_NAME", rules)` |
| `index.SaveSynonyms()` | `client.SaveSynonymsAsync("INDEX_NAME", synonyms)` |
| `client.CopyIndex()` / `MoveIndex()` | `client.OperationIndexAsync()` with `Operation = "Copy"` / `"Move"` |
| `index.Exists()` | `client.IndexExistsAsync("INDEX_NAME")` |
| `.Wait()` chaining | `client.WaitForTaskAsync("INDEX_NAME", taskID)` |
| `GenerateSecuredApiKeys` (plural) | `GenerateSecuredApiKey` (singular) |

## Indexing

```csharp
await client.SaveObjectAsync("INDEX_NAME", new { objectID = "1", name = "Record" });

await client.PartialUpdateObjectAsync("INDEX_NAME", "1", new { name = "Updated" });

await client.DeleteObjectAsync("INDEX_NAME", "1");
```

## Settings

```csharp
var settings = await client.GetSettingsAsync("INDEX_NAME");
await client.SetSettingsAsync("INDEX_NAME",
    new IndexSettings { SearchableAttributes = new List<string> { "title" } });
```

## `OperationIndexAsync` (copy / move)

```csharp
// copy
await client.OperationIndexAsync("SOURCE",
    new OperationIndexParams { Operation = "copy", Destination = "DEST" });

// move / rename
await client.OperationIndexAsync("SOURCE",
    new OperationIndexParams { Operation = "move", Destination = "DEST" });
```

## Wait pattern

```csharp
// v6
index.SaveObject(record).Wait();

// v7
var response = await client.SaveObjectAsync("INDEX_NAME", record);
await client.WaitForTaskAsync("INDEX_NAME", response.TaskID);
```

`WaitForTaskAsync` returns `GetTaskResponse` (not `void`). Optional: `maxRetries`, timeout function.

Three helpers: `WaitForTaskAsync`, `WaitForAppTaskAsync`, `WaitForApiKeyAsync`.

## `ReplaceAllObjectsAsync`

```csharp
// v7 — safe removed; scopes required
await client.ReplaceAllObjectsAsync(
    indexName: "INDEX_NAME",
    objects: objects,
    scopes: new List<ScopeType> { ScopeType.Settings, ScopeType.Rules, ScopeType.Synonyms }
);
```

## Helper changes

- `SaveObjects`: `autoGenerateObjectId` removed; objects must include `ObjectID`
- `PartialUpdateObjects`: `createIfNotExists` required (no default)
- `BrowseObjects` / `BrowseRules` / `BrowseSynonyms`: no longer return iterators; use aggregator action

## Browse aggregator

```csharp
var objects = new List<MyModel>();
await client.BrowseObjectsAsync<MyModel>(
    new BrowseObjectsParams { IndexName = "INDEX_NAME" },
    response => objects.AddRange(response.Hits)
);
```

## New helpers in v7

`WaitForAppTask`, `WaitForApiKey`, `GetSecuredApiKeyRemainingValidity`, `IndexExists`, `ChunkedBatch` (public), and transformation methods.
