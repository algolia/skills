# Crawling a whole site or section (multiple pages)

When the user gives a single URL but wants everything under it indexed, two things must be true: the crawler has to discover and follow sub-pages, and — more importantly — your extractor and index settings must be shaped from **all the page shapes it will hit**, not just the start page. A config fitted to the landing page produces junk on the article/reference/blog templates it never saw. This is the most common way a site-wide crawl yields a bad index.

## 1. Let the crawler discover sub-pages

The Crawler follows links from `startUrls`. Control coverage with:

- `startUrls` — entry point(s).
- `sitemaps` — point at the site's `sitemap.xml` for reliable, complete discovery. Prefer this whenever the site has one.
- `discoveryPatterns` — which URLs the crawler is allowed to follow (the section you want).
- `pathsToMatch` (per action) — which discovered URLs actually get extracted/indexed.
- `maxDepth` / `maxUrls` — depth and count ceilings. For a real site these are *ceilings*, not throttles — raise them (e.g. `maxDepth: 5`, `maxUrls: 2000`). Scoping is about **excluding noise** (assets, unrelated sections), not staying on one page.

```jsonc
"startUrls": ["https://docs.example.com/"],
"sitemaps": ["https://docs.example.com/sitemap.xml"],
"discoveryPatterns": ["https://docs.example.com/**"],
"maxDepth": 5,
"maxUrls": 2000,
```

## 2. Find the distinct page templates

A site is rarely one shape. Before writing the extractor, learn the range:

- Get the URL list from the sitemap, or run a shallow discovery crawl and read what was fetched (`algolia crawler stats <id>` and the crawler's URL report show the crawled URLs).
- Cluster the URLs by path pattern — `/docs/**`, `/api/**`, `/blog/**`, `/changelog/**`. Each cluster is usually a distinct template with a distinct DOM.
- Open one URL from each cluster and confirm whether the markup differs enough to need different extraction.

## 3. Sample representative pages — validate against each, not one

This is the core of "take all the pages into account." Pick 2–3 representative URLs **per template** and run `crawler test --url` against **each** — not just the start page:

```bash
for u in \
  "https://docs.example.com/getting-started" \
  "https://docs.example.com/api/search" \
  "https://docs.example.com/blog/2026-launch"; do
  echo "== $u =="
  algolia crawler test "$CID" --url "$u" | jq '.records[0].records | {n: length, first_type: .[0].record_type}'
done
```

You're confirming that *every* template yields sensible records. Empty results or wrong fields on one template mean the extractor doesn't generalize yet — fix it before indexing.

## 4. Handle the variety — one branching extractor, or multiple actions

Two ways to cover heterogeneous templates:

**A. One `recordExtractor` that branches on page type.** Detect the template from the URL or DOM and extract accordingly. Simple; everything stays in one function.

```js
({ url, $, helpers }) => {
  const path = new URL(url.href).pathname;
  if (path.startsWith("/api/"))  return extractApiRef($, url);
  if (path.startsWith("/blog/")) return extractArticle($, url);
  return extractDoc($, url, helpers);   // default docs template
};
```

**B. Multiple `actions`, one per template.** Each action has its own `pathsToMatch` + `recordExtractor`, all writing to the same index. Cleaner when templates differ a lot, and lets you use different helpers per type (e.g. `helpers.docsearch` for docs, a hand-written extractor for the API reference).

```jsonc
"actions": [
  { "indexName": "content", "pathsToMatch": ["https://docs.example.com/api/**"],  "recordExtractor": { "__type": "function", "source": "…" } },
  { "indexName": "content", "pathsToMatch": ["https://docs.example.com/blog/**"], "recordExtractor": { "__type": "function", "source": "…" } },
  { "indexName": "content", "pathsToMatch": ["https://docs.example.com/**"],      "recordExtractor": { "__type": "function", "source": "…" } }
]
```

Order matters: the Crawler applies the **first** action whose `pathsToMatch` matches, so put specific patterns before the catch-all (`/**`) at the end. Give every record a `record_type` so retrieval can tell templates apart.

## 5. Unify settings, then verify across templates

All templates share one index, so a single set of index settings must serve them all — make sure `searchableAttributes` / `attributesForFaceting` cover the fields **every** template produces (see [rag-index-settings.md](rag-index-settings.md)). Apply them explicitly with `algolia settings import` (as always — `initialIndexSettings` isn't reliable).

Then verify with queries that span the whole site, not one page:

```bash
for q in "how do I authenticate" "search endpoint parameters" "latest release notes"; do
  echo "== $q =="
  algolia search content --application-id "$APP_ID" --api-key "$SEARCH_KEY" \
    --query "$q" --hitsPerPage 2 --attributesToRetrieve "record_type,content,url"
done
```

If one template's questions return nothing or junk, go back to step 3 for that template.

## Rule of thumb

Discover the whole set → group into templates → sample and test **each** template → branch or multi-action to cover them → one unified settings + a cross-template verify. Fitting the config to a single page is the most common cause of a bad site-wide index.
