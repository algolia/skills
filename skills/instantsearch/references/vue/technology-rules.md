# Technology Rules (Vue)

These rules apply to **all** Vue InstantSearch patterns. Coverage in this skill is limited to library-level rules and autocomplete; for other patterns, follow the [Source-of-truth check](source-of-truth.md) and ask the user before scaffolding non-trivial flows.

## Always

- **Before using any widget, slot, composable, prop, or middleware not explicitly documented in this skill, complete the [Source-of-truth check](source-of-truth.md).** Do not write code from training-data recall alone.
- Pick the entry point that matches the project's Vue version: `vue-instantsearch/vue3/es` for Vue 3, `vue-instantsearch/vue2/es` for Vue 2. Do not mix.
- If `vue-instantsearch` and `algoliasearch` are not already installed, install the latest versions and **wait for the install to complete** before proceeding. Use the project's package manager.
- Use `algoliasearch` v5. Prefer the lite client for web apps: `import { liteClient as algoliasearch } from "algoliasearch/lite";`
- **Declare the search client outside of the Vue component / setup function.** The reference must remain stable to preserve the client's internal cache.
- **Place `<ais-instant-search>` high in the component tree**, typically in `App.vue` or a root layout. Other widgets nest inside it.
- Use `<ais-highlight>` on displayed text attributes; use `<ais-snippet>` for long text. Set `attributesToHighlight` and `attributesToSnippet` via `<ais-configure>` so the response carries the markup.
- Use `<ais-configure>` for `hitsPerPage` and other index params.
- Prefer built-in widgets with `class-names` props (Vue InstantSearch exposes them via slots and props) over custom composables when possible.
- Set `:insights="true"` on `<ais-instant-search>` for click analytics.
- **Set up routing** by passing `:routing="true"` (or a routing object) on `<ais-instant-search>`. Read the prop type for full configuration.

## Never

- **Never use vue-instantsearch v3 syntax with v4.** Slot names and prop names changed; copy-paste from older docs will break.
- **Never guess credentials or index names.** Always ask the user.
- **Never start coding before completing discovery** (see SKILL.md Discover step).
- **Never overuse composables / mixins.** If `<ais-refinement-list>` with slot overrides achieves the design, do not write `createWidgetMixin`-based custom code.
- **Never fall back to legacy libraries.** No `vue-algolia`, no `vue-instantsearch` v3 imports in a v4 project.
- **Never guess slot props.** Vue InstantSearch's scoped slots expose specific names per widget; read the component source before destructuring in a `v-slot`.
