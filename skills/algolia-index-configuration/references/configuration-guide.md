# Configuration Guide

## Settings Change Workflow

1. Export or record current settings.
2. Identify the business reason for the change.
3. Make the smallest coherent setting change.
4. Test representative query sets before and after.
5. Decide whether an A/B test is needed.
6. Commit settings as code or document the dashboard change.

## What Good Looks Like

For any meaningful relevance change, produce:

- The current settings snapshot or location of the backup.
- The proposed settings diff.
- 10 representative queries or category pages.
- Expected top results for the most important queries.
- Facets and filters that must still work after the change.
- No-result or low-result behavior to verify.
- A rollback step if the change hurts relevance.

## Relevance Control Map

Classify the desired behavior before choosing a setting. This prevents a preference from becoming an accidental hard constraint, or a campaign override from becoming permanent ranking logic.

| Need | Primary control | Validate |
| --- | --- | --- |
| Must never return | Filters or secured filters | Restricted, region, availability, and permission scenarios never leak. |
| Should appear earlier but can still return later | Optional filters or documented ranking preference | Preferred records rise without hiding acceptable alternatives. |
| Should match first | Ordered searchable attributes and textual relevance settings | Exact, brand, title, and identifier query classes. |
| Should break textual ties | Custom ranking | Business signals only decide between otherwise comparable results. |
| Should change for a bounded intent or period | Rule or merchandising configuration | Condition, owner, expiry/review date, and affected queries. |
| Needs an explicit customer sort | Standard or virtual replica where current docs support it | Sort label, tradeoff, filters, and facet behavior stay honest. |

## Settings Decision Record

For every material change, record the customer outcome, current evidence, selected setting and rejected alternatives, hard constraints versus optional preferences, expected wins and regressions, test queries, owner, rollback action, and experiment need.

## Searchable Attributes

- Include attributes users actually search: names, titles, descriptions, brands, categories, tags, identifiers.
- Exclude display-only URLs, ranking-only metrics, internal flags, and noisy long fields unless the use case requires them.
- Order attributes by importance. Attributes on the same priority level can be listed together.
- Separate display title from searchable alternate titles when needed.

### Exact And Typo-Sensitive Terms

Do not weaken global typo behavior because a small set of identifiers needs exact treatment. Review current documented controls for SKU, part number, acronym, numeric token, postal code, and regulated-term exceptions. Test exact behavior alongside ordinary mobile typo recovery.

## Custom Ranking

- Use business metrics to break textual ties: popularity, sales, conversion rate, rating, freshness, availability, margin band, editorial priority.
- Use numeric or boolean values.
- Prefer meaningful buckets or rounded values when very precise values would prevent later ranking criteria from mattering.
- Avoid using custom ranking to compensate for missing searchable attributes or bad record granularity.

## Facets And Filters

- Declare only fields that need filtering, faceting, or searchable facet values.
- Normalize facet values before indexing.
- Use facets for user-visible refinement and filters for hidden constraints as well as visible restrictions.
- Test facet counts under common refinements.
- Decide whether hierarchical facets are needed for category trees.

### Filter Contract

For each filterable attribute, state whether it is a hard constraint, visible refinement, silent product constraint, or optional preference. Only use optional filters for the last case. Do not use them for permissions, compliance, account entitlements, or any availability rule that must be deterministic.

## Rules, Synonyms, And Merchandising

- Use synonyms for query language equivalence, not for hiding catalog gaps.
- Use rules for scoped overrides such as campaigns, redirects, pinned items, banners, or seasonal merchandising.
- Name and scope rules so a future agent can tell why they exist.
- Prefer rules with conditions over broad global overrides.
- Include expiry or review notes for campaign-specific changes.

### Choose The Right Asset

| Situation | Use | Avoid |
| --- | --- | --- |
| Equivalent user language | Synonym | Using a synonym to mask missing records or a distinct concept. |
| Typo-sensitive identifier | Current documented typo exception | Disabling typo tolerance globally. |
| Query, filter, audience, or campaign-specific intent | Rule | A global pin or broad synonym. |
| Prefer a category or brand without excluding alternatives | Optional filter where appropriate | A hard filter that removes relevant alternatives. |
| Time-bound promotion, banner, redirect, pin, or hide | Rule with condition and review date | A permanent ranking change for temporary business intent. |

Rules should have a human-readable name, owner, scope, review/expiry date, query examples, and rollback note.

## Replicas And Sorting

- Use replicas for alternate sort orders where the user explicitly chooses a sort.
- Use virtual replicas when relevant sorting is appropriate and available for the use case.
- Keep sort labels honest. If a sort significantly changes relevance, disclose or revisit the strategy.

### Replica Preflight

Before creating or recommending a replica, confirm the primary index, sort objective, replica type, settings inheritance, UI label, expected relevance tradeoff, and current product limitations. Test the same filters, facets, and record links on every sort surface.

## Experiment And Rollback Discipline

Use a controlled test for meaningful relevance changes when traffic and event coverage make it worthwhile:

1. State one hypothesis and one isolated change.
2. Define the control, variant, traffic split, duration/sample-size approach, success metric, and guardrail metric.
3. Confirm click and conversion events can support interpretation.
4. Wait for sufficient data and confidence before declaring a winner.
5. Keep a rollback path: settings export, owner, trigger, and retest query set.

Do not stop and restart a test as though it were continuous. Do not use an experiment to interpret a bundle of unrelated ranking, data, and UI changes.

## Source Notes

- Algolia relevance work starts with searchable attributes and custom ranking: https://www.algolia.com/doc/guides/managing-results/relevance-overview
- Searchable attributes are all searchable by default until explicitly configured, and ordering affects ranking: https://www.algolia.com/doc/guides/managing-results/must-do/searchable-attributes
- Custom ranking breaks ties with numeric or boolean business metrics: https://www.algolia.com/doc/guides/managing-results/must-do/custom-ranking
- Facets let users refine results and are configured by declaring attributes for faceting: https://www.algolia.com/doc/guides/managing-results/refine-results/faceting
