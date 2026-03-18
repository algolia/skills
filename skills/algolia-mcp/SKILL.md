---
name: algolia-mcp
description: Search Algolia indices via the Algolia MCP server, retrieve analytics (top searches, no-result rates, click positions, user counts), and get product recommendations (bought-together, related, trending). Triggers on search, indexing, analytics, Algolia, recommendations, MCP.
license: MIT
metadata:
  author: algolia
  version: "1.0"
---

# Algolia Search & Analytics

## Connection setup

Use `/algolia-mcp:connect` to configure the MCP client with the Algolia MCP server.
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

## Search Filter Syntax

Filters go in the `algolia_search_index` call alongside `query`:

**facetFilters** (array-based):
```
[["color:red", "color:blue"]]              → OR (red OR blue)
[["brand:Nike"], ["category:running"]]     → AND (Nike AND running)
[["size:10"], ["color:red", "color:blue"]] → mixed (size 10 AND (red OR blue))
```
Each inner array is OR'd; outer arrays are AND'd.

**numericFilters** (string-based):
```
["price < 100"]                    → single condition
["price >= 50", "price <= 200"]    → range (AND'd)
```

**Date filtering**: Dates must be stored as Unix timestamps. Use `numericFilters: ["timestamp >= 1704067200"]`.

**Attribute selection**: Use `attributesToRetrieve: ["name", "price"]` to limit response size.

## Analytics Key Details

- **`clickAnalytics: true`**: Set this on `algolia_analytics_top_searches` or `algolia_analytics_top_search_results` to include CTR, conversion rate, and click count. Only these two tools support it.
- **`revenueAnalytics: true`**: Set on the same tools to also include add-to-cart rate, purchase rate, and revenue.
- **Data delay**: Recent data has a 1–4 hour processing delay. Use date ranges ending at least 4 hours ago for complete data.

### Interpreting Results

| No-results rate | Assessment |
|----------------|------------|
| < 5% | Excellent |
| 5–10% | Good |
| 10–20% | Needs improvement |
| > 20% | Poor |

**Click positions**: Healthy = 30–40% of clicks at position 1, decreasing through 10. Even distribution = poor relevance. Concentrated at positions 5–10 = ranking issues.

**Low CTR + high search volume** = poor result relevance. Common causes: missing synonyms, content gaps, mismatched query intent.

## Recommendation Thresholds

| Threshold | Behavior |
|-----------|----------|
| 50 | More results, lower relevance |
| **60** | **Balanced (good default)** |
| 75 | Fewer results, higher relevance |

**Model parameter requirements**:
- `bought-together`, `related-products`, `looking-similar` → require `objectID`
- `trending-items` → does NOT require `objectID`. Use `facetName` + `facetValue` to filter by category
- `trending-facets` → requires `facetName`

## Required Workflow

1. **Discover first**: Always call `algolia_search_list_indices` before other tools to resolve `applicationId` and `indexName`. The `applicationId` parameter is an enum — select from the values in the tool schema, never guess.
2. **Index names are case-sensitive**: Use the exact name returned by `algolia_search_list_indices`.
3. **Date parameters**: Analytics tools accept `startDate` and `endDate` in `YYYY-MM-DD` format. Default period is the last 8 days.
4. **Permissions**: Not all tools are available to every user. Analytics tools require the Analytics permission; recommendations require the Recommend feature.

## Common Workflows

### Search Quality Audit
1. `algolia_search_list_indices` → get applicationId and index name
2. `algolia_analytics_no_results_rate` → check overall health (< 5% is excellent)
3. `algolia_analytics_searches_no_results` → find the specific failing queries
4. `algolia_analytics_top_searches` with `clickAnalytics: true` → find high-volume queries with low CTR
5. `algolia_analytics_click_positions` → check if clicks are concentrated at position 1 (good) or spread evenly (poor relevance)
6. For each problematic query: `algolia_search_index` with that query to see what results look like

### Recommendation Setup Check
1. `algolia_search_list_indices` → resolve applicationId
2. Start with `trending-items` (requires least data) to verify Recommend is working
3. Then try `bought-together` or `related-products` with a known product objectID
4. If results are empty, check event volume requirements in [recommendations reference](references/recommendations.md)

## Reference Docs

- [connection-setup](references/connection-setup.md) — MCP server configuration and authentication
- [search](references/search.md) — Search parameters, filter syntax (`facetFilters`, `numericFilters`), pagination
- [analytics](references/analytics.md) — Analytics metrics interpretation, date ranges, click/conversion tracking
- [recommendations](references/recommendations.md) — Recommendation models, thresholds, facet-based filtering
- [troubleshooting](references/troubleshooting.md) — Common errors and resolution steps
