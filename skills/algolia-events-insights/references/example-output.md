# Example Output: Minimal Event Taxonomy

Use this as a compact first event plan for a commerce search experience.

## Goal

Measure whether search and browse interactions lead to product engagement, add-to-cart, and purchase. Prepare the implementation for analytics, A/B testing, personalization, Recommend, dynamic re-ranking, and AI-readiness evaluation.

## Event Map

| User action | Algolia method | Event name | Owner | Required fields | Validation |
| --- | --- | --- | --- | --- | --- |
| P0: Search result click | `clickedObjectIDsAfterSearch` | `Product Clicked` | Frontend | `index`, `objectID`, `queryID`, one-based `position`, `userToken` | Browser payload includes queryID from the clicked hit; Algolia Debugger shows destination eligibility. |
| P0: Primary conversion caused by search | `convertedObjectIDsAfterSearch`, `addedToCartObjectIDsAfterSearch`, or `purchasedObjectIDsAfterSearch` depending on the business goal | `Product Added To Cart` or `Product Purchased` | Frontend or backend | `index`, `objectID`, `queryID`, `userToken`, price/quantity when available | Same userToken and objectID as the search journey; queryID is current or documented with an inference path. |
| P1: Purchase caused by search | `purchasedObjectIDsAfterSearch` | `Product Purchased` | Backend preferred | `index`, `objectID`, per-item `queryID` inside `objectData` for explicit search attribution, `userToken`, price, quantity, currency | Purchase event is not duplicated by frontend and backend; if queryID cannot be carried within the valid attribution window or inferred from a prior click, use the non-AfterSearch purchase method and document the feature impact. |
| P2: Product view not caused by search | `viewedObjectIDs` | `Product Viewed` | Frontend | `index`, `objectID`, `userToken` | No queryID is used when the view is not search-attributed. Treat as supporting, not a replacement for P0 events. |

## Connector Recommendation

Primary path: InstantSearch plus search-insights for result clicks and add-to-cart because the UI has the hit `objectID`, `queryID`, position, and `userToken` at the interaction moment.

Backend path: order confirmation should send final purchase events because revenue, quantity, and currency are finalized server-side.

Fallback path: use GTM only if the data layer exposes `queryID`, exact Algolia `objectID`, one-based position, and durable `userToken` at click/conversion time. Use Segment only if mappings preserve arrays and field names into the Algolia destination.

Duplicate rule: frontend may send click and add-to-cart; backend owns final purchase. Do not also fire a frontend purchase tag.

## Identity Rule

Create one durable anonymous `userToken` and use it on search requests and events. When the user logs in, either keep the anonymous token for continuity or map it deliberately to the authenticated identity according to the customer's privacy and analytics policy. Do not generate a new token per event or page view.

## First Validation Pass

1. Search for `trail running shoes`.
2. Click the third result.
3. Confirm the click payload includes the clicked hit's `objectID`, the result position, the response `queryID`, the index, and the same `userToken` used for search.
4. Add the same product to cart.
5. Confirm add-to-cart uses the same identity, record identifiers, and queryID because it is sent with an `AfterSearch` method.
6. Complete a test purchase.
7. Confirm only one purchase event is sent, and that an `AfterSearch` purchase includes a queryID within the valid attribution window or has a documented inference path from a prior click.

Validation standard:

- Arrival: event appears in Network/server logs and Algolia Debugger.
- Usability: required fields are present, arrays are shaped correctly, and positions are one-based.
- Attribution: one user timeline shows search to click to conversion with the same `userToken`, matching `queryID`, exact hit `objectID`, and no duplicate final conversion.

## Developer Handoff Sheet

| Field | Source | Owner | Validation |
| --- | --- | --- | --- |
| `queryID` | Search or browse response with click analytics enabled | Frontend search owner | Same value appears on click and search-attributed conversion. |
| `objectID` | Hit returned by Algolia | Frontend/UI owner | Matches the record the user clicked or converted on; no parent/variant mismatch. |
| `position` | Rendered hit position | Frontend/UI owner | Present on click events that require position. |
| `userToken` | Durable anonymous/authenticated identity policy | Frontend/platform owner | One test journey can be filtered by the same token in the Debugger. |
| Final purchase | Order service or backend conversion flow | Backend owner | Not duplicated by frontend purchase event. |

## Feature Readiness Notes

| Feature | Status | Notes |
| --- | --- | --- |
| Search analytics | Ready after P0 click and conversion validate | QueryID and position power click and conversion analysis. |
| Dynamic Re-Ranking | Planned | Needs enough search-attributed click/conversion volume and deduplicated user behavior. |
| NeuralSearch evaluation | Planned | Events help measure quality, even when activation does not require events. |
| Recommend | Planned | Validate current model-specific event requirements before relying on purchase or add-to-cart events. |
| Personalization | Blocked until identity is validated | Stable `userToken` is the gate. |

## Common Debugger Findings

- Ingested but weak: generic view or filter events arrive, but P0 clicks/conversions are missing.
- Ingested but unattributed: event is visible, but queryID is missing, stale, or different from the original search.
- Ingested but mismatched: event objectID uses a parent product while the search returned a variant.
- Ingested but mispositioned: result position is zero-based, so click position analysis is wrong.
- Ingested but deduplicated: all users share one userToken, so downstream models see too little usable behavior.
- Connector mismatch: Segment/GTM source event looks correct, but Algolia receives renamed, flattened, missing, or duplicate fields.

## Follow-Up Questions

- Which conversion is the business's primary success metric: purchase, lead, signup, save, download, or support deflection?
- Are purchases finalized on the backend?
- Are consent rules or account switching relevant?
- Which AI or personalization features depend on this event setup?
