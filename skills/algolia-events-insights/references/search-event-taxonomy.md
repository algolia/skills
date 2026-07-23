# Search Event Taxonomy

Use this template before or during a search, browse, autocomplete, recommendations, personalization, Dynamic Re-Ranking, or ecommerce implementation. Instantiate it for the actual UI surfaces, or explicitly mark events as implemented, validated, planned, deferred, or unknown.

| Surface | User action | Event type | Event name | Required payload | Owner/path | Validation notes |
| --- | --- | --- | --- | --- | --- | --- |
| Autocomplete | Product or content selected from Algolia hits | Click | Autocomplete Result Clicked | `eventName`, `index`, `objectIDs`, `queryID`, one-based `positions`, `userToken` | Frontend/search-insights | Direct result click. Use an after-search click only when the hit came from a search response with `queryID`. |
| Autocomplete | Query suggestion selected | Search handoff | Query Suggestion Submitted | `query`, `source`, `userToken` | Frontend | Not an object click unless the suggestion is backed by a hit and preserves hit attribution. |
| Search results page | Result clicked | Click | Search Result Clicked | `eventName`, `index`, `objectIDs`, `queryID`, one-based `positions`, `userToken` | Frontend/search-insights | Use `clickedObjectIDsAfterSearch`; validate exact hit objectID. |
| Browse or category page | Result clicked | Click | Browse Result Clicked | `eventName`, `index`, `objectIDs`, `queryID`, one-based `positions`, `userToken` | Frontend/search-insights | Use after-search attribution when browse results include `queryID`; otherwise state the non-search attribution choice. |
| Product detail page or content detail page | Result viewed after search | View | Search Result Viewed | `eventName`, `index`, `objectIDs`, `userToken` plus stored attribution when available | Frontend or connector | Use only if the view is a meaningful signal for the use case; do not substitute for P0 click/conversion. |
| Cart, save, lead, or primary action | Product added, saved, or lead submitted | Conversion | Product Added To Cart | `eventName`, `index`, `objectIDs`, `queryID` when available, `userToken` | Frontend, GTM, Segment, or backend | Use the after-search method when the conversion is attributable to a search response; compare queryID to original search. |
| Purchase or completed conversion | Purchase completed | Conversion | Product Purchased | `eventName`, `index`, `objectIDs`, `queryID` when available, `userToken`, `price`, `quantity`, `currency` where supported and needed | Backend preferred | Decide whether frontend, backend, or a deduped pipeline owns this event; validate no duplicate final conversion. |
| Recommendations | Recommended result selected | Click | Recommendation Result Clicked | `eventName`, `index`, `objectIDs`, `userToken`, recommendation attribution fields required by current docs | Frontend/search-insights or custom | Validate against current Recommend event requirements. |

## Key Decisions

- Anonymous `userToken` strategy:
- Authenticated `userToken` strategy:
- Login merge behavior:
- Event owner by surface:
- Implementation path by surface:
- Deduplication rule:
- Connector mapping risks:
- Deferred events and owner:
- Validation method:

## Readiness Checkpoints

Before calling the event setup ready, state whether these checkpoints are satisfied, planned, deferred, or unknown:

- Result clicks preserve `index`, `objectID`, `queryID`, `position`, and `userToken`.
- Query suggestions and direct-result selections are tracked as different actions.
- Conversion events are implemented, planned, or explicitly deferred by the user.
- Validation evidence exists for network payloads and downstream visibility where available.
- Events are checked for arrival, usability, and attribution, not only successful delivery.
- GTM, Segment, backend, or hybrid paths have source payload and Algolia payload validation.
- One complete user journey can be filtered by `userToken` from search to click to conversion.
