---
name: instantsearch
description: >-
  Set up and build production-quality search experiences (autocomplete, search results pages, faceted search) using InstantSearch.
  Use when the user wants to integrate, set up, or get started with Algolia search or InstantSearch in an app
  ("we signed with Algolia", "integrate instantsearch", "add a search bar"), or asks to add search, autocomplete,
  search-as-you-type, faceted filtering, or a search results page to a React, Vue, or vanilla JS application,
  or mentions Algolia, InstantSearch, or react-instantsearch.
  Do NOT use for backend index operations (records, synonyms, settings, API keys), use algolia-cli instead.
  Do NOT use for analytics, recommendations, or MCP server queries, use algolia-mcp instead.
  Do NOT use for AI/agent/conversational search, use algobot-cli instead.
license: MIT
metadata:
  author: algolia
  version: '1.3'
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

> **Note:** Coverage by library:
>
> - **React InstantSearch**: full coverage (autocomplete, search results page, custom widgets, middleware, SSR).
> - **Vue InstantSearch** and **InstantSearch.js**: library-level rules and autocomplete only. For other patterns, follow the [Source-of-truth check](#2-source-of-truth-check) and ask the user before scaffolding non-trivial flows.

## Workflow

### 0. Set up (new integrations)

When the project has no InstantSearch code yet ("integrate Algolia", "we just signed with Algolia", "add search to this app"), set it up with Create InstantSearch App. It generates new apps, and its `init`, `introspect`, and `agents-md` commands work in existing ones. Check that `npx create-instantsearch-app --help` lists `init`. If it doesn't, the version predates these commands: do the same work by hand in Discover and Build.

1. **Existing app**: run `npx create-instantsearch-app init --json` in the app root. It detects the framework, reads credentials from the project env, installs the packages, writes the search client and provider, and returns `nextSteps`. Follow them.
2. **Empty folder**: `init` returns `no_app_detected`. Run `npx create-instantsearch-app introspect --json`, then run the `data.createInstantSearchAppCommand` it returns. It generates the app with display, image, and facet attributes from the index, and with Insights on.
3. **Plan the UI**: `npx create-instantsearch-app introspect --json` returns the searchable attributes, facets, image field, and `data.widgetPlan`. Use it as the schema in Discover and build the rendering options from it.
4. **After building**: run `npx create-instantsearch-app agents-md` so later sessions know the installed version and file layout, then verify as described in Review.

### 1. Discover

Before writing any code, gather context. First check if InstantSearch is already set up in the codebase (search client, provider, existing widgets). If so, read the existing configuration instead of re-asking.

If starting fresh, go step by step, waiting for the user's answer before moving on.

- **Credentials**: Look in the project env first (`.env`, `.env.local`, and the process environment): `ALGOLIA_APP_ID` or `ALGOLIA_APPLICATION_ID`, `ALGOLIA_SEARCH_API_KEY`, and `ALGOLIA_INDEX_NAME`, with or without a framework prefix such as `NEXT_PUBLIC_` or `VITE_`. Provisioning through Stripe Projects or the Vercel Marketplace writes them there. Ask the user only for what's missing. Only the app ID and the search-only key may reach the browser; never put a write or admin key (`ALGOLIA_WRITE_API_KEY`) in client code.
- **Query Suggestions**: Ask the user if they have a Query Suggestions index.
- **Schema**: Once you have credentials, fetch a few records from the main index to discover the available attributes and their shape (`npx create-instantsearch-app introspect --json` does this and suggests widgets). Confirm with the user rather than asking them to list everything. The schema is needed before you can propose rendering options. No need to fetch from the Query Suggestions index: its shape is standard and handled by the widget.

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

### 2. Source-of-truth check

This skill bakes guidance for the highest-value patterns only. Whenever you need a widget, hook, connector, prop, middleware, future flag, or API that is **not explicitly documented in this skill**, you must consult the source of truth before writing code. Training data is stale, lossy, and frequently wrong on prop shapes.

Follow the library's source-of-truth reference for the exact commands and URL patterns:

| Library | Reference                                                  |
| ------- | ---------------------------------------------------------- |
| React   | [source-of-truth.md](references/react/source-of-truth.md)  |
| Vue     | [source-of-truth.md](references/vue/source-of-truth.md)    |
| JS      | [source-of-truth.md](references/js/source-of-truth.md)     |

The reference always covers, in order:

1. **Read installed types** in `node_modules` for prop shapes, renderState, and connector contracts.
2. **Fetch the live Algolia docs** at the canonical URL pattern.
3. **Grep installed CSS / source** for class names you intend to style.
4. **Only then write code.** If a step fails (offline, 404, missing types), ask the user before guessing.

Do this even when a pattern reference exists, if you need any prop or behavior the pattern reference does not explicitly cover.

### 3. Build

Pick the matching pattern reference for the library and the user's request. If no pattern reference exists for what the user asked for, fall back on the source-of-truth check (Step 2) and ask the user before scaffolding speculative widget trees.

Patterns available for each library:

| Pattern                                                      | React                                                                                                                                                                                            | Vue                                                                                                                                                                  | JS                                                                                                                                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Autocomplete                                                 | [features](references/react/autocomplete/features.md), [styling](references/react/autocomplete/styling.md), [anti-patterns](references/react/autocomplete/anti-patterns.md)                      | [features](references/vue/autocomplete/features.md), [styling](references/vue/autocomplete/styling.md), [anti-patterns](references/vue/autocomplete/anti-patterns.md) | [features](references/js/autocomplete/features.md), [styling](references/js/autocomplete/styling.md), [anti-patterns](references/js/autocomplete/anti-patterns.md) |
| Search results page (incl. faceted search, sort, pagination) | [features](references/react/search-results-page/features.md), [styling](references/react/search-results-page/styling.md), [anti-patterns](references/react/search-results-page/anti-patterns.md) | —                                                                                                                                                                    | —                                                                                                                                                                  |

Also read and apply the library-level references (apply regardless of pattern):

| Reference        | React                                                       | Vue                                                       | JS                                                       |
| ---------------- | ----------------------------------------------------------- | --------------------------------------------------------- | -------------------------------------------------------- |
| Technology rules | [technology-rules.md](references/react/technology-rules.md) | [technology-rules.md](references/vue/technology-rules.md) | [technology-rules.md](references/js/technology-rules.md) |
| Anti-patterns    | [anti-patterns.md](references/react/anti-patterns.md)       | [anti-patterns.md](references/vue/anti-patterns.md)       | [anti-patterns.md](references/js/anti-patterns.md)       |
| Styling          | [styling.md](references/react/styling.md)                   | [styling.md](references/vue/styling.md)                   | [styling.md](references/js/styling.md)                   |
| Glossary         | [glossary.md](references/react/glossary.md)                 | [glossary.md](references/vue/glossary.md)                 | [glossary.md](references/js/glossary.md)                 |
| Source of truth  | [source-of-truth.md](references/react/source-of-truth.md)   | [source-of-truth.md](references/vue/source-of-truth.md)   | [source-of-truth.md](references/js/source-of-truth.md)   |
| Custom widgets   | [custom-widgets.md](references/react/custom-widgets.md)     | —                                                         | —                                                        |
| Middleware       | [middleware.md](references/react/middleware.md)             | —                                                         | —                                                        |
| SSR              | [ssr.md](references/react/ssr.md)                           | —                                                         | —                                                        |
| Pattern                                                      | React                                                                                                                                                                                            | Vue | JS  |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --- | --- |
| Autocomplete                                                 | [features](references/react/autocomplete/features.md), [styling](references/react/autocomplete/styling.md), [anti-patterns](references/react/autocomplete/anti-patterns.md)                      | —   | —   |
| Search results page (incl. faceted search, sort, pagination) | [features](references/react/search-results-page/features.md), [styling](references/react/search-results-page/styling.md), [anti-patterns](references/react/search-results-page/anti-patterns.md) | —   | —   |

Also read and apply the library-level references (apply regardless of pattern):

| Reference        | React                                                       | Vue | JS  |
| ---------------- | ----------------------------------------------------------- | --- | --- |
| Technology rules | [technology-rules.md](references/react/technology-rules.md) | —   | —   |
| Anti-patterns    | [anti-patterns.md](references/react/anti-patterns.md)       | —   | —   |
| Styling          | [styling.md](references/react/styling.md)                   | —   | —   |
| Glossary         | [glossary.md](references/react/glossary.md)                 | —   | —   |
| Source of truth  | [source-of-truth.md](references/react/source-of-truth.md)   | —   | —   |
| Custom widgets   | [custom-widgets.md](references/react/custom-widgets.md)     | —   | —   |
| Middleware       | [middleware.md](references/react/middleware.md)             | —   | —   |
| SSR              | [ssr.md](references/react/ssr.md)                           | —   | —   |

Consult types and live docs first (Step 2). Ask the user only if both fail. Never fall back to legacy libraries or guessed APIs.

### 4. Style

Follow the library's styling guide step by step, then apply the pattern-specific styling guide. Match the site's existing CSS methodology, color scheme, typography, spacing, and component patterns.

### 5. Review

Review your work against the library's anti-patterns, the pattern-specific anti-patterns, and the features checklist. Fix any violations.

Then verify before reporting success. Reading your edits is not verification:

1. Run the production build (`npm run build` or the project's equivalent). It catches SSR and prerender errors the dev server hides, such as `InstantSearchNext` under Next.js `cacheComponents` (see [ssr.md](references/react/ssr.md)).
2. Start the app, open the search page, type a query, and apply a refinement. Confirm the results change and the console has no errors.
