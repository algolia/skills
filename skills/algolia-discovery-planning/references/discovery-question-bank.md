# Discovery Question Bank

Use this bank selectively. Ask the minimum number of questions needed to avoid designing the wrong Algolia implementation.

## First-Turn Triage

- What user journey are we improving: search, browse/category, autocomplete, recommendations, internal lookup, support/content discovery, or merchandising?
- What outcome matters most: conversion, revenue, add-to-cart, lead generation, content consumption, support deflection, speed, or admin efficiency?
- What is the primary content type: products, SKUs, variants, articles, locations, people, accounts, tickets, docs, or mixed/federated content?
- Is this a new implementation, migration, redesign, relevance tuning project, analytics/event setup, or launch audit?
- Which environment can we safely change: local, development, staging, production, or a temporary test index?

## Business Context

- What does a "good result" mean for this business and user? Exact textual match, availability, freshness, popularity, margin, geo proximity, personalization, diversity, or editorial control?
- Which searches or categories are most valuable?
- Which failures are most costly: no results, wrong top result, irrelevant recall, missing filters, stale data, slow UI, or unmeasured conversions?
- Who owns relevance decisions after launch: engineering, product, merchandising, content, support, or search team?
- Are there seasonal campaigns, promotions, compliance constraints, or regional catalog differences?

## Data And Governance

- Which source system owns each record field?
- What is the stable identifier for event attribution and updates?
- How frequently does each attribute change?
- Which fields are searchable, filterable, display-only, ranking-only, secured, or internal?
- Are there locales, currencies, tenants, channels, regions, or permissions that require separate records, indices, filters, or secured API keys?
- Do we need a backfill, incremental updates, partial updates, or full reindex pipeline?

## UX Context

- Does the UI need a full search results page, browse/category page, autocomplete, federated search, recommendations module, or all of these?
- Which refinements should users see, and which should be applied silently?
- Should query and refinements be shareable in the URL?
- What should happen on empty results, unavailable products, hidden content, or misspellings?
- What are the mobile filter, sort, and autocomplete expectations?

## Measurement Context

- Which events define success: click, view, add-to-cart, purchase, lead, signup, save, download, support deflection, or custom conversion?
- Are queryID and hit position available at the point where the event fires?
- How is userToken assigned across anonymous and logged-in sessions?
- Which downstream features need events: analytics, A/B testing, personalization, Recommend, dynamic re-ranking, or query categorization?

## Customer Handoff Brief

Use this when the customer needs a practical plan more than a technical deep dive.

- What platform or source system owns the searchable content: commerce platform, CMS, PIM, database, spreadsheet export, API, or mixed sources?
- Who can change data feeds, frontend code, backend checkout or lead flows, analytics tags, and Algolia settings?
- What environments exist: production only, staging, local, sandbox Algolia app, or temporary test index?
- What sample data can be shared safely: 5 representative records, 5 edge-case records, current settings, screenshots, top searches, or event payloads?
- What is the first useful milestone: searchable data, working filters, click events, conversion events, relevance tuning, UI launch, or AI readiness?
- What work can be done with configuration and content decisions, and what work definitely needs code access?

Customer-facing output:

- One short summary of the goal.
- Missing access or source material.
- The smallest useful next step.
- The owner needed for each next step.
- A plain-language risk if the step is skipped.

## Source Notes

- Algolia records should contain information useful for searching, display, sorting, and relevance: https://www.algolia.com/doc/guides/sending-and-managing-data/prepare-your-data
- Relevance improvement starts with searchable attributes and custom ranking, then expands to rules, synonyms, facets, analytics, and A/B testing: https://www.algolia.com/doc/guides/managing-results/relevance-overview
- Event requirements and event types differ by feature: https://www.algolia.com/doc/guides/sending-events/concepts/event-types
