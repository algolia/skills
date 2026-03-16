# Search Reference

## Discovery

Call `algolia_search_list_indices` first. The `applicationId` parameter is an enum listing accessible applications; the response returns exact index names for use in other tools.

## Filter syntax

### facetFilters (array-based)

```
facetFilters: [["category:shoes"]]                          // single facet
facetFilters: [["brand:Nike"], ["category:running"]]        // AND logic
facetFilters: [["color:red", "color:blue"]]                 // OR logic
facetFilters: [["size:10"], ["color:red", "color:blue"]]    // mixed AND/OR
```

Each inner array is OR'd; outer arrays are AND'd.

### numericFilters (string-based)

```
numericFilters: ["price < 100"]
numericFilters: ["price >= 50", "price <= 200"]   // range
numericFilters: ["rating > 4.5"]
numericFilters: ["quantity != 0"]
```

Multiple entries in the array are AND'd.

### Date filtering

Dates must be stored as Unix timestamps. Filter with `numericFilters`:

```
numericFilters: ["timestamp >= 1704067200", "timestamp <= 1706745599"]
```

## Pagination

- `page` is 0-indexed (page 0 = first page)
- Default `hitsPerPage`: 5, max: 1000
- Deep pagination (page > 100) degrades performance

## Attribute selection

- `attributesToRetrieve: ["name", "price"]` limits response size
- `["*"]` returns all attributes (default)
