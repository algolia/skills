---
title: Let Vercel Create the Algolia Application
impact: BLOCKING
impactDescription: an Algolia-side signup produces a second, unbilled, unconnected application
tags: provisioning, marketplace, ownership
---

## Let Vercel Create the Algolia Application

On the Vercel Marketplace path, Vercel is the system of record for the Algolia application. It creates the application, injects the credentials into the project, and puts the usage on the Vercel invoice.

Creating the application from the Algolia side instead produces a *different* application. Its credentials never appear in the Vercel project, so `vercel env pull` keeps returning nothing and the deployed app keeps failing — while the user now has two applications to reason about.

**Incorrect (provisioning from the Algolia side):**

```bash
# User said "set up Algolia for our Vercel project"
algolia auth signup
algolia application create --name "storefront" --region EU --plan free --accept-terms
vercel env add ALGOLIA_APP_ID        # hand-copying credentials Vercel would have injected
```

This creates an Algolia-billed application unknown to the Vercel Marketplace. The env vars are hand-maintained, drift on key rotation, and nothing connects the resource to the project.

**Correct (provisioning through Vercel):**

```bash
# PLAN_ID and REGION_CODE come from `vercel integration add algolia --help`; the IDs are
# version-stamped, so read them live rather than carrying one over from a previous run.
: "${PLAN_ID:?Set PLAN_ID to the exact ID from the live --help output}"
: "${REGION_CODE:?Set REGION_CODE to a cluster_region_code option from the same output}"
vercel link --yes --project storefront --scope acme-team
vercel integration add algolia --name storefront-search --scope acme-team \
  -m cluster_region_code="$REGION_CODE" --plan "$PLAN_ID" -e development --no-env-pull
```

`-e development` is illustrative — pass the environment(s) the user chose, and pull that same environment afterwards (`vercel env pull "$STAGING" --environment development`), because `env pull` defaults to Development no matter what `add` received.

Vercel creates the application, connects it to the linked project, and injects `ALGOLIA_APP_ID`, `ALGOLIA_SEARCH_API_KEY`, and `ALGOLIA_WRITE_API_KEY`.

The Algolia CLI is still the right tool for *data and configuration* against that application — use it with the injected credentials, not with its own login. `$ALGOLIA_VERCEL_SKILL_DIR` is the absolute path of the directory holding this skill's `SKILL.md` (wherever it is installed, not a path in the app's repo) and `$STAGING` is the env file pulled in the credentials phase:

```bash
node "$ALGOLIA_VERCEL_SKILL_DIR/scripts/with-algolia-env.mjs" "$STAGING" ALGOLIA_WRITE_API_KEY -- \
  algolia objects import example_products -F example.ndjson -w
```

`algolia profile add` is deprecated in Algolia CLI 1.17.0; environment variables take precedence over every other credential source, and the helper sets them for the child command from the pulled file — so no profile is needed.

## Sources

- `vercel integration add --help` (Vercel CLI 56.2.1)
- https://vercel.com/docs/cli/integration
- `algolia profile add --help` (Algolia CLI 1.17.0) — marked `[Deprecated]`
- Credential precedence: env vars > CLI flags > profile config (`algolia-cli` skill)
