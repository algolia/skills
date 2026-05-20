# Dart / Flutter

## Status

The Dart client (`algoliasearch`) is a **new-generation client** built from scratch. There is no legacy version to migrate from. If your project is currently using a community package (e.g., `dart_algolia`), this is a full replacement, not an incremental upgrade.

## Install

```sh
dart pub add 'algoliasearch:^1.0'
# or in pubspec.yaml:
# algoliasearch: ^1.0
```

For Flutter:
```sh
flutter pub add 'algoliasearch:^1.0'
```

## Package structure

The `algoliasearch` meta-package exposes sub-packages per API. You can depend on the meta-package or import only what you need:

| Sub-package | Purpose |
|-------------|---------|
| `algolia_client_search` | Search, indexing, settings, rules, synonyms |
| `algolia_client_recommend` | Recommendations |
| `algolia_client_analytics` | Analytics |
| `algolia_client_abtesting` | A/B testing |
| `algolia_client_insights` | Insights events |
| `algolia_client_ingestion` | Data ingestion / connectors |

## Client initialization

```dart
import 'package:algolia_client_search/algolia_client_search.dart';

final client = SearchClient(appId: 'APP_ID', apiKey: 'API_KEY');
```

## Search

No `initIndex` pattern — `indexName` is always an explicit parameter:

```dart
final response = await client.searchSingleIndex(
  indexName: 'INDEX_NAME',
  searchParams: SearchParamsObject(query: 'QUERY'),
);
```

## Indexing

```dart
await client.saveObject(
  indexName: 'INDEX_NAME',
  body: {'objectID': '1', 'name': 'Record'},
);

await client.partialUpdateObject(
  indexName: 'INDEX_NAME',
  objectID: '1',
  attributesToUpdate: {'name': 'Updated'},
);

await client.deleteObject(indexName: 'INDEX_NAME', objectID: '1');
```

## Wait pattern

```dart
final response = await client.saveObjects(
  indexName: 'INDEX_NAME',
  objects: records,
);
await client.waitForTask(indexName: 'INDEX_NAME', taskID: response.taskID);
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

## Resources

- [pub.dev: algoliasearch](https://pub.dev/packages/algoliasearch)
- [GitHub: algolia/algoliasearch-client-dart](https://github.com/algolia/algoliasearch-client-dart)
- [API reference](https://pub.dev/documentation/algolia_client_search/latest/)
