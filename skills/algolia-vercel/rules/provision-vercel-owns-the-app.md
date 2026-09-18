---
title: On This Path, Vercel Creates the Algolia Application
impact: HIGH
impactDescription: an Algolia-side signup produces a second application the Vercel project knows nothing about
tags: provisioning, marketplace, ownership
---

## On This Path, Vercel Creates the Algolia Application

This rule is about the application being provisioned here, not about the user's Algolia account in general. When Algolia is added as a Vercel Marketplace resource, Vercel creates *that* application, injects its credentials into the project, and puts *its* usage on the Vercel invoice. Applications the user already owns directly stay theirs — see the standalone exclusion in `SKILL.md`.

Creating this one from the Algolia side instead produces a *different* application. Its credentials never appear in the Vercel project, so `vercel env run` and `vercel env ls` keep showing nothing Algolia-shaped, and the user now has two applications to reason about.

**Incorrect (provisioning from the Algolia side):**

```bash
# User said "set up Algolia for our Vercel project"
algolia auth signup
algolia application create --name "storefront" --region EU --plan free --accept-terms
vercel env add ALGOLIA_APP_ID        # hand-copying credentials Vercel would have injected
```

The env vars are hand-maintained, drift on key rotation, and nothing connects a resource to the project.

**Correct (provisioning through Vercel):**

```bash
# PLAN_ID and REGION_CODE come from `vercel integration add algolia --help`, read live.
: "${PLAN_ID:?Set PLAN_ID to the exact ID from the live --help output}"
: "${REGION_CODE:?Set REGION_CODE to a cluster_region_code option from the same output}"
vercel link --yes --project storefront --scope acme-team
vercel integration add algolia --name storefront-search --scope acme-team \
  -m cluster_region_code="$REGION_CODE" --plan "$PLAN_ID" -e development --no-env-pull
```

`-e development` is illustrative — pass the environment(s) the user chose, and name that same environment on `vercel env run -e …` afterwards, because `env run` defaults to development.

Vercel creates the application, connects it to the linked project, and injects `ALGOLIA_APP_ID`, `ALGOLIA_SEARCH_API_KEY`, and `ALGOLIA_WRITE_API_KEY` (prefixed if `--prefix` was passed — confirm with `vercel env ls`).

The Algolia CLI is still the right tool for *data and configuration* against that application — run it with the injected credentials rather than its own login, as in `credentials-run-with-vercel-env`. `algolia profile add` is deprecated in Algolia CLI 1.17.0, and environment variables take precedence over every other credential source, so no profile and no `algolia auth login` are needed here.

## Sources

- `vercel integration add --help` (Vercel CLI 56.2.1) — `-e/--environment`, `--plan`, `-m/--metadata`, `--no-env-pull`, `--prefix`
- https://vercel.com/docs/cli/integration — provisioning, connection, and the post-provisioning `env pull`
- `algolia profile add --help` (Algolia CLI 1.17.0) — marked `[Deprecated]`
- Credential precedence: env vars > CLI flags > profile config (`algolia-cli` skill)
