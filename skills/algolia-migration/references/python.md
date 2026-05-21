# Python: v3 → v4

## Install

```sh
pip install 'algoliasearch>=4.0,<5.0'
```

## Import changes

```python
# v3
from algoliasearch.search_client import SearchClient

# v4 — synchronous
from algoliasearch.search.client import SearchClientSync

# v4 — asynchronous
from algoliasearch.search.client import SearchClient

# dedicated clients
from algoliasearch.search.client import SearchClientSync, SearchClient
from algoliasearch.abtesting.client import AbtestingClientSync, AbtestingClient
```

## Client initialization

```python
# v3
client = SearchClient.create("APP_ID", "API_KEY")

# v4 — sync
client = SearchClientSync("APP_ID", "API_KEY")

# v4 — async (use as context manager)
async with SearchClient("APP_ID", "API_KEY") as client:
    ...
```

`SearchClient.create()` factory method is removed.

## `init_index` removal

`init_index` is removed. All methods that previously lived on the index object are now on the client and require `index_name`. v4 also introduces typed model classes (dicts also accepted).

```python
# v3
index = client.init_index("INDEX_NAME")
index.search("QUERY")

# v4
from algoliasearch.search.models import SearchParams

client = SearchClientSync("APP_ID", "API_KEY")
client.search_single_index(
    index_name="INDEX_NAME",
    search_params=SearchParams(query="QUERY"),
)
# dict also accepted:
client.search_single_index(index_name="INDEX_NAME", search_params={"query": "QUERY"})
```

## Method renames

| v3 | v4 |
|----|----|
| `index.search()` | `client.search_single_index()` |
| `client.multiple_queries()` | `client.search()` |
| `index.search_for_facet_values()` | `client.search_for_facet_values()` |
| `index.save_objects()` | `client.save_objects()` |
| `index.save_object()` | `client.save_object()` |
| `index.partial_update_object()` | `client.partial_update_object()` |
| `index.delete_object()` | `client.delete_object()` |
| `index.get_settings()` | `client.get_settings()` |
| `index.set_settings()` | `client.set_settings()` |
| `index.replace_all_rules()` | `client.save_rules(clear_existing_rules=True)` |
| `index.replace_all_synonyms()` | `client.save_synonyms(replace_existing_synonyms=True)` |
| `copy_index()` / `move_index()` / `copy_rules()` / etc. | `client.operation_index()` |
| `index.exists()` | `client.index_exists()` |
| `index.wait()` / `index.wait_task()` | `client.wait_for_task()` |
| `SearchIndex.generate_secured_api_key()` (static) | `client.generate_secured_api_key()` (instance) |
| `SearchIndex.get_secured_api_key_remaining_validity()` (static) | `client.get_secured_api_key_remaining_validity()` (instance) |
| `client.clear_dictionary_entries()` / `delete_dictionary_entries()` / etc. | `client.batch_dictionary_entries()` |

## Search single index

```python
# v3
results = index.search("QUERY", {"facetFilters": ["category:Book"]})

# v4 — model class
results = client.search_single_index(
    index_name="INDEX_NAME",
    search_params=SearchParams(query="QUERY", facet_filters=["category:Book"]),
)

# v4 — dict also accepted
results = client.search_single_index(
    index_name="INDEX_NAME",
    search_params={"query": "QUERY"},
)
```

## Multiple index search

```python
# v3
results = client.multiple_queries([
    {"indexName": "INDEX_1", "query": "QUERY"},
])

# v4
from algoliasearch.search.models import SearchMethodParams, SearchForHits

results = client.search(
    search_method_params=SearchMethodParams(
        requests=[SearchForHits(index_name="INDEX_1", query="QUERY")]
    )
)
```

## Search for facet values

```python
# v3
results = index.search_for_facet_values("category", "book")

# v4
from algoliasearch.search.models import SearchForFacetValuesRequest

results = client.search_for_facet_values(
    index_name="INDEX_NAME",
    facet_name="category",
    search_for_facet_values_request=SearchForFacetValuesRequest(facet_query="book"),
)
```

## Indexing

```python
# save_objects
response = client.save_objects(
    index_name="INDEX_NAME",
    objects=[{"objectID": "1", "name": "Record"}],
)

# partial_update_object
client.partial_update_object(
    index_name="INDEX_NAME",
    object_id="1",
    attributes_to_update={"name": "Updated"},
)

# delete_object
client.delete_object(index_name="INDEX_NAME", object_id="1")
```

## Settings, synonyms, rules

```python
from algoliasearch.search.models import IndexSettings

# get_settings / set_settings
settings = client.get_settings(index_name="INDEX_NAME")
client.set_settings(
    index_name="INDEX_NAME",
    index_settings=IndexSettings(searchable_attributes=["title", "author"]),
)

# save_synonyms
client.save_synonyms(
    index_name="INDEX_NAME",
    synonym_hit=[{"objectID": "1", "type": "synonym", "synonyms": ["car", "auto"]}],
)

# save_rules
client.save_rules(index_name="INDEX_NAME", rules=[...])

# replace_all_rules → save_rules with clear_existing_rules
client.save_rules(index_name="INDEX_NAME", rules=[...], clear_existing_rules=True)

# replace_all_synonyms → save_synonyms with replace_existing_synonyms
client.save_synonyms(index_name="INDEX_NAME", synonym_hit=[...], replace_existing_synonyms=True)
```

## `operation_index` (copy / move)

```python
from algoliasearch.search.models import OperationIndexParams

# copy
client.operation_index(
    index_name="SOURCE_INDEX_NAME",
    operation_index_params=OperationIndexParams(operation="copy", destination="DESTINATION_INDEX_NAME"),
)

# move
client.operation_index(
    index_name="SOURCE_INDEX_NAME",
    operation_index_params=OperationIndexParams(operation="move", destination="DESTINATION_INDEX_NAME"),
)

# copy with scope
client.operation_index(
    index_name="SOURCE_INDEX_NAME",
    operation_index_params=OperationIndexParams(
        operation="copy", destination="DEST", scope=["rules", "settings"]
    ),
)

# check if index exists
client.index_exists(index_name="INDEX_NAME")
```

## Wait pattern

```python
# v3
response = index.set_settings({"searchableAttributes": ["title"]})
index.wait_task(response["taskID"])

# v4
from algoliasearch.search.models import IndexSettings

response = client.set_settings(
    index_name="INDEX_NAME",
    index_settings=IndexSettings(searchable_attributes=["title"]),
)
client.wait_for_task(index_name="INDEX_NAME", task_id=response.task_id)
```

Three helpers: `wait_for_task`, `wait_for_app_task`, `wait_for_api_key`.

```python
# wait_for_api_key — add
await client.wait_for_api_key(key="my-api-key", operation="add")

# wait_for_api_key — update (pass expected final state)
await client.wait_for_api_key(
    key="my-api-key",
    operation="update",
    api_key={"acl": ["search", "browse"]},
)

# wait_for_app_task (new in v4)
await client.wait_for_app_task(task_id=task_id)
```

`wait_for_task` also accepts `max_retries` (default 50):
```python
await client.wait_for_task(index_name="INDEX_NAME", task_id=task_id, max_retries=50)
```

## `replace_all_objects`

```python
# v4 — safe option removed; scopes required
client.replace_all_objects(
    index_name="INDEX_NAME",
    objects=my_objects,
    scopes=["settings", "rules", "synonyms"],
)
```

## Helper method changes

- **`save_objects`**: `autoGenerateObjectIDIfNotExist` removed — every object must have `objectID`, or use `chunked_batch`; new `wait_for_tasks` (default `False`) and `batch_size` (default 1000) options:
```python
await client.save_objects(
    index_name="INDEX_NAME",
    objects=my_objects,
    wait_for_tasks=True,
    batch_size=1000,
)
```

- **`delete_objects`**: new `wait_for_tasks` and `batch_size` options

- **`partial_update_objects`**: `create_if_not_exists` is now an explicit keyword argument:
```python
await client.partial_update_objects(
    index_name="INDEX_NAME",
    objects=my_objects,
    create_if_not_exists=True,
)
```

## Browse aggregator

```python
# v3 — iterator
for obj in index.browse_objects({"query": ""}):
    process(obj)

# v4 — aggregator callback
objects = []
await client.browse_objects(
    index_name="INDEX_NAME",
    aggregator=lambda response: objects.extend(response.hits),
)
```

## Secured API key

```python
# v3 — static methods on SearchIndex
key = SearchIndex.generate_secured_api_key(
    "parentApiKey", {"validUntil": 1893456000}
)
remaining = SearchIndex.get_secured_api_key_remaining_validity(key)

# v4 — instance methods on client
key = client.generate_secured_api_key(
    parent_api_key="parentApiKey",
    restrictions={"validUntil": 1893456000},
)
remaining = client.get_secured_api_key_remaining_validity(secured_api_key=key)
```

## New in v4

**`chunked_batch`** (was internal):
```python
from algoliasearch.search.models import Action

responses = await client.chunked_batch(
    index_name="INDEX_NAME",
    objects=my_objects,
    action=Action.ADDOBJECT,
    wait_for_tasks=True,
    batch_size=1000,
)
```

**`AccountClient` removed** — compose cross-app copy manually:
```python
src = SearchClientSync("SRC_APP_ID", "SRC_API_KEY")
dst = SearchClientSync("DST_APP_ID", "DST_API_KEY")

settings = await src.get_settings(index_name="SOURCE_INDEX")
await dst.set_settings(index_name="DEST_INDEX", index_settings=settings)

rules = []
await src.browse_rules("SOURCE_INDEX", aggregator=lambda r: rules.extend(r.hits))
if rules:
    await dst.save_rules(index_name="DEST_INDEX", rules=rules)

synonyms = []
await src.browse_synonyms("SOURCE_INDEX", aggregator=lambda r: synonyms.extend(r.hits))
if synonyms:
    await dst.save_synonyms(index_name="DEST_INDEX", synonyms=synonyms)

objects = []
await src.browse_objects("SOURCE_INDEX", aggregator=lambda r: objects.extend(r.hits))
await dst.replace_all_objects(index_name="DEST_INDEX", objects=objects)
```

**Transformation helpers** (require `transformation_region` at init):
```python
from algoliasearch.search.config import SearchConfig

client = SearchClientSync.create_with_config(
    SearchConfig("APP_ID", "API_KEY", transformation_region="us")
)

await client.save_objects_with_transformation(
    index_name="INDEX_NAME", objects=my_objects, wait_for_tasks=False, batch_size=1000
)

await client.replace_all_objects_with_transformation(
    index_name="INDEX_NAME", objects=my_objects, batch_size=1000,
    scopes=["settings", "rules", "synonyms"],
)

await client.partial_update_objects_with_transformation(
    index_name="INDEX_NAME", objects=my_objects,
    create_if_not_exists=False, wait_for_tasks=False, batch_size=1000,
)
```

## Method changes reference

Full rename table from v3 to v4:

| v3 | v4 |
|----|----|
| `client.multiple_queries()` | `client.search()` |
| `client.clear_dictionary_entries()` | `client.batch_dictionary_entries()` |
| `client.delete_dictionary_entries()` | `client.batch_dictionary_entries()` |
| `client.replace_dictionary_entries()` | `client.batch_dictionary_entries()` |
| `client.save_dictionary_entries()` | `client.batch_dictionary_entries()` |
| `client.copy_index()` | `client.operation_index()` |
| `client.copy_rules()` | `client.operation_index()` |
| `client.copy_synonyms()` | `client.operation_index()` |
| `client.move_index()` | `client.operation_index()` |
| `SearchIndex.generate_secured_api_key()` (static) | `client.generate_secured_api_key()` (instance) |
| `SearchIndex.get_secured_api_key_remaining_validity()` (static) | `client.get_secured_api_key_remaining_validity()` (instance) |
| `index.batch()` | `client.batch()` |
| `index.browse_objects()` | `client.browse_objects()` |
| `index.browse_rules()` | `client.browse_rules()` |
| `index.browse_synonyms()` | `client.browse_synonyms()` |
| `index.clear_objects()` | `client.clear_objects()` |
| `index.clear_rules()` | `client.clear_rules()` |
| `index.clear_synonyms()` | `client.clear_synonyms()` |
| `index.copy_settings()` | `client.operation_index()` |
| `index.delete()` | `client.delete_index()` |
| `index.delete_by()` | `client.delete_by()` |
| `index.delete_object()` | `client.delete_object()` |
| `index.delete_objects()` | `client.delete_objects()` |
| `index.delete_rule()` | `client.delete_rule()` |
| `index.delete_synonym()` | `client.delete_synonym()` |
| `index.exists()` | `client.index_exists()` |
| `index.get_object()` | `client.get_object()` |
| `index.get_objects()` | `client.get_objects()` |
| `index.get_rule()` | `client.get_rule()` |
| `index.get_settings()` | `client.get_settings()` |
| `index.get_synonym()` | `client.get_synonym()` |
| `index.get_task()` | `client.get_task()` |
| `index.partial_update_object()` | `client.partial_update_object()` |
| `index.partial_update_objects()` | `client.partial_update_objects()` |
| `index.replace_all_objects()` | `client.replace_all_objects()` |
| `index.replace_all_rules()` | `client.save_rules()` (with `clear_existing_rules=True`) |
| `index.replace_all_synonyms()` | `client.save_synonyms()` (with `replace_existing_synonyms=True`) |
| `index.save_object()` | `client.save_object()` |
| `index.save_objects()` | `client.save_objects()` |
| `index.save_rule()` | `client.save_rule()` |
| `index.save_rules()` | `client.save_rules()` |
| `index.save_synonym()` | `client.save_synonym()` |
| `index.save_synonyms()` | `client.save_synonyms()` |
| `index.search()` | `client.search_single_index()` |
| `index.search_for_facet_values()` | `client.search_for_facet_values()` |
| `index.search_rules()` | `client.search_rules()` |
| `index.search_synonyms()` | `client.search_synonyms()` |
| `index.set_settings()` | `client.set_settings()` |
| `index.wait()` / `index.wait_task()` | `client.wait_for_task()` |

Recommend API renames:

| v3 | v4 |
|----|----|
| `client.get_frequently_bought_together()` | `client.get_recommendations()` |
| `client.get_related_products()` | `client.get_recommendations()` |
| `client.get_recommendations()` | `client.get_recommendations()` |
