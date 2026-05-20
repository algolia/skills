# PHP: v3 → v4

## Install

```sh
composer require algolia/algoliasearch-client-php "^4.0"
```

## Namespace changes

```php
// v3
use Algolia\AlgoliaSearch\SearchClient;

// v4
use Algolia\AlgoliaSearch\Api\SearchClient;
use Algolia\AlgoliaSearch\Api\RecommendClient;
use Algolia\AlgoliaSearch\Api\AbtestingClient;
use Algolia\AlgoliaSearch\Api\AnalyticsClient;
use Algolia\AlgoliaSearch\Api\QuerySuggestionsClient;
```

## `initIndex` removal

```php
// v3
$index = $client->initIndex('INDEX_NAME');
$results = $index->search('QUERY');

// v4
$results = $client->searchSingleIndex(
    'INDEX_NAME',
    (new SearchParamsObject())->setQuery('QUERY')
);

// Or using an associative array
$results = $client->searchSingleIndex('INDEX_NAME', ['query' => 'QUERY']);
```

## Method renames

| v3 | v4 |
|----|----|
| `$index->search()` | `$client->searchSingleIndex()` |
| `$client->multipleQueries()` | `$client->search()` |
| `$index->searchForFacetValues()` | `$client->searchForFacetValues()` |
| `$index->saveObject()` | `$client->saveObject('INDEX_NAME', $obj)` |
| `$index->partialUpdateObject()` | `$client->partialUpdateObject('INDEX_NAME', $id, $update)` |
| `$index->deleteObject()` | `$client->deleteObject('INDEX_NAME', $id)` |
| `$index->getSettings()` | `$client->getSettings('INDEX_NAME')` |
| `$index->setSettings()` | `$client->setSettings('INDEX_NAME', $settings)` |
| `$index->replaceAllRules()` | `$client->saveRules()` with `clearExistingRules: true` |
| `$index->replaceAllSynonyms()` | `$client->saveSynonyms()` with `replaceExistingSynonyms: true` |
| `copyIndex()` / `moveIndex()` / `copyRules()` / etc. | `$client->operationIndex()` |
| `$index->exists()` | `$client->indexExists('INDEX_NAME')` |
| `waitTask` | `waitForTask` |

## Indexing

```php
$client->saveObject('INDEX_NAME', ['objectID' => '1', 'name' => 'Record']);

$client->partialUpdateObject('INDEX_NAME', '1', ['name' => 'Updated']);

$client->deleteObject('INDEX_NAME', '1');
```

## Settings, synonyms, rules

```php
$client->getSettings('INDEX_NAME');
$client->setSettings('INDEX_NAME', (new IndexSettings())->setSearchableAttributes(['title']));

$client->saveRules('INDEX_NAME', $rules);
$client->saveSynonyms('INDEX_NAME', $synonyms);
```

## `operationIndex` (copy / move)

```php
use Algolia\AlgoliaSearch\Model\Search\OperationIndexParams;

$client->operationIndex(
    'SOURCE',
    (new OperationIndexParams())->setOperation('copy')->setDestination('DEST')
);

$client->operationIndex(
    'SOURCE',
    (new OperationIndexParams())->setOperation('move')->setDestination('DEST')
);
```

## Wait pattern

```php
// v3
$index->saveObjects($records)->wait();

// v4
$response = $client->saveObjects('INDEX_NAME', $records);
$client->waitForTask('INDEX_NAME', $response['taskID']);
```

Three helpers: `waitForTask`, `waitForAppTask`, `waitForApiKey`.

## `replaceAllObjects`

```php
// v4 — safe removed; scopes required
$client->replaceAllObjects('INDEX_NAME', $objects, [
    'scopes' => ['settings', 'rules', 'synonyms'],
]);
```

## Helper changes

| Helper | Change |
|--------|--------|
| `saveObjects` | `autoGenerateObjectIDIfNotExist` removed; every object needs `objectID` |
| `partialUpdateObjects` | `createIfNotExists` is now an explicit parameter |
| `deleteObjects` | Gained `waitForTasks` and `batchSize` parameters |
| `browseObjects` / `browseRules` / `browseSynonyms` | `$indexName` now explicit first parameter |
| `indexExists` | Renamed from `exists()` on index object |
| `chunkedBatch` | Now public; default action is `'addObject'` |
| `generateSecuredApiKey` | Accepts typed `SecuredApiKeyRestrictions` model |

## Browse aggregator

```php
$objects = [];
$client->browseObjects('INDEX_NAME', function ($response) use (&$objects) {
    $objects = array_merge($objects, $response->getHits());
});
```

## Model classes vs arrays

Both accepted. Model classes provide IDE autocompletion:

```php
// Model class (recommended)
$client->searchSingleIndex('INDEX_NAME', (new SearchParamsObject())->setQuery('QUERY'));

// Associative array
$client->searchSingleIndex('INDEX_NAME', ['query' => 'QUERY']);
```

## `AccountClient` removed

Cross-app index copying now requires composing operations manually across two client instances.
