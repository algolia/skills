# Handling JavaScript-rendered pages

Many modern pages ship a nearly-empty HTML shell and load their real content via JavaScript/XHR after the page loads. A default crawl fetches only the initial HTML, so it indexes placeholders instead of data — the single most common reason a crawl produces empty or useless records.

## Detect it

Signs the page is JS-rendered:

- The raw HTML (View Source, or `curl` the URL) shows `Loading…`, empty containers, or skeleton placeholders where the real content should be.
- The numbers/table/list only appear after the page finishes loading in a browser.
- `algolia crawler test` (without rendering) returns empty fields, or far fewer records than the page visibly shows.

## Enable rendering

Turn on `renderJavaScript` in the config so the Crawler runs a headless browser and extracts from the rendered DOM:

```json
{ "renderJavaScript": true }
```

**Use the boolean `true`, not the object form.** The object form (`{ "enabled": true, "patterns": [...], "waitTime": {...} }`) gives finer control (which URLs to render, how long to wait) but the **Algolia CLI cannot parse it** — it breaks `crawler get`/`list`/`create -F`. For a CLI-managed crawler, `renderJavaScript: true` renders every matched page with the default wait, which is enough for the large majority of pages. See [cli.md](cli.md#the-renderjavascript-gotcha).

## Confirm it worked

Always validate with the test endpoint before a full crawl:

```bash
algolia crawler test "$CID" --url "https://example.com/page/" | jq '.records[0].records[0]'
```

- If fields are now populated → rendering is working; proceed.
- If fields are still empty → the content likely needs more time to load than the default wait allows. Because the CLI only supports the boolean form, your options are to confirm the data truly is in the rendered DOM (inspect via the DOM-dump trick in [workflow.md](workflow.md#validate-before-you-index)), simplify selectors, or — for pages that genuinely need a long custom `waitTime` — configure that crawler from the Algolia dashboard, which supports the full `renderJavaScript` object.

## Performance note

Rendering runs a headless browser per page, so it's slower than plain HTML crawling. With the boolean form it applies to every matched page; keep the crawl scoped (`discoveryPatterns`, `maxUrls`) so you only render the pages you actually need.
