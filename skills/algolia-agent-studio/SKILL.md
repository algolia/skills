---
name: algolia-agent-studio
description: >
  Product-specific Algolia Agent Studio implementation, validation, and optimization guidance. Use when planning, building, integrating, or auditing Agent Studio agents, AI-powered conversational experiences, LLM provider setup, Algolia Search tools, client-side tools, MCP tools, memory, prompting, conversations, turn context, caching, analytics, feedback, authentication, approved domains, guardrails, or tool security. Do NOT use for live Agent Studio configuration, dry runs, publish/deploy actions, or config-as-code operations; use the official algobot-cli skill instead. Do NOT use for generic non-Algolia RAG or chatbot architecture unless Agent Studio is the target product.
license: MIT
metadata:
  author: algolia
  version: "0.4"
---

# Algolia Agent Studio

Use this skill for Agent Studio work after confirming the product goal and the quality of the underlying Algolia data, events, and search configuration. Agent Studio experiences are only as good as the tools, records, guardrails, and measurement loops they can rely on.

## Customer-Facing Standard

- Define the agent contract before setup: purpose, audience, tools, allowed actions, guardrails, escalation, and measurement.
- Treat data, events, permissions, and tool security as prerequisites, not follow-up polish.
- Use public `academy.algolia.com` for learning alignment and public `algolia.com/doc` for current implementation guidance when source-backed context is needed.
- When an Academy metadata reference pack is available, use only its `title`, `url`, `course`, `module`, `learning_objectives`, and `updated_at` fields for structure. If it is stale or no match exists, fall back to live Academy/docs lookup. Do not treat cached metadata as course content or implementation authority.
- Do not require custom Academy/docs access; use customer-provided sources only as optional context.
- When live Algolia data, analytics, index inspection, settings changes, or account actions are needed, use Algolia MCP, the Algolia CLI, or official Algolia skills for the live operation, then apply this skill to interpret results and validate the customer-ready implementation path.
- Produce a launch recommendation: launch, limited rollout, fix first, or do not start.
- Start the first agent with one narrow, high-intent job and the smallest tool/data surface that can solve it; breadth comes after evidence.

## Official Companion Skills

- Use official `algobot-cli` for Agent Studio setup, agent config-as-code, tools, memory, conversations, dry runs, and deploy/publish workflows.
- Use official `algolia-mcp` for live search, analytics, recommendations, and index inspection that inform the agent's tools.
- Use official `algolia-cli` for index, settings, rules, synonyms, or record changes the agent depends on.
- Use this skill after the official tool call to produce the agent contract, readiness gates, security checks, event/feedback plan, and launch recommendation.

## Source-Of-Truth Rules

- Use official `algobot-cli` and current Agent Studio docs for commands, config fields, provider behavior, completions endpoints, tool configuration, memory, analytics, feedback, and deploy/publish steps.
- Do not invent Agent Studio capabilities, endpoint URLs, tool permissions, or memory behavior.
- If the official tool or docs cannot confirm a behavior, label it as an assumption and recommend a dry run or dashboard verification.

## Workflow

1. Read `references/agent-studio-guide.md` before implementation or review.
2. Read `references/example-output.md` when producing an agent contract or customer-facing launch recommendation.
3. Start with `$algolia-discovery-planning` if business goal, audience, channel, or success metric is unclear.
4. Use `$algolia-data-modeling` and `$algolia-index-configuration` when the agent will retrieve Algolia records or answer from search results.
5. Use `$algolia-events-insights` when the experience needs analytics, feedback, personalization, Recommend, NeuralSearch optimization, or conversion measurement.
6. Use `$algolia-release-qa` before launch, especially for guardrails, approved domains, authentication, tool security, and event coverage.
7. Map the agent's room: instructions, tools, retrieval, data access, memory/context, safety, provider, and entry point. Diagnose behavior against that map before blaming the model.
8. Teach the setup as a lifecycle: create and configure, preview and test, publish and integrate, then refine with Conversations and Analytics.

## Questions To Ask

Ask the smallest useful subset before building:

- What job should the agent perform: discovery, product advice, support, shopping assistant, internal operations, merchandising, or content navigation?
- Which entry point will users see first: search bar AI mode, autocomplete, side panel, InstantSearch Chat Widget, embedded assistant, or prompt suggestions?
- Which Algolia indices, tools, or external systems may the agent use?
- Which user attributes, session state, turn context, or memory are allowed?
- Which actions are read-only versus write/action-taking?
- What should the agent refuse, escalate, or hand off?
- What LLM provider, model, region, latency, and cost constraints apply?
- What analytics, feedback, event, or conversion signals define success?
- What domains, auth model, and API-key boundaries are required?
- Which one high-intent user task should the first rollout solve, and what requests are deliberately out of scope?
- Which entry point best matches that task: search AI mode, chat widget, side panel, embedded assistant, or prompt suggestion?
- For each enabled tool, what triggers it, what data/arguments may it use, what result does the user see, and what happens on timeout or refusal?

## Implementation Standards

- Define the agent contract before code: purpose, audience, tools, allowed actions, guardrails, escalation paths, and measurement.
- Treat Quick Setup or templates as starting points, not launch readiness. Review instructions, Search tool settings, memory, prompt suggestions, guardrails, rate limits, cost controls, approved domains, and integration snippet before recommending publish.
- Treat Algolia Search tools as product APIs. Confirm index readiness, filters, searchable attributes, ranking, secured keys, and returned fields.
- Never expose admin keys, unrestricted actions, internal-only data, or unreviewed external tools to a client-facing agent.
- Keep prompts grounded in business policy and available tools. Avoid prompts that imply access to data or actions the agent cannot actually use.
- Instrument feedback and conversion loops early; AI product tuning without events becomes anecdotal.
- Validate failure modes: no results, ambiguous user intent, unavailable items, policy refusal, tool errors, auth failures, and slow LLM/tool responses.
- Use Conversations for qualitative review before relying on aggregate analytics. Look for unclear instructions, bad follow-up behavior, weak retrieval, inappropriate fallback, and guardrail misses.
- Use Analytics as a feedback loop, not a vanity dashboard. Let usage, token/cost patterns, search usage, feedback, and outcome signals drive configuration changes.
- Define each enabled tool as a contract: trigger, allowed parameters, access scope, confirmation requirement, user-visible result, failure response, and measurement event.
- Treat memory as intentional product behavior. Enable it for authenticated, multi-turn value; document identity, retention, consent, and what must never be retained. Do not assume dashboard enablement alone creates safe end-to-end memory.
- Choose the entry point by user moment. Search-side AI helps query refinement and retrieval; a conversational surface supports multi-turn help; prompt suggestions should lead only to tasks the agent can actually complete.

## Anti-Patterns

- Starting with prompts before defining tools, permissions, data boundaries, and success measures.
- Giving a client-facing agent write-capable tools before a read-only rollout has been validated.
- Relying on prompt instructions as the only guardrail for sensitive data or consequential actions.
- Shipping without approved domains, authentication review, fallback/handoff behavior, and feedback measurement.
- Treating Agent Studio as separate from search relevance, event quality, or index permissions.
- Publishing immediately after the preview gives one good answer.
- Treating Conversations as support logs only; they are the fastest way to identify bad instructions, weak retrieval, missing data, and fallback failures.
- Expanding a first agent into a broad assistant before one high-intent, read-only workflow has reliable retrieval, tool use, fallback, and measurement.
- Blaming the selected LLM before checking scope, instructions, tools, retrieval, data access, memory/context, safety, and integration state.

## Academy And Customer Education Alignment

When source-backed guidance is needed, search public Academy sources for Agent Studio and AI-readiness learning objectives and public Algolia docs for setup, tools, events, security, and current product behavior. Use source guidance procedurally, not as copied documentation. Map the request to a customer maturity level and one or more use-case bundles, then provide customer-facing setup, validation, and optimization guidance.

## Maturity Behavior

- Beginner implementation: define the agent job, audience, data sources, and simplest safe read-only flow before tool expansion.
- Production readiness: validate authentication, approved domains, tool boundaries, API keys, fallback behavior, event coverage, handoff paths, and the agent-room troubleshooting trace.
- Optimization: add feedback loops, conversation analytics, tool-result quality review, and measured prompt/tool iteration.
- AI readiness: require clean searchable data, reliable events, permission-aware tools, security review, and a clear launch or fix-first recommendation.

## Output Contract

For implementation, return an agent contract, agent-room map, tool contracts, entry-point choice, setup steps, integration code or configuration, event/feedback plan, security notes, QA cases, and a post-launch refinement loop. For audits, lead with launch blockers and the data/event/tool dependencies that must be fixed first.
