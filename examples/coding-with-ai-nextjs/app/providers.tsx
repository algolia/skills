"use client";

import type { ReactNode } from "react";
import { InstantSearchNext } from "react-instantsearch-nextjs";
import { searchClient, INDEX_NAME } from "./lib/algolia";

// SSR-safe InstantSearch provider for the App Router. Use <InstantSearchNext>
// from react-instantsearch-nextjs — NOT the plain <InstantSearch> — so search
// state hydrates correctly on the server. Everything Algolia-related lives below
// this provider and is a Client Component.
export function Providers({ children }: { children: ReactNode }) {
  return (
    <InstantSearchNext
      searchClient={searchClient}
      indexName={INDEX_NAME}
      routing={true}
      future={{ preserveSharedStateOnUnmount: true }}
    >
      {children}
    </InstantSearchNext>
  );
}
