"use client";

import { SearchBox, Hits } from "react-instantsearch";
import type { ProductHit } from "../lib/algolia";

// A hit rendered in the classic search results grid (separate from the chat
// carousel). Shares the same searchClient + index as the chat via the
// InstantSearchNext provider in app/providers.tsx.
function Hit({ hit }: { hit: ProductHit }) {
  return (
    <article className="hit">
      {hit.image ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={hit.image} alt={hit.name ?? hit.objectID} className="hit-image" />
      ) : null}
      <h3 className="hit-name">{hit.name ?? hit.objectID}</h3>
      {hit.brand ? <p className="hit-brand">{hit.brand}</p> : null}
      {hit.price != null ? <p className="hit-price">${hit.price}</p> : null}
    </article>
  );
}

export function Search() {
  return (
    <section className="search">
      <SearchBox placeholder="Search products…" />
      <Hits hitComponent={Hit} />
    </section>
  );
}
