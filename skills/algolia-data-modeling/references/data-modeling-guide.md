# Data Modeling Guide

## Contents

- [Index Contract](#index-contract)
- [Record Shape Heuristics](#record-shape-heuristics)
- [Ecommerce Record Model Decision](#ecommerce-record-model-decision)
- [Common Ecommerce Data Gaps](#common-ecommerce-data-gaps)
- [Merchandising Data Gap Readiness](#merchandising-data-gap-readiness)
- [Academy Coaching Questions](#academy-coaching-questions)
- [Minimum Data Sample Request](#minimum-data-sample-request)
- [Low-Dev Data Path](#low-dev-data-path)
- [ObjectID Decisions](#objectid-decisions)
- [Variant Modeling Patterns](#variant-modeling-patterns)
- [Variant Decision Prompt](#variant-decision-prompt)
- [Custom Ranking Metric Map](#custom-ranking-metric-map)
- [Concrete Record Templates](#concrete-record-templates)
- [Index And Replica Patterns](#index-and-replica-patterns)
- [Ingestion Guardrails](#ingestion-guardrails)
- [Source Notes](#source-notes)

## Index Contract

Define this before writing ingestion code:

- Index names for development, staging, production, and temporary rebuilds.
- Record entity and granularity.
- Stable `objectID` formula.
- Searchable attributes.
- Display attributes.
- Faceting/filtering attributes.
- Custom ranking attributes.
- Secured or hidden attributes.
- Replica and virtual replica strategy.
- Event attribution fields required by the frontend.
- Full reindex and incremental update ownership.

## Record Shape Heuristics

- Shape records around what a user expects to find and compare.
- Denormalize fields needed for search, filtering, ranking, display, and event context.
- Keep source-only relational details out of the record unless they affect search behavior.
- Normalize facet values before indexing; inconsistent casing, pluralization, or synonyms create poor filters.
- Include searchable synonyms or alternate names in records only when they represent content truth. Use synonyms/settings for query-language equivalence.
- Store image URLs, not image binaries.
- Compute ranking metrics during indexing when possible: popularity, margin band, availability score, freshness bucket, review score, conversion rate, or editorial priority.
- Round overly precise custom ranking metrics so later tie-breakers can still matter.

## Ecommerce Record Model Decision

Use this when a catalog has base products and variants such as color, size, style, region, channel, or price list. The first decision is what one Algolia record should represent. That decision affects search relevance, facets, merchandising, AI behavior, analytics, events, update cost, and frontend complexity.

| Model | One record represents | Best fit | Watchouts |
| --- | --- | --- | --- |
| Variant-level | One specific variation such as blue / size M / SKU | Precise variant matching, exact filters, variant pricing or stock, granular updates | More records, possible duplicate-looking results, requires grouping for product-family UI, AI and analytics may operate too narrowly unless parent IDs are preserved |
| Variation-group-level | One product variation group such as a color with nested sizes | Product/color merchandising, variant-aware images, cleaner results than SKU-level, better AI and analytics grouping than pure SKU-level | The grouping attribute must be chosen deliberately; updates may require resending the group record |
| Product-level / master product | One base product with all variants nested | One result per product, simpler merchandising, product-level AI/personalization/analytics, smaller record count | Facets and selected variant display can require frontend post-processing; partial variant updates are harder; filters can imply availability that only exists for one nested variant |

Decision rules:

- If users search or filter by variant attributes and expect exact matches, prefer variant-level or variation-group-level records.
- If merchandisers work at the product family level and AI, personalization, or analytics should learn at product level, prefer product-level or variation-group-level records.
- If color drives imagery and shopper intent, variation-group-level records often balance precision and manageability.
- If price, stock, image, permissions, or conversion attribution differ by SKU, preserve variant IDs even when the UI groups results.
- If product-level records contain nested variants, define how the frontend chooses the displayed image, price, URL, and availability after filters.

Output requirement:

- Name the chosen model, the grouping attribute if any, the parent ID, the event attribution IDs, and the expected UI behavior for search results, category pages, filters, and product detail handoff.

## Common Ecommerce Data Gaps

Use this section as an Academy-style diagnostic before recommending rules, boosts, replicas, or UI fixes. Many ecommerce ranking and merchandising failures are caused by missing fields rather than weak Algolia settings.

### Record Model Gap

Symptom:

- The team cannot say whether a result is a product, color group, size, SKU, regional offer, or account-specific offer.

Checks:

- Does the sample data show one row per SKU, one row per product, or a mixture?
- Can filters such as color plus size return only available matching variants?
- Can the UI display the correct image, price, URL, and stock state for the matched variant?
- Can events attribute clicks and conversions to the right product, variation group, or SKU?

Fix:

- Pick the record model first, then document the selected entity, parent ID, variant ID, grouping attribute, and analytics aggregation rule.

### Attribute Gap

Symptom:

- Merchandisers want to boost, bury, filter, or analyze product groups that the index cannot identify.

Checks:

- Newness: is there `published_at`, `first_available_at`, `launched_at`, `is_new`, or `newness_bucket`?
- Rating: is there a normalized customer rating or rating bucket?
- Sales and popularity: are there sales, views, click, add-to-cart, purchase, conversion-rate, or velocity fields?
- Margin: is margin exposed as a safe numeric value, band, or priority flag?
- Sale and campaign: are sale status, discount bands, campaign IDs, season, and collection explicit?
- Own brand: is brand ownership an explicit boolean or enum rather than inferred from a display name?

Fix:

- Add explicit merchandising attributes with allowed values and owners. Avoid inferring business concepts from product names, labels, or UI-only logic.

### Business Metric Gap

Symptom:

- Custom ranking uses raw fields, but business stakeholders disagree about why products rank the way they do.

Checks:

- Which metric should matter first when text relevance ties: sales, margin, rating, popularity, freshness, inventory, or editorial priority?
- Is the metric global, category-specific, query-specific, seasonal, or curated?
- What is the time window: 7 days, 30 days, season-to-date, all-time, or launch period?
- Should higher values rank first, or should lower values rank first?
- Are values safe to expose, or should the index use buckets such as `margin_band`?

Fix:

- Create a custom ranking metric map with field, business meaning, direction, source owner, refresh cadence, precision, and validation query.

### Precision And Tie-Breaking Gap

Symptom:

- The first custom ranking metric is so granular that later business metrics never affect ranking.

Checks:

- Do values such as rating, margin, sales, or popularity have many unique values?
- Does the business expect margin to matter after sales, or freshness to matter after rating?
- Would users perceive a difference between values such as 1,000 and 1,003 sales?

Fix:

- Reduce precision or bucket continuous metrics before indexing. Examples: `rating_rounded`, `sales_30d_bucket`, `margin_band`, `freshness_bucket`, `popularity_decile`, or `inventory_bucket`.
- Order custom ranking attributes from most important to least important business tie-breaker.
- Validate with representative queries where several records have similar textual relevance.

## Merchandising Data Gap Readiness

Before launching merchandising, check whether the data can support the business strategy. Most merchandising problems are not rule problems first; they are missing schema, timestamp, attribute, inventory, or sales-signal problems.

Use this as a coaching moment with business users: first define the merchandising strategy in business language, then confirm the index contains the attributes required to execute that strategy.

### Product Or Variant Schema

Choose whether merchandising happens at the product, variant, SKU, region, account, or grouped-variant level before indexing.

Check:

- What should one promoted hit represent: a product family, a color, a size, a SKU, a bundle, or a location-specific offer?
- Can a variant override the parent product's image, price, availability, sale status, or promotion status?
- If variants are indexed separately, is there a parent ID such as `product_id` for grouping and analytics?
- If products are indexed as one record, are variant values such as colors, sizes, price bands, and availability represented without misleading filters?

Common gap:

- Product and variant fields are mixed without a clear display rule, so a low-priority variant can override the main product, or filters imply availability that only exists for one variant.

Output requirement:

- State the selected product/variant strategy and the tradeoff for search pages, category pages, filters, merchandising, and events.

### New Products And Timestamps

Define "new" before indexing. Algolia can rank or filter by fields, but the business must decide what qualifies as new for each category.

Check:

- Is there a reliable source timestamp such as `published_at`, `first_available_at`, or `launched_at`?
- Are timestamps normalized to a consistent timezone and format before indexing?
- Does "new" mean the same thing across categories, or does apparel, electronics, content, and seasonal inventory each need a different window?
- Is there a precomputed field such as `is_new`, `newness_bucket`, or `days_since_launch_bucket` when business users need simple merchandising controls?

Common gap:

- Missing or incorrect dates cause old products to be promoted as new, or new products are not distinguishable because no attribute marks them as new.

Output requirement:

- Define the timestamp source, the business meaning of newness, the field that Algolia receives, and the owner who keeps it current.

### Promotion Attributes

Merchandising rules need explicit attributes. Do not rely on labels, names, or UI-only logic to infer promotion groups.

Check:

- Sale: `is_on_sale`, `sale_bucket`, `discount_percentage_bucket`, or campaign IDs.
- Own brand: `is_own_brand` or a normalized brand ownership flag, not only a brand name string.
- Category campaigns: `campaign_ids`, `season`, `collection`, `merchandising_priority`, or editorial flags.
- Exclusions: `is_clearance`, `is_restricted`, `is_discontinued`, or `is_hidden`.

Common gap:

- Products that should be promoted are not tagged, or products are misclassified because the source data has inconsistent brand, sale, or campaign fields.

Output requirement:

- List each merchandising group, the exact attribute that powers it, the allowed values, and the source owner.

### Inventory And Stock Buckets

Do not default to exact stock counts in Algolia. Exact counts can create noisy updates because every sale may require a reindex. Prefer business-useful buckets or booleans unless exact counts are truly needed.

Check:

- Is the product in stock, out of stock, preorder, backorder, low stock, or high inventory?
- What does "high inventory" mean for this category or business: units, days of supply, overstock status, location availability, or a manually maintained bucket?
- Should out-of-stock items be hidden, buried, shown with messaging, or excluded from promotions?
- How often does the inventory bucket need to refresh without overloading indexing?

Recommended fields:

- `in_stock`: boolean for basic availability.
- `stock_bucket`: values such as `out_of_stock`, `low`, `normal`, `high`.
- `high_inventory`: boolean only if the business has a clear definition.
- `availability_scope`: optional region/store/channel value when availability differs by context.

Common gap:

- Out-of-stock products get promoted because inventory is stale, missing, or too granular to maintain reliably.

Output requirement:

- Define the inventory bucket logic, refresh cadence, and what merchandising should do with each bucket.

### Best Sellers And Sales Signals

Define best sellers upstream. Algolia can use a ranking or filtering field, but the source data needs to decide what counts.

Check:

- Does "best selling" mean units sold, revenue, conversion rate, velocity, category rank, or a merchandising-selected group?
- Is the window fixed: 7 days, 30 days, season-to-date, category-specific, or all-time?
- Are values bucketed enough to avoid overfitting and noisy ranking changes?
- Are category-level best sellers computed within category, not globally, when category pages need local relevance?

Recommended fields:

- `best_seller_bucket`: values such as `none`, `category_top`, `site_top`, `seasonal_top`.
- `sales_velocity_bucket`: values such as `low`, `medium`, `high`.
- `category_sales_rank`: numeric rank only when maintained and meaningful.

Common gap:

- Missing or stale sales data promotes the wrong products, or a global best seller dominates unrelated categories.

Output requirement:

- Define the sales metric, time window, category scope, bucket values, and refresh owner.

### Margin, Rating, And Popularity Signals

Sales alone rarely captures the whole merchandising strategy. Decide how other metrics participate before indexing.

Check:

- Is margin used as a direct metric, a band, or a private editorial priority?
- Is customer rating trustworthy enough, and does it need a minimum review count or Bayesian average before ranking?
- Does popularity mean views, clicks, add-to-cart, purchases, conversion rate, or a blended score?
- Should these metrics be global or category-specific?
- Are values rounded or bucketed enough that downstream tie-breakers still matter?

Recommended fields:

- `margin_band`: numeric or enum such as `low`, `medium`, `high`.
- `rating_rounded`: normalized rating rounded to a useful precision.
- `review_count_bucket`: avoids overvaluing a perfect rating with too few reviews.
- `popularity_bucket` or `sales_velocity_bucket`: stable enough for ranking and merchandising.
- `editorial_priority`: curated business override when appropriate.

Common gap:

- A product with a tiny advantage in a raw metric always wins even though business users expected the next metric to break ties.

Output requirement:

- Define the metric order, precision, owner, refresh cadence, and validation query for each ranking input.

### Monitoring And Continuous Improvement

Data quality is not one-and-done. Build a review loop between data, engineering, merchandising, and customer-facing owners.

Track:

- Missing required merchandising attributes.
- Records with impossible or stale dates.
- Products with unclear product/variant ownership.
- Out-of-stock products appearing in promoted groups.
- Products marked as new or best seller outside the agreed definition.
- Record count, failed indexing jobs, last feed update, and major bucket distribution changes.

Output requirement:

- Include a data-gap report with owner, severity, affected merchandising strategy, and validation query or dashboard check.

### Impact Review

After gaps are fixed, review whether merchandising quality improved.

Measure:

- Product visibility for targeted groups.
- Click-through rate, conversion, add-to-cart, revenue, or support deflection where relevant.
- No-result and no-click queries.
- Promotion accuracy: promoted products match the intended category, stock, freshness, sale, brand, or best-seller definition.

Output requirement:

- Compare before/after examples and state which data fixes likely drove the change.

## Academy Coaching Questions

Use these questions to help nontechnical customers find data gaps before engineering starts:

- Product or variant: "When you promote this item, do you mean the whole product family, one color, one size, one SKU, or one regional offer?"
- Newness: "What exactly counts as new for this category, and which upstream field proves it?"
- Sale and own brand: "Which explicit attributes identify sale items and owned-brand items without relying on display names?"
- Inventory: "Do merchandisers need exact stock counts, or do they need useful buckets such as out of stock, low, normal, and high?"
- Best sellers: "Is best-selling based on units, revenue, velocity, conversion, category rank, or a curated list, and over what time window?"
- Ownership: "Who owns each flag or bucket, and how often does it refresh?"

If the answer is unclear, mark the implementation as provisional and produce a data-gap report before recommending indexing or merchandising rules.

## Minimum Data Sample Request

Before designing the final contract, ask for the smallest sample that exposes real complexity:

- 5 normal records users should find easily.
- 5 edge-case records: variants, unavailable items, restricted items, regional or account-specific items, localized content, stale content, or items with missing fields.
- Current field names from the source system.
- Fields shown in the UI today.
- Filters, sorts, and ranking signals the business expects.
- One or two examples of searches that should return each record.

If the customer cannot provide source records, create a provisional contract with clear placeholders and mark every assumption that must be validated before launch.

## Low-Dev Data Path

For teams without a full development team, separate data work into what can be prepared now and what needs implementation access:

- Customer can usually define searchable fields, display fields, filters, ranking intent, record examples, and owner decisions.
- Customer may be able to provide CSV exports, product feeds, CMS exports, screenshots, or API samples.
- Developer or platform owner is usually needed for automated indexing, stable objectID generation, incremental updates, secured filters, and production deployment.
- Do not let a temporary CSV shape become the long-term contract unless it includes stable IDs, variant strategy, and update ownership.

## ObjectID Decisions

Use a stable objectID that survives display-name, URL, and categorization changes. Prefer source IDs or deterministic composite IDs such as `productId::variantId::locale` when those dimensions produce distinct records.

Ask before choosing composite IDs:

- Does each variant need its own result, or should variants be grouped?
- Do locales or regions have materially different searchable text, availability, price, permissions, or events?
- Will events and analytics need to aggregate variants into products?

## Variant Modeling Patterns

Choose the variant shape before indexing. This decision affects relevance, filters, event attribution, analytics, and UI behavior.

### Product-As-Record

Use one record for the product family when:

- Users expect one result per product.
- Variants share most searchable text, categories, images, and ranking signals.
- Variant choice happens on the product detail page.
- Facets can safely represent aggregated variant values such as available colors or sizes.

Watchouts:

- Availability, price, and promotion data can become ambiguous.
- A filter such as `size:M` may show a product even if only one color has that size.
- Events may need product-level and selected-variant context.

### Variant-As-Record

Use one record per variant or SKU when:

- Users compare, filter, price, or convert at the variant level.
- Variants have distinct titles, images, prices, availability, stores, channels, or permissions.
- Merchandising needs to promote or bury specific variants.
- Events and analytics need variant-level attribution.

Watchouts:

- Results can look duplicated unless the UI groups or de-duplicates families.
- The index may grow quickly.
- Aggregated product analytics need a parent ID such as `product_id`.

### Grouped Variant Records

Use variant records plus grouping/distinct behavior when:

- Ranking and filtering need variant precision.
- The UI should usually show one product family.
- The selected variant should reflect the query or filters.

Include:

- Stable `objectID` per variant.
- Parent identifier such as `product_id`.
- Variant attributes such as color, size, material, region, channel, price, availability, image, and URL.
- Display fields for both parent product and selected variant.

### Variation-Group-Level Records

Use one record per shared variation, commonly color, when:

- Users often search by that variation.
- Images and merchandising should align to the variation.
- Product-level records are too broad for filters, but SKU-level records create too many duplicate-looking results.
- AI, analytics, and merchandising should operate above the individual SKU level.

Include:

- Stable `objectID` per variation group.
- Parent identifier such as `product_id`.
- Grouping attribute such as `color`.
- Nested variants for size, SKU, price, stock, or URL.
- Parent-level searchable text and group-level display fields.

Watchouts:

- Choose the grouping attribute carefully; color is common, but not universal.
- If the group contains nested SKUs, define how updates occur when one SKU changes price or availability.
- Events may need both group-level and SKU-level identifiers when conversion happens after size selection.

### Locale, Region, Channel, Account, And Permission Variants

Create separate records or indices when a dimension materially changes:

- Searchable text or language.
- Availability, currency, price list, or tax display.
- Compliance, permissions, or secured filters.
- Ranking signals or event streams.
- Operational ownership or deployment cadence.

Use filters when the same record can safely serve multiple contexts. Use separate records or indices when a single record would create confusing facets, unsafe access, or misleading analytics.

## Variant Decision Prompt

Ask:

1. What should one search result represent?
2. Which variant attributes can users search, filter, sort, compare, or buy?
3. Do price, availability, permissions, or images differ by variant?
4. Do events need product-level, variant-level, or both identifiers?
5. Should the UI show one family result or many variant results?
6. Which dimensions require separate records, filters, or indices?
7. If grouping variants, which shared attribute is the group key and why?
8. Should AI, personalization, analytics, and merchandising learn at product, variation group, or SKU level?

## Custom Ranking Metric Map

Before setting custom ranking, produce a metric map. Custom ranking should reflect business tie-breakers after textual relevance, not every available business number.

| Field | Meaning | Direction | Scope | Precision | Owner | Refresh | Validation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `sales_30d_bucket` | Recent sales velocity | Desc | Category-specific | Bucketed | Analytics / data pipeline | Daily | Similar products with higher recent velocity rank ahead |
| `margin_band` | Profitability group | Desc | Global or category | Bucketed | Merchandising / finance | Weekly or feed update | Higher-margin products break ties after sales |
| `freshness_bucket` | Newness window | Desc | Category-specific | Bucketed | Catalog / merchandising | Feed update | New products get visibility without overwhelming relevance |
| `rating_rounded` | Customer satisfaction | Desc | Global | Rounded | Reviews platform | Daily | Ratings affect ties only after enough review volume |

Design rules:

- Use numeric or boolean values for custom ranking fields.
- Decide the order deliberately; the first custom ranking field has the most influence when records tie on textual relevance.
- Reduce precision when two values are not meaningfully different to users or business stakeholders.
- Prefer category-specific metrics when category pages should not be dominated by global best sellers.
- Keep private or sensitive business values as bands, buckets, or priority fields instead of exposing exact values.
- Validate ranking with query sets that include likely ties, not only obvious winners.

## Concrete Record Templates

Use these as contract starters, not fixed schemas.

### Ecommerce Variant Record

Required decisions:

- `objectID`: `productId::variantId::locale` or equivalent stable composite.
- Parent ID: `product_id` for grouping and analytics aggregation.
- Variant fields: `variant_id`, `sku`, `color`, `size`, `material`, `image_url`, `variant_url`.
- Search fields: product title, brand, category, variant descriptors, searchable attributes.
- Filter fields: availability, price band, color, size, category, brand, locale, channel.
- Ranking fields: popularity, conversion rate, margin band, inventory score, freshness.
- Event fields: product ID and variant ID must both be available to the UI when conversion attribution needs both.

### B2B Account Pricing Record

Required decisions:

- Whether account-specific price and availability require separate records, secured filters, or separate indices.
- `account_id`, `price_list_id`, `contract_available`, and region/channel filters if exposed.
- Secured filters for account, role, region, or contract eligibility.
- ObjectID composite only when the same item has materially different searchable or purchasable state per account.

### Locale Or Region Record

Required decisions:

- Whether localized text, currency, compliance, inventory, or ranking differs enough to require separate records.
- ObjectID pattern such as `sourceId::locale::region` when distinct records are needed.
- Normalized locale and region filters.
- Localized searchable attributes and display fields.
- Event aggregation strategy across locales.

### Support Knowledge Base Article Record

Required decisions:

- One record per article, section, paragraph, or answer chunk.
- Stable source ID plus locale or version when content differs.
- Search fields: title, summary, body excerpt, product area, symptoms, error codes, audience.
- Filter fields: product, version, role, visibility, locale, content type.
- Ranking fields: freshness, helpfulness, support deflection, editorial priority.
- Events: article click, helpful/not helpful, case deflection, escalation, or completion.

## Index And Replica Patterns

- One primary index per searchable entity and environment is the default.
- Use replicas for explicit sort-by options such as price ascending, newest, or rating.
- Use virtual replicas for relevant sorting when the goal is to bias while retaining stronger textual relevance.
- Use separate indices when records, settings, access controls, languages, or operational ownership differ enough that one index becomes confusing.
- Avoid separate indices only because a frontend route is different; filters or rules may be enough for category/browse pages.

## Ingestion Guardrails

- Create settings as code where possible, not only by dashboard clicks.
- Use temporary indices for rebuilds and move/swap once complete when downtime or partial data would be harmful.
- Never run destructive production indexing from a local experiment without explicit confirmation.
- Track record counts, failed records, last updated timestamp, and index task completion.
- Include a sample record fixture in tests for every important entity type.

## Source Notes

- Algolia recommends records include only what helps search, display, sorting, and relevance, and that records can be denormalized rather than relational: https://www.algolia.com/doc/guides/sending-and-managing-data/prepare-your-data
- Searchable attributes should be deliberately selected because all attributes are searchable by default unless configured: https://www.algolia.com/doc/guides/managing-results/must-do/searchable-attributes
- Custom ranking attributes must be numeric or boolean and are used to break ranking ties after textual criteria: https://www.algolia.com/doc/guides/managing-results/must-do/custom-ranking
