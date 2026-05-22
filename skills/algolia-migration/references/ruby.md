# Upgrade the Ruby API client to version 3

> Keep your Ruby API client up to date to benefit from improvements and bug fixes.

The latest major version of the `algolia` gem is version 3.
This page helps you upgrade from version 2
and explains the breaking changes you need to address.

Algolia generates the version 3 clients from OpenAPI specifications,
which provides consistent behavior across all languages and up-to-date API coverage.
The main architectural change is the removal of the `init_index` pattern:
all methods are now on the `client` instance directly, with `index_name` as a parameter.

For the full list of changes, see the Ruby changelog.

## Update your dependencies

Update the `algolia` gem to version 3:

```sh
bundle add algolia --version '~> 3.0'
# or: gem install algolia -v '~> 3.0'
```

  The gem name stays `algolia`.
  Don't confuse it with the older `algoliasearch` gem, which installs version 1.

## Update imports

The module paths for API clients changed.
`Algolia::Search::Client` is now `Algolia::SearchClient`,
and all other clients follow the same flattened pattern.

```ruby
# version 2
require "algolia"
Algolia::Search::Client

# version 3
require "algolia"
Algolia::SearchClient
```

Version 3 includes dedicated client classes for each API:

```ruby
# Search API
Algolia::SearchClient
# Recommend API
Algolia::RecommendClient
# A/B testing API
Algolia::AbtestingClient
# Analytics API
Algolia::AnalyticsClient
# Ingestion API
Algolia::IngestionClient
# Insights API
Algolia::InsightsClient
# Monitoring API
Algolia::MonitoringClient
# Personalization API
Algolia::PersonalizationClient
# Query Suggestions API
Algolia::QuerySuggestionsClient
# Usage API
Algolia::UsageClient
```

## Update client initialization

Besides the class name change, client creation follows the same pattern.
The constructor still accepts your application ID and API key:

```ruby
# version 2
client = Algolia::Search::Client.create("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")

# version 3
client = Algolia::SearchClient.create("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")
```

The other major change concerns what follows initialization:
`init_index` no longer exists.

## Remove `init_index`

This is the most significant change when upgrading.
Version 2 relied on an index object with methods called on it.
In version 3, all methods belong to the `client` instance,
with `index_name` as a parameter.

```ruby
# version 2
client = Algolia::Search::Client.create("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")
index = client.init_index("INDEX_NAME")
index.search("QUERY")

# version 3
client = Algolia::SearchClient.create("ALGOLIA_APPLICATION_ID", "ALGOLIA_API_KEY")
client.search_single_index("INDEX_NAME", Algolia::Search::SearchParamsObject.new(query: "QUERY"))
```

  If you have many files to update,
  search your codebase for `init_index` or `.init_index(` to find every place that needs changing.

## Update search calls

### Search a single index

The `index.search` method is now `client.search_single_index`.
Pass the index name and search parameters as positional arguments:

```ruby
# version 2
index = client.init_index("INDEX_NAME")
results = index.search("QUERY", {
  facetFilters: ["category:Book"]
})

# version 3
results = client.search_single_index(
  "INDEX_NAME",
  Algolia::Search::SearchParamsObject.new(query: "QUERY", facet_filters: ["category:Book"])
)
```

### Search multiple indices

The `client.multiple_queries` method is now `client.search`.
Each request in the array requires an `index_name`:

```ruby
# version 2
results = client.multiple_queries([
  {indexName: "INDEX_1", query: "QUERY"},
  {indexName: "INDEX_2", query: "QUERY"}
])

# version 3
response = client.search(
  Algolia::Search::SearchMethodParams.new(
    requests: [
      Algolia::Search::SearchForHits.new(index_name: "INDEX_1", query: "QUERY"),
      Algolia::Search::SearchForHits.new(index_name: "INDEX_2", query: "QUERY")
    ]
  )
)
```

### Search for facet values

The `index.search_for_facet_values` method becomes `client.search_for_facet_values`
with an `index_name` parameter:

```ruby
# version 2
index = client.init_index("INDEX_NAME")
results = index.search_for_facet_values("category", "book")

# version 3
results = client.search_for_facet_values(
  "INDEX_NAME",
  "category",
  Algolia::Search::SearchForFacetValuesRequest.new(facet_query: "book")
)
```

## Update indexing operations

In version 3, indexing methods are on the client instead of the index object,
with `index_name` as a parameter.

### Add or replace records

```ruby
# version 2
index = client.init_index("INDEX_NAME")
index.save_object({objectID: "1", name: "Record"})
index.save_objects([{objectID: "1", name: "Record"}])

# version 3
client.save_object("INDEX_NAME", {objectID: "1", name: "Record"})
client.save_objects("INDEX_NAME", [{objectID: "1", name: "Record"}])
```

### Partially update records

```ruby
# version 2
index = client.init_index("INDEX_NAME")
index.partial_update_object({objectID: "1", name: "Updated"})

# version 3
client.partial_update_object("INDEX_NAME", "1", {name: "Updated"})
```

### Delete records

```ruby
# version 2
index = client.init_index("INDEX_NAME")
index.delete_object("1")

# version 3
client.delete_object("INDEX_NAME", "1")
```

## Update settings, synonyms, and rules

### Get and set settings

```ruby
# version 2
index = client.init_index("INDEX_NAME")
settings = index.get_settings
index.set_settings({searchableAttributes: ["title", "author"]})

# version 3
settings = client.get_settings("INDEX_NAME")
client.set_settings(
  "INDEX_NAME",
  Algolia::Search::IndexSettings.new(searchable_attributes: ["title", "author"])
)
```

### Save synonyms and rules

```ruby
# version 2
index = client.init_index("INDEX_NAME")
index.save_synonyms([{objectID: "1", type: "synonym", synonyms: ["car", "auto"]}])
index.save_rules([{objectID: "1", conditions: [{anchoring: "contains", pattern: "shoes"}], consequence: {params: {filters: "brand:nike"}}}])

# version 3
client.save_synonyms(
  "INDEX_NAME",
  [Algolia::Search::SynonymHit.new(algolia_object_id: "1", type: "synonym", synonyms: ["car", "auto"])]
)
client.save_rules(
  "INDEX_NAME",
  [Algolia::Search::Rule.new(
    algolia_object_id: "1",
    conditions: [Algolia::Search::Condition.new(pattern: "shoes", anchoring: "contains")],
    consequence: Algolia::Search::Consequence.new(
      params: Algolia::Search::ConsequenceParams.new(filters: "brand:nike")
    )
  )]
)
```

  In version 2, `index.replace_all_rules` and `index.replace_all_synonyms` replaced all rules or synonyms.
  In version 3, use `client.save_rules` or `client.save_synonyms` with `clear_existing_rules` or `replace_existing_synonyms` set to `true`.

## Update index management

The `copy_index`, `move_index`, `copy_rules`, `copy_synonyms`, and `copy_settings`
methods are all replaced by a single `operation_index` method.

### Copy an index

```ruby
# version 2
client.copy_index("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME")

# version 3
client.operation_index(
  "SOURCE_INDEX_NAME",
  Algolia::Search::OperationIndexParams.new(operation: "copy", destination: "DESTINATION_INDEX_NAME")
)
```

### Move (rename) an index

```ruby
# version 2
client.move_index("SOURCE_INDEX_NAME", "DESTINATION_INDEX_NAME")

# version 3
client.operation_index(
  "SOURCE_INDEX_NAME",
  Algolia::Search::OperationIndexParams.new(operation: "move", destination: "DESTINATION_INDEX_NAME")
)
```

### Copy only rules or settings

In version 3, use the `scope` parameter to limit the operation to specific data:

```ruby
# version 3 -- copy only rules and settings from one index to another
client.operation_index(
  "SOURCE_INDEX_NAME",
  Algolia::Search::OperationIndexParams.new(
    operation: "copy",
    destination: "DESTINATION_INDEX_NAME",
    scope: ["rules", "settings"]
  )
)
```

### Check if an index exists

In version 2, you could check if an index existed using the `exists?` method on the index object.
In version 3, use the `index_exists` helper method on the client:

```ruby
# version 2
index = client.init_index("INDEX_NAME")
index.exists?

# version 3
client.index_exists("INDEX_NAME")
```

## Update task handling

Version 2 supported chaining `.wait` on operations.
Version 3 replaces this pattern with dedicated wait helpers or the built-in `wait_for_tasks` parameter.

```ruby
# version 2
index = client.init_index("INDEX_NAME")
index.save_objects(records).wait

# version 3 -- the third argument (true) waits for tasks to complete
client.save_objects("INDEX_NAME", records, true)
```

Version 3 includes three wait helpers:

* `wait_for_task`: wait until indexing operations are done.
* `wait_for_app_task`: wait for application-level tasks.
* `wait_for_api_key`: wait for API key operations.

## Helper method changes

The following sections document breaking changes in helper method signatures and behavior between version 2 and version 3.

### Bang methods removed

All bang (`!`) variants of helper methods have been removed. In version 2, bang methods (`save_objects!`, `delete_objects!`, `partial_update_objects!`, `replace_all_objects!`) automatically waited for indexing tasks to complete. In version 3, pass `true` as the `wait_for_tasks` argument instead.

```ruby
# version 2
index.save_objects!(objects)
index.delete_objects!(["id1", "id2"])
index.partial_update_objects!(objects)
index.replace_all_objects!(objects)

# version 3
client.save_objects("INDEX_NAME", objects, true)
client.delete_objects("INDEX_NAME", ["id1", "id2"], true)
client.partial_update_objects("INDEX_NAME", objects, true, true) # create_if_not_exists, wait_for_tasks
client.replace_all_objects("INDEX_NAME", objects)
```

### `replace_all_objects`

The `safe:` option has been removed. In version 2, `safe: true` caused the helper to wait after each step. In version 3, the helper always waits—equivalent to the previous `safe: true` behavior.

The `scopes` parameter is now required and must be passed explicitly.

```ruby
# version 2
index.replace_all_objects(objects, safe: true)

# version 3
client.replace_all_objects(
  index_name: "INDEX_NAME",
  objects: objects,
  scopes: ["settings", "rules", "synonyms"]
)
```

### `save_objects` and `delete_objects`

Two new optional parameters are available in version 3: `wait_for_tasks` (default `false`) and `batch_size` (default `1,000`). In version 2, you had to call the bang variants to wait for tasks.

```ruby
# version 2
index.save_objects(objects)
index.delete_objects(["id1", "id2"])

# version 3
client.save_objects("INDEX_NAME", objects, wait_for_tasks: false, batch_size: 1000)
client.delete_objects("INDEX_NAME", ["id1", "id2"], wait_for_tasks: false, batch_size: 1000)
```

### `browse_objects`, `browse_rules`, `browse_synonyms`

These helpers moved from the index object to the client and now accept `index_name` as an explicit first argument. The block receives the full page response—use `response.hits` to access the objects for that page.

```ruby
# version 2
index.browse_objects do |object|
  process(object)
end

# version 3
client.browse_objects("INDEX_NAME") do |response|
  response.hits.each { |obj| process(obj) }
end
```

### `generate_secured_api_key` and `get_secured_api_key_remaining_validity`

Both methods were class methods in version 2. In version 3, they are available both as instance methods on the client and as class methods on `Algolia::Search::SearchClient`.

```ruby
# version 2
key = Algolia::SearchClient.generate_secured_api_key("parentApiKey", { validUntil: 1893456000 })
remaining = Algolia::SearchClient.get_secured_api_key_remaining_validity(key)

# version 3
key = client.generate_secured_api_key("parentApiKey", { validUntil: 1893456000 })
remaining = client.get_secured_api_key_remaining_validity(key)

# Class method still works too:
key = Algolia::Search::SearchClient.generate_secured_api_key("parentApiKey", { validUntil: 1893456000 })
```

### `wait_for_task`

The helper was renamed from `wait_task` and moved from the index object to the client. The `index_name` parameter is now required as an explicit argument.

```ruby
# version 2
index.wait_task(task_id)

# version 3
client.wait_for_task("INDEX_NAME", task_id)
```

### `wait_for_api_key`

In version 2, waiting for API key operations was done by calling `.wait` on the response object returned by `add_api_key`, `update_api_key`, or `delete_api_key`. Version 3 provides a standalone `wait_for_api_key` helper.

```ruby
# version 2
response = client.add_api_key(["search"])
response.wait

# version 3
client.add_api_key(acl: ["search"])
client.wait_for_api_key("my-api-key", "add")

# Wait for an update (pass the expected final state):
client.wait_for_api_key("my-api-key", "update",
  Search::ApiKey.new(acl: ["search", "browse"])
)
```

### `wait_for_app_task` and `chunked_batch`

These are new helpers in version 3 with no equivalent in version 2.

```ruby
# Wait for an application-level task:
client.wait_for_app_task(task_id)

# Batch objects in chunks with a chosen action:
client.chunked_batch("INDEX_NAME", objects, Action::ADD_OBJECT, true)
```

### `index_exists?`

This is a new helper in version 3.

```ruby
# version 2
# No equivalent — had to rescue NotFoundException from get_settings

# version 3
exists = client.index_exists?("INDEX_NAME")
```

### `copy_index_between_applications`

In version 2, the separate `Algolia::AccountClient` class provided a `copy_index` method for copying an index between two different Algolia applications. It accepted two index objects, each belonging to a different client.

In version 3, `AccountClient` is removed. You can compose existing helpers across two clients to achieve the same result.

```ruby
# version 2
account_client = Algolia::AccountClient.new
account_client.copy_index(src_index, dest_index)

# version 3
src = Algolia::Search::Client.create("SRC_APP_ID", "SRC_API_KEY")
dst = Algolia::Search::Client.create("DST_APP_ID", "DST_API_KEY")

# Copy settings
settings = src.get_settings("SOURCE_INDEX")
dst.set_settings("DEST_INDEX", settings)

# Copy rules
rules = []
src.browse_rules("SOURCE_INDEX") { |response| rules.concat(response.hits) }
dst.save_rules("DEST_INDEX", rules) unless rules.empty?

# Copy synonyms
synonyms = []
src.browse_synonyms("SOURCE_INDEX") { |response| synonyms.concat(response.hits) }
dst.save_synonyms("DEST_INDEX", synonyms) unless synonyms.empty?

# Copy objects
objects = []
src.browse_objects("SOURCE_INDEX") { |response| objects.concat(response.hits) }
dst.replace_all_objects("DEST_INDEX", objects)
```

## Method changes reference

The following tables list all method names that changed between version 2 and version 3.

  A few methods were also renamed:
  `list_indexes` is now `list_indices`,
  and `get_top_user_id` is now `get_top_user_ids`.

### Search API client

| Version 2 (legacy)                              |   | Version 3 (current)                             |
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
| `client.get_top_user_id`                        | → | `client.get_top_user_ids`                       |
| `client.list_api_keys`                          | → | `client.list_api_keys`                          |
| `client.list_indexes`                           | → | `client.list_indices`                           |
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
| `index.exists?`                                 | → | `client.index_exists`                           |
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

| Version 2 (legacy)                      |   | Version 3 (current)          |
| --------------------------------------- | - | ---------------------------- |
| `client.get_frequently_bought_together` | → | `client.get_recommendations` |
| `client.get_recommendations`            | → | `client.get_recommendations` |
| `client.get_related_products`           | → | `client.get_recommendations` |
