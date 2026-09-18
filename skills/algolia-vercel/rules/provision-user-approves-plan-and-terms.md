---
title: The Plan and the Terms Are the User's to Accept
impact: HIGH
impactDescription: provisioning attaches a billing plan and accepts a third party's legal terms on the user's behalf
tags: provisioning, billing, terms, consent
---

## The Plan and the Terms Are the User's to Accept

`vercel integration add` installs a marketplace integration on the team and provisions a resource against a billing plan. That is a commercial and a legal decision, and `--non-interactive` is the default when an agent is detected — so the confirmation screen a human would have seen does not appear. Nothing will stop a wrong `--plan`.

Ask for exactly what is still open: team/scope, project, plan, environments, and the crawler metadata if it is offered. **An answer the user already gave is an answer.** "Europe, free tier" settles the plan and the region; going back to confirm it is noise, and confirming a plan *ID* they have no way to check is worse than noise.

**Incorrect (inventing a plan ID, then treating a block as an obstacle):**

```bash
# "Provision Algolia on Vercel, Europe, free tier"
vercel integration add algolia -m cluster_region_code=cdg1 --plan "$SOME_ID_FROM_MEMORY"
# → terms not accepted; command stops
```

Two defects. The plan ID was written from memory — Algolia's are version-stamped and go stale. And when the command stops on terms, there is no flag to get past it; inventing one is worse than reporting the stop.

**Correct (read the live plans, resolve only what is still open, then run):**

```bash
vercel integration add algolia --help
```

Take the plan ID whose label is `Free` and the `cluster_region_code` option for the right region straight out of that output. Then state what is about to happen, including the part the user has not spoken to:

> Provisioning Algolia under team `acme-team`, connected to project `storefront`, region `cdg1` (Paris), on the plan listed as Free, crawler disabled, environment `development`. This installs the Algolia integration on the team and accepts Algolia's marketplace terms. Confirm and I'll run it.

Then run it with the values that came out of `--help`:

```bash
: "${PLAN_ID:?Set PLAN_ID to the exact ID from the live --help output}"
: "${REGION_CODE:?Set REGION_CODE to a cluster_region_code option from the same output}"
vercel integration add algolia --name storefront-search --scope acme-team \
  -m cluster_region_code="$REGION_CODE" --plan "$PLAN_ID" \
  -e development --no-env-pull
```

The environment list also has a downstream consequence: `vercel env run` must name the same environment, since it defaults to development.

### If a human step is required

Terms acceptance goes to a human **when the CLI or the browser demands it** — not as a routine extra gate you add. `vercel integration accept-terms <integration>` "requires an interactive terminal and human confirmation", and the marketplace flow can route acceptance to the Vercel dashboard or to a browser. If `add` stops on that, relay the message and any URL verbatim and wait. Do not look for a way around it. The dashboard marketplace flow is a fully supported alternative — the user can provision there and you pick up at the credentials phase.

Notes:

- `vercel integration accept-terms <integration>` installs the integration on the team without provisioning a resource. It is something the user runs, not something you run for them.
- `vercel integration balance algolia` is read-only and safe. `vercel integration resource create-threshold` sets up auto-recharge and is a spending decision.
- The Algolia-side equivalent of this mistake is `algolia application create --accept-terms` without asking. Same rule, different CLI.

## Sources

- `vercel --help` / `vercel env --help` global options (Vercel CLI 56.2.1) — `--non-interactive`: "Run without interactive prompts; when an agent is detected this is the default"
- `vercel integration accept-terms --help` (Vercel CLI 56.2.1) — "Requires an interactive terminal and human confirmation. Does not replace integrations that require a browser or device attestation."
- https://vercel.com/docs/cli/integration — `add`, `accept-terms`, `balance`, `resource create-threshold`
- https://vercel.com/kb/guide/using-coding-agents-to-procure-vercel-marketplace-integrations — critical actions such as choosing a paid plan or accepting terms are routed to human review
