# Technology Rules (InstantSearch.js)

These rules apply to **all** InstantSearch.js patterns. Coverage in this skill is limited to library-level rules and autocomplete; for other patterns, follow the [Source-of-truth check](source-of-truth.md) and ask the user before scaffolding non-trivial flows.

## Always

- **Before using any widget, connector, option, middleware, or router that is not explicitly documented in this skill, complete the [Source-of-truth check](source-of-truth.md).** Do not write code from training-data recall alone.
- If `instantsearch.js` and `algoliasearch` are not already installed, install the latest versions and **wait for the install to complete** before proceeding. Use the project's package manager. If the project uses a CDN (jsDelivr, unpkg with script tags), follow that pattern instead.
- Use `algoliasearch` v5. For browser bundles, prefer the lite client: `import { liteClient as algoliasearch } from "algoliasearch/lite";`
- **Declare the search client in module scope** (or a single shared module) so it is reused across the page. The reference must remain stable.
- Create the search instance once with `const search = instantsearch({ ... })` and call `search.start()` once. Do not recreate the instance on framework re-renders.
- Mount widgets via `search.addWidgets([ refinementList({...}), hits({...}), ... ])`. The factories are imported from `instantsearch.js/es/widgets`.
- Use the `highlight` widget / template helper on displayed text and `snippet` for long text. Set `attributesToHighlight` and `attributesToSnippet` via the `configure` widget so the response carries the markup.
- Use the `configure` widget for `hitsPerPage` and other index params.
- Prefer built-in widgets and template options over connectors when the widget can achieve the design.
- Set `insights: true` in `instantsearch({ insights: true, ... })` for click analytics.
- **Set up routing** by passing `routing: true` (or a routing object with `router` and `stateMapping`) in `instantsearch({...})`. Read the router type for full configuration.

## Never

- **Never use v3 syntax in a v4+ project.** Widget option names changed; copy-paste from older docs will break silently.
- **Never call `search.start()` more than once** on the same instance.
- **Never guess credentials or index names.** Always ask the user.
- **Never mix `instantsearch.js` and `react-instantsearch` / `vue-instantsearch` in the same widget tree.** Pick one library per page.
- **Never overuse connectors.** If the built-in widget with `cssClasses` and `templates` works, use it. Connectors are for genuinely custom rendering.
- **Never guess connector renderState shape.** Read `connect<Name>.d.ts` from `node_modules/instantsearch.js/es/connectors/` before destructuring.
