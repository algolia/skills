import { liteClient } from "algoliasearch/lite";

// Public config. NEXT_PUBLIC_* values are inlined into the client bundle at
// build time (App Router equivalent of Vite's import.meta.env — NOT the same).
export const APP_ID = process.env.NEXT_PUBLIC_ALGOLIA_APP_ID!;
export const SEARCH_API_KEY = process.env.NEXT_PUBLIC_ALGOLIA_SEARCH_API_KEY!;
export const INDEX_NAME = process.env.NEXT_PUBLIC_ALGOLIA_INDEX_NAME!;
export const AGENT_ID = process.env.NEXT_PUBLIC_ALGOLIA_AGENT_ID!;

// Search-only lite client, shared by InstantSearch and the chat search UI.
export const searchClient = liteClient(APP_ID, SEARCH_API_KEY);

// Minimal product-hit shape. Adjust field names to match your index schema.
export type ProductHit = {
  objectID: string;
  name?: string;
  price?: number | string;
  image?: string;
  brand?: string;
  // Per-query attribution token. InstantSearch stamps this on every hit it
  // renders in the chat carousel; the itemComponent reads it to attribute
  // click/conversion events back to the agent's search.
  __queryID?: string;
};
