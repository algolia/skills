# Get started with the Dart API client

> Keep your Dart API client up to date to benefit from improvements and bug fixes.

The `algoliasearch` Dart client is a new-generation client built from scratch.
There is no official legacy version to upgrade from.
If your project is currently using a community package (such as `dart_algolia`),
this is a full replacement, not an incremental upgrade.

The client is built around a single `SearchClient` instance with `indexName` as an explicit parameter on every method call.
There is no `initIndex` pattern.

For the full list of changes, see the [Dart changelog](/doc/libraries/sdk/changelog/dart).

## Update your dependencies

Add the `algoliasearch` package to your project:

```sh
dart pub add 'algoliasearch:^1.0'
```

For Flutter:

```sh
flutter pub add 'algoliasearch:^1.0'
```

Or add it directly to your `pubspec.yaml`:

```yaml
dependencies:
  algoliasearch: ^1.0
```

## Update imports

The `algoliasearch` meta-package exposes sub-packages per API.
You can depend on the meta-package or import only what you need:

```dart
// Search API (indexing, settings, rules, synonyms)
import 'package:algolia_client_search/algolia_client_search.dart';
// Recommend API
import 'package:algolia_client_recommend/algolia_client_recommend.dart';
// A/B testing API
import 'package:algolia_client_abtesting_v3/algolia_client_abtesting_v3.dart';
// Insights API
import 'package:algolia_client_insights/algolia_client_insights.dart';
```

## Update client initialization

```dart
import 'package:algolia_client_search/algolia_client_search.dart';

final client = SearchClient(appId: 'APP_ID', apiKey: 'API_KEY');
```

Client creation does not throw.
The `appId` and `apiKey` parameters are required.

## Understand the new API surface

There is no `initIndex` step.
All methods belong to the `client` instance with `indexName` as an explicit parameter:

```dart
// community package pattern (e.g. dart_algolia)
final algolia = Algolia.init(applicationId: 'APP_ID', apiKey: 'API_KEY');
final query = algolia.instance('INDEX_NAME').search('QUERY');

// official client
final client = SearchClient(appId: 'APP_ID', apiKey: 'API_KEY');
final response = await client.searchSingleIndex(
  indexName: 'INDEX_NAME',
  searchParams: SearchParamsObject(query: 'QUERY'),
);
```

## Update search calls

### Search a single index

```dart
final response = await client.searchSingleIndex(
  indexName: 'INDEX_NAME',
  searchParams: SearchParamsObject(
    query: 'QUERY',
    facetFilters: ['category:Book'],
  ),
);
```

### Search multiple indices

```dart
final response = await client.search(
  searchMethodParams: SearchMethodParams(
    requests: [
      SearchForHits(indexName: 'INDEX_1', query: 'QUERY'),
      SearchForHits(indexName: 'INDEX_2', query: 'QUERY'),
    ],
  ),
);
```

### Search for facet values

```dart
final response = await client.searchForFacetValues(
  indexName: 'INDEX_NAME',
  facetName: 'category',
  searchForFacetValuesRequest: SearchForFacetValuesRequest(facetQuery: 'book'),
);
```

## Update indexing operations

### Add or replace records

`saveObject` returns a `SaveObjectResponse` which carries a `taskID`.
There is **no `saveObjects` helper** — use `batch()` with `BatchWriteParams` for multiple records:

```dart
// Single object
final response = await client.saveObject(
  indexName: 'INDEX_NAME',
  body: {'objectID': '1', 'name': 'Record'},
);
await client.waitTask(indexName: 'INDEX_NAME', taskID: response.taskID);

// Multiple objects — batch() required (no saveObjects helper)
final batchResponse = await client.batch(
  indexName: 'INDEX_NAME',
  batchWriteParams: BatchWriteParams(
    requests: records
        .map((r) => BatchRequest(action: Action.addObject, body: r))
        .toList(),
  ),
);
await client.waitTask(indexName: 'INDEX_NAME', taskID: batchResponse.taskID);
```

### Partially update records

```dart
await client.partialUpdateObject(
  indexName: 'INDEX_NAME',
  objectID: '1',
  attributesToUpdate: {'name': 'Updated'},
);
```

### Delete records

```dart
await client.deleteObject(indexName: 'INDEX_NAME', objectID: '1');
```

## Update settings, synonyms, and rules

### Get and set settings

```dart
final settings = await client.getSettings(indexName: 'INDEX_NAME');

await client.setSettings(
  indexName: 'INDEX_NAME',
  indexSettings: IndexSettings(searchableAttributes: ['title', 'author']),
);
```

### Save synonyms and rules

```dart
await client.saveSynonyms(
  indexName: 'INDEX_NAME',
  synonymHit: [
    SynonymHit(objectID: '1', type: SynonymType.synonym, synonyms: ['car', 'auto']),
  ],
);

await client.saveRules(indexName: 'INDEX_NAME', rules: [...]);
```

## Update index management

### Copy an index

```dart
await client.operationIndex(
  indexName: 'SOURCE_INDEX_NAME',
  operationIndexParams: OperationIndexParams(
    operation: OperationType.copy,
    destination: 'DESTINATION_INDEX_NAME',
  ),
);
```

### Move (rename) an index

```dart
await client.operationIndex(
  indexName: 'SOURCE_INDEX_NAME',
  operationIndexParams: OperationIndexParams(
    operation: OperationType.move,
    destination: 'DESTINATION_INDEX_NAME',
  ),
);
```

### Copy only rules or settings

```dart
await client.operationIndex(
  indexName: 'SOURCE_INDEX_NAME',
  operationIndexParams: OperationIndexParams(
    operation: OperationType.copy,
    destination: 'DESTINATION_INDEX_NAME',
    scope: [ScopeType.rules, ScopeType.settings],
  ),
);
```

## Update task handling

All write operations in Algolia are asynchronous.
Use `waitTask` to block until indexing completes:

```dart
final response = await client.saveObject(
  indexName: 'INDEX_NAME',
  body: {'objectID': '1', 'name': 'Record'},
);
await client.waitTask(indexName: 'INDEX_NAME', taskID: response.taskID);
```

Three wait helpers are available:

- `waitTask`: wait until indexing operations are done.
- `waitAppTask`: wait for application-level tasks.
- `waitKeyCreation` / `waitKeyDeletion` / `waitKeyUpdate`: wait for API key operations.

## Helper method changes

The following helpers present in other Algolia clients are **not available** in the Dart client:

- **No `saveObjects`** — use `batch()` with `BatchWriteParams` and `Action.addObject`
- **No `replaceAllObjects`** — compose `operationIndex` (copy) + `batch()` + `operationIndex` (move) manually
- **No `browseObjects` / `browseRules` / `browseSynonyms`** aggregator helpers — paginate manually using the `cursor` from each `browse` response

## Method changes reference

| Community package pattern | Official client (`algoliasearch`) |
| ----------------------------------------- | ------------------------------------------------ |
| `Algolia.init(applicationId, apiKey)` | `SearchClient(appId: ..., apiKey: ...)` |
| `algolia.instance('INDEX_NAME')` | No index object — pass `indexName` per call |
| `query.search('QUERY')` | `client.searchSingleIndex(indexName, searchParams)` |
| `index.addObject(data)` | `client.saveObject(indexName, body)` |
| `index.addObjects(data)` | `client.batch(indexName, batchWriteParams)` |
| `index.updateObject(data)` | `client.partialUpdateObject(indexName, objectID, attrs)` |
| `index.deleteObject(id)` | `client.deleteObject(indexName, objectID)` |
| `index.getSettings()` | `client.getSettings(indexName)` |
| `index.setSettings(settings)` | `client.setSettings(indexName, indexSettings)` |
| `index.copyIndex(dest)` | `client.operationIndex(indexName, OperationIndexParams(operation: OperationType.copy, ...))` |
| n/a | `client.waitTask(indexName, taskID)` |
| n/a | `client.waitAppTask(taskID)` |
| n/a | `client.waitKeyCreation(key)` / `waitKeyDeletion(key)` / `waitKeyUpdate(key, apiKey)` |

## Resources

- [pub.dev: algoliasearch](https://pub.dev/packages/algoliasearch)
- [GitHub: algolia/algoliasearch-client-dart](https://github.com/algolia/algoliasearch-client-dart)
- [API reference](https://pub.dev/documentation/algolia_client_search/latest/)
