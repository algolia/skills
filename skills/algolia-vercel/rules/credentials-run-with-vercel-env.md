---
title: Run Commands Through vercel env run, Not Through a Pulled File
impact: HIGH
impactDescription: a pulled file writes secrets to disk and loads nothing, and the Algolia CLI reads different variable names than the ones Vercel injects — so commands can run against an empty or unintended application
tags: credentials, env, secrets
---

## Run Commands Through `vercel env run`, Not Through a Pulled File

`vercel env run -- <command>` fetches the linked project's environment variables and passes them to the command. Nothing is written to disk, and nothing has to be loaded afterwards. Use it for every Algolia CLI command on this path.

`vercel env pull` is the other half of that pair and a different tool: it writes a file and loads nothing. `$ALGOLIA_APP_ID` is still empty in the shell right after it, so the obvious next command sends an empty app ID — or a stale one from an unrelated application. Reach for `pull` only when something genuinely needs a file on disk (see the bottom of this rule).

**The environment has to match.** `env run` defaults to `development`. Connect `-e production` on `add` and a bare `env run` fetches development, which holds none of the Algolia variables — and that reads as "provisioning failed". Pass the same `-e` you connected with, plus `--git-branch <branch>` for a preview branch.

**The names do not match either.** Vercel injects `ALGOLIA_APP_ID`, `ALGOLIA_SEARCH_API_KEY`, `ALGOLIA_WRITE_API_KEY`. The Algolia CLI reads `ALGOLIA_APPLICATION_ID` and `ALGOLIA_API_KEY`. Something has to bridge the two, per command, choosing the write key or the search key deliberately.

**Incorrect:**

```bash
vercel env pull                                                  # overwrote .env.local
source .env.local                                                # hands a $(…) in a value to the shell
cat .env.local                                                   # dumps the write key into the transcript
ALGOLIA_APPLICATION_ID="$ALGOLIA_APP_ID" algolia indices list    # $ALGOLIA_APP_ID was never set
vercel env run -- algolia indices list                           # runs, but with no credentials the CLI understands
```

**Correct — one static block, the credentials bridged inside the child process:**

```bash
vercel env run -e development --scope acme-team -- sh -eu -c '
: "${ALGOLIA_APP_ID:?not injected — check: vercel env ls}"
: "${ALGOLIA_WRITE_API_KEY:?not injected — check: vercel env ls}"
export ALGOLIA_APPLICATION_ID="$ALGOLIA_APP_ID"
export ALGOLIA_API_KEY="$ALGOLIA_WRITE_API_KEY"
exec "$@"
' algolia-env algolia objects import example_products -F example.ndjson -w
```

Four details carry the whole thing:

- **Single quotes.** Your shell expands nothing inside them. `$ALGOLIA_APP_ID` is resolved by the child `sh`, which only exists after `env run` has injected the variables. Double quotes would expand it in the parent, where it is empty, and bake that emptiness in.
- **`${VAR:?message}` with `-u`.** A missing or empty variable prints the message and exits before `exec`, so `algolia` never runs against half a credential pair. The guard detects **absence only** — it says nothing about where a value came from or whether it is the right one.
- **The command is argv, not text.** It sits after the closing quote: `$0` is the label `algolia-env` and `"$@"` is the command. An index name or query containing `$`, a backtick or `;` stays data.
- **Swap one name for the other operation.** `ALGOLIA_WRITE_API_KEY` for an import, `ALGOLIA_SEARCH_API_KEY` for a validation query. The block is otherwise identical every time — copy it, change the key variable and the trailing command.

Never `source` or `eval` an env file, never print a value, and do not turn on `set -x` around this — tracing echoes the exported key.

**Run the app itself the same way:**

```bash
vercel env run -e development --scope acme-team -- npm run dev
```

The dev server then sees the same injected `ALGOLIA_*` names the Vercel build sees. Getting those through to browser code is `credentials-write-key-never-reaches-the-browser`.

### When a variable looks missing

```bash
vercel env ls --scope acme-team     # names and targets, no values
```

Read the real names off that output, then check, in order:

1. **Environment.** Did `env run -e …` name the environment the resource is connected to? It defaults to `development`.
2. **Connection.** Is the resource connected to *this* project — `vercel integration list --all --integration algolia --format=json --scope acme-team`?
3. **Prefix.** `--prefix` on `add`/`connect` prepends the prefix to the injected name as-is (`--prefix NEON2_` gives `NEON2_DATABASE_URL`). Do not guess what the prefixed Algolia names became: take them verbatim from `vercel env ls` and substitute them in both `${…}` references above, and in the `next.config.js` mapping, consistently.

### Local values win over the fetched ones

`env run` builds the child environment in this order, last one winning:

```
fetched Vercel records  <  local .env files  <  your shell (process env)
```

So a stale `export ALGOLIA_APP_ID=…` or an old `.env.local` **overrides** what Vercel just fetched, silently and without error. A name listed by `vercel env ls` therefore proves the project has it configured — not that the command used that value, that application, or that key.

The `${VAR:?…}` guards do not catch this: they detect an absent variable, never a wrong one. Before running anything that matters, look for stale raw names in both layers — the raw variables the integration injects, the ones the Algolia CLI reads, and any `--prefix` variants.

Inspect the **names only** — never print the values. Cover both layers: the Algolia-related names in your process environment, and the key side of every dotenv file `env run` loads (`.env.development.local`, `.env.local`, `.env.development`, `.env`).

Then resolve only the ones that are genuinely stale — `unset` them for the shell, remove or correct the dotenv entries, and leave anything the user set on purpose alone. If the app ID a command reports still looks wrong after that, recheck the selected project, resource and environment as well: the conflict may be a wrong remote link rather than a local override.

### When a file really is needed

Some tooling cannot be wrapped. Then pull — naming the target file explicitly, in a gitignored path, for the environment you connected:

```bash
grep -q '^\.env\*\.local$' .gitignore 2>/dev/null || printf '\n.env*.local\n' >> .gitignore
cut -d= -f1 .env.local 2>/dev/null          # what is there now; key side only
vercel env pull .env.local --environment development --scope acme-team
```

Look at the target first and copy out any local-only entries you need to keep, because the pull replaces the file rather than merging into it. **Omitting `--yes` is not protection.** A file the Vercel CLI generated is recognised by its header and overwritten with no prompt at all, `--yes` or not; only a file the CLI did not write triggers the confirmation (and in non-interactive mode that becomes an `action_required` result instead). If the existing file holds values you cannot afford to lose, pull into a filename nothing else uses. If `add` runs first, pass it `--no-env-pull` so its automatic pull does not write the file behind your back.

## Notes

- Browser-public variables (the `NEXT_PUBLIC_` pair) are embedded into the client bundle at **build time**, so a **deployed** app serves the values from its last build until it is rebuilt. Triggering a deployment is the user's call, not something to do to make a check pass.
- `vercel env run` needs a linked project (`vercel link`), same as `env pull`.

## Sources

- `vercel env run --help` (Vercel CLI 56.2.1, 2026-09-18) — `-e/--environment <TARGET>` "(default: development)", `--git-branch`, global `--scope`
- https://vercel.com/docs/cli/env#running-commands-with-environment-variables — "runs any command with environment variables from your linked Vercel project, without writing them to a file"; the `--` separator is required
- https://vercel.com/docs/cli/env — `env pull` writes Development variables to `[.env.local]`; `--yes` "bypass the confirmation prompt when overwriting an environment file"
- https://github.com/vercel/vercel/blob/main/packages/cli/src/commands/env/run.ts — the child environment is composed fetched records, then local env files, then `process.env`; later entries win (matches Vercel CLI 56.2.1, read 2026-09-18)
- https://github.com/vercel/vercel/blob/main/packages/cli/src/commands/env/pull.ts — a file whose header marks it as CLI-generated is overwritten without confirmation; only a file the CLI did not create prompts, or reports `action_required` when non-interactive (matches 56.2.1)
- `vercel integration add --help` (56.2.1) — `--prefix <PREFIX>`: "`--prefix NEON2_` creates `NEON2_DATABASE_URL` instead of `DATABASE_URL`"; `--no-env-pull`
- Algolia CLI 1.17.0 reads `ALGOLIA_APPLICATION_ID` and `ALGOLIA_API_KEY` from the environment (`algolia-cli` skill: env vars > flags > profile)
