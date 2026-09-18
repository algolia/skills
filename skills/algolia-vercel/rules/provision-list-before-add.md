---
title: List Resources Before Adding One
impact: HIGH
impactDescription: add always provisions a new resource, so a rerun leaves a duplicate application behind
tags: provisioning, idempotency, rerun
---

## List Resources Before Adding One

`vercel integration add` is **not** idempotent. The docs are explicit: it "provisions a new resource from a marketplace integration. If the integration isn't installed on your team yet, it installs it first."

So an already-installed integration does not make `add` a no-op. Running it twice gives two Algolia applications, and a second line item if the plan is a paid one. What happens to the *variables* is less predictable: connecting the second resource can collide with the names the first one already put on the project, and `connect` then exits naming the conflict. Expect a duplicate resource; do not assume a tidy second set of injected variables — the likely state is a billed application that nothing is wired to. A teammate rerunning the setup steps, or an agent retrying after a timeout, is enough to trigger it.

Check both scopes first. They answer different questions: `installations` is team-level (is the integration installed?), `list` is resource-level (does an Algolia application already exist, and what is it connected to?).

**Incorrect (add as the first step):**

```bash
# "Set up Algolia on Vercel" → straight to provisioning
vercel integration add algolia --plan "$SOME_ID_FROM_MEMORY"
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
| The intended resource, already connected to the target project     | Nothing. Skip `add` **and** `connect`; go straight to the credentials phase. |
| The intended resource, not connected to the target project         | `connect` it. Do not provision.                                          |
| Resources exist, but it is unclear which one is intended           | Show the user the list and let them pick.                                |
| No resource, or the user has seen the list and asked for a separate one | `add` is correct.                                                        |

Other teams' unrelated resources on the same Vercel account do not block anything. A second Algolia resource is a legitimate outcome when the user has looked at what exists and asked for one — a separate staging application, for instance. What is never legitimate is provisioning "a fresh one to be safe" without showing them what is already there.

```bash
vercel integration resource connect storefront-search storefront --scope acme-team \
  -e development --yes
```

`connect` takes the same `-e/--environment` flag as `add` and the same default of all three — name the environment the user wants, and `--yes` to skip the confirmation now that the resource and the project are both settled. Then use that same environment on `vercel env run -e …`, which defaults to development.

When several installations of the same integration exist, `add` takes `--installation-id <id>` to disambiguate which installation the new resource is provisioned under; take the ID from the `installations` output rather than guessing. `resource connect` targets an already-named resource and has **no** `--installation-id` flag — passing one is a hard error.

On a name collision, `--prefix ALGOLIA2_` sidesteps it without touching anything that exists (the prefix is prepended as-is, so include the trailing underscore). Then read the resulting names off `vercel env ls` and use them verbatim downstream — do not assume what they became. Removing the old variable with `vercel env rm` is also possible, but it is a destructive change to a variable something else may depend on: raise it as an option, do not do it by default.

## Sources

- https://vercel.com/docs/cli/integration — `add` "provisions a new resource"; `list`, `installations`, `resource connect`
- `vercel integration add --help` (Vercel CLI 56.2.1) — `--installation-id`, `--prefix` ("`--prefix NEON2_` creates `NEON2_DATABASE_URL` instead of `DATABASE_URL`"), `--no-connect`, `--no-env-pull`
- `vercel integration resource connect --help` (Vercel CLI 56.2.1) — options are `-e/--environment`, `-F/--format`, `--prefix`, `-y/--yes`; no `--installation-id`
- `vercel integration list --help` / `installations --help` (56.2.1) — `-a/--all`, `-i/--integration`, `-F/--format`
