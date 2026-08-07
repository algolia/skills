# Example Output: Ecommerce Variant Index Contract

Use this as a shape, not a fixed schema.

## Customer Goal

Help shoppers find the right shoe by brand, product name, color, size, gender, activity, price, and availability. Shoppers should usually see one product family, but filters must respect variant-level color, size, and availability.

## Recommended Variant Strategy

Use variant records with product grouping.

- One record per sellable variant because color, size, image, price, URL, and availability can differ.
- Include `product_id` so the UI can group variants into one product family when appropriate.
- Use `objectID = product_id::variant_id::locale`.
- Preserve both product-level and variant-level IDs for analytics and conversion attribution.

Tradeoff:

- Variant-level records make color, size, price, and availability filters accurate without frontend post-processing.
- The UI must group or de-duplicate variants when shoppers should see one product family.
- AI, personalization, analytics, and merchandising should preserve parent IDs so behavior can be reviewed above the SKU level.

## Sample Record

```json
{
  "objectID": "shoe-123::blue-9::en-US",
  "product_id": "shoe-123",
  "variant_id": "blue-9",
  "sku": "SHOE-123-BLU-9",
  "locale": "en-US",
  "title": "Trail Runner 2",
  "brand": "North Peak",
  "description": "Lightweight waterproof trail running shoe.",
  "category": ["Shoes", "Running", "Trail Running"],
  "gender": "Women",
  "activity": ["Running", "Hiking"],
  "color": "Blue",
  "size": "9",
  "price": 129.99,
  "price_band": "100-150",
  "in_stock": true,
  "stock_bucket": "high",
  "is_new": true,
  "first_available_at": 1751328000,
  "is_on_sale": false,
  "is_own_brand": true,
  "best_seller_bucket": "category_top",
  "sales_velocity_bucket": "high",
  "sales_30d_bucket": 4,
  "margin_band": 3,
  "rating_rounded": 4.6,
  "review_count_bucket": "100-499",
  "freshness_bucket": "new_30d",
  "image_url": "https://example.com/images/shoe-123-blue.jpg",
  "url": "https://example.com/products/trail-runner-2?color=blue&size=9"
}
```

## Merchandising Data Readiness

| Strategy | Field | Decision |
| --- | --- | --- |
| Product/variant merchandising | `product_id`, `variant_id`, `stock_bucket`, selected variant image/URL | Variants are indexed separately, then grouped in UI where appropriate. |
| New products | `first_available_at`, `is_new` | New means first available in the category within the agreed business window. Calculated before indexing. |
| On sale | `is_on_sale` | Source system owns the sale flag; Algolia rules should not infer sale status from copy or price text. |
| Own brand | `is_own_brand` | Boolean flag avoids brittle brand-name matching. |
| High inventory | `stock_bucket` | Use `low`, `normal`, `high`, `out_of_stock`; avoid exact stock counts unless required. |
| Best sellers | `best_seller_bucket`, `sales_velocity_bucket` | Bucketed upstream using category-specific sales window. |
| Margin | `margin_band` | Bucketed so private margin values are not exposed and tie-breaking stays interpretable. |
| Rating | `rating_rounded`, `review_count_bucket` | Rating is rounded; review volume prevents overvaluing thin review data. |

## Custom Ranking Metric Map

| Order | Field | Direction | Business meaning | Precision decision | Owner |
| --- | --- | --- | --- | --- | --- |
| 1 | `in_stock` | Desc | Available products should win ties over unavailable products. | Boolean | Inventory feed owner |
| 2 | `sales_30d_bucket` | Desc | Recent category sales velocity. | Bucketed 1-5 so margin can still break close ties. | Analytics pipeline |
| 3 | `margin_band` | Desc | Prefer higher-margin products when relevance and velocity are similar. | Bucketed, not exact margin. | Merchandising / finance |
| 4 | `freshness_bucket` | Desc | Give new products a controlled visibility lift. | Bucketed by category window. | Catalog owner |
| 5 | `rating_rounded` | Desc | Prefer better-rated products after stronger business metrics. | Rounded to one decimal. | Reviews platform |

## Initial Index Settings To Validate

- Searchable attributes: `title`, `brand`, `category`, `activity`, `description`, `sku`.
- Facets: `brand`, `category`, `gender`, `activity`, `color`, `size`, `price_band`, `in_stock`, `stock_bucket`, `is_on_sale`, `is_own_brand`.
- Custom ranking candidates: `desc(in_stock)`, `desc(sales_30d_bucket)`, `desc(margin_band)`, `desc(freshness_bucket)`, and `desc(rating_rounded)`. Validate exact order with representative queries and business owners.
- Replica candidates: price ascending, price descending, newest, rating if those experiences exist.

## Validation Queries

| Query or browse path | Expected behavior |
| --- | --- |
| `blue trail running shoes` | Blue trail shoes rank above generic running shoes. |
| `north peak runner` | North Peak products rank ahead of unrelated brands. |
| Filter `size:9` and `color:Blue` | Only products with an available blue size 9 variant appear. |
| Category `Trail Running` | Category results respect availability and ranking signals. |

## Customer Questions Still Needed

- Should unavailable variants disappear, sort lower, or remain visible with messaging?
- Should sale price, margin, rating, or inventory be stronger tie-breakers?
- What counts as "new", "high inventory", and "best seller" for this category?
- Should sales, margin, freshness, or rating be the stronger tie-breaker when products are textually similar?
- Are current sales, margin, and rating values too precise, and which should be bucketed before indexing?
- Who owns the upstream flags and buckets that power merchandising?
- Should analytics aggregate by product, variant, or both?
- Do region, currency, account, or permission rules change availability?
