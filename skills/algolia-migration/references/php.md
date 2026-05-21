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
```

Client initialization is unchanged — use the same `SearchClient::create()` factory.

## Remove `initIndex`

```php
// v3
$index = $client->initIndex('INDEX_NAME');
$index->search('QUERY');

// v4
$client->searchSingleIndex('INDEX_NAME', (new SearchParamsObject())->setQuery('QUERY'));

// Or using an array
$client->searchSingleIndex('INDEX_NAME', ['query' => 'QUERY']);
```

## Method renames

| v3 | v4 |
|----|----|
| `$index->search()` | `$client->searchSingleIndex()` |
| `$client->multipleQueries()` | `$client->search()` |
| `$index->searchForFacetValues()` | `$client->searchForFacetValues()` |
| `$index->saveObject()` | `$client->saveObject('INDEX_NAME', $obj)` |
| `$index->saveObjects()` | `$client->saveObjects('INDEX_NAME', $objects)` |
| `$index->partialUpdateObject()` | `$client->partialUpdateObject('INDEX_NAME', $id, $update)` |
| `$index->deleteObject()` | `$client->deleteObject('INDEX_NAME', $id)` |
| `$index->getSettings()` | `$client->getSettings('INDEX_NAME')` |
| `$index->setSettings()` | `$client->setSettings('INDEX_NAME', $settings)` |
| `$index->replaceAllRules()` | `$client->saveRules()` with `clearExistingRules: true` |
| `$index->replaceAllSynonyms()` | `$client->saveSynonyms()` with `replaceExistingSynonyms: true` |
| `copyIndex()` / `moveIndex()` / `copyRules()` / `copySynonyms()` | `$client->operationIndex()` |
| `$index->exists()` | `$client->indexExists('INDEX_NAME')` |
| `waitTask` | `waitForTask` |

## Search

```php
// searchSingleIndex with filters
$results = $client->searchSingleIndex(
    'INDEX_NAME',
    (new SearchParamsObject())->setQuery('QUERY')->setFacetFilters(['category:Book'])
);

// Multiple indices (multipleQueries → search)
$results = $client->search(
    (new SearchMethodParams())->setRequests([
        (new SearchForHits())->setIndexName('INDEX_1')->setQuery('QUERY'),
        (new SearchForHits())->setIndexName('INDEX_2')->setQuery('QUERY'),
    ])
);

// searchForFacetValues
$results = $client->searchForFacetValues(
    'INDEX_NAME',
    'category',
    (new SearchForFacetValuesRequest())->setFacetQuery('book')
);
```

## Indexing

```php
// saveObject
$client->saveObject('INDEX_NAME', ['objectID' => '1', 'name' => 'Record']);

// saveObjects
$client->saveObjects('INDEX_NAME', [['objectID' => '1', 'name' => 'Record']]);

// partialUpdateObject
$client->partialUpdateObject('INDEX_NAME', '1', ['name' => 'Updated']);

// deleteObject
$client->deleteObject('INDEX_NAME', '1');
```

## Settings, synonyms, rules

```php
$settings = $client->getSettings('INDEX_NAME');
$client->setSettings('INDEX_NAME', (new IndexSettings())->setSearchableAttributes(['title', 'author']));

$client->saveSynonyms('INDEX_NAME', [
    ['objectID' => '1', 'type' => 'synonym', 'synonyms' => ['car', 'auto']],
]);
$client->saveRules('INDEX_NAME', $rules);
```

`replaceAllRules` → `saveRules` with `clearExistingRules=true`; `replaceAllSynonyms` → `saveSynonyms` with `replaceExistingSynonyms=true`.

## `operationIndex` (copy / move)

```php
// copy
$client->operationIndex(
    'SOURCE_INDEX_NAME',
    (new OperationIndexParams())->setOperation('copy')->setDestination('DEST')
);

// move
$client->operationIndex(
    'SOURCE_INDEX_NAME',
    (new OperationIndexParams())->setOperation('move')->setDestination('DEST')
);

// copy with scope
$client->operationIndex(
    'SOURCE_INDEX_NAME',
    (new OperationIndexParams())->setOperation('copy')->setDestination('DEST')->setScope(['rules', 'settings'])
);

// indexExists
$client->indexExists('INDEX_NAME');
```

## Task handling

```php
// v3
$index->saveObjects($records)->wait();

// v4
$response = $client->saveObjects('INDEX_NAME', $records);
$client->waitForTask('INDEX_NAME', $response['taskID']);

// waitForTask with controls
$client->waitForTask('INDEX_NAME', $taskID, maxRetries: 50, timeout: 100000);

// waitForAppTask (new in v4)
$client->waitForAppTask($taskID);

// waitForApiKey (new in v4)
$client->waitForApiKey('my-api-key', 'add');
$client->waitForApiKey('my-api-key', 'update', apiKey: ['acl' => ['search']]);
$client->waitForApiKey('my-api-key', 'delete');
```

## Helper method changes

### `replaceAllObjects`

Safe copy removed; `scopes` required:

```php
$client->replaceAllObjects([
    'indexName' => 'INDEX_NAME',
    'objects'   => $objects,
    'scopes'    => ['settings', 'rules', 'synonyms'],
]);
```

### `saveObjects`

`autoGenerateObjectIDIfNotExist` removed. Every object must include `objectID`:

```php
$client->saveObjects(['indexName' => 'INDEX_NAME', 'objects' => $objects]);
```

### `partialUpdateObjects`

`createIfNotExists` is now an explicit required parameter (no default):

```php
$client->partialUpdateObjects('INDEX_NAME', $objects, true);
```

### `deleteObjects`

Parameter renamed `$objectIds` → `$objectIDs`. New `$waitForTasks` and `$batchSize` parameters:

```php
$client->deleteObjects('INDEX_NAME', ['id1', 'id2'], waitForTasks: true);
```

### `browseObjects` / `browseRules` / `browseSynonyms`

Still return iterator objects (foreach pattern). `$indexName` is now an explicit first parameter. The iterator yields page response objects — call `getHits()` to extract records:

```php
// v3
foreach ($index->browseObjects() as $object) { process($object); }

// v4
foreach ($client->browseObjects('INDEX_NAME') as $response) {
    foreach ($response->getHits() as $object) { process($object); }
}
```

### `generateSecuredApiKey`

Static method. Restrictions now use the typed `SecuredApiKeyRestrictions` model, not a plain array:

```php
// v3
$key = $client->generateSecuredApiKey('PARENT_API_KEY', ['validUntil' => time() + 3600]);

// v4
$key = $client->generateSecuredApiKey(
    'PARENT_API_KEY',
    new SecuredApiKeyRestrictions([
        'validUntil'      => time() + 3600,
        'restrictIndices' => ['INDEX_NAME'],
    ])
);
```

### `getSecuredApiKeyRemainingValidity`

Parameter renamed `$securedAPIKey` → `$securedApiKey`.

### `chunkedBatch` (now public)

```php
$client->chunkedBatch('INDEX_NAME', $objects, action: 'addObject', waitForTasks: true);
```

### Cross-app copy (`AccountClient` removed)

Compose manually across two client instances:

```php
$src = SearchClient::create('SRC_APP_ID', 'SRC_API_KEY');
$dst = SearchClient::create('DST_APP_ID', 'DST_API_KEY');

$settings = $src->getSettings('SOURCE_INDEX');
$dst->setSettings('DEST_INDEX', $settings);

$rules = [];
foreach ($src->browseRules('SOURCE_INDEX') as $response) {
    $rules = array_merge($rules, $response->getHits());
}
if (!empty($rules)) $dst->saveRules('DEST_INDEX', $rules);

$synonyms = [];
foreach ($src->browseSynonyms('SOURCE_INDEX') as $response) {
    $synonyms = array_merge($synonyms, $response->getHits());
}
if (!empty($synonyms)) $dst->saveSynonyms('DEST_INDEX', $synonyms);

$objects = [];
foreach ($src->browseObjects('SOURCE_INDEX') as $response) {
    $objects = array_merge($objects, $response->getHits());
}
$dst->replaceAllObjects('DEST_INDEX', $objects);
```

### Transformation helpers (new in v4)

Require calling `setTransformationRegion` first:

```php
$client->setTransformationRegion('us');

$client->saveObjectsWithTransformation('INDEX_NAME', $objects, false, 1000);

$client->replaceAllObjectsWithTransformation('INDEX_NAME', $objects, 1000, ['settings', 'rules', 'synonyms']);

$client->partialUpdateObjectsWithTransformation('INDEX_NAME', $objects, false, false, 1000);
```

## Method changes reference

Full rename table (camelCase):

| v3 | v4 |
|----|----|
| `$client->multipleQueries()` | `$client->search()` |
| `$index->search()` | `$client->searchSingleIndex()` |
| `$index->searchForFacetValues()` | `$client->searchForFacetValues()` |
| `$index->saveObject()` | `$client->saveObject()` |
| `$index->saveObjects()` | `$client->saveObjects()` |
| `$index->partialUpdateObject()` | `$client->partialUpdateObject()` |
| `$index->partialUpdateObjects()` | `$client->partialUpdateObjects()` |
| `$index->deleteObject()` | `$client->deleteObject()` |
| `$index->deleteObjects()` | `$client->deleteObjects()` |
| `$index->deleteBy()` | `$client->deleteBy()` |
| `$index->getObject()` | `$client->getObject()` |
| `$index->getObjects()` | `$client->getObjects()` |
| `$index->getSettings()` | `$client->getSettings()` |
| `$index->setSettings()` | `$client->setSettings()` |
| `$index->getRule()` | `$client->getRule()` |
| `$index->saveRule()` | `$client->saveRule()` |
| `$index->saveRules()` | `$client->saveRules()` |
| `$index->replaceAllRules()` | `$client->saveRules()` with `clearExistingRules: true` |
| `$index->deleteRule()` | `$client->deleteRule()` |
| `$index->clearRules()` | `$client->clearRules()` |
| `$index->searchRules()` | `$client->searchRules()` |
| `$index->getSynonym()` | `$client->getSynonym()` |
| `$index->saveSynonym()` | `$client->saveSynonym()` |
| `$index->saveSynonyms()` | `$client->saveSynonyms()` |
| `$index->replaceAllSynonyms()` | `$client->saveSynonyms()` with `replaceExistingSynonyms: true` |
| `$index->deleteSynonym()` | `$client->deleteSynonym()` |
| `$index->clearSynonyms()` | `$client->clearSynonyms()` |
| `$index->searchSynonyms()` | `$client->searchSynonyms()` |
| `$index->browseObjects()` | `$client->browseObjects('INDEX_NAME')` |
| `$index->browseRules()` | `$client->browseRules('INDEX_NAME')` |
| `$index->browseSynonyms()` | `$client->browseSynonyms('INDEX_NAME')` |
| `$index->batch()` | `$client->batch()` |
| `$index->clearObjects()` | `$client->clearObjects()` |
| `$index->delete()` | `$client->deleteIndex()` |
| `$index->exists()` | `$client->indexExists()` |
| `$index->replaceAllObjects()` | `$client->replaceAllObjects()` |
| `copyIndex()` / `moveIndex()` / `copyRules()` / `copySynonyms()` | `$client->operationIndex()` |
| `$index->{operation}->wait()` | `$client->waitForTask()` |

### Recommend API renames

| v3 | v4 |
|----|----|
| `$client->getFrequentlyBoughtTogether()` | `$client->getRecommendations()` |
| `$client->getLookingSimilar()` | `$client->getRecommendations()` |
| `$client->getRelatedProducts()` | `$client->getRecommendations()` |
| `$client->getTrendingFacets()` | `$client->getRecommendations()` |
| `$client->getTrendingItems()` | `$client->getRecommendations()` |
