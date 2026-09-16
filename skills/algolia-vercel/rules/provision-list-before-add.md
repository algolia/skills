---
title: List Resources Before Adding One
impact: BLOCKING
impactDescription: add always provisions a new resource, so a rerun leaves a duplicate application behind
tags: provisioning, idempotency, rerun
---

## List Resources Before Adding One

`vercel integration add` is **not** idempotent. The docs are explicit: it "provisions a new resource from a marketplace integration. If the integration isn't installed on your team yet, it installs it first."

So an already-installed integration does not make `add` a no-op. Running it twice gives two Algolia applications and two sets of injected variables — a split brain where half the team's records are in an application nobody is looking at, and a second line item if the plan is a paid one. A teammate rerunning the setup steps, or an agent retrying after a timeout, is enough to trigger it.

Check both scopes first. They answer different questions: `installations` is team-level (is the integration installed?), `list` is resource-level (does an Algolia application already exist, and what is it connected to?).

**Incorrect (add as the first step):**

```bash
# "Set up Algolia on Vercel" → straight to provisioning
vercel integration add algolia --plan v8.5-plg-free
```

If a resource already existed, this created a second one. Nothing in the output flags it as a duplicate.

**Correct (check, then branch):**

```bash
vercel integration installations --integration algolia --format json --scope acme-team
vercel integration list --all --integration algolia --format=json --scope acme-team
```

Read the `resources` array — name, status, product, and which projects each is connected to — and decide which of these you are in:

| What the list shows                                                | Do this                                                                 |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| The intended resource, already connected to the target project     | Nothing. Skip `add` **and** `connect`; go straight to pulling and validating credentials. |
| The intended resource, not connected to the target project         | `connect` it. Do not provision.                                          |
| Resources exist, but it is unclear which one is intended           | Show the user the list and let them pick.                                |
| No resource, or the user has seen the list and asked for a separate one | `add` is correct.                                                        |

Other teams' unrelated resources on the same Vercel account do not block anything. A second Algolia resource is a legitimate outcome when the user has looked at what exists and asked for one — a separate staging application, for instance. What is never legitimate is provisioning "a fresh one to be safe" without showing them what is already there.

```bash
vercel integration resource connect storefront-search storefront --scope acme-team \
  -e development --yes
```

`connect` takes the same `-e/--environment` flag as `add` and the same default of all three — name the environment the user wants, and `--yes` to skip the confirmation now that the resource and the project are both settled. Then pull that same environment: `vercel env pull "$STAGING" --environment development`, because the pull defaults to Development regardless.

When several installations of the same integration exist, `add` takes `--installation-id <id>` to disambiguate which installation the new resource is provisioned under; take the ID from the `installations` output rather than guessing. `resource connect` targets an already-named resource and has **no** `--installation-id` flag — passing one is a hard error.

Connecting can collide with an existing project variable. `connect` then exits naming the conflict. Prefer `--prefix ALGOLIA2_` (used as-is, so include the trailing underscore), which sidesteps the collision without touching anything that exists. Removing the old variable with `vercel env rm` is also possible, but it is a destructive change to a variable something else may depend on — raise it as an option, do not do it by default.

## Sources

- https://vercel.com/docs/cli/integration — `add`, `list`, `installations`, `resource connect`
- `vercel integration add --help` (Vercel CLI 56.2.1) — `--installation-id`, `--prefix`, `--no-connect`, `--no-env-pull`
- `vercel integration resource connect --help` (Vercel CLI 56.2.1) — options are `-e/--environment`, `-F/--format`, `--prefix`, `-y/--yes`; no `--installation-id`
- Verified output shapes (Vercel CLI 56.2.1): `{"installations": []}`, `{"resources": []}`
