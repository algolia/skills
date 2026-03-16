# Analytics Reference

## Date parameters

- Format: `YYYY-MM-DD`
- Default period: last 8 days
- All dates are UTC
- Data processing delay: 1–4 hours for recent data; use date ranges ending at least 4 hours ago for complete data

## Enabling extended metrics

Set `clickAnalytics: true` on `algolia_analytics_top_searches` or `algolia_analytics_top_search_results` to include:
- Click-through rate (CTR)
- Conversion rate
- Click count
- Average click position

Set `revenueAnalytics: true` (on the same tools) to also include:
- Add-to-cart count and rate
- Purchase count and rate
- Revenue per currency

### 0% vs null rates

- **null** — no queries existed in the period; rates cannot be computed
- **0%** — queries existed but no click/conversion events were received

## Interpreting results

### No-result rate benchmarks

| Rate   | Assessment        |
|--------|-------------------|
| < 5%   | Excellent         |
| 5–10%  | Good              |
| 10–20% | Needs improvement |
| > 20%  | Poor              |

### Click position distribution

- **Healthy**: 30–40% of clicks at position 1, decreasing through position 10
- **Poor relevance**: even distribution across all positions
- **Ranking issues**: most clicks concentrated at positions 5–10

### Low CTR with high search volume

Indicates poor result relevance. Common causes: missing synonyms, content gaps, mismatched query intent.

## Limitations

- MCP analytics tools do not support filtering by analytics tags (tags are set in application search requests, not via MCP)
- Analytics tools require the ANALYTICS permission
- Long date ranges (> 3 months) may return slower
