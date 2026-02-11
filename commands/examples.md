# Algolia Usage Examples

Interactive guide to common Algolia MCP usage patterns. Get copy-paste prompts and learn by example.

## Usage

Run the command to see all example categories:

```
/algolia:examples
```

Or jump to a specific category:

```
/algolia:examples search          # Search patterns and examples
/algolia:examples analytics       # Analytics usage patterns
/algolia:examples recommendations # Recommendations examples
```

## Quick Start Examples

### First-Time Setup

```
1. "List my Algolia indices"
   → See what indices you have access to

2. "Search products for laptop"
   → Basic text search

3. "What were the top searches yesterday?"
   → Check analytics

4. "Get products bought together with SKU-123"
   → Product recommendations
```

## Search Examples

### Basic Search

**Simple text search:**
```
"Search my products index for laptop"
```

**Specific attributes:**
```
"Search products for 'phone' and only return name, price, and image"
```

### Filtered Search

**Price filtering:**
```
"Find products containing 'shoes' priced under $100"
"Search for laptops between $500 and $1500"
```

**Category filtering:**
```
"Search products for 'phone' in electronics category"
"Find articles in the 'tutorial' category about Python"
```

**Multi-facet filtering:**
```
"Search products for 'running shoes' from Nike in size 10"
"Find laptops with 16GB RAM and SSD storage under $2000"
```

**Boolean combinations:**
```
"Search products for 'shoes' in (Nike OR Adidas) brand"
"Find products in electronics NOT in refurbished category"
```

### Pagination

**Specific page:**
```
"Show me page 3 of laptop search results"
```

**Custom page size:**
```
"Search products for 'tablet' and show 50 results per page"
```

**Browse through results:**
```
"Search products for 'phone' and show first 10 results"
[Then] "Show me the next 10 results"
```

### Advanced Search

**Date range:**
```
"Find articles published between January 1 and January 31, 2025"
```

**Availability filtering:**
```
"Find products for 'laptop' that are in stock and have quantity > 5"
```

**Rating-based search:**
```
"Search products for 'headphones' with rating above 4.5 stars"
```

### Index Exploration

**List indices:**
```
"What indices can I access?"
"List all my Algolia indices"
```

**Browse index:**
```
"Show me 20 random records from products index"
"Get first 100 products sorted by creation date"
```

## Analytics Examples

### Search Analytics

**Top searches:**
```
"What were the top 10 searches last week?"
"Show me the most popular queries in December 2024"
"Top searches for products index from January 1-15"
```

**No-result searches:**
```
"What searches returned no results yesterday?"
"Show me no-result queries from last month"
"Which product searches are failing?"
```

**No-result rate:**
```
"What's my no-result rate for last week?"
"Calculate no-result percentage for December"
"How many searches are failing in products index?"
```

### Click Analytics

**Click positions:**
```
"Where are users clicking in search results?"
"Show click distribution for last month"
"What positions get the most clicks?"
```

**Filter usage:**
```
"What filters do users click most?"
"Show me popular filter attributes from last week"
"Which facets are users using in products index?"
```

**Failed filters:**
```
"Which filter combinations are returning no results?"
"Show me filters that fail from last week"
```

### User Analytics

**User counts:**
```
"How many unique users searched yesterday?"
"Show me user count for last week"
"How many people used search in December?"
```

**Geographic distribution:**
```
"Where are my users searching from?"
"Show top 10 countries for search traffic last month"
```

### Time-Based Analytics

**Daily comparison:**
```
"Compare top searches between yesterday and today"
```

**Weekly trends:**
```
"Show me top searches for each day last week"
```

**Month-over-month:**
```
"Compare December 2024 analytics to January 2025"
```

### Combined Analytics Queries

**Complete picture:**
```
"For products index last week, show me:
1. Top 20 searches
2. No-result rate
3. Click position distribution
4. Number of unique users
5. Top 5 countries"
```

**Search quality analysis:**
```
"Analyze search quality for December:
- No-result rate
- Top 10 no-result queries
- Click distribution
- Popular filters"
```

## Recommendations Examples

### Frequently Bought Together

**Basic usage:**
```
"What products are frequently bought with SKU-12345?"
"Show items purchased together with laptop ABC"
```

**With threshold:**
```
"Get bought-together items for SKU-123 with relevance score above 70"
```

### Related Products

**Similar items:**
```
"Find products related to item XYZ"
"Show similar items to this laptop"
```

### Trending Items

**General trending:**
```
"Show trending products from last 7 days"
"What items are trending this week?"
```

**Category trending:**
```
"Show trending products in electronics category"
"What's trending in fashion from last 30 days?"
```

### Looking Similar

**Visual similarity:**
```
"Find products that look similar to item ABC"
"Show visually similar shoes to SKU-789"
```

### Advanced Recommendations

**Trending facets:**
```
"Show trending brands in the products index"
```

**Multiple models:**
```
"Show me bought-together items, related products, and trending items for SKU-456"
```
