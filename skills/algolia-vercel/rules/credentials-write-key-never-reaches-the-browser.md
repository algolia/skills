---
title: Only the Search-Only Key Goes to the Browser
impact: BLOCKING
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
# .env.local — every NEXT_PUBLIC_ value here is inlined into the client bundle
NEXT_PUBLIC_ALGOLIA_APP_ID="..."
NEXT_PUBLIC_ALGOLIA_SEARCH_API_KEY="..."
NEXT_PUBLIC_ALGOLIA_WRITE_API_KEY="..."   # shipped to every visitor
```

Using the write key "just to get search working" is the same defect from the other direction: the full client sends write requests, and its key is public.

**Correct (two keys, two scopes):**

Only the browser-safe pair gets a `NEXT_PUBLIC_` name. This is the five-variable set the merge in `credentials-pull-without-clobbering` writes:

```bash
# .env.local
NEXT_PUBLIC_ALGOLIA_APP_ID="..."          # browser
NEXT_PUBLIC_ALGOLIA_SEARCH_API_KEY="..."  # browser, search-only
ALGOLIA_APP_ID="..."                      # server
ALGOLIA_SEARCH_API_KEY="..."              # server, raw name — next.config.js / route handlers read this
ALGOLIA_WRITE_API_KEY="..."               # server only — no NEXT_PUBLIC_ twin, ever
```

Keeping the search key under both names is not a leak: it is the same search-only credential either way. The asymmetry is only about the write key.

**Correct (map the raw names to the public ones in `next.config.js`):**

The local `.env.local` above is only half the story. Vercel injects the **raw** names — `ALGOLIA_APP_ID`, `ALGOLIA_SEARCH_API_KEY`, `ALGOLIA_WRITE_API_KEY` — into builds and into the deployed runtime. It does not invent `NEXT_PUBLIC_` twins, so a client component reading `process.env.NEXT_PUBLIC_ALGOLIA_APP_ID` gets `undefined` on Vercel even though it worked locally. Derive the two public names from the raw ones in the config, and the same client code then works in both places:

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

Three things about this block:

- **Merge, do not replace.** If the project already has a `next.config.js` / `.mjs` / `.ts`, add the `env` key to the config object it already exports and leave the rest of it — `images`, `redirects`, `experimental` — untouched. Keep any wrapper too: `module.exports = withMDX(nextConfig)` stays `withMDX(nextConfig)`, with `env` added inside `nextConfig`. An ESM config uses `export default nextConfig`; a TypeScript one keeps its `NextConfig` type annotation.
- **Everything in `env` is public.** The block is inlined into the browser bundle, so it is exactly as exposed as a `NEXT_PUBLIC_` variable. Never put the write key here, and never put anything else secret here either.
- **It also makes local behave like deployed.** Locally these read from the five-variable `.env.local` the merge in `credentials-pull-without-clobbering` writes, where both the raw and public names exist; the config just overrides the public two with the raw values, which are identical. One code path, both environments.

Server-side code — route handlers, indexing scripts — keeps reading the raw `process.env.ALGOLIA_*` names directly and needs nothing from this block.

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

Never run a line-printing grep, a `cat`, or a `diff` against a file that holds real keys. To inspect a dotenv file, read the key side only: `cut -d= -f1 "$STAGING"`.

Variable names come from the integration and are not guaranteed stable — confirm them with `vercel integration guide algolia --framework <framework>` and `vercel env ls` rather than assuming these three. The security rule holds regardless of naming: exactly one key is browser-safe, and it is the search-only one.

## Sources

- `vercel integration guide algolia --framework nextjs` (Vercel CLI 56.2.1) — variable table and the `NEXT_PUBLIC_` mapping, write key marked "server-side only, never expose it in the browser"
- https://nextjs.org/docs/app/api-reference/config/next-config-js/env — `env` values are inlined into the bundle at build time
- https://www.algolia.com/doc — API key ACLs and search-only keys
