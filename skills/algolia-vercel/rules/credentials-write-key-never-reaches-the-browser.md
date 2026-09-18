---
title: Map the Injected Names, and Keep the Write Key Out of the Browser
impact: CRITICAL
impactDescription: a write key in the client bundle lets anyone overwrite or delete the index, and the wrong variable name silently points the app at nothing
tags: credentials, security, keys
---

## Map the Injected Names, and Keep the Write Key Out of the Browser

Assume the Vercel workflow already made these available to the process. The names it injects are not the names the Algolia CLI expects, nor the names a browser bundle is configured with:

| Injected                 | Means               | Algolia CLI variable           | Browser-safe |
| ------------------------ | ------------------- | ------------------------------ | ------------ |
| `ALGOLIA_APP_ID`         | Application ID      | `ALGOLIA_APPLICATION_ID`       | yes          |
| `ALGOLIA_SEARCH_API_KEY` | Search-only key     | `ALGOLIA_API_KEY` — for reads  | yes          |
| `ALGOLIA_WRITE_API_KEY`  | Write key           | `ALGOLIA_API_KEY` — for writes | **never**    |

SDK clients do not read these variables: `algoliasearch(appId, apiKey)` receives the application ID and the key chosen for that operation as explicit arguments. Server-side code is free to pass the injected values straight in.

Two consequences:

- **`ALGOLIA_API_KEY` is one slot, filled per operation.** Search and import both read it, so set it deliberately each time rather than inheriting whatever an earlier command left in it. An import running under the search key fails; a search running under the write key "works" and proves nothing about what the app will carry.
- **Exactly one key is browser-safe.** Anything a framework marks public ends up in a bundle served to every visitor. `NEXT_PUBLIC_ALGOLIA_WRITE_API_KEY` is extractable from the shipped JavaScript, and it can rewrite or wipe the index. Using the write key "just to get search working" is the same defect from the other side.

If the resource was connected with a prefix, the injected names differ. Take them verbatim from the project's configured variables and substitute them consistently — do not guess the transformation, and do not re-provision to get unprefixed names.

### Getting the two public values into client code

Follow whatever the project already does for public configuration. In Next.js, Vercel injects the **raw** names and does not invent `NEXT_PUBLIC_` twins, so derive them — merging into the existing config object, keeping any wrapper, and leaving `images`, `redirects`, `experimental` alone.

**Incorrect (write key published to every visitor):**

```js
// next.config.js
const nextConfig = {
  env: {
    NEXT_PUBLIC_ALGOLIA_APP_ID: process.env.ALGOLIA_APP_ID,
    NEXT_PUBLIC_ALGOLIA_WRITE_API_KEY: process.env.ALGOLIA_WRITE_API_KEY,
  },
};
```

**Correct (app ID and search-only key only):**

```js
// next.config.js — everything in `env` is inlined into the client bundle at build time
const nextConfig = {
  env: {
    NEXT_PUBLIC_ALGOLIA_APP_ID: process.env.ALGOLIA_APP_ID,
    NEXT_PUBLIC_ALGOLIA_SEARCH_API_KEY: process.env.ALGOLIA_SEARCH_API_KEY,
  },
};
```

That block is an example of the mapping, not a required file: other frameworks expose public values differently, and `vercel integration guide algolia --framework <your framework>` states which mechanism this integration expects. The rule is the same everywhere — app ID and search-only key to the browser, write key server-side only.

Server-side code — route handlers, indexing scripts — reads the raw injected names directly and needs no public mapping.

## Sources

- `vercel integration guide algolia --framework nextjs` — injected variable table; write key marked "server-side only, never expose it in the browser"
- <https://nextjs.org/docs/app/api-reference/config/next-config-js/env> — `env` values are inlined into the bundle at build time
- <https://www.algolia.com/doc/guides/security/api-keys/> — API key ACLs and search-only keys
- `algolia --help` (Algolia CLI 1.17.0) — `ALGOLIA_APPLICATION_ID` / `ALGOLIA_API_KEY` environment variables
