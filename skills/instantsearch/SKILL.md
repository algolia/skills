---
name: instantsearch
description: >-
  Build production-quality search experiences (autocomplete, search results pages, faceted search) using InstantSearch.
  Use when user asks to add search, autocomplete, search-as-you-type, faceted filtering, or a search results page
  to a React, Vue, or vanilla JS application, or mentions Algolia, InstantSearch, or react-instantsearch.
  Do NOT use for backend index operations (records, synonyms, settings, API keys), use algolia-cli instead.
  Do NOT use for analytics, recommendations, or MCP server queries, use algolia-mcp instead.
  Do NOT use for AI/agent/conversational search, use algobot-cli instead.
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

> **Note:** This skill currently has references for **React InstantSearch** only. If the project uses Vue or vanilla JS, let the user know and ask how they'd like to proceed.

## Workflow

### 1. Discover

Before writing any code, gather context. First check if InstantSearch is already set up in the codebase (search client, provider, existing widgets). If so, read the existing configuration instead of re-asking.

If starting fresh, go step by step, waiting for the user's answer before moving on.

- **Credentials**: Ask the user for their Algolia app ID, search-only API key, and index name.
- **Query Suggestions**: Ask the user if they have a Query Suggestions index.
- **Schema**: Once you have credentials, fetch a few records from the main index to discover the available attributes and their shape. Confirm with the user rather than asking them to list everything. The schema is needed before you can propose rendering options. No need to fetch from the Query Suggestions index: its shape is standard and handled by the widget.

  ```bash
  curl -s -X POST \
    "https://${APP_ID}.algolia.net/1/indexes/${INDEX_NAME}/query" \
    -H "x-algolia-api-key: ${API_KEY}" \
    -H "x-algolia-application-id: ${APP_ID}" \
    -H "content-type: application/json" \
    -d '{"params": "hitsPerPage=5"}'
  ```

- **Project inspection**: Read the project's existing styling approach, breakpoints, layout, responsive patterns, component library, and framework details. Identify which InstantSearch library to use (see table above).
- **Routes**: Find the detail page route pattern (e.g., `/products/[id]`, `/articles/[slug]`) and look for an existing listing or search results page. If one is found, verify it actually reads query parameters and renders dynamic results (not just a static listing). If none is found or the page is static, ask the user: "What page should search redirect to when a query is submitted? Or is there no results page?"
- **Placement**: Find where the search experience should live in the UI. Refer to the pattern's features reference for guidance, or ask the user.
- **Rendering**: Present the user with concrete, numbered options for how results should appear. These depend on the schema (what attributes are available) and the project's design. Refer to the pattern's features reference for options to present.

Do not proceed until you have credentials, schema, rendering preferences, and an understanding of the project's design.

### 2. Build

This skill currently covers **autocomplete**. If the user asks for a different search pattern (e.g., a search results page, faceted search), let them know and ask how they'd like to proceed.

Patterns available for each library:

| Pattern      | React                                                                                                                                                                       | Vue | JS  |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- | --- |
| Autocomplete | [features](references/react/autocomplete/features.md), [styling](references/react/autocomplete/styling.md), [anti-patterns](references/react/autocomplete/anti-patterns.md) | —   | —   |

Also read and apply the library-level references (apply regardless of pattern):

| Reference        | React                                                       | Vue | JS  |
| ---------------- | ----------------------------------------------------------- | --- | --- |
| Technology rules | [technology-rules.md](references/react/technology-rules.md) | —   | —   |
| Anti-patterns    | [anti-patterns.md](references/react/anti-patterns.md)       | —   | —   |
| Styling          | [styling.md](references/react/styling.md)                   | —   | —   |
| Glossary         | [glossary.md](references/react/glossary.md)                 | —   | —   |

If you are unsure how to implement a feature with built-in widgets, ask the user. Do not fall back to legacy libraries or custom connectors.

### 3. Style

Follow the library's styling guide step by step, then apply the pattern-specific styling guide. Match the site's existing CSS methodology, color scheme, typography, spacing, and component patterns.

### 4. Review

Review your work against the library's anti-patterns, the pattern-specific anti-patterns, and the features checklist. Fix any violations.
