# Writing a RAG-optimized recordExtractor

The `recordExtractor` is a JavaScript function the Crawler runs on each page. It receives `{ url, $, helpers, contentLength, fileType, dataSources }` and returns an array of records. `$` is a [Cheerio](https://cheerio.js.org/) instance over the (optionally JS-rendered) HTML.

In the crawler config the function is stored as a string (`{"__type":"function","source":"…"}`) — that's what `algolia crawler create -F config.json` reads. **The source runs as plain JavaScript — no TypeScript.** Strip any type annotations (`: string[]`, `as any`); they are syntax errors at runtime.

## Markdown for RAG — the default for docs and prose

For prose content — documentation, articles, guides, marketing pages — the best records are usually **Markdown**, not flattened text. Markdown keeps the structure an LLM benefits from (headings, lists, tables, code blocks, links) in a compact form, and it's the pattern Algolia recommends for AskAI/RAG ([Markdown indexing guide](https://www.algolia.com/doc/guides/algolia-ai/askai/guides/markdown-indexing)). Two built-in helpers do the work:

- `helpers.markdown("<css selector>")` — converts the matched HTML subtree to a Markdown string. Target the article body and exclude chrome (nav, header, breadcrumb, the "on this page" TOC).
- `helpers.splitTextIntoRecords({ text, baseRecord, maxRecordBytes, orderingAttributeName })` — splits that Markdown into one or more records under the byte cap. Each record carries the `baseRecord` fields, the chunk in a **`text`** attribute, and a numeric part (via `orderingAttributeName`). ObjectIDs are auto-suffixed per chunk (`<objectID>#0`, `#1`, …).

```js
({ url, $, helpers }) => {
  const text = helpers.markdown("main [class*=content]"); // ← TUNE this selector to the site
  if (!text) return [];
  const title = $("h1").first().text().trim() || $("title").text().trim();
  return helpers.splitTextIntoRecords({
    text,
    baseRecord: {
      record_type: "doc",
      url: url.href,
      objectID: url.href,
      page_title: title,
      lang: $("html").attr("lang") || "en",
    },
    maxRecordBytes: 4000,          // smaller = tighter chunks (better recall); larger = more context per hit, more tokens
    orderingAttributeName: "part",
  });
}
```

**The selector still needs the sample-and-test step.** Don't trust a generic selector — the docs' own example `main > *:not(nav)…` can grab only the "On this page" TOC on a given site. Use `crawler test` to check which selector captures the real article body (try `main`, `article`, `main [class*=content]`, …) before trusting it. Same discover → sample → test loop as everywhere else.

**Tuning `maxRecordBytes`.** Smaller chunks (a few thousand bytes) retrieve more precisely and keep the LLM context lean; larger chunks give more context per hit but cost more tokens per answer. Start around 3000–5000 for RAG and adjust.

When you use this pattern the Markdown lives in the **`text`** attribute — make `text` your primary `searchableAttribute` (see [rag-index-settings.md](rag-index-settings.md)).

## Emit one record per retrieval unit (for structured data)

When the page is **structured data** — a table, leaderboard, pricing grid, catalog — hand-roll an extractor instead, so you get one record per entity with clean, typed attributes rather than a wall of prose. (For docs/prose, prefer the Markdown helper above.)

Return one record per *idea* — an entity/row, a Q&A. Use a `record_type` discriminator so you can filter by kind later, and give every record a natural-language `content` field plus clean structured attributes.

```js
({ url, $ }) => {
  const records = [];
  const clean = (s) => (s || "").replace(/\s+/g, " ").trim();
  const pageTitle = clean($("title").first().text()) || clean($("h1").first().text());

  // 1) One record per entity/row — synthesize prose from the structured fields.
  const rows = $("SELECTOR_FOR_EACH_ROW");
  rows.each((r) => {
    const row = rows.eq(r);                       // .eq(i), not $(el) — see below
    const name = clean(row.find("SELECTOR_NAME").first().text());
    if (!name) return;
    const value = clean(row.find("SELECTOR_VALUE").first().text());

    records.push({
      objectID: "row:" + name.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
      record_type: "row",
      name,
      value,                                       // structured attribute (filter/facet)
      content: `${name}: ${value}.`,               // prose the LLM can cite directly
      page_title: pageTitle,
      url: url.href,
      order: r,
    });
  });

  // 2) FAQ -> one record per Q&A pair (excellent RAG units).
  const faqs = $("SELECTOR_FAQ_ITEM");
  faqs.each((i) => {
    const item = faqs.eq(i);
    const q = clean(item.find("SELECTOR_QUESTION").first().text());
    const a = clean(item.find("SELECTOR_ANSWER").first().text());
    if (!q || !a) return;
    records.push({
      objectID: "faq:" + i,
      record_type: "faq",
      question: q,
      content: `Q: ${q}\nA: ${a}`,
      page_title: pageTitle,
      url: url.href + "#faq-" + i,
      order: 1000 + i,
    });
  });

  // 3) Long prose -> chunked records (see "Chunking long prose").
  // ...

  return records;
};
```

## Reading values from attributes

Rendered pages frequently keep the real value in an **attribute** while the visible cell shows only a bar, badge, or delta. Always check attributes:

```js
const tip = cell.attr("data-tip") || "";                 // e.g. "Score: <strong>79.8%</strong> [78.1–81.4%]"
const strong = (tip.match(/<strong>([^<]+)<\/strong>/) || [])[1];
const value = strong || clean(cell.text());              // prefer the attribute value
```

When your extracted values look wrong (mangled, empty, or a UI label like "Best"), dump the element's `.html()` and its attributes via the test endpoint (see [workflow.md](workflow.md#validate-before-you-index)) to find where the real data lives.

## Iterate with `.eq(i)`, don't re-wrap elements

Use `collection.eq(i)` to get a properly-typed Cheerio node instead of `$(el)`. Re-wrapping raw elements (`$(el)`, `$(th)`) is what triggers Cheerio `Element`/`Node` type errors in typed editors, and chained mutations like `.clone().find().remove().end()` cause `this`-context errors. Prefer:

```js
const cells = row.children("td");
cells.each((i) => { const c = cells.eq(i); /* … */ });
```

To read an answer that excludes its question without a fragile clone chain, slice the string instead:

```js
const full = clean(item.text());
const a = full.startsWith(q) ? full.slice(q.length).trim() : full;
```

## Chunking long prose

Keep records small — roughly 500–1000 tokens retrieves far better than one giant record. Two options:

**Built-in helper** — `helpers.splitContentIntoRecords` extracts text from elements and splits it into multiple records under a byte cap, sharing a `baseRecord`:

```js
const proseRecords = helpers.splitContentIntoRecords({
  $elements: $("article").find("h2, h3, p, li"),
  baseRecord: { record_type: "section", page_title: pageTitle, url: url.href },
  maxRecordBytes: 4000,          // smaller chunks = better RAG recall
  orderingAttributeName: "part",
});
```

If the typed signature complains in an editor, cast just that argument: `$elements: $("article").find("h2, h3, p, li") as any` — but remember to remove the `as any` before putting the source in the config (it must be plain JS).

**Manual chunking** — when you want full control over chunk boundaries and want each chunk prefixed with its section heading (so it stays self-contained):

```js
const CH = 1400; let part = 0;
for (let s = 0; s < text.length; s += CH) {
  records.push({
    objectID: `section:${i}:${part}`,
    record_type: "section",
    section_title: heading,
    content: (heading ? heading + " — " : "") + text.slice(s, s + CH),
    page_title: pageTitle, url: url.href, order: 2000 + i * 10 + part,
  });
  part++;
}
```

## Other built-in helpers

The Crawler ships extractors that produce well-shaped records for common page types — reach for these before hand-rolling:

- `helpers.docsearch({ recordProps })` — hierarchical docs content (heading levels `lvl0`–`lvl6` + content). Good for documentation and long structured articles.
- `helpers.article()` / `helpers.page()` / `helpers.product()` — pull structured data from `og:`/JSON-LD article, generic page, and product schemas.
- `helpers.codeSnippets()` — extract fenced/`<pre>` code blocks with language.

For a data-heavy page (tables, leaderboards), a hand-written extractor that emits one prose+attributes record per row usually beats the generic helpers.

## Stable objectIDs

Use deterministic `objectID`s derived from the content (`faq:0`, `row:<slug>`), not random ones. Then re-crawls update records in place and remove stale ones, instead of duplicating.
