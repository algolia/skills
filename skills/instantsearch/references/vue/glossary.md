# Glossary (Vue)

Terms the AI must use correctly. Misusing these leads to wrong code or wrong library choices. The cross-cutting Algolia terms (Index, Replica, Facet, Refinement, Filter) match the [React glossary](../react/glossary.md). This file lists the Vue-specific additions.

| Term | Meaning | Watch out for |
|---|---|---|
| **Widget (Vue)** | A pre-built component from `vue-instantsearch` (e.g., `<ais-search-box>`, `<ais-refinement-list>`). Renders UI and manages its own search state. | Prefer widgets and slot overrides over `createWidgetMixin` when possible. |
| **Scoped slot** | A `v-slot` exposed by a widget that gives access to the widget's render data (items, refine function, etc.). | Slot prop names differ per widget. Read the component source before destructuring. |
| **Composable / Mixin** | The Vue equivalent of React's connector hook: `createWidgetMixin(connectFoo)` builds a custom widget around an `instantsearch.js` connector. | Used to access search state without a widget. Prefer slots first. |
| **Server root mixin** | `createServerRootMixin` wraps the app for SSR (`asyncData` / `serverPrefetch`). | Not the same as React's `getServerState`. Read the helper's source for the latest API shape. |
| **vue-instantsearch entry point** | `vue-instantsearch/vue3/es` for Vue 3, `vue-instantsearch/vue2/es` for Vue 2. | Mixing them does not work. Match the project's Vue version. |
| **Insights (Vue)** | Click/conversion analytics, enabled via `:insights="true"` on `<ais-instant-search>`. | Same Algolia Insights as the React skill; not the same as `algolia-mcp`. |
