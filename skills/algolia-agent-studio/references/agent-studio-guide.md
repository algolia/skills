# Agent Studio Guide

## Current Docs To Verify

The Algolia docs navigation checked on 2026-07-22 lists Agent Studio under AI-powered experiences with these areas:

- Get started: quickstart, dashboard, LLM providers, integration.
- Extend: tools overview, Algolia Search tool, Algolia Recommend tool, Display Results tool, client-side tools, MCP tools, memory.
- Customize: prompting, conversations, turn context, caching, analytics, feedback, experimental features.
- Security: user authentication, approved domains, guardrails, tool security.
- Reference: agent configuration.

Verify current docs before changing live configuration:

- https://www.algolia.com/doc/guides/algolia-ai/agent-studio
- https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/quickstart
- https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/integration
- https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/tools/algolia-search
- https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/analytics
- https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/feedback
- https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/guardrails

Current public docs position Agent Studio as a beta feature. Treat setup, launch recommendations, endpoint behavior, and production commitments as docs-verified before implementation.

## Agent Contract

Define:

- User and business goal.
- Entry point and channel.
- Available Algolia indices and external tools.
- Allowed read actions.
- Allowed write/action-taking actions.
- Authentication and user context.
- Guardrails and refusal policy.
- Escalation and handoff behavior.
- Analytics, feedback, and conversion measurement.
- Rollback or kill-switch plan.

## Academy Setup Flow

Teach Agent Studio as more than prompt setup. A good agent is scoped, connected to the right data, constrained by safety settings, integrated into the right user moment, and refined through real usage.

Use this customer-friendly sequence:

1. Choose Quick Setup or a template that matches the experience type.
2. Define scoped instructions: job, audience, tone, boundaries, and what to do when context is missing.
3. Connect the Search tool or other approved tools.
4. Review agent-specific search settings for the connected index or indices.
5. Decide whether memory, turn context, prompt suggestions, or AI mode entry points are appropriate.
6. Configure safety controls: custom guardrails, fallback responses, rate limits, cost controls, and approved domains.
7. Preview with happy path, ambiguous, out-of-scope, no-result, and blocked scenarios.
8. Publish only after readiness gates pass.
9. Integrate with the generated snippet, AI mode entry points, prompt suggestions, InstantSearch Chat Widget, or framework-specific integration.
10. Refine with Conversations and Analytics.

Agent behavior comes from the full configuration: instructions, tools, data, search settings, memory, safety controls, integration context, and feedback loops.

## The Agent Room

Use this map to define scope and diagnose unexpected behavior. An agent can only work with what is available in its configured room.

| Room component | Define | Review when behavior is weak |
| --- | --- | --- |
| Scope and instructions | Job, audience, boundaries, clarifying questions, refusal, and handoff. | Is the task in scope and is the instruction specific enough? |
| Tools | Enabled tools, triggers, allowed arguments, action boundaries, and user-visible output. | Does the agent actually have the required tool and a clear reason to call it? |
| Retrieval and search settings | Connected indices, required filters, returned fields, ranking/retrieval behavior. | Did the tool retrieve useful, permission-safe records for the task? |
| Data and context | Index access, frontend turn context, authenticated context, and allowed fields. | Was the needed data connected and available at runtime? |
| Memory | Identity, retention, consent, recall purpose, and prohibited information. | Did the task require durable prior context, and was it safely implemented? |
| Safety and operations | Guardrails, fallback, rate/cost limits, domains, auth, and ownership. | Was the request blocked, limited, escalated, or handled safely? |
| Provider and entry point | Provider/model constraints and the UI moment where the user meets the agent. | Is the experience appropriate for the job and is the integration passing context correctly? |

The model generates language. It does not grant access to data, tools, memory, or actions that are absent from this room.

## Start Narrow, Then Expand

Start the first release with one high-intent job, a read-only tool surface, and a short list of representative user tasks. Good candidates include guided product discovery, policy/support retrieval, or documentation navigation.

State what the rollout does not handle. Expand only after Conversations show reliable retrieval and behavior, Analytics shows the experience is used as intended, and the team can attribute outcomes.

## Data And Search Readiness

Before an Agent Studio implementation depends on Algolia Search tools:

- Confirm target indices have stable objectIDs, useful display fields, semantic text fields, and access-control fields.
- Confirm searchable attributes, custom ranking, synonyms, rules, filters, and replicas match the assistant journey.
- Confirm secured keys or filters prevent cross-user, cross-account, region, or permission leaks.
- Confirm the agent can explain or cite retrieved records when the product experience requires it.
- Confirm no hidden/internal attributes are exposed in tool responses or prompts.

## Tool And Entry-Point Contracts

For every tool, record its contract before enabling it.

| Contract field | Define |
| --- | --- |
| Trigger | What user intent should cause the tool to run? |
| Inputs and constraints | Which parameters, filters, and returned fields are allowed or always applied? |
| Authority | Is it read-only, a safe client UI action, or a consequential action requiring confirmation? |
| User outcome | What does the user see after the result: answer, record link, updated UI state, handoff, or refusal? |
| Failure path | What happens for no result, timeout, auth failure, invalid input, or unavailable service? |
| Measurement | Which tool, click, conversion, feedback, or handoff event proves it helped? |

Choose the entry point by user moment:

- Search AI mode or filter suggestions for query refinement within search.
- Chat widget or embedded assistant for multi-turn discovery, support, or comparison.
- Side panel for contextual help without interrupting the main task.
- Prompt suggestions only for supported follow-ups the agent can retrieve or perform.

Use current docs and the official implementation skill for exact widget, API, and tool configuration details.

## Readiness Gates

Do not treat Agent Studio as ready until these gates pass:

1. Data gate: target indices have stable objectIDs, useful display fields, permission-safe returned attributes, and records that match the agent's job.
2. Relevance gate: search tools return acceptable results for representative user tasks, including ambiguous, low-result, and no-result cases.
3. Events gate: feedback, clicks, conversions, or resolution outcomes are instrumented well enough to evaluate the agent.
4. Security gate: approved domains, authentication, tool permissions, guardrails, and least-privilege credentials are validated.
5. Operations gate: fallback, handoff, rollback, cost/latency expectations, and ownership are defined.

If one gate fails, report it as a blocker or explicit assumption before recommending launch.

## Conversations And Analytics Review

Before launch, use preview and test conversations to answer:

- Did the agent understand the user's job and ask clarifying questions when needed?
- Did the Search tool retrieve useful records for the task?
- Did the response stay grounded in retrieved data and approved policy?
- Did guardrails or fallback responses trigger for unsafe, out-of-scope, or unsupported requests?
- Did the agent handle no results, low confidence, unavailable items, tool errors, and follow-up turns?

After deployment, use Analytics as a refinement loop:

- Total conversations and trend.
- Search/tool usage.
- Token usage, latency, and cost.
- Positive/negative feedback.
- Fallback, handoff, or abandonment patterns.
- Conversions or resolved outcomes when instrumented.

Recommended loop: user interactions -> Conversations/Analytics insight -> configuration adjustment -> targeted retest -> measured improvement.

### Troubleshooting Trace

When an answer is incomplete, unsafe, or wrong, diagnose in this order:

1. Request and scope: should this agent handle the request?
2. Instructions: did they define the role, boundary, and clarification behavior?
3. Tools: was the required tool enabled and described clearly enough to be selected?
4. Retrieval: did the tool query the right index with the right filters and return useful records?
5. Data/context: was the required record, authenticated context, or frontend turn context available?
6. Memory: did the task require prior context, and was it intentionally enabled and implemented?
7. Safety/fallback: did the guardrail, confirmation, or escalation path work as designed?
8. Provider/integration: only then review model/provider limits, latency, transport, or rendering behavior.

Record the broken link and retest the original scenario plus one adjacent edge case after each change.

## Integration Facts

Verified against the completions endpoint and Conversations view in October 2026. Re-check the [conversations guide](https://www.algolia.com/doc/guides/algolia-ai/agent-studio/how-to/conversations.md) and [completions reference](https://www.algolia.com/doc/rest-api/agent-studio/completions) before relying on them; conversation endpoints are beta.

- **Conversation identity.** The request body takes an optional top-level `id` (prefix `alg_cnv_`). Without it, Agent Studio generates a new conversation per request. A turn that calls a client-side tool is two requests, so it shows as two conversations, and a follow-up that replays history shows as a third.
- **Client-chosen ids are global to the agent.** Hash a browser-supplied conversation name with the authenticated tenant and user on the server, so one user cannot write into another's transcript.
- **Message ids must be stable.** When a client replays history, send each message with the id it was first sent with (prefix `alg_msg_`). A replay with new ids duplicates turns; a replay with the same ids updates them.
- **Titles come from the first user message** (up to 60 characters). Put the user's question first in that message and any serialized context after it.
- **Request-time search parameters are a whitelist.** `algolia.searchParameters[index]` accepts only filtering and personalization keys (for example `filters`, `facet_filters`, `optional_filters`, `distinct`, `attributes_to_retrieve`, `user_token`). `hitsPerPage`, `attributesToHighlight` and `attributesToSnippet` return HTTP 422 there. Set them on the Search tool's index configuration instead.
- **Default retrieval is large.** Unset, each search returns 20 hits with full records plus `_highlightResult` and `_snippetResult`; on one text-heavy index the markup was half the payload. For answer generation, set `hitsPerPage`, `attributesToRetrieve`, and empty `attributesToHighlight` and `attributesToSnippet` on the tool.
- **The Conversations list loads after the page.** It shows "No conversations found" until its request returns, which can take well over ten seconds. Wait for it before concluding anything.

## Latency

Trace a streamed completion (`stream=true`) and time the events: `start`, `tool-input-available`, `tool-output-available`, the first `text-delta`, and `finish`. On a two-index retrieval agent the split was roughly: planning generation 3–6 s, search about 40 ms, results to first text 1–3 s, answer streaming 2–3 s.

Levers, largest first:

1. **Retrieve before the agent when retrieval is predictable.** Run the same searches server-side, concurrently with other request preparation, and pass compact results in the request context with an instruction to answer from them. Keep the Search tool attached as a fallback. On one implementation this took median time to first text from 7.9 s to 2.7 s, and the agent made no tool calls of its own. Trade-offs to handle: apply the same access filters the tool uses; build a sensible query for short follow-ups (for example, include the previous question); and note that Agent Studio's search-usage analytics no longer reflect retrieval.
2. **Shrink retrieval payloads** as described in Integration Facts.
3. **Shorten the answer contract.** Output length is streaming time; a structured envelope that repeats citations adds tokens after the answer.
4. **Model choice last.** Compare models only after the phases above are measured.

Benchmark changes against the published agent with several distinct questions per variant. Identical requests can be served from Agent Studio's response cache in well under a second, which hides the real cost.

## Events And Feedback

Plan events early:

- Search or tool result impressions when useful.
- Clicks on records, recommendations, or suggested actions.
- Conversions such as add-to-cart, purchase, lead, save, support resolution, or content completion.
- Explicit feedback such as thumbs up/down, reason codes, comments, and escalation.
- Conversation-level outcomes such as abandoned, resolved, handed off, or converted.

Use stable event names and preserve userToken/session identity when the same experience also powers search, NeuralSearch, personalization, or Recommend.

## Tooling Guardrails

- Start read-only unless the use case clearly needs actions.
- Require explicit user confirmation before consequential actions.
- Scope client-side tools to safe UI actions.
- Scope MCP or server tools with least-privilege credentials.
- Validate arguments before tool execution.
- Handle tool timeouts and errors with user-safe responses.
- Never let prompt text be the only protection for sensitive or write-capable tools.

## QA Checklist

- A two-turn conversation with a tool call appears as one conversation in Conversations, titled by the question, with no duplicated turns.
- Time to first text and total time measured per phase against the published agent, not the dashboard preview.
- Happy path and ambiguous intent.
- No results and low-confidence retrieval.
- Tool error and slow response.
- Authenticated and unauthenticated flows.
- Out-of-scope or unsafe requests.
- Prompt injection in user text and retrieved content.
- Cross-tenant/account/region access boundaries.
- Feedback and analytics payloads.
- LLM provider, model, latency, and cost assumptions.
- Approved domains and deployment environment.
- Prompt suggestions route users into supported tasks instead of broad, unanswerable requests.
- Entry points match user intent: search bar AI mode, autocomplete, side panel, embedded assistant, or chat widget.
- Existing agents using older Search tooling are reviewed before relying on newer agent-specific search settings.
- One high-intent rollout job, its deliberately out-of-scope requests, and the selected entry point are documented.
- Each enabled tool has a trigger, constrained inputs, authority, user outcome, failure path, and measurement event.
- Memory is enabled only with a documented identity, retention, consent, and safe-use plan.

## Related Skills

- `$algolia-data-modeling`: index and record readiness.
- `$algolia-index-configuration`: relevance and filters.
- `$algolia-events-insights`: events, userToken, feedback, conversions.
- `$algolia-release-qa`: security and launch checks.
