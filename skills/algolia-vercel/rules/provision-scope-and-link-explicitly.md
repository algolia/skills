---
title: Pin the Team and the Project Explicitly
impact: BLOCKING
impactDescription: an implicit scope provisions a billed resource under the wrong team
tags: provisioning, scope, team, linking
---

## Pin the Team and the Project Explicitly

`vercel integration add` connects the new resource to "the currently linked project", and every Vercel command resolves a team from ambient state — the last `vercel switch`, the `.vercel/project.json` in the directory, or the personal account. None of that is visible in the command you are about to run.

Get it wrong and a billed resource lands under the wrong team, or the credentials get injected into a project that is not the one being built.

**Incorrect (relying on ambient state):**

```bash
# User is in three Vercel teams; repo has no .vercel directory
vercel integration add algolia --plan v8.5-plg-free
```

The resource is created under whichever scope happens to be active and connected to whichever project `add` infers. If there is no linked project, the connection and the `env pull` are skipped and the credentials never reach the app.

**Correct (link and scope first, then verify):**

```bash
: "${PLAN_ID:?Set PLAN_ID to the exact ID from the live --help output}"   # never from memory
vercel whoami
vercel link --yes --project storefront --scope acme-team    # --yes once team and project are settled
vercel integration list --all --integration algolia --format=json --scope acme-team
vercel integration add algolia --name storefront-search --scope acme-team \
  --plan "$PLAN_ID" -e development --no-env-pull
```

`vercel link` is not a read-only command: it writes `.vercel/project.json` in the repo and from then on every other Vercel command resolves the project from it. That is the point — but run it on purpose, on the project the user named. It takes `--project <name-or-id>`, `--scope`/`--team`, and `--yes` to skip the setup questions; `--repo` links every project in a monorepo at once. `VERCEL_PROJECT_ID` is an alternative to `--project`, and `--project` wins if both are set.

Two flags on `add` that are easy to leave off and expensive to leave off:

- `-e/--environment` is repeatable and **defaults to all three** environments. Connect the ones the user wants — `-e development` in the example is illustrative. Whatever you pass, `vercel env pull` must then name the same environment (`--environment development`): the pull defaults to Development and ignores what `add` was given.
- `--no-env-pull` stops `add` from running `vercel env pull` on its own, which would overwrite `.env.local` before you have decided where the credentials should land.

Ask which team and which project before running anything that writes. `--scope` on a read-only `list` is free; `--scope` on `add` decides who gets billed.

## Sources

- https://vercel.com/docs/cli/link — `--project`, `--scope`, `--yes`, `--repo`, `VERCEL_PROJECT_ID` precedence
- https://vercel.com/docs/cli/integration — post-provisioning behavior, `--environment`, global `--scope`/`--team`
