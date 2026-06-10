# Glossary (InstantSearch.js)

Terms the AI must use correctly. Cross-cutting Algolia terms (Index, Replica, Facet, Refinement, Filter) match the [React glossary](../react/glossary.md). This file lists JS-specific additions.

| Term | Meaning | Watch out for |
|---|---|---|
| **Widget (JS)** | An object returned by a factory like `refinementList({...})`. Mounts via `search.addWidgets([...])` and unmounts via `removeWidgets`. | Widgets are imperative here; do not assume React/Vue lifecycle. |
| **Container** | The DOM element (CSS selector or element reference) where a widget renders, passed via the `container` option. | Required for visible widgets. The DOM must exist before `search.start()` for widgets registered up front. |
| **Connector** | A factory like `connectRefinementList(renderFn)` that returns a custom widget bound to your render function. The escape hatch for fully custom DOM. | Use when the built-in widget's `templates` cannot express the design. |
| **`templates`** | Per-widget option for replacing rendered HTML. Accepts strings, functions, or tagged templates. | Read the widget's type for accepted keys; signatures differ per widget. |
| **`cssClasses`** | Per-widget option for appending custom classes to the default `ais-*` ones. | Keys differ per widget; type-check before using. |
| **`search.start()`** | Boots the InstantSearch instance once all initial widgets are registered. | Call once. Add more widgets later with `addWidgets`. |
| **`getInitialResults`** | The SSR helper. Walks the widget tree, performs initial searches, returns serializable state. | Pair with `initialUiState` / hydration on the client. Read the source for the current API. |
| **Insights (JS)** | Click/conversion analytics, enabled via `insights: true` in `instantsearch({...})`. | Same Algolia Insights as the React/Vue skill. |
