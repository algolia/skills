# NeuralSearch Guide

## Current Docs To Verify

The Algolia docs navigation checked on 2026-06-29 lists NeuralSearch under AI relevance with these areas:

- Get started.
- Adaptive intent.
- A/B testing.
- Limitations.
- Model training.

Verify current docs before changing live configuration:

- https://www.algolia.com/doc/guides/ai-relevance/neuralsearch/get-started
- https://www.algolia.com/doc/guides/ai-relevance/neuralsearch/adaptive-intent
- https://www.algolia.com/doc/guides/ai-relevance/neuralsearch/ab-testing
- https://www.algolia.com/doc/guides/ai-relevance/neuralsearch/limitations
- https://www.algolia.com/doc/guides/ai-relevance/neuralsearch/model-training

## Readiness Assessment

Check:

- Plan eligibility and current product availability for the customer's application and desired NeuralSearch mode.
- Index records include meaningful titles, descriptions, categories, brand, attributes, and content summaries.
- Important searchable text is not split across missing, empty, or overly noisy fields.
- Filters, facets, secured attributes, and business rules are already explicit.
- Custom ranking does not overpower the relevance behavior you want to evaluate.
- Current public docs state that click and conversion events are not required to activate NeuralSearch. Without events, NeuralSearch selects semantic attributes from the record structure; with events, it selects and weights attributes from real query-to-record behavior, and the model can be retrained once events accumulate. Verify the chosen mode's current documentation before treating any cold-start, preview, or activation path as available.
- There is a representative query set and a baseline metric.

## Academy Rollout Path

Use this teaching sequence for customer guidance:

1. Understand what NeuralSearch changes: it helps with semantic, long-tail, conceptual, and natural-language relevance, while traditional keyword behavior still matters for exact and deterministic queries.
2. Confirm activation readiness: eligibility, data quality, analytics, current event guidance, representative query set, and rollback.
3. Preview before rollout: compare hybrid and baseline behavior with the evaluation set, then record useful wins, unacceptable matches, and unexplained results.
4. Test before broad rollout: use a replica, controlled configuration, or A/B test depending on the customer's traffic and risk.
5. Tune semantic behavior: review semantic settings, attribute priority, and the chosen conservative/broader-reach behavior only where current docs support it.
6. Validate with real outcomes: compare CTR, conversion, click position, zero-result/no-click behavior, long-tail engagement, and business-owner relevance review.
7. Optimize continuously with analytics, explainability, merchandising rules, and event improvements.

## Readiness Gates

Use these gates before recommending enablement:

1. Data gate: records contain meaningful titles, descriptions, categories, attributes, and content summaries; noisy or internal fields are not driving semantic matching.
2. Relevance gate: textual relevance, filters, facets, rules, merchandising, and custom ranking already behave acceptably for important exact queries.
3. Event gate: click and conversion signals are reliable enough to compare baseline and rollout behavior and to support retraining and Adaptive Intent. Events are not an activation blocker in current docs, but launching without them limits attribute selection, measurement, and optimization; treat missing events as an explicit risk.
4. Query-set gate: the team has representative head, tail, natural-language, vague, exact, filtered, and no-result queries.
5. Rollout gate: the team can stage, A/B test, monitor, and roll back.

Missing data, relevance, event, query-set, or rollout gates should become blockers or explicit risks, not footnotes.

## Hybrid Relevance Evidence

NeuralSearch combines keyword and semantic retrieval. Evaluate the combination, rather than treating semantic relevance as a replacement for keyword search.

| Evidence | Ask | Use it to decide |
| --- | --- | --- |
| Query class result | Did expected records improve for vague, long-tail, and natural-language intent without harming exact behavior? | Whether NeuralSearch helps the intended query class. |
| Result origin or score evidence | Is a result supported by keyword matching, semantic similarity, or both, where current diagnostics expose this? | Whether to inspect source text, semantic attributes, keyword settings, or blend behavior. |
| Business-rule context | Is the position caused by a pin, promotion, suppression, filter, or sort expectation? | Whether the result is a semantic issue at all. |
| Outcome signal | Did clicks, conversions, no-clicks, or no-results move for the targeted audience? | Whether a promising manual result generalizes. |

For every surprising win or regression, record the query, expected result, actual result, filters, business rules, observed evidence, hypothesis, single change tested, and retest outcome.

## Semantic Attribute Rationale

Select a small set of fields that express the meaning users search for. For each chosen field, state why it belongs, its priority, representative content, and known noise.

| Attribute type | Often useful when it contains | Risk to review |
| --- | --- | --- |
| Title or name | The user's primary product, article, or entity language. | Abbreviations, opaque codes, or duplicate variants. |
| Description or summary | Real user-facing context, use cases, materials, features, or problem statements. | Supplier boilerplate, marketing repetition, or stale copy. |
| Category or taxonomy | A stable, user-recognizable classification. | Deep internal labels or duplicate category strings. |
| Structured attributes | Meaningful concepts users describe naturally. | Treat deterministic facets and permissions as filters, not semantic hints. |

Do not add IDs, internal notes, duplicate concatenations, or unreviewed vendor text merely to increase field count. Change one attribute or priority decision per evaluation round.

## Query Evaluation Set

Include:

- Head queries.
- Long-tail queries.
- Natural-language queries.
- Conceptual/vague queries.
- Exact SKU, brand, part number, or title queries.
- Typo and synonym queries.
- Category and browse-like queries.
- No-result or low-result queries.
- Queries with filters.
- Queries with business-rule or merchandising expectations.

For each query, record expected good results, unacceptable results, filters, and business constraints.

## Data And Events Dependencies

NeuralSearch quality often depends on the same foundations as other AI relevance features:

- Clean, semantically meaningful records.
- Correct searchable attributes and display fields.
- Stable objectIDs for events and evaluation.
- Consistent userToken strategy.
- Search-attributed clicks and conversions. Current public docs do not require events for activation, but events drive semantic attribute selection and weighting, retraining, Adaptive Intent readiness, evaluation, and rollout confidence.
- A/B testing or staged rollout instrumentation.

Use `$algolia-events-insights` when events are missing or attribution is unclear.

## Optimization Workflow

1. Define the search classes NeuralSearch should improve.
2. Capture baseline metrics and a representative query set.
3. Review current NeuralSearch setup docs, limitations, and unsupported features.
4. Prepare records and settings.
5. Enable or configure in a safe environment or staged rollout.
6. Compare keyword and NeuralSearch results by query class, not only aggregate metrics.
7. Run A/B tests when meaningful traffic exists.
8. Document tradeoffs, winning configuration, and rollback.

## Configuration And Diagnostics

When the customer needs tuning, guide the agent to inspect:

- Semantic fields: which attributes carry meaning and which introduce noise.
- Attribute weights or semantic settings where supported by current docs.
- Baseline keyword behavior for exact, brand, SKU, part number, and compliance-sensitive queries.
- Long-tail and natural-language queries where NeuralSearch should help most.
- Pinned, buried, promoted, suppressed, or campaign-driven merchandising rules.
- Analytics segmentation through replicas, analytics tags, or A/B tests.
- Explainability/result panels when a result is surprising, missing, or over-promoted.

Do not recommend broad setting changes without a before/after query set and a way to isolate impact.

### Explainability-Led Triage

When a result is unexpected, work in this order:

1. Reproduce the query with the same filters, locale, sort, and user-facing conditions.
2. Check whether a rule, pin, promotion, suppression, custom ranking, or filter explains the position.
3. Inspect the available keyword, semantic, and final-score evidence in current diagnostics.
4. Inspect the record text and selected semantic attributes for missing context or noise.
5. Change one hypothesis at a time, rerun the query set, and record the decision.

This sequence prevents teams from overwriting intentional merchandising while trying to fix a relevance issue.

## QA Checklist

- Exact-match queries still behave acceptably.
- Vague and natural-language queries improve without leaking bad matches.
- Filters and secured data constraints still apply.
- Merchandising rules and pinned results behave as expected.
- No-result strategy is still acceptable.
- Event payloads preserve objectID, index, queryID where needed, and userToken.
- Analytics and A/B test reporting can isolate NeuralSearch impact.
- Virtual replicas are not assumed to work with NeuralSearch; sorted NeuralSearch experiences use current documented sort/replica guidance.
- Explainability or result inspection has been used for surprising wins and regressions.
- Business rules and merchandising behavior have been checked in semantic and exact-query scenarios.
- Long-tail performance is reviewed separately from high-volume head queries.
- Semantic attributes have a documented purpose and priority; noisy, internal, and duplicate fields are excluded or accounted for.
- Preview or explainability evidence distinguishes keyword, semantic, and hybrid behavior for representative wins and regressions.

## Related Skills

- `$algolia-data-modeling`: record and field readiness.
- `$algolia-index-configuration`: textual relevance and business ranking.
- `$algolia-events-insights`: measurement and conversion attribution.
- `$algolia-release-qa`: rollout and regression checks.
