# Release QA Checklist

## Severity Rubric

- Blocker: launch should not proceed. Examples: admin key exposed, secured records visible to the wrong user, event attribution entirely missing for required AI/personalization feature, production indexing can delete or corrupt records with no rollback.
- High: launch risk is material and should be fixed before broad rollout. Examples: top revenue queries return clearly wrong results, purchase events duplicate, mobile filters unusable, key facets missing.
- Medium: launch can proceed only with owner acceptance and follow-up. Examples: some long-tail queries weak, low-result UX rough, noncritical event metadata missing, incomplete analytics segmentation.
- Low: polish or monitoring follow-up. Examples: minor label issues, helpful additional QA coverage, documentation cleanup.

## Sample Findings

Use this shape in reports:

| Severity | Surface | Finding | Evidence | Recommended fix | Owner |
| --- | --- | --- | --- | --- | --- |
| Blocker | Security | Client exposes an admin-capable API key. | Browser bundle contains a key with write/admin capability. | Replace with search-only or secured search key; rotate exposed key. | Developer or Algolia admin |
| High | Events | Click events omit queryID. | Network payload includes objectID and userToken but no queryID after search result click. | Enable click analytics on search and pass queryID from hit to event. | Frontend developer |
| High | Data | Product variants are collapsed, hiding account-specific availability. | B2B account filter shows unavailable SKUs as purchasable. | Add account/availability filtering or separate account-aware records. | Data feed owner |
| Medium | Relevance | Synonym rule broadens support query too aggressively. | Query "returns" ranks unrelated shipping policy above return policy. | Scope synonym or add tested rule for return-policy intent. | Search owner |
| Low | UI | Empty state does not suggest next action. | No-result query renders blank results area. | Add empty-state copy and alternate navigation. | Frontend or content owner |

## Customer-Readable Report Shape

Keep the report direct:

- What blocks launch.
- What can launch with a documented risk.
- What was tested.
- What was not tested and why.
- Who needs to act next.
- The smallest retest needed after fixes.

## Evidence Matrix

Do not report a surface as passed based on an impression. Capture evidence that another owner can reproduce.

| Surface | Scenario | Evidence source | Pass condition | Owner | Residual risk |
| --- | --- | --- | --- | --- | --- |
| Search/relevance | Top and known-problem query | Saved query result, settings export, or screenshot with context | Expected records and constraints hold. | Search owner | Untested long-tail or locale behavior. |
| Events | Search -> click -> conversion | Request/response, event payload, debugger, and analytics evidence | Identity and attribution survive the full chain. | Frontend/backend analytics owner | Downstream data latency or untested server path. |
| UI | Mobile filter, sort, or empty state | Browser recording or screenshot with viewport | User can refine, recover, and continue. | Frontend owner | Device/browser coverage gap. |
| Security | Restricted user/account scenario | Key/config review and permission-boundary test | No restricted record or capability leaks. | Security or Algolia admin | Unavailable production identity path. |
| Operations | Relevance or data rollback | Settings backup, runbook, and restore rehearsal | Owner can revert safely. | Search/data owner | Unrehearsed production rollback. |

## Regression Charter

Before testing, identify the changed surface and its likely blast radius: data, relevance, UI, events, AI, and operations. Use the charter to decide which checks are mandatory, which are not applicable, and which remain untested.

## Data And Indexing

- Record count matches source expectations.
- ObjectIDs are stable and unique.
- Required searchable, display, filter, and ranking fields exist on representative records.
- Hidden, unavailable, secured, or out-of-region records behave correctly.
- Replicas are present and settings match their intended sort behavior.
- Incremental updates and full reindex paths both complete successfully.
- Indexing tasks are awaited where the application depends on fresh data.

## Relevance

- Top business queries return expected results.
- Known problem queries are included.
- No-result and low-result queries have acceptable UX or content strategy.
- Searchable attribute order matches user intent.
- Custom ranking metrics break ties as intended.
- Facets are normalized and useful.
- Rules, synonyms, typo tolerance, and optional filters are scoped and tested.
- Category/browse pages use correct filters and analytics segmentation.

## Search UI

- Search box, results, facets, current refinements, sort, pagination/infinite hits, and empty states work.
- URL routing preserves query/refinement state when required.
- Mobile filters and sort controls are usable.
- Loading and error states are visible.
- Result cards expose correct links, labels, prices, availability, and images.
- Accessibility basics are covered: labels, focus order, keyboard interaction, link names.

## Autocomplete

- Sources appear in the intended order.
- Keyboard, mouse, touch, Escape, Enter, and blur behavior work.
- Selection behavior is correct per source.
- Mobile detached mode works if enabled.
- No suggestions and slow network states are acceptable.
- Autocomplete handoff to InstantSearch or routing does not create state loops.

## Events And Analytics

- Search requests needing attribution have click analytics enabled.
- Click events include correct index, objectID, queryID, position, and userToken.
- Conversion events represent business-defined conversions.
- Server-side conversions can be tied back to userToken/objectID/index where required.
- Duplicate events are not emitted by both frontend and backend.
- Event names are stable, readable, and segmented enough for analytics.

### Attribution Chain

Verify each link, in order:

1. The search or browse request returns a `queryID` when attribution is needed.
2. The rendered hit preserves its `objectID`, index, and displayed one-based position.
3. The click or conversion payload uses the same durable `userToken` and includes `queryID` when it is search-attributed.
4. The event arrives in the debugger or another arrival surface.
5. The event is usable for the claimed analytics, personalization, A/B test, NeuralSearch, or AI-feedback feature.

A 200 response or debugger entry proves arrival, not the whole chain.

## Security And Operations

- Search-only keys are exposed client-side, not admin keys.
- Secured API keys or filters protect user/account-restricted data.
- Environment variables are used for sensitive IDs and keys according to project conventions.
- Production settings changes have a backup or repeatable config file.
- Rollback steps are documented.
- Monitoring or logs can detect failed indexing, stale data, or event drop-offs.

## Experiment And AI QA

- A/B test states the hypothesis, one isolated change, control, variant, traffic split, target metric, guardrail metric, duration/sample-size approach, and rollback decision.
- Event coverage is sufficient for test metrics; no-data or low-confidence outcomes are reported as inconclusive rather than wins.
- NeuralSearch meets current feature prerequisites and passes exact, semantic, filtered, merchandised, and no-result evaluation queries.
- Agent Studio has a narrow job, least-privilege tools, grounded retrieval, memory/retention decision, guardrails, safe fallback, approved domains, and feedback plan.

## Source Notes

- Relevance diagnostics should cover searchable attributes, custom ranking, rules, synonyms, facets, analytics, and A/B testing: https://www.algolia.com/doc/guides/managing-results/relevance-overview
- Event QA must distinguish events with and without queryID and account for feature requirements: https://www.algolia.com/doc/guides/sending-events/concepts/event-types
- InstantSearch routing and event behavior need explicit testing: https://www.algolia.com/doc/guides/building-search-ui/going-further/routing-urls/js and https://www.algolia.com/doc/guides/building-search-ui/events/js
