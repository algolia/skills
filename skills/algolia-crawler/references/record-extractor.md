# Writing a RAG-optimized recordExtractor

The `recordExtractor` is a JavaScript function the Crawler runs on each page. It receives `{ url, $, helpers, contentLength, fileType, dataSources }` and returns an array of records. `$` is a [Cheerio](https://cheerio.js.org/) instance over the (optionally JS-rendered) HTML.

In the crawler config the function is stored as a string (`{"__type":"function","source":"…"}`) — that's what `algolia crawler create -F config.json` reads. **The source runs as plain JavaScript — no TypeScript.** Strip any type annotations (`: string[]`, `as any`); they are syntax errors at runtime.

## Emit one record per retrieval unit

Don't return one record per page. Return one per *idea* — a section, a Q&A, a table row/entity. Use a `record_type` discriminator so you can filter by kind later, and give every record a natural-language `content` field plus clean structured attributes.

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
