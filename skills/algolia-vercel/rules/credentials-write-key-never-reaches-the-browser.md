---
title: Only the Search-Only Key Goes to the Browser
impact: CRITICAL
impactDescription: a write key in the client bundle lets anyone overwrite or delete the index
tags: credentials, security, keys
---

## Only the Search-Only Key Goes to the Browser

The integration injects three variables. They are not interchangeable:

| Variable                 | Purpose                                                  |
| ------------------------ | -------------------------------------------------------- |
| `ALGOLIA_APP_ID`         | Application ID                                           |
| `ALGOLIA_SEARCH_API_KEY` | Search-only key — safe to expose in the browser          |
| `ALGOLIA_WRITE_API_KEY`  | Write key — **server-side only, never expose it**        |

Anything a framework marks as public ends up in a bundle served to every visitor. In Next.js that marker is the `NEXT_PUBLIC_` prefix. A write key behind that prefix is extractable from the shipped JavaScript, and it can rewrite or wipe the index.

**Incorrect (write key exposed):**

```bash
NEXT_PUBLIC_ALGOLIA_WRITE_API_KEY="..."   # shipped to every visitor
```

Using the write key "just to get search working" is the same defect from the other direction: the full client sends write requests, and its key is public.

**Correct (map the raw names to the public ones in `next.config.js`):**

Vercel injects the **raw** names into builds and into the deployed runtime; it does not invent `NEXT_PUBLIC_` twins. Derive the two browser-safe ones in the config, and the same client code works locally and on Vercel:

```js
// next.config.js — every value in `env` is inlined into the client bundle at build time
const nextConfig = {
  env: {
    NEXT_PUBLIC_ALGOLIA_APP_ID: process.env.ALGOLIA_APP_ID,
    NEXT_PUBLIC_ALGOLIA_SEARCH_API_KEY: process.env.ALGOLIA_SEARCH_API_KEY,
    // No ALGOLIA_WRITE_API_KEY line. Not commented out — absent.
  },
};

module.exports = nextConfig;
```

- **Merge, do not replace.** If the project already has a `next.config.js` / `.mjs` / `.ts`, add the `env` key to the config object it already exports and leave `images`, `redirects`, `experimental` alone. Keep any wrapper: `module.exports = withMDX(nextConfig)` stays that, with `env` added inside `nextConfig`. An ESM config uses `export default nextConfig`; a TypeScript one keeps its `NextConfig` annotation.
- **Everything in `env` is public.** The block is inlined into the browser bundle. Never put the write key here, and nothing else secret either.
- **One mapping covers both sides.** On Vercel the raw names come from the build environment. Locally they come from `vercel env run` — so start the dev server through it and the mapping resolves the same way:

  ```bash
  vercel env run -e development --scope acme-team -- npm run dev
  ```

  Started as a bare `npm run dev`, the raw names are absent and the two public values are `undefined`. That is the symptom, not a reason to hardcode anything.
- **Prefixed variables.** If the resource was connected with `--prefix`, the injected names differ. Take them verbatim from `vercel env ls` and use those on the right-hand side of both mappings; the `NEXT_PUBLIC_` names on the left can stay as they are.

Server-side code — route handlers, indexing scripts — reads the raw `process.env.ALGOLIA_*` names directly and needs nothing from this block.

```js
// lib/algolia.js — browser: lite client, search-only key
import { liteClient as algoliasearch } from 'algoliasearch/lite';

export default algoliasearch(
  process.env.NEXT_PUBLIC_ALGOLIA_APP_ID,
  process.env.NEXT_PUBLIC_ALGOLIA_SEARCH_API_KEY,
);
```

```js
// scripts/index-products.js — server only, never imported from a client component
import { algoliasearch } from 'algoliasearch';

const client = algoliasearch(
  process.env.ALGOLIA_APP_ID,
  process.env.ALGOLIA_WRITE_API_KEY,
);
```

Checks worth running before calling the credentials phase done:

```bash
# No public mapping of the write key in source. Source files are safe to print matches from.
grep -rn "NEXT_PUBLIC.*WRITE" . --include="*.js" --include="*.ts" --include="*.tsx"

# Same check over dotenv files — -l, filenames only. A matching line here IS the key.
grep -rl "NEXT_PUBLIC.*WRITE" . --include=".env*"

# The write key is not referenced from client components
grep -rl "ALGOLIA_WRITE_API_KEY" app components src 2>/dev/null
```

Never run a line-printing grep, a `cat`, or a `diff` against a file that holds real keys. To inspect a dotenv file, read the key side only: `cut -d= -f1 .env.local`.

Variable names come from the integration and are not guaranteed stable — confirm them with `vercel env ls` and `vercel integration guide algolia --framework <framework>` rather than assuming these three. The security rule holds regardless of naming: exactly one key is browser-safe, and it is the search-only one.

## Sources

- `vercel integration guide algolia --framework nextjs` (Vercel CLI 56.2.1) — variable table and the `NEXT_PUBLIC_` mapping, write key marked "server-side only, never expose it in the browser"
- https://nextjs.org/docs/app/api-reference/config/next-config-js/env — `env` values are inlined into the bundle at build time
- https://vercel.com/docs/cli/env#running-commands-with-environment-variables — `env run` passes the project's variables to the command it starts
- https://www.algolia.com/doc/guides/security/api-keys/ — API key ACLs and search-only keys
