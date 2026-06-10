# Autocomplete (Vue)

Vue does not ship an `EXPERIMENTAL_Autocomplete` widget equivalent to React InstantSearch. The recommended path is **`@algolia/autocomplete-js`** integrated into the Vue app, optionally with a wrapper component that mounts and unmounts it via the Vue lifecycle. This is **not** an anti-pattern in Vue (it is in React).

Before implementing, run the [Source-of-truth check](../source-of-truth.md) and confirm the recommended path against the live docs.

## Recommended path: `@algolia/autocomplete-js` in a Vue component

The pattern is:

1. Install `@algolia/autocomplete-js` and `algoliasearch` v5.
2. Create a Vue component that owns a `ref` to a host element.
3. In `onMounted`, call `autocomplete({ container: ref.value, ... })`. Save the returned `instance`.
4. In `onBeforeUnmount`, call `instance.destroy()`.
5. Configure `getSources` to query the same Algolia index used elsewhere; reuse the module-level `searchClient`.

For Vue 3 with `<script setup>`:

```vue
<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from "vue";
import { autocomplete } from "@algolia/autocomplete-js";
import { liteClient as algoliasearch } from "algoliasearch/lite";
import "@algolia/autocomplete-theme-classic";

const searchClient = algoliasearch(import.meta.env.VITE_ALGOLIA_APP_ID, import.meta.env.VITE_ALGOLIA_API_KEY);
const root = ref<HTMLElement | null>(null);
let instance: ReturnType<typeof autocomplete> | undefined;

onMounted(() => {
  if (!root.value) return;
  instance = autocomplete({
    container: root.value,
    placeholder: "Search...",
    getSources: () => [
      {
        sourceId: "products",
        getItems: ({ query }) =>
          searchClient.search({
            requests: [{ indexName: "YOUR_INDEX", query, hitsPerPage: 5 }],
          }).then((res) => res.results[0].hits),
        getItemUrl: ({ item }) => `/products/${item.objectID}`,
        templates: {
          item: ({ item, html }) => html`<a href="/products/${item.objectID}">${item.name}</a>`,
        },
      },
    ],
  });
});

onBeforeUnmount(() => {
  instance?.destroy();
});
</script>

<template>
  <div ref="root"></div>
</template>
```

Confirm the `autocomplete` options shape (`getSources`, `templates`, `plugins`) and the `algoliasearch` v5 search method against installed types and the live docs before scaffolding. Both have evolved.

## Alternative: `<ais-search-box>` for non-autocomplete inputs

If the user wants a simple search input on a results page (no dropdown of suggestions), use `<ais-search-box>` inside `<ais-instant-search>`. This is not autocomplete; it is the search input for an InstantSearch widget tree. Don't confuse the two.

## Multiple sources, recent searches, query suggestions

Same building blocks as the React autocomplete: query suggestions index, recent-searches plugin, multi-source `getSources` array. Read `https://www.algolia.com/doc/ui-libraries/autocomplete/api-reference/autocomplete-js` for the up-to-date plugin and source APIs.

## Live doc

`https://www.algolia.com/doc/ui-libraries/autocomplete/integrations/vue` is the canonical Vue integration guide; consult it before scaffolding.
