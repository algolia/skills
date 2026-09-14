# Verified CDN URLs For Algolia Frontend Packages

Agents invent plausible filenames. In testing, two separate agent builds shipped a
`<script>` tag for search-insights pointing at a file that does not exist
(`search-insights.production.min.js`, then `search-insights.umd.min.js`). The 404 left
`window.aa` as a queued stub, every event silently died, and both QA write-ups still said
"events verified." A guessed URL is a launch blocker until it has returned 200.

**Rule: never ship a CDN URL you have not fetched.** `curl -sI <url>` and check for `200`
(jsDelivr redirects unversioned paths; follow with `-L`). Do it for every `<script src>` and
`<link href>` before the page-startup smoke gate, and pin a major version.

## Verified (200 on jsDelivr, September 2026)

The "Global" column is what each bundle actually defines on `window`, recorded by loading it in a headless browser — not what the package name suggests.

| Package | URL | Global |
| --- | --- | --- |
| algoliasearch v4 lite (search-only client) | `https://cdn.jsdelivr.net/npm/algoliasearch@4/dist/algoliasearch-lite.umd.js` | `algoliasearch(appId, key)` |
| algoliasearch v5 lite | `https://cdn.jsdelivr.net/npm/algoliasearch@5/dist/lite/builds/browser.umd.js` | `window['algoliasearch/lite'].liteClient(appId, key)` |
| algoliasearch v5 full | `https://cdn.jsdelivr.net/npm/algoliasearch@5/dist/algoliasearch.umd.js` | `algoliasearch.algoliasearch(appId, key)` (namespace object, not a function) |
| InstantSearch.js v4 | `https://cdn.jsdelivr.net/npm/instantsearch.js@4/dist/instantsearch.production.min.js` | `instantsearch` |
| InstantSearch CSS (Satellite theme) | `https://cdn.jsdelivr.net/npm/instantsearch.css@8/themes/satellite-min.css` | — |
| search-insights v2 | `https://cdn.jsdelivr.net/npm/search-insights@2/dist/search-insights.min.js` | `AlgoliaAnalytics` — `aa` exists only if the loader shim below (or InstantSearch's `insights: true`) created it |
| Autocomplete JS v1 | `https://cdn.jsdelivr.net/npm/@algolia/autocomplete-js@1/dist/umd/index.production.js` | `window['@algolia/autocomplete-js'].autocomplete` |
| Autocomplete classic theme | `https://cdn.jsdelivr.net/npm/@algolia/autocomplete-theme-classic@1/dist/theme.min.css` | — |
| Autocomplete Query Suggestions plugin | `https://cdn.jsdelivr.net/npm/@algolia/autocomplete-plugin-query-suggestions@1/dist/umd/index.production.js` | `window['@algolia/autocomplete-plugin-query-suggestions'].createQuerySuggestionsPlugin` |
| Autocomplete Recent Searches plugin | `https://cdn.jsdelivr.net/npm/@algolia/autocomplete-plugin-recent-searches@1/dist/umd/index.production.js` | `window['@algolia/autocomplete-plugin-recent-searches'].createLocalStorageRecentSearchesPlugin` |
| Recommend client v4 | `https://cdn.jsdelivr.net/npm/@algolia/recommend@4/dist/recommend.umd.js` | `window['@algolia/recommend'](appId, key)` |

## Known-wrong guesses (404)

- `search-insights@2/dist/search-insights.production.min.js`
- `search-insights@2/dist/search-insights.umd.min.js`
- `@algolia/recommend-js@1/dist/umd/index.production.js`

## The search-insights loader shim

The documented snippet names the global (`AlgoliaAnalyticsObject`) and defines `window.aa` as
a queue *before* the script loads; the library then drains the queue when it executes:

```html
<script>
  window.AlgoliaAnalyticsObject = 'aa';
  window.aa = window.aa || function () { (window.aa.queue = window.aa.queue || []).push(arguments); };
</script>
<script src="https://cdn.jsdelivr.net/npm/search-insights@2/dist/search-insights.min.js" async></script>
```

Both lines matter: without `AlgoliaAnalyticsObject` the library does not know which global to
bind, and queued calls are never processed even when the script loads (verified in a headless
browser: `getUserToken` answers only when the name is set). The shim is also why a 404 fails
silently: `aa('init', …)` and every event call "succeed" and sit in `aa.queue` forever.

Two things that prove nothing: `typeof window.aa === 'function'` (the shim is a function) and
`aa.queue.length` (the library keeps the array after draining it). What proves the client is
live is a callback: `aa('getVersion', v => console.log(v))` or `aa('getUserToken', null, (e, t) => …)`.
The smoke gate probes `getVersion` with a one-second timeout; do the same by hand if you skip
the script.

With InstantSearch.js v4.8+ you can skip the shim entirely: `instantsearch({ insights: true })`
loads search-insights itself and wires click and conversion events through `bindEvent`. Adding a
manual `clickedObjectIDsAfterSearch` on top of it double-fires — the most common event bug we
see in agent-built pages.
