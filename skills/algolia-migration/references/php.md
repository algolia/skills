# Upgrade the PHP API client to version 4

> Keep your PHP API client up to date to benefit from improvements and bug fixes.

The latest major version of the `algoliasearch-client-php` package is version 4.
This page helps you upgrade from version 3
and explains the breaking changes you need to address.

Algolia generates the version 4 clients from OpenAPI specifications,
which provides consistent behavior across all languages and up-to-date API coverage.
The main architectural change is the removal of the `initIndex` pattern:
all methods are now on the `$client` instance directly, with `indexName` as a parameter.

For the full list of changes, see the PHP changelog.

## Update your dependencies

Update the `algoliasearch-client-php` package to version 4:

```sh
composer require algolia/algoliasearch-client-php "^4.0"
```

## Update imports

The namespace for API clients changed in version 4.
The `SearchClient` class moved from `Algolia\AlgoliaSearch` to `Algolia\AlgoliaSearch\Api`.

```php
<?php
// version 3
use Algolia\AlgoliaSearch\SearchClient;

// version 4
use Algolia\AlgoliaSearch\Api\SearchClient;
```

Version 4 also includes dedicated clients for each API.
If you only need methods from a specific API,
import the matching client:

```php
<?php
// Search API
use Algolia\AlgoliaSearch\Api\SearchClient;
// Recommend API
use Algolia\AlgoliaSearch\Api\RecommendClient;
// A/B testing API
use Algolia\AlgoliaSearch\Api\AbtestingClient;
// Analytics API
use Algolia\AlgoliaSearch\Api\AnalyticsClient;
// Personalization API
use Algolia\AlgoliaSearch\Api\PersonalizationClient;
// Query Suggestions API
use Algolia\AlgoliaSearch\Api\QuerySuggestionsClient;
```

## Update client initialization

Client creation uses the same `SearchClient::create()` factory method.
The constructor still accepts your application ID and API key:

```php
// version 3
$client = SearchClient::create('ALGOLIA_APPLICATION_ID', 'ALGOLIA_API_KEY');

// version 4
$client = SearchClient::create('ALGOLIA_APPLICATION_ID', 'ALGOLIA_API_KEY');
```

## Remove `initIndex`

This is the most significant change when upgrading.
Version 3 relied on an index object with methods called on it.
In version 4, all methods belong to the `$client` instance,
with `indexName` as a parameter.

```php
// version 3
$client = SearchClient::create('ALGOLIA_APPLICATION_ID', 'ALGOLIA_API_KEY');
$index = $client->initIndex('INDEX_NAME');
$index->search('QUERY');

// version 4
$client = SearchClient::create('ALGOLIA_APPLICATION_ID', 'ALGOLIA_API_KEY');
$client->searchSingleIndex(
    'INDEX_NAME',
    (new SearchParamsObject())->setQuery('QUERY')
);
```

  If you have many files to update,
  search your codebase for `initIndex` or `->initIndex(` to find every place that needs changing.

## Use model classes or associative arrays

Version 4 methods accept both **model classes** and **associative arrays** as parameters.

```php
// Using a model class
$client->searchSingleIndex(
    'INDEX_NAME',
    (new SearchParamsObject())->setQuery('QUERY')
    );

// Using an associative array
$client->searchSingleIndex(
    'INDEX_NAME',
    ['query' => 'QUERY']
    );
```

Model classes give you IDE autocompletion, type safety,
and predictable structure that works well with AI coding assistants.
The code examples in this guide use model classes,
but you can use arrays anywhere a model is expected.

## Update search calls

### Search a single index

The `$index->search()` method is now `$client->searchSingleIndex()`.
Pass the index name and search parameters as positional arguments:

```php
// version 3
$index = $client->initIndex('INDEX_NAME');
$results = $index->search('QUERY', [
    'facetFilters' => ['category:Book'],
]);

// version 4
$results = $client->searchSingleIndex(
    'INDEX_NAME',
    (new SearchParamsObject())
        ->setQuery('QUERY')
        ->setFacetFilters(['category:Book'])
);
```

### Search multiple indices

The `$client->multipleQueries()` method is now `$client->search()`.
Each request in the array requires an `indexName`:

```php
// version 3
$results = $client->multipleQueries([
    ['indexName' => 'INDEX_1', 'query' => 'QUERY'],
    ['indexName' => 'INDEX_2', 'query' => 'QUERY'],
]);

// version 4
$results = $client->search(
    (new SearchMethodParams())->setRequests([
        (new SearchForHits())
            ->setIndexName('INDEX_1')
            ->setQuery('QUERY'),
        (new SearchForHits())
            ->setIndexName('INDEX_2')
            ->setQuery('QUERY'),
    ])
);
```

### Search for facet values

The `$index->searchForFacetValues()` method becomes `$client->searchForFacetValues()`
with an `indexName` parameter:

```php
// version 3
$index = $client->initIndex('INDEX_NAME');
$results = $index->searchForFacetValues('category', 'book');

// version 4
$results = $client->searchForFacetValues(
    'INDEX_NAME',
    'category',
    (new SearchForFacetValuesRequest())->setFacetQuery('book')
);
```

## Update indexing operations

In version 4, indexing methods are on the client instead of the index object,
with `indexName` as a parameter.

### Add or replace records

```php
// version 3
$index = $client->initIndex('INDEX_NAME');
$index->saveObject(['objectID' => '1', 'name' => 'Record']);
$index->saveObjects([['objectID' => '1', 'name' => 'Record']]);

// version 4
$client->saveObject(
    'INDEX_NAME',
    ['objectID' => '1', 'name' => 'Record']
);
// saveObjects works the same way:
$client->saveObjects(
    'INDEX_NAME',
    [['objectID' => '1', 'name' => 'Record']]
);
```

### Partially update records

```php
// version 3
$index = $client->initIndex('INDEX_NAME');
$index->partialUpdateObject(['objectID' => '1', 'name' => 'Updated']);

// version 4
$client->partialUpdateObject(
    'INDEX_NAME',
    '1',
    ['name' => 'Updated']
);
```

### Delete records

```php
// version 3
$index = $client->initIndex('INDEX_NAME');
$index->deleteObject('1');

// version 4
$client->deleteObject(
    'INDEX_NAME',
    '1'
);
```

## Update settings, synonyms, and rules

### Get and set settings

```php
// version 3
$index = $client->initIndex('INDEX_NAME');
$settings = $index->getSettings();
$index->setSettings(['searchableAttributes' => ['title', 'author']]);

// version 4
$settings = $client->getSettings('INDEX_NAME');
$client->setSettings(
    'INDEX_NAME',
    (new IndexSettings())->setSearchableAttributes(['title', 'author'])
);
```

### Save synonyms and rules

```php
// version 3
$index = $client->initIndex('INDEX_NAME');
$index->saveSynonyms([['objectID' => '1', 'type' => 'synonym', 'synonyms' => ['car', 'auto']]]);
$index->saveRules([['objectID' => '1', 'conditions' => [['anchoring' => 'contains', 'pattern' => 'shoes']], 'consequence' => ['params' => ['query' => 'sneakers']]]]);

// version 4
$client->saveSynonyms(
    'INDEX_NAME',
    [['objectID' => '1', 'type' => 'synonym', 'synonyms' => ['car', 'auto']]]
);
$client->saveRules(
    'INDEX_NAME',
    [['objectID' => '1', 'conditions' => [['anchoring' => 'contains', 'pattern' => 'shoes']], 'consequence' => ['params' => ['query' => 'sneakers']]]]
);
```

  In version 3, `$index->replaceAllRules()` and `$index->replaceAllSynonyms()` replaced all rules or synonyms.
  In version 4, use `$client->saveRules()` or `$client->saveSynonyms()` with the `clearExistingRules` or `replaceExistingSynonyms` parameter set to `true`.

## Update index management

The `copyIndex`, `moveIndex`, `copyRules`, `copySynonyms`, and `copySettings`
methods are all replaced by a single `operationIndex` method.

### Copy an index

```php
// version 3
$client->copyIndex('SOURCE_INDEX_NAME', 'DESTINATION_INDEX_NAME');

// version 4
$client->operationIndex(
    'SOURCE_INDEX_NAME',
    (new OperationIndexParams())
        ->setOperation('copy')
        ->setDestination('DESTINATION_INDEX_NAME')
);
```

### Move (rename) an index

```php
// version 3
$client->moveIndex('SOURCE_INDEX_NAME', 'DESTINATION_INDEX_NAME');

// version 4
$client->operationIndex(
    'SOURCE_INDEX_NAME',
    (new OperationIndexParams())
        ->setOperation('move')
        ->setDestination('DESTINATION_INDEX_NAME')
);
```

### Copy only rules or settings

In version 4, use the `scope` parameter to limit the operation to specific data:

```php
// version 4 -- copy only rules and settings from one index to another
$client->operationIndex(
    'SOURCE_INDEX_NAME',
    (new OperationIndexParams())
        ->setOperation('copy')
        ->setDestination('DESTINATION_INDEX_NAME')
        ->setScope(['rules', 'settings'])
);
```

### Check if an index exists

In version 3, you could check if an index existed using the `exists` method on the index object.
In version 4, use the `indexExists` helper method on the client:

```php
// version 3
$index = $client->initIndex('INDEX_NAME');
$index->exists();

// version 4
$client->indexExists('INDEX_NAME');
```

## Update task handling

Version 3 supported chaining `->wait()` on operations.
Version 4 replaces this pattern with dedicated wait helpers.

```php
// version 3
$index = $client->initIndex('INDEX_NAME');
$index->saveObjects($records)->wait();

// version 4
$response = $client->saveObjects(
    'INDEX_NAME',
    $records
);
$client->waitForTask('INDEX_NAME', $response['taskID']);
```

Version 4 includes three wait helpers:

* `waitForTask`: wait until indexing operations are done.
* `waitForAppTask`: wait for application-level tasks.
* `waitForApiKey`: wait for API key operations.

## Helper method changes

The following sections document breaking changes in helper method signatures and behavior between version 3 and version 4.

### `replaceAllObjects`

The `'safe'` request option has been removed. In version 3, passing `'safe' => true` caused the helper to wait after each step. In version 4, the helper always waits—equivalent to the previous `'safe' => true` behavior.

The `scopes` parameter is optional. When omitted, it defaults to `['settings', 'rules', 'synonyms']`.

```php
// version 3
$index->replaceAllObjects($objects, ['safe' => true]);

// version 4
$client->replaceAllObjects('INDEX_NAME', $objects);
```

### `saveObjects`

The `autoGenerateObjectIDIfNotExist` request option has been removed. In version 4, every object must include an `objectID`. To have the API generate object IDs, use `chunkedBatch` with `action: 'addObject'`.

```php
// version 3
$index->saveObjects($objects, ['autoGenerateObjectIDIfNotExist' => true]);

// version 4
// Objects must include objectID, or use chunkedBatch with 'addObject' action
$client->saveObjects('INDEX_NAME', $objects);
```

### `partialUpdateObjects`

The `createIfNotExists` option has moved from the `$requestOptions` array to an explicit required parameter.

```php
// version 3
$index->partialUpdateObjects($objects, ['createIfNotExists' => true]);

// version 4
$client->partialUpdateObjects(
    'INDEX_NAME',
    $objects,
    true,   // createIfNotExists — required, no default
);
```

### `deleteObjects`

The helper moved to the client and two new optional parameters are available: `$waitForTasks` (default `false`) and `$batchSize` (default `1,000`). The parameter was also renamed from `$objectIds` to `$objectIDs`.

```php
// version 3
$index->deleteObjects(['id1', 'id2']);

// version 4
$client->deleteObjects('INDEX_NAME', ['id1', 'id2'], waitForTasks: true);
```

### `browseObjects`, `browseRules`, `browseSynonyms`

These helpers still return iterator objects in version 4. The only change is that `$indexName` is now an explicit first parameter instead of being implicit from the index object.

```php
// version 3
foreach ($index->browseObjects() as $object) {
    process($object);
}

// version 4
foreach ($client->browseObjects('INDEX_NAME') as $object) {
    process($object);
}
```

### `generateSecuredApiKey` and `getSecuredApiKeyRemainingValidity`

For `generateSecuredApiKey`, the restrictions parameter now uses a typed `SecuredApiKeyRestrictions` model instead of a plain array.

For `getSecuredApiKeyRemainingValidity`, the parameter was renamed from `$securedAPIKey` to `$securedApiKey`.

```php
// version 3
$key = $client->generateSecuredApiKey(
    'PARENT_API_KEY',
    ['validUntil' => time() + 3600, 'restrictIndices' => ['INDEX_NAME']]
);

$remaining = $client->getSecuredApiKeyRemainingValidity($securedAPIKey);

// version 4
$key = $client->generateSecuredApiKey(
    'PARENT_API_KEY',
    new SecuredApiKeyRestrictions([
        'validUntil' => time() + 3600,
        'restrictIndices' => ['INDEX_NAME'],
    ])
);

$remaining = $client->getSecuredApiKeyRemainingValidity(
    securedApiKey: $securedApiKey
);
```

### `waitForTask`

The method was renamed from `waitTask` to `waitForTask`. It also gained optional `$maxRetries` and `$timeout` parameters for controlling retry behavior.

```php
// version 3
$index->waitTask($taskID);

// version 4
$client->waitForTask('INDEX_NAME', $taskID);

// With explicit retry controls:
$client->waitForTask('INDEX_NAME', $taskID, maxRetries: 50, timeout: 100000);
```

### `waitForAppTask`

This is a new helper in version 4.

```php
$client->waitForAppTask($taskID);
```

### `waitForApiKey`

This is a new standalone helper in version 4. In version 3, you had to poll `getApiKey` manually after key mutations.

```php
// Wait for a key to be created:
$client->waitForApiKey('my-api-key', 'add');

// Wait for a key update (pass the expected final state):
$client->waitForApiKey('my-api-key', 'update', apiKey: ['acl' => ['search']]);

// Wait for a key to be deleted:
$client->waitForApiKey('my-api-key', 'delete');
```

### `indexExists`

The helper was renamed from `exists()` on the index object to `indexExists()` on the client.

```php
// version 3
$exists = $index->exists();

// version 4
$exists = $client->indexExists('INDEX_NAME');
```

### `chunkedBatch`

`chunkedBatch` is now a public helper. In version 3, chunking was an internal implementation detail of `saveObjects`. The default `$action` is `'addObject'` and the default `$waitForTasks` is `false`.

```php
$client->chunkedBatch('INDEX_NAME', $objects, action: 'addObject', waitForTasks: true);
```

### `copyIndexBetweenApplications`

In version 3, the separate `Algolia\AccountClient` class provided a static `copyIndex` method for copying an index between two different Algolia applications. It accepted two `SearchIndex` objects and raised an exception if the destination already existed or if both indices were in the same application.

In version 4, `AccountClient` is removed. You can compose existing helpers across two clients to achieve the same result.

```php
// version 3
use Algolia\AccountClient;

AccountClient::copyIndex($srcIndex, $destIndex);

// version 4
$src = SearchClient::create('SRC_APP_ID', 'SRC_API_KEY');
$dst = SearchClient::create('DST_APP_ID', 'DST_API_KEY');

// Copy settings
$settings = $src->getSettings('SOURCE_INDEX');
$dst->setSettings('DEST_INDEX', $settings);

// Copy rules
$rules = [];
foreach ($src->browseRules('SOURCE_INDEX') as $rule) {
    $rules[] = $rule;
}
if (!empty($rules)) {
    $dst->saveRules('DEST_INDEX', $rules);
}

// Copy synonyms
$synonyms = [];
foreach ($src->browseSynonyms('SOURCE_INDEX') as $synonym) {
    $synonyms[] = $synonym;
}
if (!empty($synonyms)) {
    $dst->saveSynonyms('DEST_INDEX', $synonyms);
}

// Copy objects
$objects = [];
foreach ($src->browseObjects('SOURCE_INDEX') as $object) {
    $objects[] = $object;
}
$dst->replaceAllObjects('DEST_INDEX', $objects);
```

### `saveObjectsWithTransformation`

New in version 4. Routes objects through the Algolia Push connector. Requires `setTransformationRegion` to be called at client initialization.

```php
$client->setTransformationOptions(new TransformationOptions('us'));

$client->saveObjectsWithTransformation('INDEX_NAME', $objects, false, 1000);
```

### `replaceAllObjectsWithTransformation`

New in version 4. Atomically replaces all objects via the Push connector (copy settings/rules/synonyms to a temp index → push objects → move back). Requires `setTransformationRegion` at client initialization.

```php
$client->replaceAllObjectsWithTransformation(
    'INDEX_NAME',
    $objects,
    1000,
    ['settings', 'rules', 'synonyms']
);
```

### `partialUpdateObjectsWithTransformation`

New in version 4. Routes partial updates through the Push connector. The `$createIfNotExists` parameter is required with no default value.

```php
$client->partialUpdateObjectsWithTransformation(
    'INDEX_NAME',
    $objects,
    false,   // $createIfNotExists — required, no default
    false,   // $waitForTasks
    1000     // $batchSize
);
```

## Method changes reference

The following tables list all method names that changed between version 3 and version 4.

### Search API client

| Version 3 (legacy)                           |   | Version 4 (current)                          |
| -------------------------------------------- | - | -------------------------------------------- |
| `$client->addApiKey`                         | → | `$client->addApiKey`                         |
| `$client->addApiKey->wait`                   | → | `$client->waitForApiKey`                     |
| `$client->clearDictionaryEntries`            | → | `$client->batchDictionaryEntries`            |
| `$client->copyIndex`                         | → | `$client->operationIndex`                    |
| `$client->copyRules`                         | → | `$client->operationIndex`                    |
| `$client->copySynonyms`                      | → | `$client->operationIndex`                    |
| `$client->deleteApiKey`                      | → | `$client->deleteApiKey`                      |
| `$client->deleteDictionaryEntries`           | → | `$client->batchDictionaryEntries`            |
| `$client->generateSecuredApiKey`             | → | `$client->generateSecuredApiKey`             |
| `$client->getApiKey`                         | → | `$client->getApiKey`                         |
| `$client->getSecuredApiKeyRemainingValidity` | → | `$client->getSecuredApiKeyRemainingValidity` |
| `$client->listApiKeys`                       | → | `$client->listApiKeys`                       |
| `$client->listIndices`                       | → | `$client->listIndices`                       |
| `$client->moveIndex`                         | → | `$client->operationIndex`                    |
| `$client->multipleBatch`                     | → | `$client->multipleBatch`                     |
| `$client->multipleQueries`                   | → | `$client->search`                            |
| `$client->replaceDictionaryEntries`          | → | `$client->batchDictionaryEntries`            |
| `$client->restoreApiKey`                     | → | `$client->restoreApiKey`                     |
| `$client->saveDictionaryEntries`             | → | `$client->batchDictionaryEntries`            |
| `$client->updateApiKey`                      | → | `$client->updateApiKey`                      |
| `$index->batch`                              | → | `$client->batch`                             |
| `$index->browseObjects`                      | → | `$client->browseObjects`                     |
| `$index->browseRules`                        | → | `$client->browseRules`                       |
| `$index->browseSynonyms`                     | → | `$client->browseSynonyms`                    |
| `$index->clearObjects`                       | → | `$client->clearObjects`                      |
| `$index->clearRules`                         | → | `$client->clearRules`                        |
| `$index->clearSynonyms`                      | → | `$client->clearSynonyms`                     |
| `$index->copySettings`                       | → | `$client->operationIndex`                    |
| `$index->delete`                             | → | `$client->deleteIndex`                       |
| `$index->deleteBy`                           | → | `$client->deleteBy`                          |
| `$index->deleteObject`                       | → | `$client->deleteObject`                      |
| `$index->deleteObjects`                      | → | `$client->deleteObjects`                     |
| `$index->deleteRule`                         | → | `$client->deleteRule`                        |
| `$index->deleteSynonym`                      | → | `$client->deleteSynonym`                     |
| `$index->exists`                             | → | `$client->indexExists`                       |
| `$index->findObject`                         | → | `$client->searchSingleIndex`                 |
| `$index->getObject`                          | → | `$client->getObject`                         |
| `$index->getObjects`                         | → | `$client->getObjects`                        |
| `$index->getRule`                            | → | `$client->getRule`                           |
| `$index->getSettings`                        | → | `$client->getSettings`                       |
| `$index->getSynonym`                         | → | `$client->getSynonym`                        |
| `$index->getTask`                            | → | `$client->getTask`                           |
| `$index->partialUpdateObject`                | → | `$client->partialUpdateObject`               |
| `$index->partialUpdateObjects`               | → | `$client->partialUpdateObjects`              |
| `$index->replaceAllObjects`                  | → | `$client->replaceAllObjects`                 |
| `$index->replaceAllRules`                    | → | `$client->saveRules`                         |
| `$index->replaceAllSynonyms`                 | → | `$client->saveSynonyms`                      |
| `$index->saveObject`                         | → | `$client->saveObject`                        |
| `$index->saveObjects`                        | → | `$client->saveObjects`                       |
| `$index->saveRule`                           | → | `$client->saveRule`                          |
| `$index->saveRules`                          | → | `$client->saveRules`                         |
| `$index->saveSynonym`                        | → | `$client->saveSynonym`                       |
| `$index->saveSynonyms`                       | → | `$client->saveSynonyms`                      |
| `$index->search`                             | → | `$client->searchSingleIndex`                 |
| `$index->searchForFacetValues`               | → | `$client->searchForFacetValues`              |
| `$index->searchRules`                        | → | `$client->searchRules`                       |
| `$index->searchSynonyms`                     | → | `$client->searchSynonyms`                    |
| `$index->setSettings`                        | → | `$client->setSettings`                       |
| `$index->{operation}->wait`                  | → | `$client->waitForTask`                       |

### Recommend API client

| Version 3 (legacy)                     |   | Version 4 (current)           |
| -------------------------------------- | - | ----------------------------- |
| `$client->getFrequentlyBoughtTogether` | → | `$client->getRecommendations` |
| `$client->getLookingSimilar`           | → | `$client->getRecommendations` |
| `$client->getRecommendations`          | → | `$client->getRecommendations` |
| `$client->getRelatedProducts`          | → | `$client->getRecommendations` |
| `$client->getTrendingFacets`           | → | `$client->getRecommendations` |
| `$client->getTrendingItems`            | → | `$client->getRecommendations` |
