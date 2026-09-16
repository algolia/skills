---
title: The Plan and the Terms Are the User's to Accept
impact: BLOCKING
impactDescription: provisioning attaches a billing plan and accepts a third party's legal terms on the user's behalf
tags: provisioning, billing, terms, consent
---

## The Plan and the Terms Are the User's to Accept

`vercel integration add` installs a marketplace integration on the team and provisions a resource against a billing plan. That is a commercial and a legal decision, and it is not one an agent gets to make silently.

Two things follow, and they are easy to confuse:

1. **You must not pick the plan.** `--non-interactive` is "the default when an agent is detected", so the confirmation screen a human would have seen does not appear. Nothing will stop a wrong `--plan`.
2. **You also cannot promise to accept the terms.** Terms acceptance can require a human: `vercel integration accept-terms <integration>` requires an interactive terminal and human confirmation, and the marketplace flow can route the acceptance to the Vercel dashboard. If the command stops and asks for that, it has stopped for a reason.

**Incorrect (inventing a plan ID, then treating a block as an obstacle):**

```bash
# "Provision Algolia on Vercel, Europe, free tier"
vercel integration add algolia -m cluster_region_code=cdg1 --plan v8.5-plg-free
# → terms not accepted; command stops
```

Two defects. The plan ID was written from memory — Algolia's are version-stamped and go stale — and the user never saw the real list. And when the command stops on terms, there is no flag to get past it and inventing one is worse than reporting the stop.

**Correct (read the live plans, resolve only what is still open, then run):**

The user said "Europe, free tier". That is an answer; do not ask for it again. What is still unknown is which plan ID carries the Free label and which cluster code is the European one, and both are in `--help`:

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

Set both from that output — `PLAN_ID` to the ID printed next to `Free`, `REGION_CODE` to the European cluster code. The user already chose the labels; do not go back and ask them to confirm an ID they have no way to check.

The environment list is also the user's to confirm, and it has a consequence downstream: `vercel env pull` must name the same environment, since it defaults to Development on its own.

If it stops on terms, relay the message and any URL verbatim and wait for the user. The Vercel dashboard marketplace flow is a fully supported alternative — the user can provision there and you pick up at the credentials phase.

Notes:

- `vercel integration accept-terms <integration>` installs the integration on the team without provisioning a resource. It is something the user runs, not something you run for them.
- `vercel integration balance algolia` is read-only and safe. `vercel integration resource create-threshold` sets up auto-recharge and is a spending decision.
- The Algolia-side equivalent of this mistake is `algolia application create --accept-terms` without asking. Same rule, different CLI.

## Sources

- https://vercel.com/docs/cli/integration — non-interactive detection, `accept-terms` ("requires an interactive terminal and human confirmation"), `balance`, `create-threshold`
- `vercel --help` (Vercel CLI 56.2.1) — `--non-interactive`: "when an agent is detected this is the default"
- https://vercel.com/kb/guide/using-coding-agents-to-procure-vercel-marketplace-integrations — critical actions such as choosing a paid plan or accepting terms are routed to human review
