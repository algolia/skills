# Events Guide

## Contents

- [Fast Path](#fast-path)
- [Academy Coaching Model](#academy-coaching-model)
- [Event Readiness Model](#event-readiness-model)
- [Implementation Path Selector](#implementation-path-selector)
- [Low-Dev Implementation Path](#low-dev-implementation-path)
- [Connector-Specific Handoff Questions](#connector-specific-handoff-questions)
- [Code Pattern References](#code-pattern-references)
- [Validation Workflow](#validation-workflow)
- [Agent Checklist](#agent-checklist)
- [Event Taxonomy Template](#event-taxonomy-template)
- [Common Event Choices](#common-event-choices)
- [Feature Readiness Signals](#feature-readiness-signals)
- [Attribution Rules](#attribution-rules)
- [Valid But Not Useful Enough](#valid-but-not-useful-enough)
- [Common Failure Patterns](#common-failure-patterns)
- [Identity Strategy](#identity-strategy)
- [QA](#qa)
- [Source Notes](#source-notes)

## Fast Path

For most implementations, start with this smallest useful setup:

| Moment | Event | Owner | Required attribution |
| --- | --- | --- | --- |
| User clicks a search or browse result | `clickedObjectIDsAfterSearch` | Frontend | index, objectID, queryID, position, userToken |
| User converts after search | `convertedObjectIDsAfterSearch` or a more specific conversion method | Frontend or backend | index, objectID, queryID for explicit search attribution, userToken |
| User adds to cart | `addedToCartObjectIDsAfterSearch` when caused by search | Frontend or backend | index, objectID, queryID, userToken, price/quantity when available |
| User purchases | `purchasedObjectIDsAfterSearch` when caused by search | Backend preferred | index, objectID, per-item `queryID` inside `objectData` for explicit search attribution because purchased items can come from different searches, userToken, revenue fields when available |
| User views a product/content item outside search | `viewedObjectIDs` | Frontend | index, objectID, userToken |

Do not begin with every possible event. Begin with the actions that unlock the customer's stated goal, then expand after the first payloads are validated.

## Academy Coaching Model

Events work best when the agent teaches both sides of the implementation:

- Business users define what to track and why: KPIs, required user actions, affected Algolia-powered surfaces, priority, and success criteria.
- Technical users define how tracking works: event method, payload schema, queryID propagation, userToken strategy, objectID source, frontend/backend owner, validation, and monitoring.

When a customer asks for event setup, produce both outputs:

- Event Plan: business-readable priority list of P0, P1, and P2 events mapped to surfaces and outcomes.
- Developer Handoff Sheet: technical payload requirements, field sources, owner, trigger, deduplication rule, and validation steps.

## Event Readiness Model

Teach customers that an event can arrive successfully and still fail to power analytics or AI features. Validation has three layers:

| Layer | Question | Evidence |
| --- | --- | --- |
| Arrival | Did Algolia receive the event? | Network response, server log, Events Health, or Debugger entry |
| Usability | Are required fields present and shaped correctly? | `eventName`, event type/subtype, `index`, `objectIDs`, `userToken`, `queryID` for post-query events, `positions` where required |
| Attribution | Is the event tied to the right search, item, and user? | Same `queryID` from search to click to conversion, same durable `userToken`, exact Algolia `objectID`, one-based position, no duplicate owner |

Do not mark an event setup ready from arrival alone. A 200 response, successful tag fire, Segment debugger event, or Algolia Debugger entry is only the first layer.

## Implementation Path Selector

Choose the path before writing code or building tags. The best path depends on where the required attribution fields are available.

| Path | Use when | Strengths | Risks to validate |
| --- | --- | --- | --- |
| InstantSearch plus search-insights | The UI is built with InstantSearch or can use its event helpers/middleware | Simplest starting point; queryID and hit context are close to the user action; fewer custom mappings | Ensure `clickAnalytics` and `userToken` are configured; validate custom conversions beyond automatic events |
| Custom frontend with Insights API | The app owns rendering and can access search responses | Full control over payloads and timing | Manual position calculation, stale queryID, objectID mismatch, token resets |
| Google Tag Manager | Marketing-managed frontend, limited code deploys, shared analytics tagging | Fast iteration and broad template coverage | Variables may not contain hit `objectID`, `queryID`, position, or durable `userToken`; duplicate triggers are common |
| Segment or CDP | Centralized identity and event pipeline, multi-platform analytics, server-side purchase confirmation | Stronger identity governance and backend conversion support | Mappings may rename/drop fields; anonymous ID and userToken may diverge; source debugger can pass while Algolia payload fails |
| Backend events | Purchase, lead acceptance, support resolution, subscription, or other final conversion is server-side | Reliable final outcome and revenue data | Must persist search attribution or infer from prior click; avoid duplicate frontend/backend final conversions |
| Hybrid | Clicks happen in the frontend but final conversions happen later or server-side | Matches many commerce architectures | Requires explicit handoff of `queryID`, `objectID`, `index`, and `userToken` across pages and systems |

Output requirement:

- Recommend one primary path and one fallback path.
- Name where each required field comes from.
- State the expected debugging surface: browser Network, GTM preview, Segment debugger, backend logs, Events Health, Algolia Debugger, or user timeline.
- State the duplicate-prevention rule.

### P0/P1/P2 Priority Model

Use this model to keep event setup simple:

- P0 must-have: result clicks and primary conversions after search or browse, with `queryID`, `userToken`, `objectID`, `index`, and position when required.
- P1 important: add-to-cart, purchase, lead, save, support resolution, recommendation interactions, or other business outcomes that unlock additional measurement and optimization value.
- P2 nice-to-have: context-specific or weaker signals such as broad views, filter interactions, or secondary engagement events. Add these after P0 is validated.

Do not let customers start with a giant taxonomy. Teach them that healthy P0 events usually create more value than many loosely defined P2 events.

## Low-Dev Implementation Path

Use this path when the customer has limited engineering access.

1. Identify the one search UI flow and one conversion flow that matter most.
2. Confirm whether the frontend exposes `objectID`, `index`, `queryID`, result position, and `userToken` to the browser or data layer.
3. If a tag manager is used, only use it when those values are available at the exact interaction moment and duplicate events can be prevented.
4. If purchase, lead acceptance, support resolution, or subscription completion happens server-side, ask for the backend owner. A browser-only tag is usually not enough for reliable final conversions.
5. Produce an owner handoff table: field needed, where it should come from, who can expose it, and how to validate it.

Minimum viable validation:

- One click event from a search result has correct `index`, `objectID`, `queryID`, `position`, and `userToken`.
- One primary conversion event uses the same identity and record identifiers.
- Refreshing, navigating, or logging in does not create a new unrelated token unless that is the intended identity policy.
- Repeating the flow does not double-send the same event from both frontend and backend.

## Connector-Specific Handoff Questions

### InstantSearch Or Search Insights

- Is `clickAnalytics` enabled for searches that produce clickable results?
- Is the Insights client initialized once?
- Is the same `userToken` used for searches and events?
- Which events are automatic, and which require manual `sendEvent` or equivalent handling?
- Do custom conversion events preserve the originating `queryID`?

### Google Tag Manager

- Where does `queryID` come from, and is it available at the exact click or conversion moment?
- Which data layer variable contains the Algolia `objectID`, not a SKU or parent product ID?
- How is `userToken` defined and reused across templates?
- Which triggers could fire twice?
- Does GTM preview show the same payload shape that Algolia receives?

### Segment Or CDP

- Which Segment identifier maps to Algolia `userToken`: anonymous ID, user ID, or a custom field?
- Are `queryID`, `objectIDs`, and `positions` mapped with the exact property names expected by the Algolia destination?
- Are arrays preserved as arrays, not flattened strings?
- Does the Segment debugger event match the Algolia Debugger event after transformation?
- Is server-side purchase attribution linked to the original frontend click or search context?

### Backend Conversion Flow

- What frontend action captures the `queryID`, `objectID`, `index`, and `userToken` before navigation or checkout?
- How are those values stored through cart, checkout, account creation, or payment?
- What is the maximum delay between search and conversion, and does the event still qualify as search-attributed?
- Which owner sends the final conversion, and what prevents frontend and backend duplicates?

## Code Pattern References

Use these as implementation shapes, then adapt to the local project and current Algolia docs.

### React InstantSearch Result Click

1. Enable click analytics for searches that render clickable hits.
2. Use the InstantSearch event helpers or middleware when available.
3. Send the click from the hit component, using the hit's objectID, index, queryID, and rendered position.

Implementation checklist:

- The hit component receives or can derive `objectID`.
- The search response includes `queryID`.
- The UI knows the displayed position for the clicked hit.
- The same `userToken` is used on the search request and the click event.

### Vanilla JavaScript Search Result Click

1. Store the search response `queryID` with rendered hits.
2. Render each hit with its `objectID`, `index`, and position.
3. On click, send the search-attributed click event before or alongside navigation.
4. Avoid recomputing position after filtering or client-side sorting.

### Backend Purchase Or Lead Conversion

Use backend ownership when the conversion is finalized server-side, such as purchase, lead acceptance, subscription, or support case resolution.

Capture at the time of user action:

- `userToken`
- `objectID`
- `index`
- `queryID` when using an `AfterSearch` conversion method for explicit search attribution; purchase events carry the `queryID` per item inside `objectData` rather than at the top level
- price, quantity, currency, or conversion metadata when relevant

Then send the final conversion from the backend with the same identity and record identifiers. Decide whether the frontend sends an intermediate event, such as add-to-cart, to avoid duplicate purchase conversions.

### Validation Payload Example

Every validated event should be explainable in plain language:

- Event name: business-readable action.
- Method: click, conversion, view, add-to-cart, or purchase.
- Index: the index or replica that produced the interaction.
- ObjectIDs: records the user interacted with.
- queryID: present for search-attributed interactions.
- positions: present when the method requires ranking position.
- userToken: stable anonymous or authenticated identity.
- Owner: browser, backend, or deduped pipeline.

## Validation Workflow

Validate a complete journey, not isolated events:

1. Perform a search or browse request that returns a `queryID`.
2. Record the `userToken` used on the search.
3. Click a result and verify `eventType`, `eventName`, `index`, exact `objectID`, one-based `position`, `queryID`, and `userToken`.
4. Trigger add-to-cart or the primary conversion.
5. Compare the conversion `queryID` to the original search/click `queryID`.
6. Confirm the same `userToken` ties search, click, and conversion together.
7. Inspect Events Health or Debugger for warnings, errors, destination/feature eligibility, and user timeline continuity when available.
8. Repeat the journey once to check duplicates.
9. Test a non-search path and confirm it uses a non-AfterSearch method or has a documented attribution choice.

Troubleshoot in this order:

1. Missing or incorrect `queryID`.
2. Inconsistent `userToken`.
3. Incorrect, missing, or non-index `objectID`.
4. Incorrect `positions`, especially zero-based positions.
5. Timing or attribution-window issues.
6. Duplicate frontend/backend/tag/CDP ownership.
7. Weak event type overinvestment, such as filter clicks without P0 result clicks.

## Agent Checklist

1. Ask what business outcome the event should prove.
2. Locate where the search response provides `queryID`, hit `objectID`, and displayed position.
3. Locate where the app stores or can create `userToken`.
4. Decide whether browser or backend owns each event.
5. Implement one flow end to end before adding more event types.
6. Validate payloads in the browser/network tab or server logs.
7. Confirm events appear in the relevant Algolia debugging, analytics, or feature-readiness surface when available.

## Event Taxonomy Template

Create a table with:

- User action.
- Algolia event method.
- `eventName`.
- Index.
- ObjectIDs source.
- QueryID source.
- Position source.
- UserToken source.
- Frontend/backend owner.
- Deduplication rule.
- Downstream feature unlocked.

## Common Event Choices

- Search result click: `clickedObjectIDsAfterSearch`.
- Search-attributed conversion: `convertedObjectIDsAfterSearch`.
- Search-attributed add to cart: `addedToCartObjectIDsAfterSearch`.
- Search-attributed purchase: `purchasedObjectIDsAfterSearch`.
- Non-search result interaction: use the corresponding method without `AfterSearch`.
- Product/content view unrelated to a prior search: `viewedObjectIDs`.
- Filter interactions: filter event methods when the feature requires them.

## Feature Readiness Signals

Map event types to the feature goal before implementation:

| Feature goal | Stronger signals | Weak or supporting signals | Readiness note |
| --- | --- | --- | --- |
| Search analytics and A/B testing | Search-attributed clicks and conversions | Generic views | QueryID and userToken continuity matter for trustworthy rates |
| Dynamic Re-Ranking | `clickedObjectIDsAfterSearch`, conversion events after search | Filter interactions | Needs enough events per query/record and deduplicates repeated user behavior |
| NeuralSearch activation, evaluation, and optimization | Search-attributed clicks and conversions; add-to-cart and purchase when relevant | Broad views, filter clicks | Current public NeuralSearch docs do not require events for activation, but events guide semantic attribute selection and unlock retraining and Adaptive Intent. Verify current requirements before activation, then use stronger outcomes to measure and improve behavior. |
| Recommend | Product clicks, add-to-cart, purchase, multi-item conversions where relevant | Generic page views | Model-specific minimums and event choices vary; verify current docs |
| Personalization | Events with stable `userToken` | Events with regenerated or shared tokens | Identity continuity is the gate |
| Revenue insights | Add-to-cart, purchase, lead, subscription, revenue-bearing conversions | Clicks alone | Validate price, quantity, currency, and final-conversion owner |

## Attribution Rules

- Set `clickAnalytics: true` on searches that need queryID attribution.
- Keep the same `userToken` on the search request and the later event.
- Preserve the exact `objectID` and `index` from the hit the user interacted with.
- Send positions when required by the event method.
- Events with queryID are time-sensitive. Current public docs state that click and conversion events with `queryID` must occur within one hour of the corresponding search request.
- If a conversion cannot carry a queryID, validate whether Algolia can infer it from an earlier click with the same userToken, app, index, and objectID. Otherwise use the non-AfterSearch event method and state which downstream features may not count it.
- Category pages powered by empty-query searches plus filters still need search-style event attribution when users interact with results.

## Valid But Not Useful Enough

Teach customers that an event can be accepted and still not help the feature they care about. Check for:

- Weak signal: filter events and generic views may be valid but often do not carry the same downstream value as clicks and conversions tied to records.
- Stale queryID: search-attributed events are time-sensitive and must use the queryID from the relevant search context.
- ObjectID mismatch: the event objectID must match the record returned by the original search or browse response. Parent/variant mismatches can make the event unusable for attribution.
- UserToken problem: a hardcoded, shared, or frequently regenerated token can make real user behavior impossible to interpret.
- Duplicate ownership: frontend and backend events can double-count unless the taxonomy assigns one owner or a deduplication rule.

Debugger visibility proves ingestion. Feature readiness requires the payload to be attributable, consistent, and meaningful.

## Common Failure Patterns

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Event returns 200 but does not power target feature | Ingestible but not usable or not eligible for the feature | Check required fields and destination/feature eligibility |
| Click event has position 0 | Position was copied from a zero-based array index | Send one-based positions, or use the hit/event helper when possible |
| ObjectID validation fails | Event sends SKU, parent ID, variant ID, or URL instead of Algolia `objectID` | Use the exact `objectID` returned by the hit |
| Conversion appears but is not attributed to search | Missing, stale, or mismatched `queryID` | Carry the originating queryID through click, PDP, cart, and conversion |
| Personalization resets or feels generic | `userToken` changes between page views, login, or systems | Define anonymous/authenticated token policy and validate one user timeline |
| Metrics look inflated | Duplicate events from frontend, backend, GTM, or CDP | Assign one owner per final event and add deduplication rules |
| Segment or GTM looks correct but Algolia is wrong | Connector mapping renamed, flattened, or dropped fields | Validate both connector debugger and Algolia Debugger |
| Events degrade after release | UI route, data layer, identity, or checkout changed | Add post-release event smoke checks |

## Identity Strategy

Ask how the product treats:

- Anonymous sessions.
- Login and logout.
- Cross-device behavior.
- Server-side purchases.
- Consent restrictions.
- Shared accounts.
- B2B account switching.

Do not generate a new random user token for every event. Use a durable anonymous token and connect or replace it deliberately on login according to the business and privacy requirements.

## QA

- Use a test index or staging app when possible.
- Verify the browser/network payload, not only the source code.
- Confirm events appear in Algolia debugging/analytics tools when available.
- Trigger the same flow twice and check for unintended duplicate events.
- Test query, browse/category, autocomplete, recommendation, and direct-navigation flows separately.
- Filter the debugger by `userToken` and follow one complete journey from search to click to conversion.
- Compare queryID from the original search response to the queryID on click and conversion events.
- Inspect whether the event destination/readiness indicators match the intended downstream features.
- After UI, routing, identity, checkout, analytics, or connector changes, re-run search to click to conversion.
- Monitor event volume, freshness, validation warnings, duplicate patterns, and unexpected drops after release.
- For multi-item purchases, confirm objectIDs, quantities, prices, and currency align by item.
- For multi-index setups, confirm the event references the index that produced the hit or the documented aggregation strategy.

## Source Notes

- Algolia Insights supports click, conversion, and view events, and different features need different event types: https://www.algolia.com/doc/guides/sending-events/concepts/event-types
- `AfterSearch` methods are for interactions tied to Algolia search or browse requests, require `queryID`, and are time-sensitive: https://www.algolia.com/doc/guides/sending-events/concepts/event-types
- Algolia's implementation-path guide covers frontend, ecommerce platform, CDP/tag manager, manual, batch, and external analytics options: https://www.algolia.com/doc/guides/sending-events/getting-started
- InstantSearch has dedicated event guidance for click and conversion events: https://www.algolia.com/doc/guides/building-search-ui/events/js
- Segment and connector paths must preserve Algolia event fields through mapping and transformation before the payload reaches Algolia: https://www.algolia.com/doc/guides/sending-events/connectors/segment
- Google Tag Manager paths require search-related data attributes such as index, objectID, position, and queryID in the page templates: https://www.algolia.com/doc/guides/sending-events/connectors/google-tag-manager
