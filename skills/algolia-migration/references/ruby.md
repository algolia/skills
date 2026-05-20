# Ruby: v2 → v3

## Install

```sh
bundle add algolia --version='~>3.0'
```

> The gem name is `algolia`. Do not confuse with the older `algoliasearch` gem (v2).

## Require / module changes

```ruby
# v2
require "algolia"
Algolia::Search::Client

# v3 — module hierarchy flattened
require "algolia"
Algolia::SearchClient
```

v3 ships dedicated clients: `SearchClient`, `RecommendClient`, `AbtestingClient`, `AnalyticsClient`, `IngestionClient`, `InsightsClient`, `MonitoringClient`, `PersonalizationClient`, `QuerySuggestionsClient`, `UsageClient`.

## `init_index` removal

```ruby
# v2
client = Algolia::Search::Client.create("APP_ID", "API_KEY")
index  = client.init_index("INDEX_NAME")
index.search("QUERY")

# v3
client = Algolia::SearchClient.create("APP_ID", "API_KEY")
client.search_single_index(
  "INDEX_NAME",
  Algolia::Search::SearchParamsObject.new(query: "QUERY")
)
```

## Method renames

| v2 | v3 |
|----|----|
| `index.search` | `client.search_single_index` |
| `client.multiple_queries` | `client.search` |
| `index.search_for_facet_values` | `client.search_for_facet_values` |
| `index.save_object` | `client.save_object("INDEX_NAME", obj)` |
| `index.partial_update_object` | `client.partial_update_object("INDEX_NAME", id, update)` |
| `index.delete_object` | `client.delete_object("INDEX_NAME", id)` |
| `index.get_settings` | `client.get_settings("INDEX_NAME")` |
| `index.set_settings` | `client.set_settings("INDEX_NAME", settings)` |
| `index.replace_all_rules` | `client.save_rules(..., clear_existing_rules: true)` |
| `index.replace_all_synonyms` | `client.save_synonyms(..., replace_existing_synonyms: true)` |
| `copy_index` / `move_index` / `copy_rules` / etc. | `client.operation_index` |
| `index.exists?` | `client.index_exists` |
| `list_indexes` | `list_indices` |
| `get_top_user_id` | `get_top_user_ids` |

## Indexing

```ruby
client.save_object("INDEX_NAME", { objectID: "1", name: "Record" })

client.partial_update_object("INDEX_NAME", "1", { name: "Updated" })

client.delete_object("INDEX_NAME", "1")
```

## `operation_index` (copy / move)

```ruby
client.operation_index(
  "SOURCE",
  Algolia::Search::OperationIndexParams.new(operation: "copy", destination: "DEST")
)
```

## Wait pattern

Bang methods (`save_objects!`, `delete_objects!`, etc.) are removed.

```ruby
# v2
index.save_objects!(objects)

# v3 — pass wait_for_tasks: true (third positional argument)
client.save_objects("INDEX_NAME", objects, true)

# Or use explicit helper
task = client.save_objects("INDEX_NAME", objects)
client.wait_for_task("INDEX_NAME", task.task_id)
```

Three helpers: `wait_for_task`, `wait_for_app_task`, `wait_for_api_key`.

## `replace_all_objects`

```ruby
# v3 — safe removed; scopes positional arg (not keyword)
# Default scopes already include settings, rules, synonyms — pass all four positional args to override:
client.replace_all_objects("INDEX_NAME", objects, 1000, ["settings", "rules", "synonyms"])

# Or rely on defaults:
client.replace_all_objects("INDEX_NAME", objects)
```

## Browse

```ruby
# v3 — aggregator receives the full page response
client.browse_objects("INDEX_NAME") do |response|
  response.hits.each { |hit| process(hit) }
end
```

## Secured API key

`generate_secured_api_key` and `get_secured_api_key_remaining_validity` are available as both instance and class methods in v3.

## `AccountClient` removed

Cross-app index copying now requires composing helpers across two client instances.
