---
name: instantsearch
description: "Build production-quality search experiences (autocomplete, search results pages, faceted search) using InstantSearch. Use when user asks to add search, autocomplete, search-as-you-type, faceted filtering, or a search results page to a React, Vue, or vanilla JS application, or mentions Algolia, InstantSearch, or react-instantsearch. Do NOT use for backend index operations (records, synonyms, settings, API keys), use algolia-cli instead. Do NOT use for analytics, recommendations, or MCP server queries, use algolia-mcp instead. Do NOT use for AI/agent/conversational search, use algobot-cli instead."
license: MIT
metadata:
  author: algolia
  version: '1.0'
---

# InstantSearch

Build production-quality search experiences with InstantSearch. Follow the workflow below in order. Do not skip steps.

## Supported libraries

InstantSearch comes in three libraries. Detect which one applies from the project's dependencies or framework, or ask the user.

| Library             | Package               | When to use                                              |
| ------------------- | --------------------- | -------------------------------------------------------- |
| React InstantSearch | `react-instantsearch` | React, Next.js, Remix                                    |
| Vue InstantSearch   | `vue-instantsearch`   | Vue, Nuxt                                                |
| InstantSearch.js    | `instantsearch.js`    | Vanilla JS, or any framework without a dedicated library |

Once identified, use the matching reference directory (e.g., `references/react/`) for all technology rules, anti-patterns, styling, glossary, and pattern-specific guidance.

> **Note:** References currently cover **React InstantSearch** only. For Vue or vanilla JS, inform the user about limited guidance and ask how to proceed. This also applies to non-autocomplete patterns below.

## Workflow

### 1. Discover

Before writing any code, gather context. Check if InstantSearch is already set up (search client, provider, existing widgets) — if so, read existing configuration instead of re-asking. If starting fresh, collect the following before proceeding. If any information is missing, ask the user rather than assuming.

- **Credentials**: Algolia app ID, search-only API key, and index name. Ask if they have a Query Suggestions index.
- **Schema**: Fetch records to discover attributes and their shape — confirm with the user rather than asking them to list everything. No need to fetch from Query Suggestions: its shape is standard.

  ```bash
  curl -s -X POST \
    "https://${APP_ID}.algolia.net/1/indexes/${INDEX_NAME}/query" \
    -H "x-algolia-api-key: ${API_KEY}" \
    -H "x-algolia-application-id: ${APP_ID}" \
    -H "content-type: application/json" \
    -d '{"params": "hitsPerPage=5"}'
  ```

- **Project inspection**: Read styling approach, breakpoints, component library, and framework to identify which InstantSearch library applies (see table above).
- **Routes & Placement**: Find the detail page route pattern (e.g., `/products/[id]`) and any existing search results page. Verify it reads query parameters and renders dynamic results. Find where the search experience should live in the UI.
- **Rendering**: Present numbered options for how results should appear, based on available schema attributes and project design. Refer to the pattern's features reference.

Do not proceed until you have credentials, schema, rendering preferences, and an understanding of the project's design.

### 2. Build

This skill currently covers **autocomplete** for React. Read both the pattern-specific and library-level references before writing code.

**Autocomplete (React):** [features](references/react/autocomplete/features.md) · [styling](references/react/autocomplete/styling.md) · [anti-patterns](references/react/autocomplete/anti-patterns.md)

**Library-level (apply to all patterns):** [technology-rules](references/react/technology-rules.md) · [anti-patterns](references/react/anti-patterns.md) · [styling](references/react/styling.md) · [glossary](references/react/glossary.md)

If unsure how to implement a feature with built-in widgets, ask the user. Do not fall back to legacy libraries or custom connectors.

### 3. Style

Follow the library's styling guide step by step, then apply the pattern-specific styling guide. Match the site's existing CSS methodology, color scheme, typography, spacing, and component patterns.

### 4. Review

Review your work against the library's anti-patterns, the pattern-specific anti-patterns, and the features checklist. Fix any violations.
