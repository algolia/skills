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

Onboarding guide for provisioning Algolia as a Vercel Marketplace resource, and for repairing one that already exists. Covers 10 rules across 5 phases, ordered so each phase's gate must hold before the next begins.

Ends at a query run with the search-only key, then continues into the UI with `instantsearch` if that is what the user asked for.

## When to Apply

Reference these guidelines when:

- The user is on Vercel and has no Algolia application yet
- The user asks to add Algolia "from the Vercel Marketplace", or names `vercel integration add algolia`
- A Marketplace-provisioned resource needs a **rerun or repair** — it exists but is not connected to the target project, or the injected `ALGOLIA_*` variables never reached the local environment
- A Vercel-provisioned Algolia application needs its first successful query

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
| 2        | Credentials  | An Algolia CLI command runs under `vercel env run` with the injected credentials; the write key is not reachable from browser code | `credentials-` |
| 3        | Example data | CONDITIONAL — only when the requested search has no data to run against and the user wants a demo index. When it runs: a newly named index holds records and nothing pre-existing was modified | `data-` |
| 4        | Validation   | A query with the search-only key returns, and the claim made about it matches what it returned | `validate-`    |
| 5        | Handoff      | CONDITIONAL — only when UI was asked for. Then the UI work continues with the index name and the credential references it needs | `handoff-`     |

## Quick Reference

Each rule file carries an `impact` of CRITICAL, HIGH or MEDIUM. That is editorial severity — how much damage getting it wrong does, and which rule to read first when time is short. It is not runtime enforcement, and it does not say whether a phase runs: the conditions for that stay in the category table above and in each rule's body.

### 1. Provisioning

- `provision-vercel-owns-the-app` - On this path Vercel creates the application; do not run `algolia auth signup` or `algolia application create`
- `provision-list-before-add` - `integration add` always creates a new resource; list first and pick the intended one
- `provision-scope-and-link-explicitly` - Pin the team with `--scope` and the project with `vercel link --project`
- `provision-read-help-for-plans-and-metadata` - Plan IDs and metadata keys are live data; never write them from memory
- `provision-user-approves-plan-and-terms` - Plan, terms and environments are the user's decision; a human step only when the CLI or browser requires one

### 2. Credentials

- `credentials-run-with-vercel-env` - Run every Algolia command through `vercel env run -e <connected env>`, bridging `ALGOLIA_APP_ID` → `ALGOLIA_APPLICATION_ID` inside the child; `env pull` only when a file is genuinely required
- `credentials-write-key-never-reaches-the-browser` - Only the search-only key gets a `NEXT_PUBLIC_` mapping, in the `next.config.js` `env` block

### 3. Example data — only when there is nothing to search

- `data-additive-example-index` - Import into a new index name; never clear or delete to make room, and do not seed on a repair or when an index already holds records

### 4. Validation

- `validate-search-returns-hits` - Query with the search-only key and read `nbHits`; "no error" is not a passing search, and a 0-hit response proves access, not results

### 5. Handoff — only when UI was asked for

- `handoff-ui-to-instantsearch` - Keep going into the UI with `instantsearch`; do not stop at the query and leave the ask unfinished

## How to Use

**Read the rule file for a phase before you run that phase's commands**, not afterwards. The Sequence below is an outline, not a script you can follow safely on its own: every judgement call it compresses — which resource, which plan, which index name, what to do when a variable is missing or points at the wrong application — lives in the rule files:

```
rules/provision-vercel-owns-the-app.md
rules/provision-list-before-add.md
rules/provision-scope-and-link-explicitly.md
rules/provision-read-help-for-plans-and-metadata.md
rules/provision-user-approves-plan-and-terms.md
rules/credentials-run-with-vercel-env.md
rules/credentials-write-key-never-reaches-the-browser.md
rules/data-additive-example-index.md
rules/validate-search-returns-hits.md
rules/handoff-ui-to-instantsearch.md
```

Each rule file contains why it matters, an incorrect example with what it breaks, a correct example, and sources for the commands and flags used.

## Sequence

The happy path for a **new setup**. Steps 2–3 are the read-only discovery; step 0 is not read-only (`vercel login` authenticates and writes local CLI config) and step 1 (`vercel link`) writes `.vercel/project.json`; step 4 is the one command that creates a resource and attaches it to a billing plan. The working directory stays on the app.

```bash
# 0. Tooling and auth, before anything else.
#    Not installed? Run either CLI through npx, or install it per the official docs.
vercel --version    || npx vercel --version         # https://vercel.com/docs/cli
algolia --version   || npx @algolia/cli --version   # https://www.algolia.com/doc/tools/cli/get-started/overview/
vercel whoami       || vercel login                 # opens a browser; hand the user the URL if you cannot open one

# 1. Pin the team and the project (--yes is safe once both are settled)
vercel link --yes --project storefront --scope acme-team

# 2. Check what already exists (never skip — see provision-list-before-add)
vercel integration installations --integration algolia --format json --scope acme-team
vercel integration list --all --integration algolia --format=json --scope acme-team

# 3. Read the live plans and metadata keys for this integration
vercel integration add algolia --help

# 4. Provision — only once the user has settled plan, region, terms AND environments.
#    Set PLAN_ID and REGION_CODE from step 3's own output: the user picks the LABEL
#    ("Free", "Europe"), you read the matching ID off the help you just ran.
#    -e development is ILLUSTRATIVE — pass the environment(s) the user chose, and name
#    that same one on every `vercel env run` below.
: "${PLAN_ID:?Set PLAN_ID to the exact ID from the live --help output}"
: "${REGION_CODE:?Set REGION_CODE to a cluster_region_code option from the same output}"
vercel integration add algolia --name storefront-search --scope acme-team \
  -m cluster_region_code="$REGION_CODE" --plan "$PLAN_ID" \
  -e development --no-env-pull

# 5. Confirm the variable NAMES the integration injected. No values are printed.
#    If --prefix was used, the names differ — use whatever this prints, verbatim, below.
vercel env ls --scope acme-team

# 6. ONLY IF THERE IS NOTHING TO SEARCH and the user wants a demo index. Skip on a repair.
cat > example.ndjson <<'EOF'
{"objectID":"1","name":"Wireless Headphones","category":"Audio","price":129}
{"objectID":"2","name":"Mechanical Keyboard","category":"Input","price":89}
{"objectID":"3","name":"27-inch Monitor","category":"Displays","price":329}
EOF
vercel env run -e development --scope acme-team -- sh -eu -c '
: "${ALGOLIA_APP_ID:?not injected — check: vercel env ls}"
: "${ALGOLIA_WRITE_API_KEY:?not injected — check: vercel env ls}"
export ALGOLIA_APPLICATION_ID="$ALGOLIA_APP_ID"
export ALGOLIA_API_KEY="$ALGOLIA_WRITE_API_KEY"
exec "$@"
' algolia-env algolia objects import example_products -F example.ndjson -w

# 7. Validate with the key the browser will use. On a repair, point this at an index the
#    application already has (algolia indices list) — read-only, no seeding.
vercel env run -e development --scope acme-team -- sh -eu -c '
: "${ALGOLIA_APP_ID:?not injected — check: vercel env ls}"
: "${ALGOLIA_SEARCH_API_KEY:?not injected — check: vercel env ls}"
export ALGOLIA_APPLICATION_ID="$ALGOLIA_APP_ID"
export ALGOLIA_API_KEY="$ALGOLIA_SEARCH_API_KEY"
exec "$@"
' algolia-env algolia search example_products --query "headphones" --output json

# 8. Run the app with the same variables.
vercel env run -e development --scope acme-team -- npm run dev
```

The `sh -eu -c` block is **single-quoted on purpose**: your shell expands nothing, so `$ALGOLIA_APP_ID` is resolved by the child, after `env run` has fetched the variables. The `${VAR:?…}` guards stop before `exec` if one is missing, and the command sits after the closing quote as argv, so a query containing `$` or `;` stays data. Change the key variable and the trailing command; leave the rest identical.

The guards catch an **absent** variable, not a wrong one. `env run` layers the fetched records first, then local `.env` files, then your shell — last wins — so a stale export or an old `.env.local` overrides what Vercel just sent, with no error. A name in `vercel env ls` means the project has it configured, not that the command used that value. Precedence, prefixed names and how to clear a stale local value: `rules/credentials-run-with-vercel-env.md`.

`-e` on `env run` must name the environment you connected on `add`. It defaults to `development` regardless of what `add` received, so `-e production` on `add` plus a bare `env run` fetches variables that are not there.

Branches off this path:

- **Step 2 lists the intended resource, already connected to this project** → skip steps 3–4 and `connect` entirely. Go to step 5; a missing variable locally is a credentials problem, not a provisioning problem.
- **Step 2 lists the intended resource, not connected to this project** → connect it with the environment the user chose: `vercel integration resource connect storefront-search storefront --scope acme-team -e development --yes`, then step 5.
- **Step 2 lists resources but none is the one the user wants** → show them the list and let them choose; only provision when they say they want a separate one.
- **Repair only** ("the variables never reached my machine", "`process.env.ALGOLIA_APP_ID` is undefined", "it is pointing at the wrong application") → steps 5, 7 and 8, and nothing else. Do not seed a demo index and do not build UI. Check the local layers too: a stale shell export or `.env.local` overrides the fetched values, so "wrong app ID" is usually local, not a provisioning fault. A query that returns `nbHits` 0 against an existing index still shows the credentials work — report that, do not seed to make the number bigger.

**When the app is Next.js**, getting the two browser-safe values into client code is `next.config.js`, not a dotenv file — see `rules/credentials-write-key-never-reaches-the-browser.md`. For any other framework the same principle holds (search-only key to the browser, write key never), but the mechanism differs: read `vercel integration guide algolia --framework <framework>` rather than porting the Next.js snippet.

## Stop and Ask

These are the user's decisions. Ask once for the ones you do not already have an answer to — an answer they already gave ("free tier", "Europe", "the acme-team account") counts, and re-confirming it is noise. Do not add approval gates beyond these.

| Ambiguity                                                      | Ask                                                                      |
| -------------------------------------------------------------- | ------------------------------------------------------------------------ |
| An Algolia application already exists and its ownership is unclear | Keep the existing application, or have Vercel provision and bill a separate one? |
| More than one Vercel team                                      | Which team should own and be billed for the resource?                    |
| No linked Vercel project                                       | Which project? Link it before provisioning.                              |
| Plan not chosen, or its terms not yet accepted                 | Which plan, and do you accept the provider terms?                        |
| Crawler metadata (`crawler`, `crawler_domain`) offered         | Enable the crawler, and for which domain?                                |
| Environments to connect (`production`/`preview`/`development`) | Which ones? `-e` on `add` defaults to all three, and `vercel env run -e` must then name the one you want — it defaults to development. |
| Nothing in the application to search                           | Seed a small example index, or point at data you already have?           |

`vercel integration add` runs non-interactively when it detects an agent, so a prompt you would have relied on will not appear — settle these before running it, not during.

Terms acceptance is not yours to give, and it becomes a human step when the CLI or the browser makes it one: `vercel integration accept-terms` requires an interactive terminal and human confirmation, and `add` can stop on the same requirement or send the user to the dashboard. If it does, relay the message and the URL and wait. The Vercel dashboard marketplace flow is a fully supported alternative — if the user prefers it, let them provision there and pick up at step 5.

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

Commands were verified against Vercel CLI 56.2.1 and Algolia CLI 1.17.0, against [`vercel env`](https://vercel.com/docs/cli/env#running-commands-with-environment-variables), [`vercel integration`](https://vercel.com/docs/cli/integration) and [`vercel link`](https://vercel.com/docs/cli/link). Plan IDs, metadata keys, and variable names come from the live integration and change without notice — read them from `vercel integration add algolia --help`, `vercel integration guide algolia`, and `vercel env ls` at run time.
