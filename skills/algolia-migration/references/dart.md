# Dart / Flutter

## Install

The `algoliasearch` Dart client is a new-generation client built from scratch. There is no official legacy version. If your project is currently using a community package (e.g., `dart_algolia`), this is a full replacement, not an incremental upgrade.

```sh
dart pub add 'algoliasearch:^1.0'
# or in pubspec.yaml: algoliasearch: ^1.0
```

For Flutter:
```sh
flutter pub add 'algoliasearch:^1.0'
```

## Import changes

The `algoliasearch` meta-package exposes sub-packages per API. Import the meta-package or only what you need:

| Sub-package | Purpose |
|-------------|---------|
| `algolia_client_search` | Search, indexing, settings, rules, synonyms |
| `algolia_client_recommend` | Recommendations |
| `algolia_client_analytics` | Analytics |
| `algolia_client_abtesting` | A/B testing |
| `algolia_client_insights` | Insights events |
| `algolia_client_ingestion` | Data ingestion / connectors |

```dart
import 'package:algolia_client_search/algolia_client_search.dart';
```

## Client initialization

```dart
final client = SearchClient(appId: 'APP_ID', apiKey: 'API_KEY');
```

## No `initIndex` pattern

There is no `initIndex` and no index object. Pass `indexName` as an explicit parameter to every method call.

## Method renames

Not applicable — this is a new client with no prior official version to rename from.

## Search

```dart
final response = await client.searchSingleIndex(
  indexName: 'INDEX_NAME',
  searchParams: SearchParamsObject(query: 'QUERY'),
);
```

## Indexing

`saveObject` returns `SaveObjectResponse` which carries `taskID`. There is **no `saveObjects` helper** — use `batch()` with `BatchWriteParams` for multiple objects:

```dart
// Single object
final response = await client.saveObject(
  indexName: 'INDEX_NAME',
  body: {'objectID': '1', 'name': 'Record'},
);
await client.waitForTask(indexName: 'INDEX_NAME', taskID: response.taskID);

// Multiple objects — batch() required
final batchResponse = await client.batch(
  indexName: 'INDEX_NAME',
  batchWriteParams: BatchWriteParams(
    requests: records
        .map((r) => BatchRequest(action: Action.addObject, body: r))
        .toList(),
  ),
);
await client.waitForTask(indexName: 'INDEX_NAME', taskID: batchResponse.taskID);
```

```dart
await client.partialUpdateObject(
  indexName: 'INDEX_NAME',
  objectID: '1',
  attributesToUpdate: {'name': 'Updated'},
);

await client.deleteObject(indexName: 'INDEX_NAME', objectID: '1');
```

## Settings

```dart
final settings = await client.getSettings(indexName: 'INDEX_NAME');

await client.setSettings(
  indexName: 'INDEX_NAME',
  indexSettings: IndexSettings(searchableAttributes: ['title']),
);
```

## `operationIndex` (copy / move)

```dart
await client.operationIndex(
  indexName: 'SOURCE',
  operationIndexParams: OperationIndexParams(
    operation: OperationType.copy,
    destination: 'DEST',
  ),
);
```

## Helper method changes

Not applicable — this is a new client. Notable absences compared to other Algolia clients:
- No `saveObjects` bulk helper — use `batch()` with `BatchWriteParams`
- No `replaceAllObjects` helper
- No `browseObjects` / `browseRules` / `browseSynonyms` aggregator helpers

## Method changes reference

| Community package pattern | Official client (`algoliasearch`) |
|--------------------------|----------------------------------|
| `algolia.instance('INDEX_NAME')` | `SearchClient(appId, apiKey)` — no index object |
| `index.search(query)` | `client.searchSingleIndex(indexName, searchParams)` |
| `index.addObject(data)` | `client.saveObject(indexName, body)` |
| `index.addObjects(data)` | `client.batch(indexName, batchWriteParams)` |
| `index.updateObject(data)` | `client.partialUpdateObject(indexName, objectID, attrs)` |
| `index.deleteObject(id)` | `client.deleteObject(indexName, objectID)` |
| n/a | `client.waitForTask(indexName, taskID)` |
| n/a | `client.getSettings(indexName)` |
| n/a | `client.setSettings(indexName, indexSettings)` |
| n/a | `client.operationIndex(indexName, operationIndexParams)` |

## Resources

- [pub.dev: algoliasearch](https://pub.dev/packages/algoliasearch)
- [GitHub: algolia/algoliasearch-client-dart](https://github.com/algolia/algoliasearch-client-dart)
- [API reference](https://pub.dev/documentation/algolia_client_search/latest/)
