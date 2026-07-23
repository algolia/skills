# Example Output: Agent Studio Contract

Use this shape before implementation or launch review.

## Agent Purpose

Help shoppers compare products, narrow choices, and answer product-availability questions using approved Algolia search results. The agent may recommend products and explain tradeoffs, but it must not invent inventory, discounts, delivery promises, or warranty terms.

## Audience And Channel

- Audience: ecommerce shoppers.
- Channel: web product discovery experience.
- Primary goal: increase confident product selection and add-to-cart.
- Secondary goal: reduce unsupported product questions.

## Agent Room Map

| Component | Rollout decision |
| --- | --- |
| Scope | Compare products and narrow choices; exclude account, order, delivery, warranty, and regulated advice. |
| Retrieval | Use the product index with region and availability filters. |
| Memory | Do not enable for the first single-session rollout. |
| Safety | Refuse unsupported claims and hand off account-specific questions. |
| Entry point | Product-discovery chat surface for multi-turn comparison. |

## Allowed Tools And Data

| Tool or source | Allowed use | Guardrail |
| --- | --- | --- |
| Product search index | Retrieve product candidates, filters, availability, and product attributes. | Apply region, availability, and account filters before presenting results. |
| Product detail URL | Link users to product pages. | Do not claim availability unless the result includes it. |
| Conversation context | Use stated preferences such as budget, size, activity, or style. | Do not store sensitive data unless the implementation explicitly supports it. |

## Tool Contract

| Field | Product search rollout |
| --- | --- |
| Trigger | A user asks to find, compare, or narrow products. |
| Constraints | Apply approved availability and region filters; return only safe display fields. |
| Authority | Read-only retrieval. |
| User outcome | Explain tradeoffs and link to supported product records. |
| Failure path | Ask one clarifying question, offer a safe fallback, or hand off when retrieval cannot answer. |
| Measurement | Tool use, product click, add-to-cart, feedback, fallback, and handoff events. |

## Required Readiness Checks

- Data records include useful titles, categories, descriptions, attributes, price, availability, and URLs.
- Secured or restricted records cannot appear for unauthorized users.
- Instructions are scoped to the agent's job and include what to do when the answer depends on context.
- Agent-specific search settings are reviewed for the connected index.
- Prompt suggestions and entry points lead to supported tasks.
- Search events and feedback events are defined before optimization.
- Fallback behavior exists for no results, ambiguous intent, unavailable products, and tool errors.
- The agent refuses requests outside its job, such as medical, legal, warranty, or account-specific claims unless approved tools support them.

## Measurement Plan

| Signal | Purpose |
| --- | --- |
| Product clicked from agent recommendation | Measures whether suggestions are useful. |
| Add to cart after agent interaction | Measures product-discovery impact. |
| Positive or negative feedback | Flags answer quality and tool issues. |
| No-result or fallback turns | Reveals data, relevance, or prompt gaps. |

## Launch Recommendation

Status: limited rollout.

Launch to a controlled audience after validating product filters, event payloads, fallback states, and approved-domain/security configuration. Do not broaden rollout until feedback and conversion events are visible.

## Refinement Loop

1. Review five to ten real Conversations before reading aggregate metrics.
2. Label issues as instruction problem, search/retrieval problem, data gap, guardrail/fallback problem, or integration/event problem.
3. Use Analytics to confirm whether the issue is isolated or recurring.
4. Make one configuration change at a time.
5. Retest the original conversation pattern and one adjacent edge case before expanding rollout.
