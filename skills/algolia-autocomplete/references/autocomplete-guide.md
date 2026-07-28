# Autocomplete Guide

## Official Skill Bridge

Use the official `instantsearch` skill and current Algolia docs as the implementation authority. This guide owns the customer-facing choices that determine whether an autocomplete is useful and verifiable.

| Use the official skill/docs for | Use this skill for |
| --- | --- |
| Package APIs, supported framework patterns, renderers, plugins, code-level integrations, and installed-library checks. | Source strategy, customer journey, selection and URL contract, mobile behavior, attribution handoff, and QA. |
| Current Autocomplete or InstantSearch integration details. | Whether a source should exist, what it means to the user, when it appears, and what happens after selection. |

Work in this sequence: frame the journey and source contracts here, implement with the official skill/docs, then return here for customer-readiness QA.

## Academy Experience Quality Standard

Use this review before calling an Autocomplete experience ready. Passing an API smoke test alone is insufficient.

| Check | Pass when | Typical failure |
| --- | --- | --- |
| Helpful | Each visible item helps complete, improve, narrow, resume, or redirect a search. | Internal terms, generic noise, or content with no next-step value. |
| Clear | A user can distinguish a suggested search, direct record, category scope, recent search, or page. | Unlabeled federated groups or mixed selection behavior without cues. |
| Focused | The panel prioritizes the most useful few choices. | A mini results page, excessive source groups, or product cards overwhelming suggestions. |
| Device-usable | The best guidance remains usable with the mobile keyboard open and stays close to the input on desktop. | Hidden suggestions, tiny touch targets, or needless internal scrollbars. |
| Accessible | Pointer, touch, and keyboard users get equivalent navigation, destinations, and visible active states. | Enter opens a different path than click, or focus feedback is unclear. |

Ask the practical question: “Does this help the user take the next step?” Do not add a source merely because it can be technically connected.

## Experience Design

Autocomplete should help users express intent. Decide whether the panel should show:

- Query suggestions.
- Products or records.
- Categories.
- Content results.
- Recent searches.
- Popular searches.
- Actions or shortcuts.
- Redirects.
- Multiple federated sources.

Order sources by user value and keep each source small enough for fast scanning.

## Source Contract

Define the following before implementation. A source that cannot complete this contract is not ready to expose.

| Source | Appears when | Uses | Fills input with | Selection outcome | Carries forward | Event treatment |
| --- | --- | --- | --- | --- | --- | --- |
| Query suggestions | User types, and optionally on focus | Query Suggestions index | Suggested query | Submit or route to results | Query and, if selected, approved category scope | Result-page interactions are attributed to the resulting search. |
| Product/content hits | User types | Primary or federated index | Usually the record label, only if continuing search | Open the record | Record URL and any required context | Send a click only when the source response provides search attribution. |
| Category suggestion | User types or focus state | Static, facet, or Query Suggestions category data | Query if present | Route to a category page or scoped search | Explicit category/filter state | Attribute the resulting search, then downstream interactions. |
| Recent search | Focus or empty query | Approved local or server-side history | Prior query | Resubmit or route to prior search | Query and any retained, safe scope | Treat the subsequent results search as the attribution origin. |
| Redirect/action | Exact approved condition | Rules or static source | Depends on action | Navigate or execute the approved action | Only declared parameters | Track as a navigation/action, not a fabricated search click. |

For every source, define the same outcome for mouse, touch, Enter, and keyboard navigation. If a source renders a link, ensure its URL encodes the same query and scope used by the selection handler.

## Journey-To-Pattern Selector

Choose advanced patterns in response to a user problem, not as a feature checklist.

| User need | Prefer | Guardrail |
| --- | --- | --- |
| Resume an earlier task | Recent searches in the empty-query state. | Confirm storage and privacy expectations; keep the list short. |
| Find a starting point before typing | Popular searches, useful categories, or approved shortcuts. | Keep it helpful rather than promotional. |
| Narrow an ambiguous broad query | Category scope. | Show only one or two meaningful scopes and carry the chosen scope into the result. |
| Reach policies, FAQs, stores, or support | Federated content source. | Label the content type and make the destination predictable. |
| Avoid a likely no-result dead end | Better query suggestions, alternatives, or a relevant non-product path. | Do not imply a result exists when it does not. |

## Content Budget By Device

Use the Academy ranges as a starting point, then validate with real content and the actual viewport rather than treating them as a fixed product rule.

| Surface | Starting budget | Layout standard |
| --- | --- | --- |
| Mobile | About 4-7 query suggestions and only the strongest few direct results. | Use a focused overlay, keep the input at the top, make rows easy to tap, and retain a visible “see all results” path above the keyboard. |
| Desktop | About 6-10 query suggestions with a small adjacent or following direct-result group. | Keep the panel visually connected to the input, label groups, show hover/focus state, and avoid a needless internal scrollbar. |

Keep the input-clear action separate from closing a mobile overlay. They solve different user intentions.

## Academy Mental Model

Use this distinction when explaining or reviewing autocomplete:

- Query Suggestion: "Here is something useful to search for."
- Product or content result: "Here is a record you may want to open."
- Recent search: "Here is something you already started."
- Autocomplete: the full search-box experience that can combine those sources.

A good autocomplete experience reduces effort before the user commits to a results page. It should help the user ask a better question, resume a prior search, or jump directly to a useful record without overwhelming them.

## Query Suggestions Readiness

Before connecting Query Suggestions to Autocomplete, verify:

- The source index is the index users actually search.
- The Query Suggestions index exists and is not confused with the source index.
- Suggestions are generated from useful search behavior, approved external suggestions, or facet values.
- Minimum letters and minimum hits are configured to avoid vague or low-value suggestions.
- Banned words or exclusions remove offensive, internal, test, stale, or irrelevant terms.
- Sample suggestions are clear, useful, searchable, clean, and likely to return worthwhile results.

If suggestions are noisy, fix the Query Suggestions configuration before polishing the UI.

### Category-Bearing Suggestions

Categories are useful only when their role is unambiguous. Choose one:

- Scope: carry the selected category into the results-page filter or InstantSearch state.
- Destination: route to a category landing page with the selected query.
- Context only: show the category as a label and do not imply filtering.

Do not show a category merely because it is available in the source data. Test the URL or state handoff with a real category-bearing suggestion and confirm that keyboard selection behaves exactly like pointer selection.

For a compact category-scope experience, show only one or two strong scopes, distinguish them from ordinary query suggestions, and phrase them as a scope, such as “in Women's Running.” Avoid repeating the typed query as a separate category item.

## Selection Behavior

For each source, define what selection does:

- Submit a query.
- Navigate to a search results page.
- Update InstantSearch UI state.
- Navigate directly to a record.
- Apply a category/filter.
- Execute an action.

Do not leave selection behavior implicit; this is where many autocomplete implementations feel broken.

Suggested defaults:

- Query Suggestions usually submit or navigate to a search query.
- Product/content results usually navigate directly to a record.
- Category suggestions usually apply a scope/filter or navigate to a category page.
- Recent searches usually resubmit the prior query.
- Federated support/content results should use labels and destinations that make their source obvious.

Different sources can have different selection behavior, but the visual design must make the difference clear.

## Focus, Empty, And Failure States

The zero-query panel is part of the experience, not leftover space. Choose one intentional behavior:

- Keep the panel closed until the user types.
- Open with recent searches when resumption is valuable and storage is appropriate.
- Open with approved popular searches, categories, or shortcuts when they help discovery.

For every visible group, decide what happens when it is empty, slow, or unavailable. Hide empty groups cleanly, use an approved fallback where it preserves user value, and avoid blank headings or stale items. A stalled indicator should acknowledge delay without preventing users from continuing to type or submit.

### No-Result Guidance

Autocomplete should prevent dead ends where it can. When a query has weak product intent or is likely to fail, prefer a better suggested query, a useful category, an approved non-product result, or an explicit route to all search results. Keep the guidance truthful: do not turn an unavailable product query into an unrelated direct-result list.

## Implementation Guardrails

- Use Autocomplete's `getSources` model and plugins when possible.
- Use `getAlgoliaResults` for Algolia-backed sources.
- Preserve keyboard navigation, focus management, and accessible labels.
- Test detached mobile behavior when enabled.
- Avoid returning too many hits per source.
- Debounce and loading states should make latency understandable without blocking typing.
- When integrated with InstantSearch, keep query state synchronization one-way or carefully controlled to avoid loops.
- Prefer the library's accessible generated input and item URL behavior unless the official implementation guidance calls for a custom renderer.
- Keep the source contract in code comments or implementation notes so a later source change does not silently change routing or attribution.

## Event And Analytics Notes

- Track suggestion clicks and direct-result clicks according to the downstream analytics needs.
- Preserve userToken across autocomplete and the search/results page.
- If a suggestion leads to a search results page, ensure the resulting search can still generate queryID-attributed events.
- If a direct product result is clicked from autocomplete, choose the event method that accurately reflects whether the item came from an Algolia query.
- Do not infer queryID attribution for a static, recent, redirect, or otherwise non-search source. Preserve the source type so the event plan stays honest.

## Integration Handoff

For a separate results page, define the route parameters and verify the page reads them into its search state. For same-page InstantSearch, define the single owner of query and refinement state, then verify an Autocomplete selection updates it without a duplicate search loop.

For federated results, label the source and make the destination predictable. A user should be able to tell whether Enter opens a product, searches a query, scopes a category, or navigates to a different content surface.

## Staged Implementation And Review

Build and verify in layers. This avoids spending time on templates or complex federation before the foundations are real:

1. Mount the generated Autocomplete input in an empty container and confirm it accepts focus and typing.
2. Connect and review Query Suggestions with realistic user prefixes; fix noisy source data before display polish.
3. Add a small direct-result source, distinct label, required display fields, and a keyboard-safe destination.
4. Add open-on-focus content only when the empty-query journey has a purpose; validate recent searches and popular suggestions separately.
5. Validate detached/mobile behavior with the keyboard open, then run the quality standard and event handoff QA.

Use official docs and the official implementation skill for current package and plugin syntax at each layer.

## QA

- Keyboard navigation: arrow keys, Enter, Escape, Tab.
- Mouse and touch selection.
- Empty query behavior.
- No suggestions behavior.
- Multiple source ordering and labels.
- Mobile detached mode.
- Slow network and stalled search indicator.
- Integration with URL routing or InstantSearch state.
- Pointer and keyboard selection produce the same URL or search state.
- Category-bearing suggestions either carry their intended scope or are clearly context-only.
- Query Suggestions use the Query Suggestions index, not the source index.
- Suggestion text is shopper/user-friendly, not internal or test language.
- Mobile layout remains usable when the keyboard is open.
- Each empty, slow, or unavailable source has intentional behavior with no blank labeled panel.
- The quality standard passes: helpful, clear, focused, device-usable, and accessible.
- Mobile keeps the top input and strongest guidance visible with the keyboard open; clear and close actions are distinct.

## Review Output Template

Return these sections when planning or auditing:

1. Official Skill Usage Note: framework/package and current implementation authority.
2. Source Contract: source order, trigger, selection destination, scope handoff, fallback, and event treatment.
3. Customer UI Plan: focus/empty behavior, mobile mode, labels, and direct-result versus query-submission cues.
4. Data and Event Readiness: required record fields, URLs, objectIDs, userToken continuity, and queryID boundaries.
5. QA: keyboard, pointer, touch, mobile, routing/state, latency, no-suggestions, and attribution checks.

## Source Notes

- Autocomplete is a production-ready JavaScript library for building autocomplete experiences: https://www.algolia.com/doc/ui-libraries/autocomplete/introduction/what-is-autocomplete
- Autocomplete sources can include static terms, Algolia results, recent searches, and other sources, while the developer controls rendering: https://www.algolia.com/doc/ui-libraries/autocomplete/introduction/what-is-autocomplete
- Autocomplete does not provide the same ready-made UI widget set as InstantSearch; it provides behavior and accessibility primitives while the implementation controls rendering: https://www.algolia.com/doc/ui-libraries/autocomplete/introduction/what-is-autocomplete
- Get started with Autocomplete: use `@algolia/autocomplete-js` for the standard renderer; use the core package only when a custom renderer is genuinely needed. Autocomplete generates an accessible input from a container, while item URLs support direct keyboard access: https://www.algolia.com/doc/ui-libraries/autocomplete/introduction/getting-started
- Query Suggestions can carry category data; define how the category is applied to same-page state or a routed results URL: https://www.algolia.com/doc/ui-libraries/autocomplete/guides/adding-suggested-searches
- Official plugins cover recent searches, Query Suggestions, Algolia Insights, tags, and redirect URLs. Confirm the current API in docs before coding: https://www.algolia.com/doc/ui-libraries/autocomplete/core-concepts/plugins
