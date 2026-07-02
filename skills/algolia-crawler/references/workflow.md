# End-to-end workflow (CLI)

The complete run to take one or more web pages from zero to a verified, RAG-optimized Algolia index, using the **Algolia CLI**. Adapt the placeholders (`YOUR_APP_ID`, URLs, index name, selectors) to the customer's case. Credentials and CLI gotchas are in [cli.md](cli.md).

## 1. Decide the index shape first

Before writing anything, look at the target page(s) and decide what a good *retrieval unit* is:

- A docs/article/marketing page → one record per section (heading + prose), plus one record per FAQ Q&A.
- A data page (table, leaderboard, pricing, catalog) → one record per row/entity, with a synthesized natural-language `content` field **and** the structured columns as attributes.

Keep records small and self-contained (see the RAG record mental model in SKILL.md).

**Indexing a whole site or section?** First map the page *templates* you'll crawl (e.g. docs vs API reference vs blog) — each may need its own extraction, and one config has to work for all of them. See [site-crawls.md](site-crawls.md) for the discover → group → sample → cover workflow; the steps below then apply per template.

## 2. Write the config

A Crawler config is a JSON file. The `recordExtractor` is stored as `{"__type": "function", "source": "<stringified function>"}`. Build it safely with `jq --rawfile` so quotes/newlines in the function don't break the JSON:

```bash
# extractor.js holds the recordExtractor function (see record-extractor.md)
jq -n --arg appId "$APP_ID" --arg apiKey "$WRITE_KEY" --rawfile src extractor.js '{
  appId: $appId,
  apiKey: $apiKey,                       # write key the crawler uses to index
  indexPrefix: "kb_",
  startUrls: ["https://example.com/page/"],
  sitemaps: ["https://example.com/sitemap.xml"],        # optional: reliable sub-page discovery
  discoveryPatterns: ["https://example.com/page/**"],   # URLs the crawler may follow
  exclusionPatterns: ["https://example.com/page/**/*.{png,jpg,svg,css,js}"],
  ignoreQueryParams: ["utm_*","ref","fbclid"],
  maxDepth: 2, maxUrls: 100, rateLimit: 8,
  renderJavaScript: true,                # boolean form — required by the CLI (see cli.md)
  schedule: "every 1 day at 3:00 am",
  actions: [{
    indexName: "content",                # final index = indexPrefix + indexName = kb_content
    pathsToMatch: ["https://example.com/page/**"],
    recordExtractor: { "__type": "function", source: $src }
  }]
}' > config.json
```

Scope the crawl to the section you want with `discoveryPatterns` (exclude assets and unrelated paths) instead of the whole domain — but raise `maxDepth`/`maxUrls` enough to cover all the sub-pages you *do* want. For a multi-template site, see [site-crawls.md](site-crawls.md). Keep `renderJavaScript` a boolean — the CLI rejects the object form ([cli.md](cli.md#the-renderjavascript-gotcha)).

## 3. Create the crawler

```bash
algolia crawler create my-crawler -F config.json   # prints nothing on success
CID=$(algolia crawler list | grep -i my-crawler | awk '{print $1}')   # recover the id
algolia crawler get "$CID" | jq '{name, renderJavaScript: .config.renderJavaScript}'
```

`create` is silent on success, so fetch the id afterward with `crawler list` (or `crawler get my-crawler`). See [cli.md](cli.md#gotchas).

## 4. Validate before you index

This is the most important step. `crawler test` runs the config against a live URL and returns the records it *would* produce **without indexing anything**. Iterate here, not on live crawls. For a site-wide crawl, run it against a representative URL from **each** page template, not just one — see [site-crawls.md](site-crawls.md).

```bash
algolia crawler test "$CID" --url "https://example.com/page/" \
  | jq '.records[0].records[0]'          # inspect the first extracted record
```

To try selector changes without touching the stored crawler, pass an override config: `algolia crawler test "$CID" --url … -F trial-config.json`. Check that:

- Records have real values, not empty fields (empty = rendering too slow or wrong selectors).
- The `content` field reads as a useful, self-contained sentence.
- Record counts match what you expect (N rows, M FAQs, etc.).

**Debugging tip — use `crawler test` as a DOM inspector.** If selectors return nothing, temporarily return the raw markup so you can see the real rendered structure, then fix your selectors:

```js
({ $ }) => [{ objectID: "debug", html: $("table").first().html()?.slice(0, 2000) }]
```

Put that in a trial config, run `crawler test … -F trial-config.json`, read the HTML, adjust selectors, repeat until records look right.

## 5. Apply index settings explicitly

Do **not** rely on `initialIndexSettings` in the config — in practice it often does not get applied, leaving `searchableAttributes`/`attributesForFaceting` unset (so filters and facets silently fail). Apply them yourself after the index exists. See [rag-index-settings.md](rag-index-settings.md) for the recommended `settings.json`.

```bash
algolia settings import kb_content \
  --application-id "$APP_ID" --api-key "$WRITE_KEY" \
  -F settings.json --wait
```

## 6. Reindex (the crawl that writes records)

```bash
algolia crawler reindex "$CID"
```

Returns quickly; the crawl runs async. Poll with `algolia crawler get "$CID"` (watch `lastReindexEndedAt`) or `algolia crawler stats "$CID"` until it reports done.

## 7. Verify by searching

Query the index the way a RAG system will, and confirm you get sensible hits:

```bash
algolia search kb_content --application-id "$APP_ID" --api-key "$SEARCH_KEY" \
  --query "a realistic user question" --hitsPerPage 3 \
  --attributesToRetrieve "content,url"
# confirm facets/filters work too, e.g. --filters "record_type:faq"
```

If the empty-query `nbHits` matches your expected record count and targeted queries return the right records, the index is ready. Hand off to **algobot-cli** to build the retrieval/agent layer on top.

## 8. Keep it fresh

The `schedule` field (Later.js text syntax, e.g. `"every 1 day at 3:00 am"`) triggers recurring reindexes. Note that a scheduled reindex reuses the stored config but does **not** re-apply settings — so if you change settings, run the `settings import` from step 5 again.
