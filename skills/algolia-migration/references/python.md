# Upgrade the Python API client to version 4

> Keep your Python API client up to date to benefit from improvements and bug fixes.

The latest major version of the `algoliasearch` package is version 4.
This page helps you upgrade from version 3
and explains the breaking changes you need to address.

Algolia generates the version 4 clients from OpenAPI specifications,
which provides consistent behavior across all languages and up-to-date API coverage.
The main architectural change is the removal of the `init_index` pattern:
all methods are now on the `client` instance directly, with `index_name` as a parameter.

For the full list of changes, see the Python changelog.

## Update your dependencies

Update the `algoliasearch` package to version 4:

```sh
pip install 'algoliasearch>=4.0,<5.0'
```

## Update imports

The import path changed from `algoliasearch.search_client` to `algoliasearch.search.client`.

```python
# version 3
from algoliasearch.search_client import SearchClient

# version 4
from algoliasearch.search.client import SearchClient, SearchClientSync
```

Version 4 also includes dedicated packages for each API.
If you only need methods from a specific API,
you can import them separately:

```python
# Search API
from algoliasearch.search.client import SearchClient, SearchClientSync
# A/B testing API
from algoliasearch.abtesting.client import AbtestingClient, AbtestingClientSync
# Analytics API
from algoliasearch.analytics.client import AnalyticsClient, AnalyticsClientSync
# Ingestion API
from algoliasearch.ingestion.client import IngestionClient, IngestionClientSync
# Insights API
from algoliasearch.insights.client import InsightsClient, InsightsClientSync
# Personalization API
from algoliasearch.personalization.client import (
    PersonalizationClient,
    PersonalizationClientSync,
)
# Query Suggestions API
from algoliasearch.query_suggestions.client import (
    QuerySuggestionsClient,
    QuerySuggestionsClientSync,
)
# Recommend API
from algoliasearch.recommend.client import RecommendClient, RecommendClientSync
# Monitoring API
from algoliasearch.monitoring.client import MonitoringClient, MonitoringClientSync
```

## Update client initialization

Client creation changed in version 4.
The `SearchClient.create()` factory method is gone.
Create a `SearchClientSync` instance for synchronous code
or a `SearchClient` instance for asynchronous code.

```python
# version 3
from algoliasearch.search_client import SearchClient
client = SearchClient.create("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")

# version 4 (synchronous)
from algoliasearch.search.client import SearchClientSync
client = SearchClientSync("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")

# version 4 (asynchronous)
from algoliasearch.search.client import SearchClient
async with SearchClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY") as client:
    ...
```

Note the naming: `SearchClientSync` is the synchronous client,
while `SearchClient` (without suffix) is the asynchronous client.
The asynchronous client supports the
[`async with`](https://peps.python.org/pep-0492/#asynchronous-context-managers-and-async-with) syntax
to automatically close open connections.

## Understand the new API surface

Version 4 introduces three major changes to the API surface:

* **No more `init_index`.**
  Version 3 relied on an index object with methods called on it.
  In version 4, all methods belong to the `client` instance,
  with `index_name` as a parameter.
* **Synchronous and asynchronous clients.**
  Version 4 includes `SearchClientSync` for synchronous code
  and `SearchClient` for asynchronous code (with `async/await`).
  Version 3 only had a synchronous client.
* **Typed model classes.**
  Version 4 includes model classes like `SearchParams` and `IndexSettings`
  for all API parameters (see [Use model classes or dictionaries](#use-model-classes-or-dictionaries)).

```python
# version 3
client = SearchClient.create("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")
index = client.init_index("INDEX_NAME")
index.search("QUERY")

# version 4
client = SearchClientSync("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")
client.search_single_index(
    index_name="INDEX_NAME",
    search_params=SearchParams(query="QUERY"),
)
```

  If you have many files to update,
  search your codebase for `init_index` or `.init_index(` to find every place that needs changing.

## Use model classes or dictionaries

Version 4 methods accept both **model classes** and **dictionaries** as parameters.

```python
# Using a model class
from algoliasearch.search.models.search_params import SearchParams

client.search_single_index(
    index_name="INDEX_NAME",
    search_params=SearchParams(query="QUERY"),
)

# Using a dictionary
client.search_single_index(
    index_name="INDEX_NAME",
    search_params={"query": "QUERY"},
)
```

Model classes give you IDE autocompletion, type safety,
and predictable structure that works well with AI coding assistants.
The code examples in this guide use model classes,
but you can use dictionaries anywhere a model is expected.

## Update search calls

### Search a single index

The `index.search()` method is now `client.search_single_index()`.
Pass the index name and search parameters as separate arguments:

```python
# version 3
index = client.init_index("INDEX_NAME")
results = index.search("QUERY", {
    "facetFilters": ["category:Book"],
})

# version 4
results = client.search_single_index(
    index_name="INDEX_NAME",
    search_params=SearchParams(
        query="QUERY",
        facet_filters=["category:Book"],
    ),
)
```

### Search multiple indices

The `client.multiple_queries()` method is now `client.search()`.
Each request in the list requires an `indexName`:

```python
# version 3
results = client.multiple_queries([
    {"indexName": "INDEX_1", "query": "QUERY"},
    {"indexName": "INDEX_2", "query": "QUERY"},
])

# version 4
results = client.search(
    search_method_params=SearchMethodParams(
        requests=[
            SearchForHits(index_name="INDEX_1", query="QUERY"),
            SearchForHits(index_name="INDEX_2", query="QUERY"),
        ],
    ),
)
```

### Search for facet values

The `index.search_for_facet_values()` method becomes `client.search_for_facet_values()`
with an `index_name` parameter:

```python
# version 3
index = client.init_index("INDEX_NAME")
results = index.search_for_facet_values("category", "book")

# version 4
results = client.search_for_facet_values(
    index_name="INDEX_NAME",
    facet_name="category",
    search_for_facet_values_request=SearchForFacetValuesRequest(facet_query="book"),
)
```

## Update indexing operations

In version 4, indexing methods are on the client instead of the index object,
with `index_name` as a parameter.

### Add or replace records

```python
# version 3
index = client.init_index("INDEX_NAME")
index.save_objects([{"objectID": "1", "name": "Record"}])

# version 4
response = client.save_objects(
    index_name="INDEX_NAME",
    objects=[{"objectID": "1", "name": "Record"}],
)
```

### Partially update records

```python
# version 3
index = client.init_index("INDEX_NAME")
index.partial_update_object({"objectID": "1", "name": "Updated"})

# version 4
client.partial_update_object(
    index_name="INDEX_NAME",
    object_id="1",
    attributes_to_update={"name": "Updated"},
)
```

### Delete records

```python
# version 3
index = client.init_index("INDEX_NAME")
index.delete_object("1")

# version 4
client.delete_object(
    index_name="INDEX_NAME",
    object_id="1",
)
```

## Update settings, synonyms, and rules

### Get and set settings

```python
# version 3
index = client.init_index("INDEX_NAME")
settings = index.get_settings()
index.set_settings({"searchableAttributes": ["title", "author"]})

# version 4
settings = client.get_settings(
    index_name="INDEX_NAME",
)
client.set_settings(
    index_name="INDEX_NAME",
    index_settings=IndexSettings(searchable_attributes=["title", "author"]),
)
```

### Save synonyms and rules

```python
# version 3
index = client.init_index("INDEX_NAME")
index.save_synonyms([{"objectID": "1", "type": "synonym", "synonyms": ["car", "auto"]}])
index.save_rules([{"objectID": "1", "conditions": [{"anchoring": "contains", "pattern": "shoes"}], "consequence": {"params": {"query": "sneakers"}}}])

# version 4
client.save_synonyms(
    index_name="INDEX_NAME",
    synonym_hit=[
        {"objectID": "1", "type": "synonym", "synonyms": ["car", "auto"]},
    ],
)
client.save_rules(
    index_name="INDEX_NAME",
    rules=[
        {
            "objectID": "1",
            "conditions": [{"anchoring": "contains", "pattern": "shoes"}],
            "consequence": {"params": {"query": "sneakers"}},
        },
    ],
)
```

  In version 3, `index.replace_all_rules()` and `index.replace_all_synonyms()` replaced all rules or synonyms.
  In version 4, use `client.save_rules()` or `client.save_synonyms()` with the `clear_existing_rules` or `replace_existing_synonyms` parameter set to `True`.

## Update index management

The `copy_index`, `move_index`, `copy_rules`, `copy_synonyms`, and `copy_settings`
methods are all replaced by a single `operation_index` method.

### Copy an index

```python
# version 3
client.copy_index("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME")

# version 4
client.operation_index(
    index_name="SOURCE_INDEX_NAME",
    operation_index_params=OperationIndexParams(
        operation="copy",
        destination="DESTINATION_INDEX_NAME",
    ),
)
```

### Move (rename) an index

```python
# version 3
client.move_index("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME")

# version 4
client.operation_index(
    index_name="SOURCE_INDEX_NAME",
    operation_index_params=OperationIndexParams(
        operation="move",
        destination="DESTINATION_INDEX_NAME",
    ),
)
```

### Copy only rules or settings

In version 4, use the `scope` parameter to limit the operation to specific data:

```python
# version 4 -- copy only rules and settings from one index to another
client.operation_index(
    index_name="SOURCE_INDEX_NAME",
    operation_index_params=OperationIndexParams(
        operation="copy",
        destination="DESTINATION_INDEX_NAME",
        scope=["rules", "settings"],
    ),
)
```

### Check if an index exists

In version 3, you could check if an index existed using the `exists` method on the index object.
In version 4, use the `index_exists` helper method on the client:

```python
# version 3
index = client.init_index("INDEX_NAME")
index.exists()

# version 4
client.index_exists(
    index_name="INDEX_NAME",
)
```

## Update task handling

Version 3 supported chaining `.wait()` on operations.
Version 4 replaces this pattern with dedicated wait helpers.

```python
# version 3
index = client.init_index("INDEX_NAME")
index.set_settings({"searchableAttributes": ["title"]}).wait()

# version 4
response = client.set_settings(
    index_name="INDEX_NAME",
    index_settings=IndexSettings(searchable_attributes=["title"]),
)
client.wait_for_task(index_name="INDEX_NAME", task_id=response.task_id)
```

Version 4 includes three wait helpers:

* `wait_for_task`: wait until indexing operations are done.
* `wait_for_app_task`: wait for application-level tasks.
* `wait_for_api_key`: wait for API key operations.

## Helper method changes

The following sections document breaking changes in helper method signatures and behavior between version 3 and version 4.

### `replace_all_objects`

The `safe` option has been removed. In version 3, passing `safe=True` in `request_options` caused the helper to wait after each step. In version 4, the helper always waits—equivalent to the previous `safe=True` behavior.

The `scopes` parameter is optional. When omitted, it defaults to `["settings", "rules", "synonyms"]`.

```python
# version 3
index.replace_all_objects(
    objects=my_objects,
    request_options={"safe": True},
)

# version 4
await client.replace_all_objects(
    index_name="INDEX_NAME",
    objects=my_objects,
)
```

### `save_objects`

The `autoGenerateObjectIDIfNotExist` option has been removed. In version 4, every object must include an `object_id`, or you must use `chunked_batch` with `action="addObject"` if you want the API to generate object IDs.

Two new optional parameters are available:

* `wait_for_tasks` (waits for all indexing tasks before returning, default `False`)
* `batch_size` (controls objects per API call, default `1,000`)

```python
# version 3
index.save_objects(my_objects, {"autoGenerateObjectIDIfNotExist": True})

# version 4
await client.save_objects(
    index_name="INDEX_NAME",
    objects=my_objects,
    wait_for_tasks=True,
    batch_size=1000,
)
```

### `delete_objects`

Two new optional parameters are available:

* `wait_for_tasks` (default `False`)
* `batch_size` (default `1,000`)

```python
# version 3
index.delete_objects(object_ids=["id1", "id2"])

# version 4
await client.delete_objects(
    index_name="INDEX_NAME",
    object_ids=["id1", "id2"],
    wait_for_tasks=True,
    batch_size=1000,
)
```

### `partial_update_objects`

The `create_if_not_exists` parameter moved from `request_options` to an explicit keyword argument.

```python
# version 3
index.partial_update_objects(my_objects, {"createIfNotExists": True})

# version 4
await client.partial_update_objects(
    index_name="INDEX_NAME",
    objects=my_objects,
    create_if_not_exists=True,
)
```

### `browse_objects`, `browse_rules`, `browse_synonyms`

These helpers now use an `aggregator` callback instead of returning an iterator. The helper calls `aggregator` with each page of results as it paginates.

```python
# version 3
for obj in index.browse_objects({"query": ""}):
    process(obj)

# version 4
objects = []

await client.browse_objects(
    index_name="INDEX_NAME",
    aggregator=lambda response: objects.extend(response.hits),
)
```

### `generate_secured_api_key` and `get_secured_api_key_remaining_validity`

Both methods were static methods on the index class in version 3. In version 4 they are instance methods on the client.

```python
# version 3
from algoliasearch.search_index import SearchIndex

key = SearchIndex.generate_secured_api_key("parentApiKey", {"validUntil": 1893456000})
remaining = SearchIndex.get_secured_api_key_remaining_validity(key)

# version 4
key = client.generate_secured_api_key(
    parent_api_key="parentApiKey",
    restrictions={"validUntil": 1893456000},
)
remaining = client.get_secured_api_key_remaining_validity(secured_api_key=key)
```

### `wait_for_task`

The helper was renamed from `wait_task` to `wait_for_task`, moved to the client, and now accepts explicit `max_retries` (default `50`) and `timeout` parameters. In version 3 it retried indefinitely with no cap.

```python
# version 3
index.wait_task(task_id)

# version 4
await client.wait_for_task(
    index_name="INDEX_NAME",
    task_id=task_id,
    max_retries=50,
)
```

### `wait_for_app_task`

This is a new helper in version 4.

```python
await client.wait_for_app_task(task_id=task_id)
```

### `wait_for_api_key`

This is a new standalone helper in version 4.

```python
# Wait for a key to be created:
await client.wait_for_api_key(key="my-api-key", operation="add")

# Wait for a key update (pass the expected final state):
await client.wait_for_api_key(
    key="my-api-key",
    operation="update",
    api_key={"acl": ["search", "browse"]},
)
```

### `index_exists`

The helper was renamed from `exists()` on the index object to `index_exists()` on the client.

```python
# version 3
exists = index.exists()

# version 4
exists = await client.index_exists(index_name="INDEX_NAME")
```

### `chunked_batch`

`chunked_batch` is now a public helper. In version 3, chunking was an internal detail of `save_objects`. The `action` parameter defaults to `Action.ADDOBJECT` and `wait_for_tasks` defaults to `False`.

```python
responses = await client.chunked_batch(
    index_name="INDEX_NAME",
    objects=my_objects,
    action=Action.ADDOBJECT,
    wait_for_tasks=True,
    batch_size=1000,
)
```

### `account_copy_index`

In version 3, `AccountClient.copy_index` allowed copying an index between two different Algolia applications. It accepted two `SearchIndex` objects and raised if the destination already existed or if both indices were on the same app.

In version 4, `AccountClient` is removed. You can compose existing helpers across two clients to achieve the same result.

```python
# version 3
from algoliasearch.account_client import AccountClient

AccountClient.copy_index(source_index, destination_index)

# version 4
src = SearchClient("SRC_APP_ID", "SRC_API_KEY")
dst = SearchClient("DST_APP_ID", "DST_API_KEY")

# Copy settings
settings = await src.get_settings(index_name="SOURCE_INDEX")
await dst.set_settings(index_name="DEST_INDEX", index_settings=settings.to_dict())

# Copy rules
rules = []
await src.browse_rules("SOURCE_INDEX", aggregator=lambda r: rules.extend(r.hits))
if rules:
    await dst.save_rules(index_name="DEST_INDEX", rules=rules)

# Copy synonyms
synonyms = []
await src.browse_synonyms("SOURCE_INDEX", aggregator=lambda r: synonyms.extend(r.hits))
if synonyms:
    await dst.save_synonyms(index_name="DEST_INDEX", synonyms=synonyms)

# Copy objects
objects = []
await src.browse_objects("SOURCE_INDEX", aggregator=lambda r: objects.extend(r.hits))
await dst.replace_all_objects(index_name="DEST_INDEX", objects=objects)
```

### `save_objects_with_transformation`

New in version 4. Routes objects through the Algolia Push connector. Requires `transformation_region` at client initialization.

```python
client = SearchClient.create_with_config(
    SearchConfig("APP_ID", "API_KEY", transformation_options=TransformationOptions(region="us"))
)

await client.save_objects_with_transformation(
    index_name="INDEX_NAME",
    objects=my_objects,
    wait_for_tasks=False,
    batch_size=1000,
)
```

### `replace_all_objects_with_transformation`

New in version 4. Atomically replaces all objects via the Push connector (copy settings/rules/synonyms to a temp index → push objects → move back). Requires `transformation_region` at client initialization.

```python
await client.replace_all_objects_with_transformation(
    index_name="INDEX_NAME",
    objects=my_objects,
    batch_size=1000,
    scopes=["settings", "rules", "synonyms"],
)
```

### `partial_update_objects_with_transformation`

New in version 4. Routes partial updates through the Push connector. The `create_if_not_exists` parameter defaults to `False`.

```python
await client.partial_update_objects_with_transformation(
    index_name="INDEX_NAME",
    objects=my_objects,
    create_if_not_exists=False,
    wait_for_tasks=False,
    batch_size=1000,
)
```

## Method changes reference

The following tables list all method names that changed between version 3 and version 4.

### Search API client

| Version 3 (legacy)                              |   | Version 4 (current)                             |
| ----------------------------------------------- | - | ----------------------------------------------- |
| `client.add_api_key`                            | → | `client.add_api_key`                            |
| `client.add_api_key.wait`                       | → | `client.wait_for_api_key`                       |
| `client.clear_dictionary_entries`               | → | `client.batch_dictionary_entries`               |
| `client.copy_index`                             | → | `client.operation_index`                        |
| `client.copy_rules`                             | → | `client.operation_index`                        |
| `client.copy_synonyms`                          | → | `client.operation_index`                        |
| `client.delete_api_key`                         | → | `client.delete_api_key`                         |
| `client.delete_dictionary_entries`              | → | `client.batch_dictionary_entries`               |
| `client.generate_secured_api_key`               | → | `client.generate_secured_api_key`               |
| `client.get_api_key`                            | → | `client.get_api_key`                            |
| `client.get_secured_api_key_remaining_validity` | → | `client.get_secured_api_key_remaining_validity` |
| `client.list_api_keys`                          | → | `client.list_api_keys`                          |
| `client.list_indices`                           | → | `client.list_indices`                           |
| `client.move_index`                             | → | `client.operation_index`                        |
| `client.multiple_batch`                         | → | `client.multiple_batch`                         |
| `client.multiple_queries`                       | → | `client.search`                                 |
| `client.replace_dictionary_entries`             | → | `client.batch_dictionary_entries`               |
| `client.restore_api_key`                        | → | `client.restore_api_key`                        |
| `client.save_dictionary_entries`                | → | `client.batch_dictionary_entries`               |
| `client.update_api_key`                         | → | `client.update_api_key`                         |
| `index.batch`                                   | → | `client.batch`                                  |
| `index.browse_objects`                          | → | `client.browse_objects`                         |
| `index.browse_rules`                            | → | `client.browse_rules`                           |
| `index.browse_synonyms`                         | → | `client.browse_synonyms`                        |
| `index.clear_objects`                           | → | `client.clear_objects`                          |
| `index.clear_rules`                             | → | `client.clear_rules`                            |
| `index.clear_synonyms`                          | → | `client.clear_synonyms`                         |
| `index.copy_settings`                           | → | `client.operation_index`                        |
| `index.delete`                                  | → | `client.delete_index`                           |
| `index.delete_by`                               | → | `client.delete_by`                              |
| `index.delete_object`                           | → | `client.delete_object`                          |
| `index.delete_objects`                          | → | `client.delete_objects`                         |
| `index.delete_rule`                             | → | `client.delete_rule`                            |
| `index.delete_synonym`                          | → | `client.delete_synonym`                         |
| `index.exists`                                  | → | `client.index_exists`                           |
| `index.find_object`                             | → | `client.search_single_index`                    |
| `index.get_object`                              | → | `client.get_object`                             |
| `index.get_objects`                             | → | `client.get_objects`                            |
| `index.get_rule`                                | → | `client.get_rule`                               |
| `index.get_settings`                            | → | `client.get_settings`                           |
| `index.get_synonym`                             | → | `client.get_synonym`                            |
| `index.get_task`                                | → | `client.get_task`                               |
| `index.partial_update_object`                   | → | `client.partial_update_object`                  |
| `index.partial_update_objects`                  | → | `client.partial_update_objects`                 |
| `index.replace_all_objects`                     | → | `client.replace_all_objects`                    |
| `index.replace_all_rules`                       | → | `client.save_rules`                             |
| `index.replace_all_synonyms`                    | → | `client.save_synonyms`                          |
| `index.save_object`                             | → | `client.save_object`                            |
| `index.save_objects`                            | → | `client.save_objects`                           |
| `index.save_rule`                               | → | `client.save_rule`                              |
| `index.save_rules`                              | → | `client.save_rules`                             |
| `index.save_synonym`                            | → | `client.save_synonym`                           |
| `index.save_synonyms`                           | → | `client.save_synonyms`                          |
| `index.search`                                  | → | `client.search_single_index`                    |
| `index.search_for_facet_values`                 | → | `client.search_for_facet_values`                |
| `index.search_rules`                            | → | `client.search_rules`                           |
| `index.search_synonyms`                         | → | `client.search_synonyms`                        |
| `index.set_settings`                            | → | `client.set_settings`                           |
| `index.{operation}.wait`                        | → | `client.wait_for_task`                          |

### Recommend API client

| Version 3 (legacy)                      |   | Version 4 (current)          |
| --------------------------------------- | - | ---------------------------- |
| `client.get_frequently_bought_together` | → | `client.get_recommendations` |
| `client.get_recommendations`            | → | `client.get_recommendations` |
| `client.get_related_products`           | → | `client.get_recommendations` |
