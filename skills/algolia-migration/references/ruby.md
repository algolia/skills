# Ruby: v2 → v3

## Install

```sh
bundle add algolia --version '~> 3.0'
```

> The gem name is `algolia`. Do not confuse with the older `algoliasearch` gem (v2).

## Import changes

```ruby
# v2
require "algolia"
Algolia::Search::Client  # nested module

# v3 — module hierarchy flattened
require "algolia"
Algolia::SearchClient
```

v3 ships dedicated clients: `SearchClient`, `RecommendClient`, `AbtestingClient`, `AnalyticsClient`, `IngestionClient`, `InsightsClient`, `MonitoringClient`, `PersonalizationClient`, `QuerySuggestionsClient`, `UsageClient`.

## Client initialization

```ruby
# v2
client = Algolia::Search::Client.create("APP_ID", "API_KEY")

# v3
client = Algolia::SearchClient.create("APP_ID", "API_KEY")
```

## Remove `init_index`

```ruby
# v2
index = client.init_index("INDEX_NAME")
index.search("QUERY")

# v3
client.search_single_index(
  "INDEX_NAME",
  Algolia::Search::SearchParamsObject.new(query: "QUERY")
)
```

## Method renames

| v2 | v3 |
|----|----|
| `client.multiple_queries()` | `client.search()` |
| `index.search()` | `client.search_single_index("INDEX_NAME", ...)` |
| `index.search_for_facet_values()` | `client.search_for_facet_values("INDEX_NAME", ...)` |
| `index.save_object()` | `client.save_object("INDEX_NAME", obj)` |
| `index.partial_update_object()` | `client.partial_update_object("INDEX_NAME", id, update)` |
| `index.delete_object()` | `client.delete_object("INDEX_NAME", id)` |
| `index.get_settings()` | `client.get_settings("INDEX_NAME")` |
| `index.set_settings()` | `client.set_settings("INDEX_NAME", settings)` |
| `index.replace_all_rules()` | `client.save_rules(..., clear_existing_rules: true)` |
| `index.replace_all_synonyms()` | `client.save_synonyms(..., replace_existing_synonyms: true)` |
| `copy_index()` / `move_index()` / `copy_rules()` | `client.operation_index()` |
| `index.exists?` | `client.index_exists("INDEX_NAME")` |
| `list_indexes` | `list_indices` |
| `get_top_user_id` | `get_top_user_ids` |

## Multiple index search

```ruby
response = client.search(Algolia::Search::SearchMethodParams.new(requests: [
  Algolia::Search::SearchForHits.new(index_name: "INDEX_1", query: "QUERY"),
  Algolia::Search::SearchForHits.new(index_name: "INDEX_2", query: "QUERY"),
]))
```

## Indexing

```ruby
client.save_object("INDEX_NAME", { objectID: "1", name: "Record" })
client.partial_update_object("INDEX_NAME", "1", { name: "Updated" })
client.delete_object("INDEX_NAME", "1")
```

## `operation_index` (copy / move)

```ruby
# copy
client.operation_index("SOURCE",
  Algolia::Search::OperationIndexParams.new(operation: "copy", destination: "DEST"))

# move
client.operation_index("SOURCE",
  Algolia::Search::OperationIndexParams.new(operation: "move", destination: "DEST"))

# copy with scope
client.operation_index("SOURCE",
  Algolia::Search::OperationIndexParams.new(operation: "copy", destination: "DEST",
    scope: ["rules", "settings"]))

# check if index exists (new in v3)
client.index_exists("INDEX_NAME")
```

## Wait pattern

Bang methods (`save_objects!`, `delete_objects!`, etc.) are removed.

```ruby
# v2
index.save_objects(records).wait

# v3 — pass true as third arg to wait
client.save_objects("INDEX_NAME", records, true)

# or explicit helper
task = client.save_objects("INDEX_NAME", records)
client.wait_for_task("INDEX_NAME", task.task_id)

# new helpers
client.wait_for_app_task(task_id)
client.wait_for_api_key("my-api-key", "add")
client.wait_for_api_key("my-api-key", "update",
  Algolia::Search::ApiKey.new(acl: ["search", "browse"]))
```

## Helper method changes

- **`replace_all_objects`**: `safe` removed; scopes required as keyword args:
```ruby
client.replace_all_objects(index_name: "INDEX_NAME", objects: objects,
  scopes: ["settings", "rules", "synonyms"])
```
- **`save_objects`**: new `wait_for_tasks` and `batch_size` keyword args:
```ruby
client.save_objects("INDEX_NAME", objects, wait_for_tasks: false, batch_size: 1000)
```
- **`delete_objects`**: new `wait_for_tasks` and `batch_size` keyword args:
```ruby
client.delete_objects("INDEX_NAME", ["id1", "id2"], wait_for_tasks: false, batch_size: 1000)
```
- **`partial_update_objects`**: `create_if_not_exists` and `wait_for_tasks` params:
```ruby
client.partial_update_objects("INDEX_NAME", objects, true, true)
```
- **`browse_objects` / `browse_rules` / `browse_synonyms`**: block receives the full page response (not individual hits); use `response.hits`:
```ruby
# v2 — block received individual objects
index.browse_objects { |object| process(object) }

# v3 — block receives page response
client.browse_objects("INDEX_NAME") do |response|
  response.hits.each { |obj| process(obj) }
end
```
- **`generate_secured_api_key` / `get_secured_api_key_remaining_validity`**: available as both instance and class methods:
```ruby
key = client.generate_secured_api_key("parentApiKey", { validUntil: 1893456000 })
remaining = client.get_secured_api_key_remaining_validity(key)
```
- **`chunked_batch`** (new public helper):
```ruby
client.chunked_batch("INDEX_NAME", objects, Algolia::Search::Action::ADD_OBJECT, true)
```
- **`index_exists?`** (new helper alias)

## Cross-app copy (`AccountClient` removed)

```ruby
src = Algolia::SearchClient.create("SRC_APP_ID", "SRC_API_KEY")
dst = Algolia::SearchClient.create("DST_APP_ID", "DST_API_KEY")

settings = src.get_settings("SOURCE_INDEX")
dst.set_settings("DEST_INDEX", settings)

rules = []
src.browse_rules("SOURCE_INDEX") { |response| rules.concat(response.hits) }
dst.save_rules("DEST_INDEX", rules) unless rules.empty?

# repeat for synonyms, then browse_objects + replace_all_objects
```

## Method changes reference

| v2 | v3 |
|----|----|
| `client.multiple_queries()` | `client.search()` |
| `client.copy_index()` | `client.operation_index()` |
| `client.move_index()` | `client.operation_index()` |
| `client.copy_rules()` | `client.operation_index()` |
| `client.copy_synonyms()` | `client.operation_index()` |
| `client.copy_settings()` | `client.operation_index()` |
| `client.list_indexes` | `client.list_indices` |
| `client.get_top_user_id` | `client.get_top_user_ids` |
| `index.batch()` | `client.batch("INDEX_NAME", ...)` |
| `index.browse_objects()` | `client.browse_objects("INDEX_NAME", ...)` (aggregator block) |
| `index.browse_rules()` | `client.browse_rules("INDEX_NAME", ...)` |
| `index.browse_synonyms()` | `client.browse_synonyms("INDEX_NAME", ...)` |
| `index.clear_objects()` | `client.clear_objects("INDEX_NAME")` |
| `index.clear_rules()` | `client.clear_rules("INDEX_NAME")` |
| `index.clear_synonyms()` | `client.clear_synonyms("INDEX_NAME")` |
| `index.delete()` | `client.delete_index("INDEX_NAME")` |
| `index.delete_by()` | `client.delete_by("INDEX_NAME", ...)` |
| `index.delete_object()` | `client.delete_object("INDEX_NAME", id)` |
| `index.delete_objects()` | `client.delete_objects("INDEX_NAME", ids)` |
| `index.delete_rule()` | `client.delete_rule("INDEX_NAME", id)` |
| `index.delete_synonym()` | `client.delete_synonym("INDEX_NAME", id)` |
| `index.exists?` | `client.index_exists("INDEX_NAME")` |
| `index.get_object()` | `client.get_object("INDEX_NAME", id)` |
| `index.get_objects()` | `client.get_objects(...)` |
| `index.get_rule()` | `client.get_rule("INDEX_NAME", id)` |
| `index.get_settings()` | `client.get_settings("INDEX_NAME")` |
| `index.get_synonym()` | `client.get_synonym("INDEX_NAME", id)` |
| `index.get_task()` | `client.get_task("INDEX_NAME", task_id)` |
| `index.partial_update_object()` | `client.partial_update_object("INDEX_NAME", ...)` |
| `index.partial_update_objects()` | `client.partial_update_objects("INDEX_NAME", ...)` |
| `index.replace_all_objects()` | `client.replace_all_objects(index_name:, objects:, ...)` |
| `index.replace_all_rules()` | `client.save_rules("INDEX_NAME", rules)` |
| `index.replace_all_synonyms()` | `client.save_synonyms("INDEX_NAME", synonyms)` |
| `index.save_object()` | `client.save_object("INDEX_NAME", obj)` |
| `index.save_objects()` | `client.save_objects("INDEX_NAME", objs)` |
| `index.save_rule()` | `client.save_rule("INDEX_NAME", ...)` |
| `index.save_rules()` | `client.save_rules("INDEX_NAME", rules)` |
| `index.save_synonym()` | `client.save_synonym("INDEX_NAME", ...)` |
| `index.save_synonyms()` | `client.save_synonyms("INDEX_NAME", synonyms)` |
| `index.search()` | `client.search_single_index("INDEX_NAME", ...)` |
| `index.search_for_facet_values()` | `client.search_for_facet_values("INDEX_NAME", ...)` |
| `index.search_rules()` | `client.search_rules("INDEX_NAME", ...)` |
| `index.search_synonyms()` | `client.search_synonyms("INDEX_NAME", ...)` |
| `index.set_settings()` | `client.set_settings("INDEX_NAME", ...)` |
| `index.{op}.wait` | `client.wait_for_task("INDEX_NAME", task_id)` |

Recommend API renames:

| v2 | v3 |
|----|----|
| `recommend.get_frequently_bought_together()` | `recommend.get_recommendations()` |
| `recommend.get_related_products()` | `recommend.get_recommendations()` |
