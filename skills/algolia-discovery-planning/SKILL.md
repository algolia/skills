---
name: algolia-discovery-planning
description: >
  START HERE for any non-trivial Algolia work — building, adding, migrating, redesigning, auditing, or configuring search, browse, autocomplete, indexing, relevance, recommendations, personalization, merchandising, events, or analytics. Invoke this FIRST even when the task already seems scoped or the user names one specific feature (e.g. "add InstantSearch", "build a storefront search"): its job is to map the request to the full Algolia implementation lifecycle and load every companion skill each in-scope phase needs (algolia-search-implementation, algolia-data-modeling, algolia-index-configuration, algolia-ui-libraries, algolia-instantsearch-ui, algolia-autocomplete, algolia-events-insights, algolia-neuralsearch, algolia-agent-studio, algolia-release-qa) rather than jumping straight into a single skill. This skill plans and orchestrates; the focused companion skills and the official Algolia skills execute. Do NOT use for live account inspection or write actions; use algolia-mcp or algolia-cli for those.
license: MIT
metadata:
  author: algolia
  version: "0.4"
---

# Algolia Discovery Planning

Use this skill before implementation work when the business goal, data shape, UX, event strategy, or success criteria are unclear. The job is to slow down just enough to avoid encoding the wrong search strategy.

## Orchestrate The Whole Library (do this first)

These skills are a **suite that spans the Algolia implementation lifecycle**, not a set of independent tools where one match wins. A request that looks like a single-skill task ("build search", "add autocomplete", "index my data") almost always spans several phases. Before writing code or changing settings:

1. **Map the request to the lifecycle** and mark every phase that is in scope:

   | Phase | Load this skill | Typical trigger |
   | --- | --- | --- |
   | Run a net-new build end to end | `algolia-search-implementation` | greenfield search/browse/ecommerce build; keeps checkpoints, signposts, and deferrals explicit |
   | Shape the data / records | `algolia-data-modeling` | new index, catalog, variants, objectID, ETL |
   | Configure relevance | `algolia-index-configuration` | searchable attrs, ranking, facets, synonyms, rules, replicas, sort |
   | Choose the UI library | `algolia-ui-libraries` | framework fit, InstantSearch vs Autocomplete, SSR/routing, mobile SDKs, upgrades |
   | Build the results/browse UI | `algolia-instantsearch-ui` | search results page, filters, category/browse |
   | Build typeahead | `algolia-autocomplete` | query suggestions, autocomplete panel |
   | Instrument behavior | `algolia-events-insights` | click/view/add-to-cart/conversion, personalization, Recommend, A/B |
   | Pre-launch check | `algolia-release-qa` | before shipping or after a risky change |
   | AI / conversational | `algolia-agent-studio`, `algolia-neuralsearch` | agents, RAG, semantic/neural retrieval |

2. **State the phase plan** to the user: which phases apply, which skill owns each, and the order (a greenfield build usually runs data-modeling → index-configuration → instantsearch-ui / autocomplete → events-insights → release-qa).

3. **Load each in-scope skill via the Skill tool for its phase, and actually apply its guidance.** Do not skip a phase silently, and do not substitute your own knowledge for a skill that applies. If you deliberately skip a phase, say so and why.

4. **Never claim a skill informed the work unless it was opened.** Report which skills ran and what each changed.

This is the default behavior for any multi-phase task. Only collapse to a single focused skill for a genuinely narrow, single-phase ask (e.g. "rename one facet label").

## Customer-Facing Standard

- Ask only the questions needed to choose a responsible next step.
- State assumptions plainly when proceeding with incomplete context.
- Use public `academy.algolia.com` for learning alignment and public `algolia.com/doc` for current implementation guidance when source-backed context is needed.
- When an Academy metadata reference pack is available, use only its `title`, `url`, `course`, `module`, `learning_objectives`, and `updated_at` fields for structure. If it is stale or no match exists, fall back to live Academy/docs lookup. Do not treat cached metadata as course content or implementation authority.
- Do not require custom Academy/docs access; use customer-provided sources only as optional context.
- When live Algolia data, analytics, index inspection, settings changes, or account actions are needed, use Algolia MCP, the Algolia CLI, or official Algolia skills for the live operation, then apply this skill to interpret results and validate the customer-ready implementation path.
- Produce a concrete next step, owner handoff, and validation artifact.

## Official Companion Skills

- Use official `algolia-mcp` when discovery needs live search, analytics, recommendations, or index discovery.
- Use official `algolia-cli` when discovery identifies records, settings, rules, synonyms, keys, backups, or index operations.
- Use official `algobot-cli` for Agent Studio, RAG, conversational AI, and agent configuration paths.
- Use official `instantsearch` for production InstantSearch or Autocomplete implementation paths.

## Source-Of-Truth Rules

- Do not answer account-specific questions from memory. Use MCP, CLI, dashboard exports, customer-provided screenshots, or sample files when live evidence is needed.
- Do not recommend a product capability, package, command, or API shape without checking the official skill or current public docs when it affects implementation.
- If evidence is unavailable, label the recommendation as provisional and name the exact artifact needed to confirm it.

## Workflow

1. Identify the implementation surface: indexing, relevance configuration, Search UI, Autocomplete, events, analytics, recommendations, personalization, merchandising, migration, or QA.
2. Ask only the questions that block a responsible first design. Do not ask every checklist item at once.
3. If the user wants you to proceed without answers, state the assumptions and choose reversible defaults.
4. If the customer does not have a dedicated development or Algolia team, produce a practical handoff plan before implementation: what can be decided now, what access is needed, what likely requires developer help, and the safest first milestone.
5. Load **every** in-scope companion skill (usually several, per the lifecycle map above), in phase order, and apply each — do not stop at the first match:
   - `$algolia-search-implementation` for net-new builds, as the checkpoint checklist that spans the phases below.
   - `$algolia-data-modeling` for records, indices, replicas, ETL, and record identity.
   - `$algolia-index-configuration` for relevance, ranking, facets, synonyms, rules, and replicas.
   - `$algolia-events-insights` for click, conversion, view, and Add-to-Cart events.
   - `$algolia-ui-libraries` for choosing the current UI library and docs path before UI implementation.
   - `$algolia-instantsearch-ui` for search results pages and browse/category experiences.
   - `$algolia-autocomplete` for query suggestions and typeahead experiences.
   - `$algolia-release-qa` for launch checks, diagnostics, and regressions.

## Context Questions

Read `references/discovery-question-bank.md` when the task is ambiguous or customer-facing. Select 3-7 questions from the relevant section, then proceed with explicit assumptions.

Prefer questions that uncover:

- Business outcomes: revenue, conversion, deflection, content discovery, operational efficiency.
- Users and journeys: searchers, merchandisers, developers, support agents, admins.
- Content and data: product, article, location, user-generated, B2B catalog, secured content.
- Ranking intent: exact match, popularity, margin, availability, freshness, geo, personalization, business priority.
- UX shape: search page, category browse, federated search, autocomplete, filters, sort-by, recommendations.
- Measurement: events available, conversion definitions, analytics ownership, A/B testing appetite.
- Governance: environments, index naming, access controls, rollout plan, rollback plan.

## Academy And Customer Education Alignment

When source-backed guidance is needed, search public Academy sources for relevant learning objectives and public Algolia docs for implementation details. Classify the request by maturity level: beginner implementation, production readiness, optimization, or AI readiness. Also classify the use case: ecommerce search, content search, B2B catalog, support knowledge base, marketplace, or AI shopping assistant.

## Start Prompt

When the user is unsure where to begin, offer this prompt:

```text
Use the Algolia Discovery Planning skill to help me choose the right implementation path. Ask me only the questions needed to understand my goal, data, search UI, events, and launch risk. Assume I may not know which technical details matter yet. Then recommend the next Algolia skill, the smallest useful first milestone, and the validation artifact I should create.
```

## Maturity Behavior

- Beginner implementation: identify the simplest correct first milestone and the minimum source material needed.
- Production readiness: identify launch blockers, owners, rollback needs, and validation artifacts.
- Optimization: identify baseline metrics, representative query sets, and controlled improvement paths.
- AI readiness: identify whether data, events, permissions, and relevance evaluation are strong enough for NeuralSearch, Agent Studio, or AI assistants.

## Output Contract

When discovery is needed, produce:

- Known facts.
- Open questions that materially change the design.
- Assumptions you will use if the user wants you to continue.
- Recommended next skill or implementation step.
- Customer handoff notes when the team needs help from a platform owner, developer, analytics owner, or implementation vendor.
- Evidence needed before implementation, such as sample records, settings export, analytics screenshots, event payloads, or code access.

Keep the response short enough that the user can answer. The point is momentum with fewer hidden traps.
