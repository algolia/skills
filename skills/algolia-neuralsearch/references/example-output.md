# Example Output: NeuralSearch Readiness Report

Use this shape before recommending rollout.

## Recommendation

Status: fix first.

NeuralSearch is promising for long-tail and natural-language product queries, but the rollout should wait until the team validates semantic fields, removes noisy record text, and confirms event quality for measurement.

## Readiness Gates

| Gate | Status | Evidence | Required action |
| --- | --- | --- | --- |
| Semantic record fields | Needs work | Product titles and descriptions exist, but some records contain supplier boilerplate and duplicated category text. | Clean noisy fields or exclude them from semantic relevance inputs where appropriate. |
| Filters and permissions | Ready | Region and availability filters are present and tested. | Keep these deterministic during NeuralSearch testing. |
| Representative query set | Needs work | Top exact-match queries exist, but vague and natural-language examples are missing. | Build a 30-query evaluation set across exact, vague, synonym-heavy, and long-tail queries. |
| Events and measurement | Needs work | Click events exist, but conversion attribution is incomplete. | Treat as a measurement and optimization risk; fix conversion events before relying on outcome metrics or Adaptive Intent. |
| Rollback path | Ready | Settings can be restored from exported configuration. | Keep rollback notes with the experiment plan. |

## Query Evaluation Set

| Query class | Example | Expected behavior |
| --- | --- | --- |
| Exact product | `trail runner 2` | Exact product appears first. |
| Natural language | `shoes for muddy half marathon training` | Waterproof trail running shoes rank above casual shoes. |
| Attribute-heavy | `blue womens size 9 trail shoes` | Results respect color, gender, size, and trail intent. |
| Compliance-sensitive | `kids allergy safe snack` | Safety and category constraints remain deterministic. |
| Merchandised | `holiday gift set` | Rules and campaigns still behave as intended. |

## Semantic Attribute Rationale

| Attribute | Priority | Why it carries meaning | Risk or follow-up |
| --- | --- | --- | --- |
| `name` | High | Uses the shopper's product language. | Check opaque variant codes and duplicate names. |
| `description` | Medium | Explains use case, material, and activity context. | Remove repeated supplier boilerplate. |
| `categories` | Medium | Gives a stable shopper-facing classification. | Keep permissions and availability as deterministic filters. |

## Hybrid Evidence Log

| Query | Observation | Evidence to inspect | Next action |
| --- | --- | --- | --- |
| `shoes for muddy half marathon training` | A waterproof trail shoe improved from page two to the top group. | Compare keyword/semantic evidence and the result's description. | Keep as a candidate win; validate with traffic. |
| `trail runner 2` | Exact product must remain first. | Check exact keyword behavior, pins, and custom ranking before semantic fields. | Block rollout if the deterministic result regresses. |

## Rollout Plan

1. Clean semantic fields and confirm record examples.
2. Fix primary conversion events before relying on outcome metrics or Adaptive Intent.
3. Build the evaluation query set.
4. Run a controlled test against current relevance.
5. Review wins, regressions, and unexplainable results.
6. Launch gradually with rollback notes.

## Diagnostics And Optimization

| Area | What to inspect | Why it matters |
| --- | --- | --- |
| Semantic fields | Titles, descriptions, categories, attributes, summaries, and noisy/internal text | NeuralSearch can only reason over the data it receives. |
| Exact queries | SKU, brand, part number, regulated/compliance terms | Semantic expansion should not break deterministic expectations. |
| Long-tail queries | Multi-word, natural-language, vague, and conceptual searches | These are often where NeuralSearch creates the clearest value. |
| Merchandising | Pinned, buried, promoted, suppressed, and campaign results | Business logic should remain intentional after semantic changes. |
| Explainability | Surprising top results, missing expected results, and low-confidence matches | Helps decide whether to adjust data, semantic settings, or business rules. |
| Analytics segmentation | Replica, A/B test, or analytics tags | Lets the team isolate NeuralSearch impact from unrelated changes. |
