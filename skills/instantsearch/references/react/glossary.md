# Glossary

Terms the AI must use correctly. Misusing these leads to wrong code or wrong library choices.

| Term | Meaning | Watch out for |
|---|---|---|
| **Widget** | A pre-built UI component from React InstantSearch (e.g., `<SearchBox>`, `<RefinementList>`). Renders UI and manages its own search state. | Prefer widgets over hooks/connectors when possible. |
| **Connector / Hook** | Connectors are the underlying API shared across all InstantSearch libraries. In React InstantSearch, hooks (e.g., `useSearchBox`) wrap connectors and are the way to access search state without a widget. | Prefer widgets over hooks when a widget can do the job. |
| **Autocomplete widget** | `EXPERIMENTAL_Autocomplete`, exported from `react-instantsearch`. Despite the `EXPERIMENTAL_` prefix, this is the maintained autocomplete component. | Do not confuse with the **standalone autocomplete library** (`@algolia/autocomplete-js`), which is a separate, legacy package. |
| **Index** | An Algolia index. A collection of records configured for search. Has its own settings (searchable attributes, ranking, facets). | Never hardcode index names. Always ask the user. |
| **Replica** | A copy of an index with different ranking or sorting. Used for "sort by" features (e.g., price ascending). | Not a separate dataset. It shares records with the primary index. Don't create a new index when the user wants sorting. |
| **Facet** | An attribute configured for filtering in the index settings. Used with widgets like `<RefinementList>` or `<Menu>`. | Not every attribute is a facet. Only those configured as `attributesForFaceting` in the index settings. |
| **Refinement** | A filter actively applied by the user (e.g., selecting "Nike" in a brand facet). | "Refinement" is the Algolia/InstantSearch term. The AI may say "filter". That's fine conversationally, but use "refinement" in code (e.g., `<RefinementList>`, `<CurrentRefinements>`). |
| **Filter** | A broader term. In Algolia, filters can be set programmatically via `<Configure filters="..." />` or by the user via refinement widgets. | Don't confuse programmatic filters (set by the developer) with refinements (set by the user). |
