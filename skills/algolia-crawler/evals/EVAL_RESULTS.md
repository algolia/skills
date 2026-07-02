# Algolia Crawler Skill — Evaluation Results

Evaluation performed on 2026-07-02 using Claude Opus 4.8 (1M context).

## Summary

The skill was evaluated across 4 realistic user scenarios, comparing **with-skill** (Claude reads the skill before responding) vs **without-skill** (Claude relies on general knowledge). Each output was graded against the assertions in [`evals.json`](evals.json).

| Metric | Without Skill | With Skill |
|--------|:------------:|:----------:|
| **Eval 1** — JS-rendered pricing page → support agent | 57% (4/7) | **100% (7/7)** |
| **Eval 2** — Debug a broken recordExtractor | 75% (3/4) | **100% (4/4)** |
| **Eval 3** — Index a docs site for RAG | 80% (4/5) | **100% (5/5)** |
| **Eval 4** — Whole-site crawl across page templates | 83% (5/6) | **100% (6/6)** |
| **Average pass rate** | **~74%** | **100%** |

Cost of the skill: with-skill runs used ~40% more tokens on average (~48.6k vs ~34.6k) — the cost of reading SKILL.md and its references.

## Where the skill makes the difference

A capable model already handles the *generic* RAG shaping well without the skill — one record per retrieval unit, natural-language `content`, chunking long prose, recommending semantic/NeuralSearch. The docs scenario (Eval 3) baseline was strong here, as this is well-documented DocSearch territory.

The skill's value concentrates on **CLI-specific correctness and non-obvious gotchas** that the baseline consistently got wrong:

- **Boolean `renderJavaScript`.** Baselines reached for the documented object form (`{ enabled, patterns, waitTime }`), which breaks `crawler get`/`list`/`create -F` in the CLI. The skill steers to `renderJavaScript: true`.
- **Validate before indexing with `algolia crawler test`.** Baselines relied on the dashboard URL Tester or skipped validation; the skill makes the test-before-reindex loop (and using it as a DOM inspector) central.
- **Apply index settings explicitly.** Baselines relied on `initialIndexSettings` (Eval 1) or omitted settings application entirely (Eval 3, which missed this assertion) — the exact trap that leaves facets/filters silently broken. The skill mandates `algolia settings import` after the first crawl.
- **Staying CLI-only.** Baselines drifted to the dashboard/REST; the skill keeps the whole workflow in `algolia crawler …`.
- **Validating across page templates.** On a whole-site crawl (Eval 4), the baseline configured sub-page discovery and even proposed multiple actions, but never validated the extractor against a representative page *per template* — so a config fitted to the homepage would silently misfire on other page types. The skill's `site-crawls.md` makes "discover → group templates → sample and `crawler test` each" explicit.

## Eval details

### Eval 1 — JS-rendered pricing page for a support agent
Both runs correctly identified the page as JS-rendered, emitted feature- and plan-level records with natural-language content, and kept structured attributes. Only the with-skill run used the boolean render form, validated with `algolia crawler test`, applied settings explicitly with `algolia settings import`, and stayed CLI-only. The baseline used the object render form + `initialIndexSettings` and steered to the dashboard.

### Eval 2 — Debug a broken recordExtractor
This is where the skill's marginal value is smallest: debugging "empty field / mashed text" is something a strong model reasons about well (read the value from an attribute, inspect the rendered DOM, target a specific child). The skill added the `algolia crawler test` DOM-dump loop and the `.eq(i)` extraction pattern explicitly.

### Eval 3 — Index a docs site for RAG
Baseline was strong on chunking and semantic retrieval. It missed applying index settings explicitly (relied on defaults / `initialIndexSettings`). The with-skill run scoped the crawl, chunked per section, and applied settings with `algolia settings import`.

### Eval 4 — Whole-site crawl across page templates
Given only a root URL, both runs configured autonomous sub-page discovery and acknowledged multiple page types, and both proposed a branching extractor / multiple actions. Only the with-skill run **validated the extractor against a representative page per template** (`crawler test` on more than one URL) and stayed CLI-only end to end — the baseline configured coverage but never sampled/tested across templates, the exact step that keeps a site-wide config from being overfit to the start page.

## Method

For each scenario, two subagents ran the same prompt — one with the skill available, one without — and produced an advisory answer with concrete commands/config (no live Algolia credentials were used). Outputs were graded against the per-eval `expectations` in `evals.json`.
