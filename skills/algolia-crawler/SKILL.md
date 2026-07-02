---
name: algolia-crawler
description: >-
  Use this skill whenever a user wants to crawl one or more web pages or a
  whole site and turn them into an Algolia index using the Algolia CLI —
  especially for RAG, AI search, semantic search, or Agent Studio retrieval.
  Triggers: "index my website/docs with Algolia", "set up the Algolia Crawler",
  "crawl this page for RAG", "scrape my site into Algolia", "build a knowledge
  base for my AI agent from these URLs", writing or debugging a crawler
  recordExtractor, or handling JavaScript-rendered pages that won't index. It
  guides ingestion end-to-end with `algolia crawler` commands: inspect the
  page, write a RAG-optimized recordExtractor, validate with `algolia crawler
  test` BEFORE indexing, apply index settings explicitly, then reindex. Do NOT
  use for building the chatbot/agent layer itself (use algobot-cli), raw
  record/synonym/settings ops on an existing index (use algolia-cli), frontend
  search UI (use instantsearch), or read-only search/analytics (use
  algolia-mcp).
license: MIT
metadata:
  author: algolia
  version: "1.0"
---

# Algolia Crawler

Turn web pages into a **RAG-optimized Algolia index** with the [Algolia Crawler](https://www.algolia.com/doc/tools/crawler/getting-started/overview), driven entirely by the **Algolia CLI** (`algolia crawler …`). The Crawler visits URLs, extracts content with a JavaScript `recordExtractor`, and writes Algolia records on a schedule — no scraping code to maintain.

The single most important idea: **crawling for RAG is not the same as crawling for site search.** A RAG record is a chunk of text that will be dropped into an LLM's context window *in isolation*. That changes how you shape every record (see [The RAG record mental model](#the-rag-record-mental-model)).

## When to use this skill vs. the others

| Need | Skill |
|------|-------|
| Crawl/ingest web pages into an index (this workflow) | **algolia-crawler** |
| Build the chatbot / agent / RAG app on top of the index | **algobot-cli** |
| Raw record/settings/synonym/rule ops on an existing index | **algolia-cli** |
| Read-only search, analytics, recommendations | **algolia-mcp** |
| Frontend search UI (autocomplete, results, facets) | **instantsearch** |

**Rule of thumb:** if the user wants to *get web content into Algolia*, you're in the right skill. Once the index exists and they want to *ask questions over it*, hand off to **algobot-cli**.

## The RAG record mental model

Each record is retrieved and shown to an LLM alone, without the surrounding page. So optimize for that:

1. **Small and single-topic.** One idea, one fact, one Q&A per record — not a whole page. Granular records retrieve precisely and waste less of the context window.
2. **Self-contained.** Every record carries the context needed to stand alone: the entity it's about, the page title, the section heading. The LLM won't see the rest of the page.
3. **Natural-language `content`, even for structured data.** This is the highest-leverage move. Don't store only `{model: "X", score: 0.87}` — also synthesize a sentence: *"Model X scores 0.87 on relevance…"*. Both keyword and vector retrieval, and the LLM itself, want prose.
4. **Structured attributes for filtering.** Alongside `content`, keep clean fields (`category`, `type`, `date`, numeric values) so retrieval can be scoped with `filters` and facets.

If you internalize only one thing from this skill, make it this list. Everything else is mechanics.

## The workflow

Follow these steps in order. Full commands, config, and code live in the references — read them as you reach each step.

1. **Set up the CLI and credentials.** Install the CLI and export your Crawler credentials (a Crawler *user ID* + *API key*, distinct from your app keys), plus an Algolia **write** API key for the target index and your **App ID**. See [cli.md](references/cli.md#setup-and-credentials).
2. **Inspect the page first — is it JavaScript-rendered?** Many modern pages load their real content via XHR after load, so a naive crawl indexes empty shells. Detect this and enable rendering. See [javascript-rendering.md](references/javascript-rendering.md).
3. **Write a `recordExtractor` that emits RAG records.** For docs and prose, the recommended default is Algolia's Markdown helpers (`helpers.markdown` + `helpers.splitTextIntoRecords`) — they preserve headings/lists/code and are Algolia's own AskAI/RAG pattern. Hand-roll an extractor when you need per-entity structured records (tables, catalogs). Either way, follow the mental model above. See [record-extractor.md](references/record-extractor.md).
4. **Validate with `algolia crawler test` BEFORE indexing.** It runs your config against a live URL and returns the records it *would* create, without writing anything. Use it as your feedback loop — and as a DOM inspector to fix selectors against the real rendered markup. See [workflow.md](references/workflow.md#validate-before-you-index).
5. **Apply index settings explicitly.** Do not rely on `initialIndexSettings` to configure the index — in practice it frequently does not apply. Set `searchableAttributes`, `attributesForFaceting`, etc. yourself with `algolia settings import` after the first crawl. See [rag-index-settings.md](references/rag-index-settings.md).
6. **Reindex, then verify** by searching the index (`algolia search`) for a few realistic RAG questions before trusting it.
7. **Schedule** a recurring crawl so the index stays fresh as the source pages change.

**Crawling a whole site or section (one URL → all its sub-pages)?** The crawler discovers sub-pages via `startUrls`/`sitemaps`/`discoveryPatterns` — but the config must be shaped from *all* the page types it will hit, not just the start page. A config fitted to the landing page produces junk on the article/reference/blog templates it never saw. Discover the URL set, group it into templates, sample a representative page per template, and validate the extractor against **each**. See [site-crawls.md](references/site-crawls.md).

The complete, copy-adaptable end-to-end run (create → test → settings → reindex → verify) is in [workflow.md](references/workflow.md).

## Two things that will bite you

These are the non-obvious failures. Both references cover them, but they're worth stating up front:

- **JavaScript-rendered data.** If the page shows `Loading…` placeholders in its initial HTML, or the numbers/table appear only after load, you must enable `renderJavaScript`. A crawl without it indexes nothing useful. ([javascript-rendering.md](references/javascript-rendering.md))
- **Values hidden in attributes.** Rendered pages often keep the real value in an attribute (e.g. `data-tip="Score: 79.8%"`) while the visible cell shows only a bar or a delta. Extract from the attribute, not the visible text. ([record-extractor.md](references/record-extractor.md#reading-values-from-attributes))

## Driving it with the CLI

Everything runs through `algolia crawler …` (and `algolia settings` / `algolia search` for the index side). Full cheatsheet and the gotchas below are in [cli.md](references/cli.md).

```bash
algolia crawler create <name> -F config.json     # create (prints nothing on success)
algolia crawler test   <id> --url <url> [-F cfg] # extract records WITHOUT indexing
algolia crawler reindex <id>                      # start a crawl that writes records
algolia crawler get    <id>                        # inspect crawler + config/status
algolia crawler stats  <id>                        # crawl status summary
```

Two CLI realities to plan around (details in [cli.md](references/cli.md#gotchas)):

- **Set `renderJavaScript: true` (boolean).** The CLI only accepts the boolean form; the object form (`{ enabled, patterns, waitTime }`) makes `get`/`list`/`create -F` fail to parse. Boolean `true` uses the default render wait, which is enough for most pages — confirm with `crawler test` (empty values mean the page needs more render time).
- **`create` prints nothing and there's no config-update or delete command.** After `create`, recover the id from `algolia crawler list` (`get` needs a UUID — it doesn't accept a name). If `list` errors because another crawler in the account uses a non-boolean `renderJavaScript`, there's no pure-CLI recovery — look the id up via the Crawler REST list endpoint (`GET /1/crawlers?name=<name>`). To change a config, re-create; to delete, use the dashboard or REST `DELETE`.

## References

- [workflow.md](references/workflow.md) — the full end-to-end CLI run: config, test-before-index loop, settings, reindex, verify, schedule.
- [site-crawls.md](references/site-crawls.md) — crawling a whole site/section: discover sub-pages, group page templates, sample and validate each, cover them with a branching extractor or multiple actions.
- [record-extractor.md](references/record-extractor.md) — RAG record patterns, helpers, reading values from attributes, chunking long prose.
- [rag-index-settings.md](references/rag-index-settings.md) — index settings tuned for retrieval, NeuralSearch/vector, query-time filtering for RAG.
- [javascript-rendering.md](references/javascript-rendering.md) — detecting and handling JavaScript-rendered pages.
- [cli.md](references/cli.md) — setup, credentials, the `algolia crawler` command cheatsheet, and the CLI gotchas in detail.
