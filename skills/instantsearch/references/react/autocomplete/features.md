# Autocomplete Feature Implementation Guidance

The autocomplete widget is exported as `EXPERIMENTAL_Autocomplete` from `react-instantsearch`. Despite the `EXPERIMENTAL_` prefix, this is the widget to use. It is the maintained autocomplete path in React InstantSearch.

## Discovering Widget Capabilities

Before implementing any feature manually, read the type definitions from `node_modules/react-instantsearch` to discover `EXPERIMENTAL_Autocomplete`'s available props. Do not rely on training data or web searches for this. The installed types are the source of truth. Many features (recent searches, keyboard navigation, responsive behavior, etc.) are handled via built-in props.

- Use built-in props rather than building custom behavior
- If a feature is available as a prop, use it. Do not reimplement it
- If the widget cannot do what's needed, ask the user before reaching for a connector or custom code
- Handle empty and error states. Provide a no-results component. The widget won't display anything for empty results by default. Inspect the types to find the right prop for this (e.g., on the index configuration), and provide a component that renders a helpful message

## Placement

Explore the codebase to find where the autocomplete should live. Look for an existing search input, a header/navbar, or a natural entry point. If the site already has a search bar placeholder, replace it. If not, ask the user where the autocomplete should go.

## Features Checklist

Consider each of the following. Include them when the index and use case support it:

- [ ] Multiple sources in grouped sections (if the index has multiple relevant data types)
- [ ] Rich result previews (adapted to rendering preferences from discovery)
- [ ] Submit navigates to a search results page
- [ ] Recent searches shown as a source
- [ ] Responsive behavior (desktop dropdown, mobile full-screen)

## Multiple Sources

The autocomplete should present results from multiple sources in visually grouped sections. Common sources:

- **Query suggestions**: predicted searches based on what the user is typing
- **Products/items**: actual records from the main index, rendered as rich previews
- **Categories**: matching category names for quick navigation
- **Brands/collections**: matching brand or collection names

Adapt the sources to what the index actually supports. Check the discovery context for the query suggestions index and available schema. Not every index has query suggestions or categories. Don't fabricate sources.

When using `showQuerySuggestions`, you must also set `getURL` on it. Otherwise selecting a suggestion has no action. Typically this navigates to the search results page with the suggestion as the query.

## Rich Result Previews

The record schema (discovered from the user or existing code) is the source of truth for what data is available and what can be rendered. Don't guess which attributes exist. Check the schema first.

Common patterns:

- Image thumbnail + highlighted name + price + rating
- Image + highlighted name + short description
- Compact text-only for non-product sources (categories, brands)

Adapt these to the actual attributes in the index. If the records have no image field, don't propose an image layout. If they have a description, offer it as an option.

Always use `<Highlight attribute="..." hit={hit} />` for text attributes that should reflect the search query.

## Item Navigation

Records typically have a URL (e.g., a product detail page). Each autocomplete result must be navigable:

- Use `indices[].getURL` to return the item's URL. This handles keyboard navigation (Enter key)
- In `indices[].itemComponent`, render items as links so they are clickable

Both are needed. `getURL` alone doesn't make items clickable; a link in `itemComponent` alone doesn't handle keyboard Enter.

Use the detail page route pattern found during discovery. If the record doesn't have an explicit URL attribute, ask the user which record attribute to use for the URL slug. Do not assume `objectID` is the right value. The detail page may use a different field (e.g., `id`, `slug`, `handle`).

## Submit and Search Results Page

When the user submits a query (enter key or search button), the autocomplete should navigate to the search results page found during discovery.

- If a results page route exists, wire the autocomplete submit to that route using the project's existing routing patterns
- If there is no results page, the autocomplete should only show dropdown results with no submit behavior

For responsive behavior, interaction states, and all autocomplete styling details, see [Autocomplete styling](styling.md).

## Search parameters

The autocomplete widget does not use `<Configure>`. Unlike most widgets, it does not inherit from it. Each index source controls its own search parameters (like `hitsPerPage` or `filters`) through its own configuration. Do not add a `<Configure>` widget to pass search parameters for autocomplete.
