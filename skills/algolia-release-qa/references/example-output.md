# Example Output: Customer-Readable QA Report

Use this shape when reporting launch readiness.

## Summary

Launch should wait until the blocker and high-severity event issue are fixed. Search relevance is usable for the tested query set, but analytics and AI-readiness are not reliable yet because click attribution is incomplete.

## Findings

| Severity | Surface | Finding | Evidence | Recommended fix | Owner |
| --- | --- | --- | --- | --- | --- |
| Blocker | Security | Admin-capable key appears in the browser bundle. | Client-side network inspection shows a key with write-capable permissions. | Replace it with a search-only or secured search key and rotate the exposed key. | Developer or Algolia admin |
| High | Events | Search result clicks do not include `queryID`. | Click payload contains `objectID` and `userToken`, but no `queryID`. | Enable queryID retrieval on searches and pass the clicked hit's `queryID` to the event. | Frontend developer |
| Medium | Relevance | Top query `waterproof trail shoe` ranks an unavailable product first. | Tested query returns an out-of-stock item above available alternatives. | Add availability as a custom ranking or filtering strategy according to merchandising rules. | Search owner |
| Low | UI | Empty state gives no next step. | No-result query shows a blank results area. | Add alternate query/category suggestions. | Frontend or content owner |

## Evidence Matrix

| Surface | Scenario | Evidence | Status | Residual risk |
| --- | --- | --- | --- | --- |
| Search relevance | `waterproof trail shoe` | Saved result set and availability filter review. | Needs follow-up | Long-tail and locale scenarios not yet run. |
| Events | Search -> click -> add to cart | Browser payload and debugger show queryID, objectID, index, position, and userToken. | Click ready; conversion incomplete | Purchase path is server-side and not yet inspected. |
| Security | Client bundle | Key review found an admin-capable key. | Blocked | Key rotation and secured-key retest required. |
| Rollback | Settings change | Exported settings and owner runbook available. | Ready | Production restore has not been rehearsed. |

## Tests Run

- 10 top revenue queries.
- 5 known problem queries.
- Category browse with filters.
- Mobile filter and sort behavior.
- Click and add-to-cart event payload inspection.
- Client-side key exposure check.

## Tests Not Run

- Production analytics trend review because the event fix is required first.
- A/B test analysis because no experiment is active.
- Purchase event validation because test checkout access was unavailable.

## Launch Recommendation

Do not launch broadly yet. Fix the exposed key and missing click attribution, then rerun security and event QA. Relevance and UI issues can launch with owner acceptance if the blocker and high issue are resolved.

## Smallest Retest

1. Confirm the browser uses only a search-only or secured key after rotation.
2. Search, click a result, and complete the primary conversion path; verify the full attribution chain and duplicate-event ownership.
3. Rerun the top-query, known-problem-query, and mobile empty-state checks.
