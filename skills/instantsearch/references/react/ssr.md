# Server-side Rendering (React)

Pick the right tool for the framework. Mixing the two paths causes hydration mismatches and double-fetches.

| Framework / setup                                      | Use                                                            | Do not                                       |
| ------------------------------------------------------ | -------------------------------------------------------------- | -------------------------------------------- |
| Next.js **App Router**                                 | `<InstantSearchNext>` from `react-instantsearch-nextjs`        | `getServerState`. Don't add it on top.       |
| Next.js **Pages Router**                               | `getServerState` + `<InstantSearchSSRProvider>` (this file)    | `<InstantSearchNext>` (App Router only)      |
| Remix, vanilla React SSR, anything that hydrates HTML  | `getServerState` + `<InstantSearchSSRProvider>` (this file)    | A naive `<InstantSearch>` without SSR helpers, which renders empty results on the server |
| Vite SPA, CRA-style, anything fully CSR                | Plain `<InstantSearch>`                                        | Any SSR helpers                              |

Live doc: `https://www.algolia.com/doc/guides/building-search-ui/going-further/server-side-rendering/react`.

## Path A: Next.js App Router

Use `<InstantSearchNext>` and stop. It already integrates with App Router's RSC + streaming and walks the tree on the server. The provider goes high in the tree (a `layout.tsx` is typical), with `routing` and `insights` props as usual.

```tsx
// app/layout.tsx
"use client";

import { InstantSearchNext } from "react-instantsearch-nextjs";
import { liteClient as algoliasearch } from "algoliasearch/lite";

const searchClient = algoliasearch(process.env.NEXT_PUBLIC_ALGOLIA_APP_ID!, process.env.NEXT_PUBLIC_ALGOLIA_API_KEY!);

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <InstantSearchNext
          searchClient={searchClient}
          indexName="YOUR_INDEX"
          routing
          insights
        >
          {children}
        </InstantSearchNext>
      </body>
    </html>
  );
}
```

Do not call `getServerState` from a server component or page. Do not wrap children in `<InstantSearchSSRProvider>`. Doing either creates a second SSR pass that races with `<InstantSearchNext>`'s and produces hydration mismatches.

For prop details specific to App Router, read `node_modules/react-instantsearch-nextjs/dist/es/InstantSearchNext.d.ts`.

## Path B: Pages Router, Remix, vanilla React SSR

Use `getServerState` to walk the tree and pre-fetch results, pass the result via `<InstantSearchSSRProvider>`. The `<InstantSearch>` provider stays as the inner provider.

```tsx
// pages/search.tsx (Pages Router shape; adapt to your framework's data-loading API)
import {
  InstantSearch,
  InstantSearchSSRProvider,
  type InstantSearchServerState,
} from "react-instantsearch";
import { getServerState } from "react-instantsearch/server";
import { liteClient as algoliasearch } from "algoliasearch/lite";

const searchClient = algoliasearch(process.env.NEXT_PUBLIC_ALGOLIA_APP_ID!, process.env.NEXT_PUBLIC_ALGOLIA_API_KEY!);

type Props = { serverState?: InstantSearchServerState; url: string };

function SearchPage({ serverState, url }: Props) {
  return (
    <InstantSearchSSRProvider {...serverState}>
      <InstantSearch
        searchClient={searchClient}
        indexName="YOUR_INDEX"
        routing={{ /* router with serverUrl: url, see below */ }}
        insights
      >
        {/* widget tree */}
      </InstantSearch>
    </InstantSearchSSRProvider>
  );
}

export async function getServerSideProps({ req }: { req: { url?: string } }) {
  const protocol = "https";
  const url = `${protocol}://${req.headers?.host ?? "localhost"}${req.url ?? "/"}`;
  const serverState = await getServerState(<SearchPage url={url} />, { renderToString });
  return { props: { serverState, url } };
}
```

A few things matter:

- The component passed to `getServerState` must be the **same tree** the client renders, so it can collect search params from every nested widget. Refactor shared components rather than duplicating the tree.
- `routing` needs a `serverUrl` (or equivalent) so the server-side router resolves URL-derived state. Read `routing.router`'s type for the option name in the installed version.
- Pass `renderToString` (from `react-dom/server`) into `getServerState`. Required for the walker.

For prop details, read:

- `node_modules/react-instantsearch/dist/es/server/getServerState.d.ts`
- `node_modules/react-instantsearch/dist/es/components/InstantSearchSSRProvider.d.ts`

## Common pitfalls

- **Mixing App Router with `getServerState`.** Causes double-fetch and hydration mismatches. Pick one path.
- **Different widget trees on server and client.** `getServerState` only sees what's in its tree; widgets mounted later won't have server-prefetched data. Render the same tree on both sides.
- **Stateful `searchClient` per request.** The client must be stable. Declare it module-level (outside the component) and reuse across requests; do not create a new client inside `getServerSideProps`.
- **Forgetting `serverUrl` for routing on the server.** Without it, the router cannot read the request URL and state mapping breaks on first render.
- **Putting the provider too low in the tree.** SSR walks from `<InstantSearchSSRProvider>` down. If half the widget tree lives outside it, those widgets won't have server data.

If your setup does not fit either path, ask the user. Do not invent a third way.
