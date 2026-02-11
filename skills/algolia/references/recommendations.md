# Recommendations Reference

## Prerequisites

- Recommend feature enabled on Algolia plan
- SEARCH permission on the application
- Events tracking configured (views, clicks, conversions)
- Models train automatically within 24–48 hours of first events; updates daily after that

## Model parameter requirements

| Model              | `objectID` | `facetName` | `facetValue`                  |
|--------------------|------------|-------------|-------------------------------|
| `bought-together`  | Required   | —           | —                             |
| `related-products` | Required   | —           | —                             |
| `looking-similar`  | Required   | —           | —                             |
| `trending-items`   | —          | Optional    | Optional (requires facetName) |
| `trending-facets`  | —          | Required    | —                             |

All models require `applicationId`, `indexName`, `model`, and `threshold`.

## Threshold guidance

- `threshold: 50` — more results, lower relevance
- `threshold: 60` — balanced (good default)
- `threshold: 75` — fewer results, higher relevance

Range is 0–100. Higher values are stricter.

## Event volume requirements

**Minimum for basic recommendations:**
- 1,000+ events/month
- 100+ unique products with events
- 50+ unique users

**For high-quality recommendations:**
- 10,000+ events/month
- 500+ unique products
- 500+ unique users

`trending-items` requires the least data and is the best model to test first.
