# Python: v3 → v4

## Install

```sh
pip install 'algoliasearch>=4,<5'
```

## Import changes

```python
# v3
from algoliasearch.search_client import SearchClient

# v4 — synchronous
from algoliasearch.search.client import SearchClientSync

# v4 — asynchronous
from algoliasearch.search.client import SearchClient
```

## Client initialization

```python
# v3
client = SearchClient.create("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")

# v4 — sync
client = SearchClientSync("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")

# v4 — async (use as context manager)
async with SearchClient("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY") as client:
    ...
```

`SearchClient.create()` factory method is removed.

## `init_index` removal

```python
# v3
index = client.init_index("INDEX_NAME")
index.search("QUERY")

# v4
from algoliasearch.search.models.search_params import SearchParams
client.search_single_index(
    index_name="INDEX_NAME",
    search_params=SearchParams(query="QUERY"),
)
```

## Method renames

| v3 | v4 |
|----|----|
| `index.search()` | `client.search_single_index()` |
| `client.multiple_queries()` | `client.search()` |
| `index.search_for_facet_values()` | `client.search_for_facet_values()` |
| `index.save_objects()` | `client.save_objects()` |
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

## Search

```python
# v4 — model class
client.search_single_index(
    index_name="INDEX_NAME",
    search_params=SearchParams(query="QUERY", filters="brand:Acme"),
)

# v4 — dict also accepted
client.search_single_index(
    index_name="INDEX_NAME",
    search_params={"query": "QUERY"},
)
```

## Indexing

```python
client.save_object(index_name="INDEX_NAME", body={"objectID": "1", "name": "item"})

client.partial_update_object(
    index_name="INDEX_NAME",
    object_id="1",
    attributes_to_update={"name": "Updated"},
)

client.delete_object(index_name="INDEX_NAME", object_id="1")
```

## `operation_index` (copy / move)

```python
from algoliasearch.search.models import OperationIndexParams

client.operation_index(
    index_name="SOURCE",
    operation_index_params=OperationIndexParams(operation="copy", destination="DEST"),
)
```

## Wait pattern

```python
# v3
response = index.save_object({"objectID": "1", "name": "item"})
index.wait_task(response["taskID"])

# v4
response = client.save_object(index_name="INDEX_NAME", body={"objectID": "1", "name": "item"})
client.wait_for_task(index_name="INDEX_NAME", task_id=response.task_id)
```

Three helpers: `wait_for_task`, `wait_for_app_task`, `wait_for_api_key`.

## `replace_all_objects`

```python
# v4 — safe removed; scopes required
client.replace_all_objects(
    index_name="INDEX_NAME",
    objects=my_objects,
    scopes=["settings", "rules", "synonyms"],
)
```

## `save_objects` changes

- `autoGenerateObjectIDIfNotExist` removed — every object must have `objectID`, or use `chunked_batch`
- New options: `wait_for_tasks` (default `False`), `batch_size` (default 1000)

## `partial_update_objects`

```python
# v3
index.partial_update_objects(objects, {"createIfNotExists": True})

# v4
client.partial_update_objects(
    index_name="INDEX_NAME",
    objects=my_objects,
    create_if_not_exists=True,
)
```

## Browse aggregator

```python
# v3
for obj in index.browse_objects({"query": ""}):
    process(obj)

# v4
objects = []
client.browse_objects(
    index_name="INDEX_NAME",
    aggregator=lambda response: objects.extend(response.hits),
)
```

## `chunked_batch`

```python
from algoliasearch.search.models import Action
client.chunked_batch(
    index_name="INDEX_NAME",
    objects=my_objects,
    action=Action.ADDOBJECT,
    wait_for_tasks=True,
    batch_size=1000,
)
```

## Transformation helpers (new in v4)

Require `transformation_region` at client init:
```python
client.save_objects_with_transformation(index_name="INDEX_NAME", objects=my_objects)
client.replace_all_objects_with_transformation(index_name="INDEX_NAME", objects=my_objects)
client.partial_update_objects_with_transformation(index_name="INDEX_NAME", objects=my_objects)
```
