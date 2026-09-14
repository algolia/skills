# Verified CDN URLs For Algolia Frontend Packages

Agents invent plausible filenames. In one benchmark, two separate builds shipped a
`<script>` tag for search-insights pointing at a file that does not exist
(`search-insights.production.min.js`, then `search-insights.umd.min.js`). The 404 left
`window.aa` as a queued stub, every event silently died, and both QA write-ups still said
"events verified." A guessed URL is a launch blocker until it has returned 200.

**Rule: never ship a CDN URL you have not fetched.** `curl -sI <url>` and check for `200`
(jsDelivr redirects unversioned paths; follow with `-L`). Do it for every `<script src>` and
`<link href>` before the page-startup smoke gate, and pin a major version.

## Verified (200 on jsDelivr, September 2026)

| Package | URL | Global |
| --- | --- | --- |
| algoliasearch v4 lite (search-only client) | `https://cdn.jsdelivr.net/npm/algoliasearch@4/dist/algoliasearch-lite.umd.js` | `algoliasearch` |
| algoliasearch v5 lite | `https://cdn.jsdelivr.net/npm/algoliasearch@5/dist/lite/builds/browser.umd.js` | `algoliasearch.liteClient` |
| algoliasearch v5 full | `https://cdn.jsdelivr.net/npm/algoliasearch@5/dist/algoliasearch.umd.js` | `algoliasearch` |
| InstantSearch.js v4 | `https://cdn.jsdelivr.net/npm/instantsearch.js@4/dist/instantsearch.production.min.js` | `instantsearch` |
| InstantSearch CSS (Satellite theme) | `https://cdn.jsdelivr.net/npm/instantsearch.css@8/themes/satellite-min.css` | — |
| search-insights v2 | `https://cdn.jsdelivr.net/npm/search-insights@2/dist/search-insights.min.js` | `aa` |
| Autocomplete JS v1 | `https://cdn.jsdelivr.net/npm/@algolia/autocomplete-js@1/dist/umd/index.production.js` | `['@algolia/autocomplete-js']` |
| Autocomplete classic theme | `https://cdn.jsdelivr.net/npm/@algolia/autocomplete-theme-classic@1/dist/theme.min.css` | — |
| Autocomplete Query Suggestions plugin | `https://cdn.jsdelivr.net/npm/@algolia/autocomplete-plugin-query-suggestions@1/dist/umd/index.production.js` | `['@algolia/autocomplete-plugin-query-suggestions']` |
| Autocomplete Recent Searches plugin | `https://cdn.jsdelivr.net/npm/@algolia/autocomplete-plugin-recent-searches@1/dist/umd/index.production.js` | `['@algolia/autocomplete-plugin-recent-searches']` |
| Recommend client v4 | `https://cdn.jsdelivr.net/npm/@algolia/recommend@4/dist/recommend.umd.js` | `['@algolia/recommend']` |

## Known-wrong guesses (404)

- `search-insights@2/dist/search-insights.production.min.js`
- `search-insights@2/dist/search-insights.umd.min.js`
- `@algolia/recommend-js@1/dist/umd/index.production.js`

## The search-insights loader shim

The documented snippet defines `window.aa` as a queue *before* the script loads:

```html
<script>
  window.aa = window.aa || function () { (window.aa.queue = window.aa.queue || []).push(arguments); };
</script>
<script src="https://cdn.jsdelivr.net/npm/search-insights@2/dist/search-insights.min.js" async></script>
```

That shim is why a 404 fails silently: `aa('init', …)` and every event call succeed and sit
in `aa.queue` forever. `typeof window.aa === 'function'` proves nothing. The smoke gate checks
that `window.aa.queue` is empty after load; do the same by hand if you skip the script.

With InstantSearch.js v4.8+ you can skip the shim entirely: `instantsearch({ insights: true })`
loads search-insights itself and wires click and conversion events through `bindEvent`. Adding a
manual `clickedObjectIDsAfterSearch` on top of it double-fires — the most common event bug in
the benchmark.
