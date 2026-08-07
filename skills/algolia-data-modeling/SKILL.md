---
name: algolia-data-modeling
description: >
  Algolia data modeling and indexing guidance. Use before or alongside indexing records or building Algolia search UI for net-new search, browse, autocomplete, ecommerce, personalization, Dynamic Re-Ranking, recommendations, or analytics-aware implementations. Makes record shape, objectID, display fields, facets, ranking fields, and event attribution explicit decisions. Use for records, variants, SKUs, indices, replicas, searchable and faceting attributes, denormalization, merchandising fields, timestamps, inventory, event attribution, indexing pipelines, partial updates, secured data, multi-language or multi-region strategies, and migrations. Do NOT use for live imports, exports, record mutations, settings changes, or account actions; use algolia-cli or algolia-mcp. Do NOT use for frontend UI implementation; use algolia-instantsearch-ui, algolia-autocomplete, algolia-ui-libraries, or the official instantsearch skill.
license: MIT
metadata:
  author: algolia
  version: "0.5"
---

# Algolia Data Modeling

Use this skill to shape the data before code writes records to Algolia. Good relevance usually starts with records that match the user journey, not the source database schema.

## Customer-Facing Standard

- Ask for sample records and edge cases before making record-shape claims.
- State assumptions plainly when source data is missing.
- Use public `academy.algolia.com` for learning alignment and public `algolia.com/doc` for current implementation guidance when source-backed context is needed.
- When an Academy metadata reference pack is available, use only its `title`, `url`, `course`, `module`, `learning_objectives`, and `updated_at` fields for structure. If it is stale or no match exists, fall back to live Academy/docs lookup. Do not treat cached metadata as course content or implementation authority.
- Do not require custom Academy/docs access; use customer-provided sources only as optional context.
- When live Algolia data, analytics, index inspection, settings changes, or account actions are needed, use Algolia MCP, the Algolia CLI, or official Algolia skills for the live operation, then apply this skill to interpret results and validate the customer-ready implementation path.
- Produce an indexing contract, validation queries, owner handoff, and reindex/update path.
- For ecommerce catalogs, explicitly choose between variant-level, variation-group-level, and product-level record models before discussing merchandising or UI behavior.

## Official Companion Skills

- Use official `algolia-mcp` or `algolia-cli` when live sample records, existing index shape, object counts, imports, or exports need to be inspected.
- Use this skill after the official tool call to turn findings into a customer-facing indexing contract, variant strategy, and validation plan.

## Source-Of-Truth Rules

- Do not infer a final record model from database tables alone. Require sample records, UI expectations, event needs, and update ownership.
- Do not prescribe exact Algolia settings, API commands, or migration steps without routing live operations through official `algolia-cli`, `algolia-mcp`, or current docs.
- Treat any schema without stable IDs, variant ownership, timestamp ownership, inventory strategy, and event identifiers as provisional.
- Before indexing records or starting UI implementation, create or update an index contract when practical. If the user needs a quick prototype, proceed with a minimal provisional contract and list the assumptions to revisit.
- Do not treat merchandising rules as a substitute for missing merchandising data. Newness, sale status, brand ownership, inventory, best-seller status, margin, and popularity must be explicit fields or documented upstream computations.

## Index Contract Decision Point

Before indexing or UI work, create `algolia/index-contract.md` or an equivalent artifact when practical. If you proceed without a complete contract, call out which decisions are provisional:

- Index names.
- Record model: variant-level, variation-group-level, product-level, or non-commerce equivalent.
- Record granularity.
- `objectID` strategy.
- Searchable attributes.
- Displayed attributes.
- Faceting attributes.
- Ranking signals.
- Ranking metric grain, order, direction, precision, and bucket logic.
- Merchandising fields.
- Inventory fields.
- Event attribution fields.
- Update owner and cadence.
- Validation queries.

For demos and prototypes, produce a one-paragraph data contract, three validation queries, and explicit deferred production concerns.

## Workflow

1. Read `references/data-modeling-guide.md` before making data-shape decisions.
2. Read `references/example-output.md` when producing a customer-facing indexing contract or showing what good output looks like.
3. Ask for context if record granularity, business goal, or filtering requirements are unknown.
4. Design the index contract first: index names, environments, objectID strategy, record shape, searchable attributes, faceting attributes, ranking signals, and update ownership.
5. Choose the variant strategy before writing code: product record, variant record, grouped variants, or separate records by locale, region, tenant, channel, price list, or permission set.
6. Run a merchandising data-gap check before indexing: schema clarity, timestamps/newness, promo attributes, inventory buckets, best-seller buckets, margin/popularity metrics, metric precision, and upstream ownership.
7. Prefer denormalized, search-ready records. Avoid forcing the UI to join or infer critical ranking/filtering fields at query time.
8. Design custom ranking inputs as business tie-breakers, not raw database dumps. Decide which metrics matter first, whether higher or lower is better, and whether values should be rounded or bucketed so later ranking attributes can still influence ties.
9. Include a migration and reindexing plan when changing objectIDs, record granularity, or settings that affect relevance.
10. Teach business users that many merchandising issues are data readiness issues first. Rules and boosts cannot reliably promote new, sale, own-brand, high-inventory, high-margin, popular, or best-selling products if those concepts are not represented in the indexed records.

## Questions To Ask

Ask the smallest useful subset:

- Can you share 5 normal records and 5 edge cases, including variants, unavailable items, restricted content, regional differences, or records that often search poorly?
- What entity should a search result represent: product, variant, SKU, article, location, account, or another unit?
- Should variants appear as separate hits, one hit per product, one hit per shared variation such as color, grouped choices inside one hit, or filtered silently by availability, channel, region, account, or permissions?
- What attributes must users search, filter, sort, display, or use for ranking?
- Which attributes must merchandising use to promote or suppress products: new, rating, sales, popularity, margin, on sale, own brand, high inventory, best seller, seasonal, campaign, or editorial priority?
- How does the business define "new", "high inventory", and "best selling" per category, and where are those buckets calculated before indexing?
- Which custom ranking metrics should act first, second, and third when text relevance ties: sales, margin, rating, popularity, freshness, inventory, or editorial priority?
- Are ranking metrics too precise for useful tie-breaking, and should they be rounded or bucketed such as `sales_30d_bucket`, `margin_band`, or `freshness_bucket`?
- Which attributes are stable identifiers versus volatile display or ranking fields?
- What records should be hidden, delayed, or secured by user/account/region/channel?
- How often do records change, and which system owns those changes?
- Does the same content need separate indices for locales, regions, tenants, environments, or user segments?

## Implementation Standards

- Treat `objectID` as a stable contract. Do not derive it from mutable display fields.
- Make variant modeling explicit. Do not accidentally index one source row per SKU if users expect one product result, and do not collapse variants if color, size, availability, price, region, or permissions materially change search behavior.
- Keep record size intentional: include fields needed for retrieval, ranking, faceting, display, analytics context, and event attribution.
- Separate production, staging, and development indices. Do not test destructive indexing against production.
- Use replicas for alternate sort orders and virtual replicas for relevant sorting when appropriate.
- Preserve queryID/objectID/position compatibility for events when shaping UI responses.
- Do not require exact stock counts in Algolia for merchandising unless there is a clear operational reason. Prefer stable buckets or booleans such as `in_stock`, `stock_bucket`, or `high_inventory` so every sale does not force unnecessary reindexing.
- Calculate category-specific freshness, high-inventory, sale, own-brand, and best-seller flags upstream before indexing. Do not expect Algolia rules to infer missing business definitions from incomplete records.
- Explain continuous values versus buckets. Exact sales, margin, inventory, or timestamp values can be useful, but buckets often make merchandising and custom ranking easier to reason about and less noisy.
- Treat custom ranking as ordered tie-breaking after textual relevance. If the first ranking metric is highly precise, later metrics may rarely matter; reduce precision or bucket values when the business expects a second or third metric to participate.
- For ecommerce, preserve the difference between product identity, variation identity, and SKU identity. Use parent IDs and selected-variant fields when the UI must show one family result while events or filters still need variant-level truth.

## Anti-Patterns

- Indexing one row per SKU by default when the shopper expects one product family.
- Collapsing variants when availability, price, permissions, color, size, or event attribution must differ by variant.
- Using exact inventory counts as a merchandising input when buckets would satisfy the business need with fewer updates.
- Promoting "new" products without a reliable timestamp or explicit newness attribute.
- Promoting "best sellers" without a defined time window, category scope, and refresh owner.
- Ranking by raw sales, margin, rating, or popularity without deciding the business order, direction, time window, category scope, and precision.
- Using a highly precise first custom ranking metric that prevents later business metrics from resolving ties.
- Adding display-only or internal fields to searchable text because they are convenient in the source system.
- Designing events after the record contract, causing `objectID`, `index`, `queryID`, or variant aggregation problems later.

## Pre-Indexing Checkpoints

Before indexing records, state whether these items are ready, provisional, or deferred:

- `objectID` stability.
- Facets used by the UI and their normalization.
- Ranking fields and why they matter.
- Ranking metric precision: raw, rounded, bucketed, or curated.
- Retrievable display fields.
- Image, URL, title, price, availability, or other UI-required fields.
- Event attribution fields.
- Inventory, availability, or permissions fields needed by the UI.
- Update owner and cadence for volatile fields.

## Ecommerce Record Model Strategy

Choose one of these patterns and state the tradeoff:

- Variant-level records: one record represents a specific sellable variation such as a color/size SKU. Use when users search, filter, compare, price, or convert at the variant level; when color/size/availability/image must be exact; or when granular updates matter. Plan grouping or distinct behavior if the UI should show product families.
- Variation-group-level records: one record groups variants that share a key attribute such as color. Use when the UI and merchandising usually operate at a product/color level, but filters and images still need more precision than a master product record.
- Product-level or master-product records: one record represents the base product and contains all variants. Use when merchandising, analytics, and AI behavior should operate at product level and users expect one product result. Document any frontend work needed to show the right variant after filters.
- Locale, region, channel, or account variants: split into separate records or indices when text, price, availability, permissions, or events differ enough to change search behavior.
- Secured variants: never rely on UI hiding alone. Permission-sensitive variants need secured filters, separate indices, or record-level access strategy.

For each model, state the impact on textual relevance, faceting accuracy, merchandising control, AI/personalization behavior, analytics aggregation, update cost, record count, and UI complexity.

## Academy And Customer Education Alignment

When source-backed guidance is needed, search public Academy sources for indexing and data-readiness learning objectives and public Algolia docs for records, objectID, facets, replicas, and current implementation details. Map the customer to beginner implementation, production readiness, optimization, or AI readiness. Use source context to guide decisions and questions; do not paste long course or docs excerpts.

## Maturity Behavior

- Beginner implementation: produce the simplest correct record contract and ask only for sample records, source owner, objectID candidates, required filters, and primary ranking goals.
- Production readiness: add environment naming, update ownership, secured fields, rollback/reindex plan, and validation queries.
- Optimization: add ranking signals, query analytics, replica strategy, and controlled relevance tests.
- AI readiness: validate semantic fields, event attribution fields, permissions, noisy attributes, and whether NeuralSearch or Agent Studio prerequisites are met.

## Deliverables

For design work, return a concise index contract with sample records, record model strategy, merchandising data-gap report, custom ranking metric map, and validation queries. For code work, implement the contract and include the reindex/update path plus validation commands or tests.
