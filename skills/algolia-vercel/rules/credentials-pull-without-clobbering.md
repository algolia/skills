---
title: Pull Credentials to a Staging File, Then Load Them by Parsing It
impact: BLOCKING
impactDescription: env pull overwrites its target file, defaults to the Development environment, and a pulled file is not loaded by anything until you load it
tags: credentials, env, secrets
---

## Pull Credentials to a Staging File, Then Load Them by Parsing It

Three separate problems live in this one step.

**It overwrites.** `vercel env pull` writes `.env.local` by default and replaces it. A project that keeps local-only variables there loses them. `vercel integration add` runs `env pull` for you after provisioning, so this can happen without you typing the command — pass `--no-env-pull` to `add` and do the pull yourself. A staging path is not immune either: if `.env.algolia.local` is already on disk from an earlier run, pulling into it destroys whatever it held.

**It pulls the wrong environment by default.** `env pull` targets **Development** unless `--environment` says otherwise, and it does not inherit the `-e` values that `add` or `resource connect` received. Connect only `-e production` and a bare `env pull` stages a file with no Algolia variables in it — which then gets misread as "provisioning failed". Pass `--environment <the one you connected>`, plus `--git-branch <branch>` for a preview branch.

**It only writes a file.** Nothing reads it afterwards. The shell does not get the values, and Next.js does not read `.env.algolia.local` — it reads `.env.local`, `.env.development`, `.env`. A command written as `ALGOLIA_APPLICATION_ID="$ALGOLIA_APP_ID" algolia …` right after a pull sends an *empty* app ID, or worse, a stale one left over from an unrelated application.

The file also contains a live write-capable API key. Do not print it, diff it, or grep it in a way that echoes matching lines.

**Incorrect (default target and environment, contents echoed, values never loaded):**

```bash
vercel env pull                             # may have just destroyed .env.local
vercel env pull .env.algolia.local          # and this destroys an earlier staging file
cat .env.local                              # dumps ALGOLIA_WRITE_API_KEY into the transcript
cp .env.local .env.local.bak                # an un-ignored copy of a write key
diff .env.local.bak .env.local              # prints both versions of every secret
ALGOLIA_APPLICATION_ID="$ALGOLIA_APP_ID" algolia indices list   # $ALGOLIA_APP_ID was never set
```

`source .env.algolia.local` is not the fix. It hands the file's contents to the shell as code: a value containing `$(...)`, a backtick, or `&&` gets executed. Parse the file instead.

**Correct (ignore, stage without overwriting, pull the connected environment, check names only):**

```bash
# 1. Make it unignorable-by-accident BEFORE anything writes it.
#    The leading \n guards against a .gitignore with no trailing newline, which would
#    otherwise splice the pattern onto the previous line and silently ignore nothing.
grep -q '^\.env\*\.local$' .gitignore 2>/dev/null || printf '\n.env*.local\n' >> .gitignore

# 2. See what the integration injected — names and targets, no values
vercel env ls --scope acme-team

# 3. Pick a staging path and STOP if anything is already there. Do not inspect it and
#    decide it looks fine — see "Fail closed" below.
STAGING=.env.algolia.local
if [ -e "$STAGING" ]; then
  echo "refusing to touch existing $STAGING — choose an unused .env.*.local path" >&2
  exit 1
fi

# 4. Pull into the now-guaranteed-fresh path, naming the environment you connected on `add`
#    (`-e development` above → `--environment development` here). Bare `env pull` = Development.
vercel env pull "$STAGING" --environment development --scope acme-team

# 5. Confirm the names arrived. cut takes the key side of each line; no value can reach stdout
cut -d= -f1 "$STAGING" | grep '^ALGOLIA_'
```

**Fail closed — an existing staging file is a stop, not an input.**

The tempting shortcut is to list the names in the existing file and reuse it when all three are present. That check cannot do the job it looks like it is doing. `ALGOLIA_APP_ID`, `ALGOLIA_SEARCH_API_KEY` and `ALGOLIA_WRITE_API_KEY` are the same three names in a file pulled last month, in a file pulled for a *different* project in the same repo, and in one holding keys that have since been rotated. Names present means nothing about which application the values point at. Reuse it and the seeding, the validation query and the merged `.env.local` all silently target the wrong application — and the failure surfaces later as an empty search or records in a stranger's index, far from the command that caused it.

So do not reuse, and do not overwrite either — the file on disk may be the only copy of a key the user holds. Stop, tell them what path is in the way, and continue with a different one:

```bash
STAGING=.env.algolia.2.local    # any unused path still matching the ignored .env*.local
```

Then pass that same `$STAGING` to everything downstream — the helper invocations, the merge, and the validation query — so a later step cannot fall back to the original path. `--environment` on the new pull still has to name the environment `add` or `resource connect` was given.

**Correct (load the values for a CLI command, by parsing):**

`$ALGOLIA_VERCEL_SKILL_DIR` is the absolute path of the directory containing this skill's `SKILL.md`, wherever it is installed — not a path inside the app's repository. Resolve it once; the working directory stays on the app.

```bash
node "$ALGOLIA_VERCEL_SKILL_DIR/scripts/with-algolia-env.mjs" "$STAGING" ALGOLIA_WRITE_API_KEY -- \
  algolia objects import example_products -F example.ndjson -w
```

The helper reads the file with `node:util` `parseEnv`, sets `ALGOLIA_APPLICATION_ID` and `ALGOLIA_API_KEY` for that child process only, and spawns it without a shell. The parsed file wins over the ambient environment, so a stale `export ALGOLIA_API_KEY=…` from another application cannot take over. It exits `2` and names the variable if a key is missing, and otherwise passes the command's own exit code through.

**Correct (load the values for the Next.js app, by merging):**

Next.js reads `.env.local`. Merge the five values it needs into that file, rewriting only those keys and leaving every other line — including comments — exactly as it found them:

```bash
node - "$STAGING" <<'EOF'
const { readFileSync, writeFileSync, existsSync } = require('node:fs');
const { parseEnv } = require('node:util');

const pulled = parseEnv(readFileSync(process.argv[2], 'utf8'));
const managed = {
  ALGOLIA_APP_ID: pulled.ALGOLIA_APP_ID,
  ALGOLIA_SEARCH_API_KEY: pulled.ALGOLIA_SEARCH_API_KEY,             // raw name, read server-side
  ALGOLIA_WRITE_API_KEY: pulled.ALGOLIA_WRITE_API_KEY,               // server-side only
  NEXT_PUBLIC_ALGOLIA_APP_ID: pulled.ALGOLIA_APP_ID,                 // browser-safe
  NEXT_PUBLIC_ALGOLIA_SEARCH_API_KEY: pulled.ALGOLIA_SEARCH_API_KEY, // browser-safe
};
for (const [k, v] of Object.entries(managed)) if (!v) throw new Error(`missing value for ${k}`);

const lines = existsSync('.env.local') ? readFileSync('.env.local', 'utf8').split('\n') : [];
const seen = new Set();
const merged = lines.map((line) => {
  const key = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)=/)?.[1];
  if (!key || !(key in managed)) return line;   // unrelated lines kept verbatim
  seen.add(key);
  return `${key}=${JSON.stringify(managed[key])}`;
});
for (const [key, value] of Object.entries(managed)) {
  if (!seen.has(key)) merged.push(`${key}=${JSON.stringify(value)}`);
}
while (merged.at(-1) === '') merged.pop();
writeFileSync('.env.local', merged.join('\n') + '\n');
console.log('merged (names only):', Object.keys(managed).join(', '));
EOF
```

Rerunning it is a no-op on an unchanged pull, and unrelated keys and comments already in `.env.local` survive it. It prints key names, never values.

`ALGOLIA_SEARCH_API_KEY` is copied under its bare name **as well as** under the `NEXT_PUBLIC_` one. Server-side code reads the raw variable — a route handler, an indexing script — and it is already the browser-safe key, so there is nothing to withhold. The variable that must never get a `NEXT_PUBLIC_` twin is `ALGOLIA_WRITE_API_KEY`.

This merge only fixes the **local** machine. Vercel injects the raw `ALGOLIA_*` names into builds and never creates the `NEXT_PUBLIC_` twins, so the deployed browser bundle still has nothing until the two public names are derived from the raw ones in `next.config.js`. That mapping, and the rule that the write key never appears in it, are in `credentials-write-key-never-reaches-the-browser` — do it as part of this phase, not later.

Then confirm the mapping actually reaches the code, in both places it has to:

```bash
# Locally: Next.js only reads .env.local at server start — restart, then hit the page.
cut -d= -f1 .env.local | grep '^\(NEXT_PUBLIC_\)\?ALGOLIA'   # names only, all five present
npm run dev                                                  # then load the search page
```

Deployed is a separate check, and it is the user's call: Vercel inlines `NEXT_PUBLIC_` values at **build** time, so the browser sees them only after the next deployment. Until then, a working local page says nothing about production. Say that rather than implying the deployed app is fixed.

If the user would rather not keep a second dotenv file, delete the staging file once the merge is done.

## Notes

- `vercel env pull` defaults to the Development environment; use `--environment production` or `--git-branch <name>` for a different target. It never picks up the `-e` values from `add`/`connect` — match them yourself.
- If a variable is absent after a pull, check in this order: did you pull the environment the resource is connected to, is the resource connected to *this* project (`vercel integration list --all --integration algolia --format=json`), and was it connected with a `--prefix` (the names would be `ALGOLIA2_…`).
- Vercel applies environment variables at build time, so the **deployed** app picks up new variables only on the next deployment. That is the user's call, not something to trigger to make a check pass.

## Sources

- `vercel env pull --help` (Vercel CLI 56.2.1) — default target `[.env.local]`, `--environment`, `--git-branch`; writes a file and nothing else
- `vercel integration add --help` (Vercel CLI 56.2.1) — `--no-env-pull`, `--no-connect`, `--prefix`
- https://vercel.com/docs/cli/integration — post-provisioning `env pull`
- https://nextjs.org/docs/app/guides/environment-variables — which files Next.js loads, and `NEXT_PUBLIC_`
- `node:util` `parseEnv` — Node.js ≥ 20.12
