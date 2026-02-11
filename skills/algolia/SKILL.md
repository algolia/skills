---
name: algolia
description: Search Algolia indices, retrieve analytics (top searches, no-result rates, click positions, user counts), and get product recommendations (bought-together, related, trending). Triggers on search, indexing, analytics, Algolia, recommendations.
license: MIT
metadata:
  author: algolia
  version: "1.0"
---

# Algolia Search & Analytics

## Connection setup

Use `/algolia:connect` to configure the MCP client with the Algolia MCP server.
For clients that don't support commands, see [connection-setup](references/connection-setup.md) for manual setup.

## Tool selection

### Search

| Task                   | Tool                              |
|------------------------|-----------------------------------|
| Search an index        | `algolia_search_index`            |
| List available indices | `algolia_search_list_indices`     |
| Explore facet values   | `algolia_search_for_facet_values` |

### Analytics

| Task                     | Tool                                            |
|--------------------------|-------------------------------------------------|
| Top searches             | `algolia_analytics_top_searches`                |
| Searches with no results | `algolia_analytics_searches_no_results`         |
| No-results rate          | `algolia_analytics_no_results_rate`             |
| Click positions          | `algolia_analytics_click_positions`             |
| No-click rate            | `algolia_analytics_no_click_rate`               |
| Searches without clicks  | `algolia_analytics_top_searches_without_clicks` |
| Search volume            | `algolia_analytics_number_of_searches`          |
| Top search results       | `algolia_analytics_top_search_results`          |
| Unique users             | `algolia_analytics_number_of_users`             |
| Top filters              | `algolia_analytics_top_filters`                 |
| Filters with no results  | `algolia_analytics_top_filters_no_results`      |
| Top countries            | `algolia_analytics_top_countries`               |

### Recommendations

| Task                       | Tool                      | `model` parameter  |
|----------------------------|---------------------------|--------------------|
| Frequently bought together | `algolia_recommendations` | `bought-together`  |
| Related products           | `algolia_recommendations` | `related-products` |
| Trending items             | `algolia_recommendations` | `trending-items`   |
| Trending facets            | `algolia_recommendations` | `trending-facets`  |
| Visually similar items     | `algolia_recommendations` | `looking-similar`  |

## Required workflow

1. **Discover first**: Always call `algolia_search_list_indices` before other tools to resolve `applicationId` and `indexName`. The `applicationId` parameter is an enum — select from the values in the tool schema, never guess.
2. **Index names are case-sensitive**: Use the exact name returned by `algolia_search_list_indices`.
3. **Date parameters**: Analytics tools accept `startDate` and `endDate` in `YYYY-MM-DD` format. Default period is the last 8 days.
4. **Permissions**: Not all tools are available to every user. Analytics tools require the Analytics permission; recommendations require the Recommend feature.

## Reference docs

- [connection-setup](references/connection-setup.md) — MCP server configuration and authentication
- [search](references/search.md) — Search parameters, filter syntax (`facetFilters`, `numericFilters`), pagination
- [analytics](references/analytics.md) — Analytics metrics interpretation, date ranges, click/conversion tracking
- [recommendations](references/recommendations.md) — Recommendation models, thresholds, facet-based filtering
- [troubleshooting](references/troubleshooting.md) — Common errors and resolution steps
