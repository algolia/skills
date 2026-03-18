# Algolia MCP Skill — Evaluation Results

Evaluation performed on 2026-03-18 using Claude Opus 4.6 (1M context).

## Summary

The skill was evaluated across 5 realistic user scenarios, comparing **with-skill** (Claude reads the skill before responding) vs **without-skill** (Claude relies on general knowledge).

| Eval | With Skill | Without Skill | Delta |
|------|:----------:|:-------------:|:-----:|
| **Eval 1** — Search with filters | 100% (6/6) | 17% (1/6) | **+83%** |
| **Eval 2** — Analytics report | 100% (6/6) | 33% (2/6) | **+67%** |
| **Eval 3** — Recommendations | 100% (6/6) | 33% (2/6) | **+67%** |
| **Eval 4** — Multi-step investigation | 100% (6/6) | 17% (1/6) | **+83%** |
| **Eval 5** — Date filtering + pagination | 100% (6/6) | 33% (2/6) | **+67%** |
| **Average** | **100%** | **27%** | **+73%** |

## Eval Details

### Eval 1: Search with Filters

**Prompt:** *"I want to search my 'products' index for shoes under $100 in either red or blue. Show me only the name, price, and color fields. Also, what are the available facet values for the 'brand' attribute?"*

| Assertion | Without Skill | With Skill |
|-----------|:---:|:---:|
| Calls `algolia_search_list_indices` first | FAIL | PASS |
| Uses `facetFilters` with OR syntax `[["color:red", "color:blue"]]` | FAIL | PASS |
| Uses `numericFilters` with string syntax `["price < 100"]` | FAIL | PASS |
| Combines facetFilters AND numericFilters in same call | FAIL | PASS |
| Sets `attributesToRetrieve` to `["name", "price", "color"]` | PASS | PASS |
| Uses `algolia_search_for_facet_values` for brand | FAIL | PASS |

**Key finding:** Without the skill, Claude used a generic `algolia_search` tool with a combined `filters` string instead of the MCP-specific `facetFilters`/`numericFilters` array parameters. It also used `facets` parameter instead of the dedicated `algolia_search_for_facet_values` tool.

### Eval 2: Analytics Report

**Prompt:** *"Give me a search quality report for my 'ecommerce' index over the last 30 days — I want to know the no-results rate, top searches that have no clicks, and the click position distribution. Include click-through rates where possible."*

| Assertion | Without Skill | With Skill |
|-----------|:---:|:---:|
| Calls `algolia_search_list_indices` first | FAIL | PASS |
| Uses `algolia_analytics_no_results_rate` with correct dates | FAIL | PASS |
| Uses `algolia_analytics_top_searches_without_clicks` | FAIL | PASS |
| Uses `algolia_analytics_click_positions` | FAIL | PASS |
| Sets `clickAnalytics: true` on a supported tool | PASS | PASS |
| Does NOT use algolia-cli commands | PASS | PASS |

**Key finding:** The baseline fabricated all tool names using camelCase (`algolia_getNoResultsRate`, `algolia_getClickThroughRate`) instead of the actual snake_case MCP tool names (`algolia_analytics_no_results_rate`). It also skipped the discovery step entirely.

### Eval 3: Recommendations

**Prompt:** *"For product ID 'SKU-1234' in my 'catalog' index, show me frequently bought together items and related products. Also show me what's trending in the 'shoes' category. Use a balanced relevance threshold."*

| Assertion | Without Skill | With Skill |
|-----------|:---:|:---:|
| Calls `algolia_search_list_indices` first | FAIL | PASS |
| Uses `algolia_recommendations` with `bought-together` + objectID | FAIL | PASS |
| Uses `algolia_recommendations` with `related-products` + objectID | FAIL | PASS |
| Uses `trending-items` with `facetName`/`facetValue` | FAIL | PASS |
| Sets threshold to 60 (balanced default) | PASS | PASS |
| Does NOT pass objectID for trending-items | PASS | PASS |

**Key finding:** The baseline guessed the tool name as `algolia_get_recommendations` (wrong) and used threshold 50 instead of the documented balanced default of 60. It also used `facetFilters` instead of the dedicated `facetName`/`facetValue` parameters for trending-items.

### Eval 4: Multi-Step Investigation (harder)

**Prompt:** *"Our 'ecommerce' index has a no-results rate of 18%. I need to find the specific queries that are failing, then for the top 3 failing queries, actually run those searches to see what results come back. Also check if our click-through rates have been improving — compare the last 7 days vs the previous 7 days."*

| Assertion | Without Skill | With Skill |
|-----------|:---:|:---:|
| Calls `algolia_search_list_indices` first | FAIL | PASS |
| Uses `algolia_analytics_searches_no_results` | FAIL | PASS |
| Uses `algolia_search_index` to test failing queries | FAIL | PASS |
| Uses `algolia_analytics_top_searches` with `clickAnalytics: true` for BOTH date ranges | FAIL | PASS |
| Sets `clickAnalytics: true` on `algolia_analytics_top_searches` specifically | FAIL | PASS |
| Uses correct YYYY-MM-DD date format | PASS | PASS |

**Key finding:** The baseline invented a non-existent `algolia_getClickThroughRate` endpoint instead of using `algolia_analytics_top_searches` with `clickAnalytics: true`. The skill's Search Quality Audit workflow guided the correct multi-step approach. The with-skill run also accounted for the 1-4 hour data processing delay by ending date ranges at the previous day.

### Eval 5: Date Filtering + Pagination (harder)

**Prompt:** *"Search my 'events' index for all conferences happening after January 1st 2025. The date is stored as a Unix timestamp field called 'event_date'. Filter to only events in 'technology' or 'science' categories with a ticket price between $50 and $500. Show me page 3 with 20 results per page."*

| Assertion | Without Skill | With Skill |
|-----------|:---:|:---:|
| Calls `algolia_search_list_indices` first | FAIL | PASS |
| Uses numericFilters with Unix timestamp (1735689600) | FAIL | PASS |
| Uses facetFilters with OR syntax for categories | PASS | PASS |
| Uses numericFilters for price range | FAIL | PASS |
| Combines all filters in a single `algolia_search_index` call | FAIL | PASS |
| Sets page to 2 (0-indexed) and hitsPerPage to 20 | PASS | PASS |

**Key finding:** The baseline used the wrong tool name (`algolia_search`), guessed the field name as `ticket_price` instead of `price`, and used `>` instead of `>=` for the date filter. The skill's explicit Unix timestamp guidance and filter syntax examples prevented all these mistakes.

## What the Skill Adds

The biggest areas where the skill outperforms general knowledge:

1. **Correct MCP tool names** — Every baseline fabricated plausible but wrong tool names (camelCase vs snake_case, missing `analytics_` prefix, wrong base names)
2. **Discovery workflow** — `algolia_search_list_indices` as mandatory first step (every baseline skipped it)
3. **`clickAnalytics: true`** — Knowing this flag exists and which tools support it (`top_searches`, `top_search_results` only)
4. **Filter syntax** — `facetFilters` array-based OR/AND vs `numericFilters` string-based format
5. **Recommendation parameters** — Which models need `objectID` vs `facetName`/`facetValue`, and threshold guidance
6. **Multi-step workflows** — Search Quality Audit pattern: analytics → identify problems → search to diagnose

## Improvements Made

1. **Surfaced filter syntax** (facetFilters OR/AND, numericFilters strings) from reference into main SKILL.md
2. **Surfaced `clickAnalytics: true`** guidance with which tools support it
3. **Surfaced recommendation thresholds** (50/60/75) and model parameter requirements table
4. **Added analytics interpretation benchmarks** (no-results rate thresholds, click position patterns)
5. **Added Common Workflows** section (Search Quality Audit, Recommendation Setup Check)
6. **Added algolia-cli cross-reference** for write operations

## Reproducibility

- Model: Claude Opus 4.6 (1M context)
- Eval definitions: `evals/evals.json`
- Date: 2026-03-18
- Each eval was run once per configuration
