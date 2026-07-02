# Index settings for RAG retrieval

Apply these **explicitly** after the first crawl — do not rely on the crawler's `initialIndexSettings`, which frequently fails to apply and leaves the index with default (null) settings, so `filters` and facets silently return nothing. See [workflow.md](workflow.md#5-apply-index-settings-explicitly) for the `algolia settings import` command.

## Recommended baseline

```json
{
  "searchableAttributes": ["content", "question", "model", "section_title", "page_title"],
  "attributesForFaceting": [
    "searchable(record_type)",
    "searchable(provider)",
    "searchable(model)"
  ],
  "customRanking": ["asc(order)"],
  "attributesToSnippet": ["content:80"],
  "attributesToHighlight": ["content"],
  "distinct": 0
}
```

Why these choices for RAG:

- **`searchableAttributes` with `content` first.** `content` holds the natural-language text your retrieval matches against; ordering it first weights it highest.
- **`attributesForFaceting` with `searchable(...)`.** Lets the RAG layer scope retrieval with `filters` (e.g. `record_type:faq`) *and* get facet counts. Use `filterOnly(attr)` if you only need filtering and not counts — but note `filterOnly` attributes don't appear in facet results, which surprises people.
- **`customRanking: ["asc(order)"]`.** The `order` you set in the extractor gives a stable, meaningful tiebreak (rank, document order) when text relevance ties.
- **`distinct: 0`.** RAG wants recall — keep every chunk. Only raise it if near-duplicate records hurt.

## Add semantic retrieval (NeuralSearch / vectors)

Keyword search alone misses paraphrased questions ("how do I cancel" vs. a doc titled "Ending your subscription"). For RAG, enable Algolia's **NeuralSearch** on the index (dashboard → index → NeuralSearch, or via the API) so retrieval is hybrid keyword + semantic over your `content` field. This is usually the biggest single lever on retrieval quality — recommend it whenever the user's queries will be natural-language questions.

## Query-time settings for RAG

Retrieval quality is also a query-time concern. When the RAG layer queries the index:

- **`removeWordsIfNoResults: "allOptional"`** (or set `optionalWords`) so a long natural-language question still returns hits when not every word matches. Default AND-matching returns nothing for "which model hallucinates least" against records that don't contain all those words.
- **`attributesToRetrieve`** — return only what the LLM needs (`content`, `url`, key attributes) to keep the context lean.
- **`filters`** — scope to the right `record_type`/category for the question.
- **`hitsPerPage`** — retrieve a handful (3–8) of chunks to assemble into the prompt.

These live in the query, not the index settings, so they're set by whatever does retrieval (Agent Studio, your app, etc.) — see **algobot-cli** for building that layer.
