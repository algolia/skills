---
title: Read Plans and Metadata From --help, Never From Memory
impact: BLOCKING
impactDescription: invented plan IDs and metadata keys fail the command or provision the wrong thing
tags: provisioning, plans, metadata, regions
---

## Read Plans and Metadata From --help, Never From Memory

`vercel integration add <name> --help` fetches the plans and metadata keys **for that integration, live**. It is not a static template: the same command run against a different integration returns different keys and different plan IDs.

Algolia's plan IDs are version-stamped, so any value written from memory has a shelf life. Its region codes are Vercel cluster codes, not Algolia region names — `EU` and `us-east-1` are both wrong here.

**Incorrect (plausible values written from memory):**

```bash
vercel integration add algolia --plan free -m region=EU
```

`free` is not a plan ID and `region` is not a metadata key for this integration. Worse, a value that merely *looks* right can be accepted and provision something the user did not ask for.

**Correct (read, then pass what it returned):**

```bash
vercel integration add algolia --help
```

Observed with Vercel CLI 56.2.1 on 2026-09-16 — treat as an example of the *shape*, not as the current values:

```
Metadata options for "algolia":

  cluster_region_code
    Primary region where your application will be hosted
    Options: cdg1, lhr1, sfo1, cle1, iad1
  crawler (true/false)        Default: false
  crawler_domain (required)

Available billing plans for "Algolia":

  v8.5-plg-free       Free
  v8.5-plg-grow       Grow
  v8.5-plg-grow-plus  Grow Plus
```

Then pass exactly what that run printed — the IDs in the block above are last-known, not current. Set the two variables from the output you just read; the `:?` expansions stop the command if either is unset, so a forgotten step cannot silently provision a default:

```bash
: "${PLAN_ID:?Set PLAN_ID to the exact ID from the live --help output}"
: "${REGION_CODE:?Set REGION_CODE to a cluster_region_code option from the same output}"
vercel integration add algolia --name storefront-search --scope acme-team \
  -m cluster_region_code="$REGION_CODE" --plan "$PLAN_ID" \
  -e development --no-env-pull
```

The user chooses the **label** — "the free one", "Europe". Resolving that label to the ID the CLI wants is your job, off the help output, not a second question back to them.

`-m`/`--metadata` is repeatable (`-m crawler=true -m crawler_domain=example.com`). Pick the region closest to the app's users and confirm it with the user — it is not cheap to change later.

`-e development` is a placeholder for the environment the user picked. Whichever you pass, the credentials phase has to pull that same one — `vercel env pull` defaults to Development and does not inherit `-e`.

The same rule covers the variable names and setup steps: get them from `vercel integration guide algolia --framework <framework>`, which is also live. Do not invent an API key, a key name, or a flag that `--help` did not list.

## Sources

- `vercel integration add algolia --help` and `vercel integration add neon --help` (Vercel CLI 56.2.1) — different metadata keys and plans per integration, confirming the block is live data
- https://vercel.com/docs/cli/integration — "Run `vercel integration add <integration-name> --help` to see available products, metadata options, and billing plans an integration offers."
