---
name: algolia-vercel
description: >-
  Provision Algolia through the Vercel Marketplace and take a Vercel-hosted
  project from no Algolia at all to a validated first search. Use when the user
  has picked Vercel and has no Algolia application yet — "set up Algolia on
  Vercel", "add Algolia from the Vercel Marketplace", "vercel integration add
  algolia" — and to rerun or repair an application that was already provisioned
  this way: a resource that is not connected to the project, or injected
  ALGOLIA_APP_ID / ALGOLIA_SEARCH_API_KEY / ALGOLIA_WRITE_API_KEY that are
  missing locally. Do NOT use merely because a project is Next.js — Next.js
  alone does not mean Vercel. Do NOT use when the user already has a standalone
  Algolia application they intend to keep; it stays standalone. Do NOT use for
  records, settings, synonyms, rules, or keys on an existing application
  (algolia-cli), for search UI (instantsearch), for read-only search and
  analytics (algolia-mcp), or for accounts created outside Vercel
  (algolia-quickstart).
license: MIT
metadata:
  author: algolia
  version: "1.0"
---

# Algolia on Vercel

Onboarding guide for provisioning Algolia as a Vercel Marketplace resource, and for repairing one that already exists. Covers 10 rules across 5 phases, ordered so each phase's gate must hold before the next begins. Vercel owns the Algolia application on this path: it creates it, injects the credentials, and bills it.

Ends at a query that returns hits, then continues into the UI with `instantsearch` if that is what the user asked for.

## When to Apply

Reference these guidelines when:

- The user is on Vercel and has no Algolia application yet
- The user asks to add Algolia "from the Vercel Marketplace", or names `vercel integration add algolia`
- A Marketplace-provisioned resource needs a **rerun or repair** — it exists but is not connected to the target project, or `ALGOLIA_APP_ID` / `ALGOLIA_SEARCH_API_KEY` / `ALGOLIA_WRITE_API_KEY` never reached the local environment
- A Vercel-provisioned Algolia application needs its first records and its first successful query

Do **not** apply when:

- The project is Next.js but nothing indicates Vercel hosting. Next.js does not imply Vercel — check for a `.vercel/` directory, a linked project, `vercel.json`, or ask.
- The user has a **standalone** Algolia application — their own account, their own keys — and intends to keep it. It stays standalone; do not provision a Marketplace resource alongside it. Moving it is a migration the user has to ask for.
- The work is records, settings, synonyms, rules, API keys, or index operations on an application that already exists → `algolia-cli`.
- The work is search UI and the credentials are already available → `instantsearch`.
- The account is being created outside Vercel → `algolia-quickstart`.

## Rule Categories by Priority

| Priority | Category     | Gate (must hold before the next phase)                                                     | Prefix         |
| -------- | ------------ | ------------------------------------------------------------------------------------------ | -------------- |
| 1        | Provisioning | The intended Algolia resource exists and is connected to the target project                 | `provision-`   |
| 2        | Credentials  | App ID and both keys load from the staged file; the write key is not reachable from browser code | `credentials-` |
| 3        | Example data | CONDITIONAL — only when the requested first search has no data to run against. When it runs: a newly named index holds records and no pre-existing index was modified. Skipped on a repair | `data-` |
| 4        | Validation   | A real query with the search-only key returns `nbHits` ≥ 1 — against the seeded index, or read-only against an index that already exists | `validate-`    |
| 5        | Handoff      | CONDITIONAL — only when UI was asked for. Then the UI work continues with the index name and the credential references it needs | `handoff-`     |

## Quick Reference

### 1. Provisioning (BLOCKING)

- `provision-vercel-owns-the-app` - Do not run `algolia auth signup` or `algolia application create` on this path
- `provision-list-before-add` - `integration add` always creates a new resource; list first and pick the intended one
- `provision-scope-and-link-explicitly` - Pin the team with `--scope` and the project with `vercel link --project`
- `provision-read-help-for-plans-and-metadata` - Plan IDs and metadata keys are live data; never write them from memory
- `provision-user-approves-plan-and-terms` - Plan and provider terms are the user's decision, and the CLI may hand terms acceptance back to a browser

### 2. Credentials (BLOCKING)

- `credentials-pull-without-clobbering` - `vercel env pull` overwrites its target and defaults to Development; ignore the staging pattern first, stop if the staging path already exists, pull the environment you connected, merge by parsing
- `credentials-write-key-never-reaches-the-browser` - Only the search-only key gets a `NEXT_PUBLIC_` mapping, in `.env.local` and in the `next.config.js` `env` block that Vercel builds need

### 3. Example data (CONDITIONAL — new setups that need data)

- `data-additive-example-index` - Import into a new index name; never clear or delete to make room, and do not seed at all when an index with records already exists

### 4. Validation (REQUIRED)

- `validate-search-returns-hits` - Query with the search-only key and read `nbHits`; "no error" is not a passing search

### 5. Handoff (CONDITIONAL — EXIT when UI was asked for)

- `handoff-ui-to-instantsearch` - Keep going into the UI with `instantsearch`; do not stop at the query and leave the ask unfinished

## How to Use

**Read the rule file for a phase before you run that phase's commands**, not afterwards. The Sequence below is safe on its own, but every judgement call it compresses — which resource, which plan, what to do when a variable is missing — lives in the rule files:

```
rules/provision-vercel-owns-the-app.md
rules/provision-list-before-add.md
rules/provision-scope-and-link-explicitly.md
rules/provision-read-help-for-plans-and-metadata.md
rules/provision-user-approves-plan-and-terms.md
rules/credentials-pull-without-clobbering.md
rules/credentials-write-key-never-reaches-the-browser.md
rules/data-additive-example-index.md
rules/validate-search-returns-hits.md
rules/handoff-ui-to-instantsearch.md
```

Each rule file contains why it matters, an incorrect example with what it breaks, a correct example, and sources for the commands and flags used.

[`scripts/with-algolia-env.mjs`](scripts/with-algolia-env.mjs) runs one Algolia CLI command with credentials read from the staged env file. It parses the file with `node:util` `parseEnv` — it never sources or evals it — and overrides only `ALGOLIA_APPLICATION_ID` and `ALGOLIA_API_KEY`, so a stale export cannot point the command at a different application. Needs Node ≥ 20.12.

Every example below invokes it as `"$ALGOLIA_VERCEL_SKILL_DIR/scripts/with-algolia-env.mjs"`. Set that variable once (step 0 below) to the **absolute path of the directory containing the `SKILL.md` you are reading** — wherever this skill happens to be installed. Do not write a repository-relative path such as `skills/algolia-vercel/…`: installed on its own, this skill is not inside the app's repository. Keep the working directory on the app being wired up; only the helper path points at the skill.

## Sequence

The happy path for a **new setup**. Step 0 and steps 2–3 only read; step 1 (`vercel link`) writes `.vercel/project.json` in the repo; step 4 is the one command that creates a resource and attaches it to a billing plan.

```bash
# 0. Tooling and auth, before anything else.
#    Not installed? Run either CLI through npx, or install it per the official docs.
vercel --version    || npx vercel --version         # https://vercel.com/docs/cli
algolia --version   || npx @algolia/cli --version   # https://www.algolia.com/doc/tools/cli/get-started/overview/
vercel whoami       || vercel login                 # opens a browser; hand the user the URL if you cannot open one

#    Resolve this skill's installed directory ONCE — absolute, no trailing slash. cwd stays the app.
ALGOLIA_VERCEL_SKILL_DIR="$HOME/.claude/skills/algolia-vercel"   # replace with this skill's real path
test -f "$ALGOLIA_VERCEL_SKILL_DIR/scripts/with-algolia-env.mjs"

# 1. Pin the team and the project (--yes is safe once both are settled)
vercel link --yes --project storefront --scope acme-team

# 2. Check what already exists (never skip — see provision-list-before-add)
vercel integration installations --integration algolia --format json --scope acme-team
vercel integration list --all --integration algolia --format=json --scope acme-team

# 3. Read the live plans and metadata keys for this integration
vercel integration add algolia --help

# 4. Provision — only once the user has settled plan, region, terms AND environments.
#    Set PLAN_ID and REGION_CODE from step 3's own output — the user picks the LABEL
#    ("Free", "Europe"), you read the matching ID off the help you just ran. The IDs are
#    version-stamped, so nothing here hardcodes one; the expansions below abort the command
#    rather than let an unset or remembered value through.
#    -e development here is ILLUSTRATIVE: pass the environment(s) the user chose, and pull
#    that same environment in step 5. --no-env-pull keeps add's automatic pull from
#    overwriting .env.local behind your back.
: "${PLAN_ID:?Set PLAN_ID to the exact ID from the live --help output}"
: "${REGION_CODE:?Set REGION_CODE to a cluster_region_code option from the same output}"
vercel integration add algolia --name storefront-search --scope acme-team \
  -m cluster_region_code="$REGION_CODE" --plan "$PLAN_ID" \
  -e development --no-env-pull

# 5. Stage the credentials. Ignore the pattern BEFORE anything writes it, and pull only
#    into a path that does not exist yet — see below for why an existing one is a stop.
grep -q '^\.env\*\.local$' .gitignore 2>/dev/null || printf '\n.env*.local\n' >> .gitignore
STAGING=.env.algolia.local
if [ -e "$STAGING" ]; then
  echo "refusing to touch existing $STAGING — choose an unused .env.*.local path" >&2
  exit 1
fi
vercel env ls --scope acme-team                                  # names and targets, no values
vercel env pull "$STAGING" --environment development --scope acme-team   # match step 4's -e
cut -d= -f1 "$STAGING" | grep '^ALGOLIA_'                        # confirm the names, no values

# 6. NEW SETUPS THAT NEED DATA ONLY — skip entirely on a repair, or when an index with
#    records already exists. Import example records into a NEW index with the write key.
node "$ALGOLIA_VERCEL_SKILL_DIR/scripts/with-algolia-env.mjs" "$STAGING" ALGOLIA_WRITE_API_KEY -- \
  algolia objects import example_products -F example.ndjson -w

# 7. Validate with the key the browser will use. On a repair, point this at the index that
#    already exists (algolia indices list) — a read-only query, no seeding.
node "$ALGOLIA_VERCEL_SKILL_DIR/scripts/with-algolia-env.mjs" "$STAGING" ALGOLIA_SEARCH_API_KEY -- \
  algolia search example_products --query "headphones" --output json
```

Step 5 stops rather than reuses. A file already at the staging path is credentials from *some* run — possibly a different Algolia application, a different project, or a rotated key — and the variable names inside it look identical in every one of those cases, so the names cannot tell you it is the right one. Pulling over it destroys it; trusting it wires the app to whatever it happens to hold. Neither is acceptable silently, so the existence test is a hard stop: set `STAGING` to an unused path that still matches the ignored pattern (`.env.algolia.2.local`, `.env.algolia-storefront.local`), thread that same `$STAGING` through every later command — the helper invocations in steps 6 and 7 and the merge — and pull fresh into it. Only the user can decide to delete the old file; say what is there and let them.

`--environment` on the pull must name the environment you connected on `add`: `vercel env pull` defaults to Development regardless of what `add` received, so `-e production` plus a bare `env pull` stages nothing. For a preview branch, add `--git-branch <branch>`.

Branches off this path:

- **Step 2 lists the intended resource, already connected to this project** → skip steps 3–4 and the `connect` command entirely. Go to step 5; a missing variable locally is a pull problem, not a provisioning problem.
- **Step 2 lists the intended resource, not connected to this project** → connect it with the environment the user chose and pull the same one: `vercel integration resource connect storefront-search storefront --scope acme-team -e development --yes`, then step 5.
- **Step 2 lists resources but none is the one the user wants** → show them the list and let them choose; only provision when they say they want a separate one.
- **Repair only** ("the variables never reached my machine", "`process.env.ALGOLIA_APP_ID` is undefined") → steps 5 and 7 plus the merge, and nothing else. Do not seed a demo index and do not build UI; validate read-only against an index the application already has. Seed only if the user's own first search has no data behind it.

The staging file is not a file Next.js reads. Merging it into `.env.local` is part of the credentials phase — see `rules/credentials-pull-without-clobbering.md`.

## Stop and Ask

These are the user's decisions. Ask for the ones you do not already have an answer to, once — an answer they already gave ("free tier", "Europe", "the acme-team account") counts, and re-confirming it is noise.

| Ambiguity                                                      | Ask                                                                      |
| -------------------------------------------------------------- | ------------------------------------------------------------------------ |
| An Algolia application already exists and its ownership is unclear | Keep the existing application, or have Vercel provision and bill a separate one? |
| More than one Vercel team                                      | Which team should own and be billed for the resource?                    |
| No linked Vercel project                                       | Which project? Link it before provisioning.                              |
| Plan not chosen, or its terms not yet accepted                 | Which plan, and do you accept the provider terms?                        |
| Crawler metadata (`crawler`, `crawler_domain`) offered         | Enable the crawler, and for which domain?                                |
| Environments to connect (`production`/`preview`/`development`) | Which ones? `-e` defaults to all three, and `vercel env pull` must then name the same one — it defaults to Development. |

`vercel integration add` runs non-interactively when it detects an agent, so a prompt you would have relied on will not appear — settle these before running it, not during.

Terms acceptance is not yours to give. `vercel integration accept-terms` requires an interactive terminal and human confirmation, and `add` can stop on the same requirement or send the user to the dashboard. If it does, relay the message and the URL and wait. Do not look for a way around it. The Vercel dashboard marketplace flow is a fully supported alternative — if the user prefers it, let them provision there and pick up at step 5.

## Companion Skills

Referencing a skill does not install it. Offer the explicit command when the user needs one:

| Next step                                             | Skill                    | Install                                                    |
| ----------------------------------------------------- | ------------------------ | ---------------------------------------------------------- |
| Build the search UI                                   | `instantsearch`          | `npx skills add algolia/skills --skill instantsearch`      |
| Records, settings, synonyms, rules, keys, backups     | `algolia-cli`            | `npx skills add algolia/skills --skill algolia-cli`        |
| Crawl a site into the index                           | `algolia-crawler`        | `npx skills add algolia/skills --skill algolia-crawler`    |
| Plan a full implementation                            | `algolia-discovery-planning` | `npx skills add algolia/skills --skill algolia-discovery-planning` |

## Source Note

The rule-category / prefixed-rule layout of this skill is modelled on the public [`vercel-labs/agent-skills`](https://github.com/vercel-labs/agent-skills) format (`skills/react-best-practices`, `skills/composition-patterns`). Algolia adapted it for onboarding; this is not an endorsed or adopted Vercel skill.

Commands were verified against Vercel CLI 56.2.1, Algolia CLI 1.17.0, [`vercel integration`](https://vercel.com/docs/cli/integration) and [`vercel link`](https://vercel.com/docs/cli/link). Plan IDs, metadata keys, and variable names come from the live integration and change without notice — read them from `vercel integration add algolia --help` and `vercel integration guide algolia` at run time.
