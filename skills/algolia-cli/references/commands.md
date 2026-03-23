# Algolia CLI Command Reference

Complete reference for agent-useful commands. All examples use non-interactive flags to avoid TTY prompts.

---

## Auth

### `algolia auth login`

Sign in to your Algolia account via OAuth 2.0 with PKCE. Opens the browser for sign-in, starts a local callback server to receive the redirect automatically.

```bash
algolia auth login [flags]
```

| Flag             | Default | Description                                          |
|------------------|---------|------------------------------------------------------|
| `--app-name`     |         | Auto-select application by name (skips interactive)  |
| `--profile-name` |         | Name for the CLI profile (defaults to app name)      |
| `--default`      | `true`  | Set the profile as the default                       |
| `--no-browser`   | `false` | Print the authorize URL instead of opening browser   |

```bash
# Sign in interactively (opens browser)
algolia auth login

# Auto-select an application by name
algolia auth login --app-name "My App" --default

# SSH / container: print URL, still waits for redirect
algolia auth login --no-browser
```

After sign-in, the CLI fetches your applications, lets you pick one (or auto-selects via `--app-name`), and creates a CLI profile with the Admin API key.

### `algolia auth logout`

Sign out by revoking stored OAuth tokens on the server and removing them from the local keychain.

```bash
algolia auth logout
```

### `algolia auth signup`

Create a new Algolia account via the browser. Opens the sign-up page, then completes the same OAuth flow as `login`.

```bash
algolia auth signup [flags]
```

| Flag             | Default | Description                                          |
|------------------|---------|------------------------------------------------------|
| `--app-name`     |         | Name for the first application                       |
| `--profile-name` |         | Name for the CLI profile (defaults to app name)      |
| `--default`      | `true`  | Set the profile as the default                       |
| `--no-browser`   | `false` | Print the authorize URL instead of opening browser   |

```bash
# Create a new account (opens browser to sign-up page)
algolia auth signup
```

---

## Application Management

### `algolia application list`

List all Algolia applications associated with your account. Requires an active OAuth session (`algolia auth login`). Applications that already have a local CLI profile are marked.

```bash
algolia application list
```

Aliases: `ls`

In interactive mode, offers to configure unconfigured applications as CLI profiles. Use `-o json` for machine-readable output.

### `algolia application create`

Create a new Algolia application and optionally configure it as a CLI profile. Requires an active OAuth session.

```bash
algolia application create [flags]
```

| Flag             | Default                  | Description                                     |
|------------------|--------------------------|-------------------------------------------------|
| `--name`         | `My First Application`   | Name for the application                        |
| `--region`       |                          | Region code (e.g. `CA`, `US`, `EU`)             |
| `--profile-name` |                          | Name for the CLI profile (defaults to app name) |
| `--default`      | `false`                  | Set the new profile as the default              |
| `--dry-run`      | `false`                  | Preview the create request without sending it   |

```bash
# Create with specific options
algolia application create --name "My App" --region CA

# Create and set as default profile
algolia application create --name "My App" --region CA --default

# Preview what would be created
algolia application create --name "My App" --region CA --dry-run
```

### `algolia application select`

Select an Algolia application to use as the default CLI profile. If the selected application already has a local profile, it is set as default. Otherwise, a new profile is created.

```bash
algolia application select [flags]
```

| Flag         | Default | Description                             |
|--------------|---------|-----------------------------------------|
| `--app-name` |         | Select application by name (non-interactive) |

Aliases: `use`

```bash
# Select interactively
algolia application select

# Select by name (non-interactive)
algolia application select --app-name "My App"
```

**Note:** `--app-name` is required in non-interactive mode.

---

## Profile Management

### `algolia profile add`

Create a new CLI profile with Algolia credentials.

```bash
algolia profile add --name "<name>" --app-id "<app-id>" --api-key "<api-key>" [--default]
```

| Flag        | Short | Required | Description            |
|-------------|-------|----------|------------------------|
| `--name`    | `-n`  | Yes*     | Profile name           |
| `--app-id`  |       | Yes*     | Algolia Application ID |
| `--api-key` |       | Yes*     | Algolia API key        |
| `--default` | `-d`  | No       | Set as default profile |

*All three must be provided to skip interactive mode.

```bash
# Add default profile
algolia profile add --name "default" --app-id "ABC123" --api-key "xyz789" --default

# Add secondary profile
algolia profile add --name "staging" --app-id "STG456" --api-key "stg000"
```

### `algolia profile list`

List all configured profiles.

```bash
algolia profile list
```

Output columns: NAME, APPLICATION ID, NUMBER OF INDICES, DEFAULT.

### `algolia profile remove`

Remove a profile from the configuration.

```bash
algolia profile remove <profile> [-y]
```

| Flag        | Short | Default | Description              |
|-------------|-------|---------|--------------------------|
| `--confirm` | `-y`  | `false` | Skip confirmation prompt |

```bash
# Remove the profile named "staging"
algolia profile remove staging -y
```

### `algolia profile setdefault`

Set the default profile.

```bash
algolia profile setdefault <profile>
```

```bash
# Set the default profile to "production"
algolia profile setdefault production
```

---

## API Keys

### `algolia apikeys list`

List all API keys for the application.

```bash
algolia apikeys list
```

Output columns: KEY, DESCRIPTION, ACL, INDICES, VALIDITY, MAX HITS PER QUERY, MAX QUERIES PER IP PER HOUR, REFERERS, CREATED AT.

**Required ACL:** `admin`

### `algolia apikeys create`

Create a new API key.

```bash
algolia apikeys create [flags]
```

| Flag            | Short | Default | Description                                  |
|-----------------|-------|---------|----------------------------------------------|
| `--acl`         |       |         | Comma-separated ACLs (search, browse, addObject, deleteObject, listIndexes, deleteIndex, settings, editSettings, analytics, recommendation, usage, logs, seeUnretrievableAttributes) |
| `--indices`     | `-i`  |         | Index names or patterns (supports `*` wildcard) |
| `--validity`    | `-u`  | `0`     | Duration after which the key expires (e.g., `1h`, `30m`) |
| `--referers`    | `-r`  |         | Allowed referrers (supports `*` wildcard)    |
| `--description` | `-d`  |         | Description to identify the key              |

```bash
# Create a search-only key for one index
algolia apikeys create --acl search,browse --indices MOVIES --description "Search & Browse API Key"

# Create a key with multiple indices, a referer restriction, and 1-hour validity
algolia apikeys create --acl search --indices MOVIES,SERIES --referers "https://example.com" --validity 1h --description "Restricted search key"
```

**Required ACL:** `admin`

### `algolia apikeys get`

Get details of a specific API key.

```bash
algolia apikeys get <api-key>
```

```bash
# Get API key details
algolia apikeys get abcdef1234567890
```

**Output format:** JSON object.

### `algolia apikeys delete`

Delete an API key.

```bash
algolia apikeys delete <api-key> [-y]
```

| Flag        | Short | Default | Description              |
|-------------|-------|---------|--------------------------|
| `--confirm` | `-y`  | `false` | Skip confirmation prompt |

```bash
# Delete an API key
algolia apikeys delete abcdef1234567890 -y
```

**Required ACL:** `admin`

---

## Search

### `algolia search`

Run a search query against an index.

```bash
algolia search <index> [flags]
```

| Flag            | Short | Default | Description             |
|-----------------|-------|---------|-------------------------|
| `--query`       |       | `""`    | Search query string     |
| `--filters`     |       |         | Filter expression       |
| `--hitsPerPage` |       | `20`    | Results per page        |
| `--page`        |       | `0`     | Page number (0-indexed) |
| `--output`      | `-o`  | `json`  | Output format           |

```bash
# Basic search
algolia search MOVIES --query "toy story"

# With filters
algolia search MOVIES --query "toy story" --filters "(genres:Animation OR genres:Family) AND original_language:en"

# Paginated
algolia search MOVIES --query "toy story" --hitsPerPage 5 --page 2

# Save results to file
algolia search MOVIES --query "toy story" > results.json

# Extract only hits
algolia search MOVIES --query "toy story" --output="jsonpath={$.Hits}" > hits.json
```

**Required ACL:** `search`

---

## Indices

### `algolia indices list`

List all indices in the application.

```bash
algolia indices list
```

Output columns: NAME, ENTRIES, SIZE, UPDATED AT, CREATED AT, LAST BUILD DURATION, PRIMARY, REPLICAS.

**Required ACL:** `listIndexes`

### `algolia indices delete`

Delete one or more indices.

```bash
algolia indices delete <index> [<index2> ...] [-y] [-r] [-w]
```

| Flag                 | Short | Default | Description                 |
|----------------------|-------|---------|-----------------------------|
| `--confirm`          | `-y`  | `false` | Skip confirmation prompt    |
| `--include-replicas` | `-r`  | `false` | Also delete replica indices |
| `--wait`             | `-w`  | `false` | Wait for completion         |

```bash
# Delete single index
algolia indices delete MOVIES -y

# Delete index and its replicas
algolia indices delete MOVIES -y -r

# Delete multiple indices
algolia indices delete MOVIES SERIES ANIMES -y
```

**Required ACL:** `deleteIndex`

### `algolia indices clear`

Remove all records from an index. Settings, synonyms, and rules are preserved.

```bash
algolia indices clear <index> [-y] [-w]
```

| Flag        | Short | Default | Description              |
|-------------|-------|---------|--------------------------|
| `--confirm` | `-y`  | `false` | Skip confirmation prompt |
| `--wait`    | `-w`  | `false` | Wait for completion      |

```bash
algolia indices clear MOVIES -y
```

**Required ACL:** `deleteIndex`

### `algolia indices copy`

Copy an index to another. Destination index is overwritten.

```bash
algolia indices copy <source> <destination> [-s <scope>] [-y] [-w]
```

| Flag        | Short | Default | Description                                      |
|-------------|-------|---------|--------------------------------------------------|
| `--scope`   | `-s`  | all     | Comma-separated: `settings`, `synonyms`, `rules` |
| `--confirm` | `-y`  | `false` | Skip confirmation prompt                         |
| `--wait`    | `-w`  | `false` | Wait for completion                              |

```bash
# Copy everything (records + settings + synonyms + rules)
algolia indices copy SERIES MOVIES -y

# Copy only settings
algolia indices copy SERIES MOVIES --scope settings -y

# Copy synonyms and rules
algolia indices copy SERIES MOVIES --scope synonyms,rules -y
```

**Required ACL:** `settings`, `editSettings`, `browse`, `addObject`

### `algolia indices move`

Move (rename) an index. The source index is deleted after the move.

```bash
algolia indices move <source> <destination> [-y] [-w]
```

| Flag        | Short | Default | Description              |
|-------------|-------|---------|--------------------------|
| `--confirm` | `-y`  | `false` | Skip confirmation prompt |
| `--wait`    | `-w`  | `false` | Wait for completion      |

```bash
algolia indices move TEST_MOVIES MOVIES -y
```

**Required ACL:** `addObject`

---

## Objects (Records)

### `algolia objects browse`

Export all records from an index. Output is **ndjson** (one JSON object per line).

```bash
algolia objects browse <index> [flags]
```

| Flag                     | Short | Default | Description                     |
|--------------------------|-------|---------|---------------------------------|
| `--attributesToRetrieve` |       | all     | Comma-separated attribute names |
| `--filters`              |       |         | Filter expression               |
| `--query`                |       |         | Search query                    |
| `--output`               | `-o`  | `json`  | Output format                   |

```bash
# Browse all records
algolia objects browse MOVIES

# Specific attributes only
algolia objects browse MOVIES --attributesToRetrieve title,overview,genres

# With filter
algolia objects browse MOVIES --filters "genres:Drama"

# Export to file
algolia objects browse MOVIES > movies.ndjson
```

**Output format:** ndjson — one JSON object per line, not a JSON array.

**Required ACL:** `browse`

### `algolia objects import`

Import records into an index from an **ndjson** file.

```bash
algolia objects import <index> -F <file> [flags]
```

| Flag                                     | Short | Default | Description                              |
|------------------------------------------|-------|---------|------------------------------------------|
| `--file`                                 | `-F`  |         | File path (`-` for stdin) — **required** |
| `--batch-size`                           | `-b`  | `1000`  | Records per batch                        |
| `--auto-generate-object-id-if-not-exist` | `-a`  | `false` | Auto-generate objectIDs                  |
| `--wait`                                 | `-w`  | `false` | Wait for completion                      |

```bash
# Import from file
algolia objects import MOVIES -F movies.ndjson

# Import from stdin
cat movies.ndjson | algolia objects import MOVIES -F -

# Copy records between indices via pipe
algolia objects browse SERIES | algolia objects import MOVIES -F -

# Auto-generate IDs
algolia objects import MOVIES -F movies.ndjson -a

# Wait for indexing to complete
algolia objects import MOVIES -F movies.ndjson -w
```

**Input format:** ndjson — one JSON object per line. Each object should have an `objectID` field unless `-a` is used.

**Required ACL:** `addObject`

### `algolia objects delete`

Delete records by ID or by filter.

```bash
algolia objects delete <index> [--object-ids <ids> | --filters <filter>] [-y] [--wait]
```

| Flag           | Short | Default | Description                |
|----------------|-------|---------|----------------------------|
| `--object-ids` |       |         | Comma-separated object IDs |
| `--filters`    |       |         | Filter expression          |
| `--confirm`    | `-y`  | `false` | Skip confirmation prompt   |
| `--wait`       |       | `false` | Wait for completion        |

You must specify either `--object-ids` or `--filters`.

```bash
# Delete by IDs
algolia objects delete MOVIES --object-ids 1,2,3 -y

# Delete by filter
algolia objects delete MOVIES --filters "type:Scripted" -y
```

**Required ACL:** `deleteObject`

### `algolia objects update`

Partially update records from an **ndjson** file. Only specified attributes are modified.

```bash
algolia objects update <index> -F <file> [flags]
```

| Flag                     | Short | Default | Description                              |
|--------------------------|-------|---------|------------------------------------------|
| `--file`                 | `-F`  |         | File path (`-` for stdin) — **required** |
| `--create-if-not-exists` | `-c`  | `false` | Create records if missing                |
| `--wait`                 | `-w`  | `false` | Wait for completion                      |
| `--continue-on-error`    | `-C`  | `false` | Skip invalid records                     |

```bash
# Partial update
algolia objects update MOVIES -F updates.ndjson

# Create if not exists
algolia objects update MOVIES -F updates.ndjson -c

# Wait for completion
algolia objects update MOVIES -F updates.ndjson -w
```

**Input format:** ndjson. Each object must have an `objectID`. Supports `_operation` for built-in operations (Add, Remove, Increment, Decrement).

**Required ACL:** `addObject`

---

## Settings

### `algolia settings get`

Get the settings of an index.

```bash
algolia settings get <index>
```

```bash
# Print to terminal
algolia settings get MOVIES

# Save to file
algolia settings get MOVIES > settings.json
```

**Output format:** JSON object.

**Required ACL:** `settings`

### `algolia settings set`

Set individual settings on an index.

```bash
algolia settings set <index> [--<settingName>=<value>] [-f] [-w]
```

| Flag                    | Short | Default | Description              |
|-------------------------|-------|---------|--------------------------|
| `--forward-to-replicas` | `-f`  | `false` | Apply to replica indices |
| `--wait`                | `-w`  | `false` | Wait for completion      |

```bash
# Disable typo tolerance
algolia settings set MOVIES --typoTolerance="false"

# Forward change to replicas
algolia settings set MOVIES --typoTolerance="false" -f
```

**Required ACL:** `editSettings`

### `algolia settings import`

Import settings from a JSON file.

```bash
algolia settings import <index> -F <file> [-f] [-w]
```

| Flag                    | Short | Default | Description                              |
|-------------------------|-------|---------|------------------------------------------|
| `--file`                | `-F`  |         | File path (`-` for stdin) — **required** |
| `--forward-to-replicas` | `-f`  | `false` | Apply to replicas                        |
| `--wait`                | `-w`  | `false` | Wait for completion                      |

```bash
# Import from file
algolia settings import MOVIES -F settings.json

# Import and forward to replicas
algolia settings import MOVIES -F settings.json -f

# Copy settings between indices
algolia settings get SERIES | algolia settings import MOVIES -F -
```

**Input format:** Standard JSON (not ndjson).

**Required ACL:** `editSettings`

---

## Rules

### `algolia rules browse`

Export all rules from an index. Aliases: `list`, `l`.

```bash
algolia rules browse <index>
```

```bash
# Print rules
algolia rules browse MOVIES

# Save to file
algolia rules browse MOVIES > rules.ndjson
```

**Output format:** ndjson — one rule per line.

**Required ACL:** `settings`

### `algolia rules import`

Import rules from an **ndjson** file.

```bash
algolia rules import <index> -F <file> [-f] [-c] [-y] [-w]
```

| Flag                     | Short | Default | Description                              |
|--------------------------|-------|---------|------------------------------------------|
| `--file`                 | `-F`  |         | File path (`-` for stdin) — **required** |
| `--forward-to-replicas`  | `-f`  | `true`  | Apply to replicas                        |
| `--clear-existing-rules` | `-c`  | `false` | Delete existing rules first              |
| `--confirm`              | `-y`  | `false` | Skip confirmation prompt                 |
| `--wait`                 | `-w`  | `false` | Wait for completion                      |

```bash
# Import rules
algolia rules import MOVIES -F rules.ndjson -y

# Replace all existing rules
algolia rules import MOVIES -F rules.ndjson -c -y

# Copy rules between indices
algolia rules browse SERIES | algolia rules import MOVIES -F - -y

# Don't forward to replicas
algolia rules import MOVIES -F rules.ndjson -f=false -y
```

**Input format:** ndjson. Batched at 1000 rules per request.

**Required ACL:** `editSettings`

### `algolia rules delete`

Delete specific rules by ID.

```bash
algolia rules delete <index> --rule-ids <ids> [-y] [-w]
```

| Flag                    | Short | Default | Description                             |
|-------------------------|-------|---------|-----------------------------------------|
| `--rule-ids`            |       |         | Comma-separated rule IDs — **required** |
| `--forward-to-replicas` |       | `false` | Delete from replicas too                |
| `--confirm`             | `-y`  | `false` | Skip confirmation prompt                |
| `--wait`                | `-w`  | `false` | Wait for completion                     |

```bash
# Delete rules
algolia rules delete MOVIES --rule-ids rule-1,rule-2 -y
```

**Required ACL:** `editSettings`

---

## Synonyms

### `algolia synonyms browse`

Export all synonyms from an index. Aliases: `list`, `l`.

```bash
algolia synonyms browse <index>
```

```bash
# Print synonyms
algolia synonyms browse MOVIES

# Save to file
algolia synonyms browse MOVIES > synonyms.ndjson
```

**Output format:** ndjson — one synonym per line.

**Required ACL:** `settings`

### `algolia synonyms import`

Import synonyms from an **ndjson** file.

```bash
algolia synonyms import <index> -F <file> [-f] [-r] [-w]
```

| Flag                          | Short | Default | Description                              |
|-------------------------------|-------|---------|------------------------------------------|
| `--file`                      | `-F`  |         | File path (`-` for stdin) — **required** |
| `--forward-to-replicas`       | `-f`  | `true`  | Apply to replicas                        |
| `--replace-existing-synonyms` | `-r`  | `false` | Replace all existing synonyms            |
| `--wait`                      | `-w`  | `false` | Wait for completion                      |

```bash
# Import synonyms
algolia synonyms import MOVIES -F synonyms.ndjson

# Replace all existing synonyms
algolia synonyms import MOVIES -F synonyms.ndjson -r

# Copy synonyms between indices
algolia synonyms browse SERIES | algolia synonyms import MOVIES -F -

# Don't forward to replicas
algolia synonyms import MOVIES -F synonyms.ndjson -f=false
```

**Input format:** ndjson. Each synonym must have `objectID` and `type` fields.

**Synonym types:**

| Type             | Required Fields                                |
|------------------|------------------------------------------------|
| `synonym`        | `synonyms` (array of strings)                  |
| `oneWaySynonym`  | `input` (string), `synonyms` (array)           |
| `altCorrection1` | `word` (string), `corrections` (array)         |
| `altCorrection2` | `word` (string), `corrections` (array)         |
| `placeholder`    | `placeholder` (string), `replacements` (array) |

**Required ACL:** `editSettings`

### `algolia synonyms delete`

Delete specific synonyms by ID.

```bash
algolia synonyms delete <index> --synonym-ids <ids> [-y] [-w]
```

| Flag                    | Short | Default | Description                                |
|-------------------------|-------|---------|--------------------------------------------|
| `--synonym-ids`         |       |         | Comma-separated synonym IDs — **required** |
| `--forward-to-replicas` |       | `false` | Delete from replicas too                   |
| `--confirm`             | `-y`  | `false` | Skip confirmation prompt                   |
| `--wait`                | `-w`  | `false` | Wait for completion                        |

```bash
# Delete synonyms
algolia synonyms delete MOVIES --synonym-ids syn-1,syn-2 -y
```

**Required ACL:** `editSettings`

### `algolia synonyms save`

Create or update a single synonym interactively.

```bash
algolia synonyms save <index> --id <id> [--type <type>] [flags]
```

| Flag                    | Short | Default   | Description                                                                  |
|-------------------------|-------|-----------|------------------------------------------------------------------------------|
| `--id`                  | `-i`  |           | Synonym ID — **required**                                                    |
| `--type`                | `-t`  | `synonym` | Type: `synonym`, `oneWaySynonym`, `altCorrection1`, `altCorrection2`, `placeholder` |
| `--synonyms`            | `-s`  |           | Comma-separated synonyms (for `synonym` and `oneWaySynonym`)                 |
| `--input`               | `-n`  |           | Input word (for `oneWaySynonym`)                                             |
| `--placeholder`         | `-l`  |           | Placeholder token (for `placeholder`)                                        |
| `--replacements`        | `-r`  |           | Comma-separated replacements (for `placeholder`)                             |
| `--word`                | `-w`  |           | Base word (for `altCorrection1`, `altCorrection2`)                           |
| `--corrections`         | `-c`  |           | Comma-separated corrections (for `altCorrection1`, `altCorrection2`)         |
| `--forward-to-replicas` | `-f`  | `false`   | Apply to replicas                                                            |
| `--wait`                |       | `false`   | Wait for completion                                                          |

```bash
# Regular two-way synonym
algolia synonyms save MOVIES --id syn-1 --synonyms film,movie,picture

# One-way synonym
algolia synonyms save MOVIES --id syn-2 --type oneWaySynonym --input "JS" --synonyms "JavaScript"

# Placeholder
algolia synonyms save MOVIES --id syn-3 --type placeholder --placeholder "<director>" --replacements "Spielberg,Nolan,Tarantino"
```

**Required ACL:** `editSettings`

---

## Crawler

Crawler commands require separate authentication: set `ALGOLIA_CRAWLER_USER_ID` and `ALGOLIA_CRAWLER_API_KEY` environment variables, or add `crawler_user_id` and `crawler_api_key` to your profile config file (`~/.config/algolia/config.toml`).

### `algolia crawler list`

List crawlers, optionally filtered by name or application ID.

```bash
algolia crawler list [flags]
```

| Flag       | Default | Description       |
|------------|---------|-------------------|
| `--name`   |         | Filter by name    |
| `--app-id` |         | Filter by app ID  |

Aliases: `l`

```bash
# List all crawlers
algolia crawler list

# Filter by name
algolia crawler list --name my-crawler

# Filter by app ID
algolia crawler list --app-id ABC123
```

Output columns: ID, NAME, STATUS, LAST REINDEX. Use `-o json` for machine-readable output.

### `algolia crawler get`

Get details of a specific crawler.

```bash
algolia crawler get <crawler_id> [flags]
```

| Flag            | Short | Default | Description                       |
|-----------------|-------|---------|-----------------------------------|
| `--config-only` | `-c`  | `false` | Display only the crawler config   |

```bash
# Get full crawler details
algolia crawler get my-crawler

# Get config only (useful for piping to create)
algolia crawler get my-crawler --config-only
```

**Output format:** JSON.

### `algolia crawler create`

Create a new crawler from a configuration file.

```bash
algolia crawler create <name> -F <file> [flags]
```

| Flag        | Short | Default | Description                                        |
|-------------|-------|---------|----------------------------------------------------|
| `--file`    | `-F`  |         | Path to config file (`-` for stdin) — **required** |
| `--dry-run` |       | `false` | Preview the create request without sending it      |

Aliases: `new`, `n`, `c`

```bash
# Create from file
algolia crawler create my-crawler -F config.json

# Create from another crawler's config
algolia crawler get other-crawler --config-only | algolia crawler create my-crawler -F -

# Dry run
algolia crawler create my-crawler -F config.json --dry-run
```

### `algolia crawler run`

Start or resume a crawler. Previously ongoing crawls will be resumed; otherwise, the crawler waits for its next scheduled run.

```bash
algolia crawler run <crawler_id> [--dry-run]
```

| Flag        | Default | Description                                   |
|-------------|---------|-----------------------------------------------|
| `--dry-run` | `false` | Preview the run request without sending it    |

```bash
algolia crawler run my-crawler
```

### `algolia crawler pause`

Pause one or more crawlers.

```bash
algolia crawler pause <crawler_id>... [--dry-run]
```

| Flag        | Default | Description                                     |
|-------------|---------|-------------------------------------------------|
| `--dry-run` | `false` | Preview the pause request without sending it    |

```bash
# Pause one
algolia crawler pause my-crawler

# Pause multiple
algolia crawler pause my-crawler-1 my-crawler-2
```

### `algolia crawler reindex`

Request the specified crawler(s) to start (or restart) crawling.

```bash
algolia crawler reindex <crawler_id>... [--dry-run]
```

| Flag        | Default | Description                                       |
|-------------|---------|---------------------------------------------------|
| `--dry-run` | `false` | Preview the reindex request without sending it    |

```bash
# Reindex one
algolia crawler reindex my-crawler

# Reindex multiple
algolia crawler reindex my-crawler-1 my-crawler-2
```

### `algolia crawler unblock`

Unblock a crawler by cancelling the task that is blocking it.

```bash
algolia crawler unblock <crawler_id> [-y] [--dry-run]
```

| Flag        | Short | Default | Description                                       |
|-------------|-------|---------|---------------------------------------------------|
| `--confirm` | `-y`  | `false` | Skip confirmation prompt                          |
| `--dry-run` |       | `false` | Preview the unblock request without sending it    |

```bash
algolia crawler unblock my-crawler -y
```

### `algolia crawler crawl`

Immediately crawl specific URLs. Records are pushed to the live index (or temporary index if a reindex is ongoing).

```bash
algolia crawler crawl <crawler_id> --urls <url>,... [flags]
```

| Flag     | Short | Default | Description                                          |
|----------|-------|---------|------------------------------------------------------|
| `--urls` | `-u`  |         | Comma-separated URLs (max 50) — **required**         |
| `--save` | `-s`  | `false` | Save URLs to `extraUrls` in the crawler config       |

```bash
# Crawl specific URLs
algolia crawler crawl my-crawler --urls https://example.com,https://example.com/page2

# Crawl and save to config
algolia crawler crawl my-crawler --urls https://example.com --save
```

### `algolia crawler test`

Test a URL against the crawler's configuration and show the extracted records.

```bash
algolia crawler test <crawler_id> --url <url> [flags]
```

| Flag       | Short | Default | Description                                            |
|------------|-------|---------|--------------------------------------------------------|
| `--url`    | `-u`  |         | The URL to test — **required**                         |
| `--config` | `-F`  |         | Config file to override the crawler's config (`-` for stdin) |
| `--dry-run`|       | `false` | Preview the test request without sending it            |

```bash
# Test a URL
algolia crawler test my-crawler --url https://example.com

# Test with config override
algolia crawler test my-crawler --url https://example.com -F config.json

# Dry run
algolia crawler test my-crawler --url https://example.com --dry-run
```

**Output format:** JSON.

### `algolia crawler stats`

Get a summary of crawled URL statuses for a crawler.

```bash
algolia crawler stats <crawler_id>
```

```bash
algolia crawler stats my-crawler
```

Output columns: STATUS, CATEGORY, REASON, COUNT. Use `-o json` for machine-readable output.

---

## Describe

### `algolia describe`

Describe the CLI's command tree in a machine-readable JSON format. Useful for agents and automation to discover available commands and flags.

```bash
algolia describe [command] [subcommand]...
```

Aliases: `schema`

```bash
# Describe the root command (lists all top-level commands)
algolia describe

# Describe a specific command
algolia describe search

# Describe a subcommand
algolia describe objects browse
```

**Output format:** JSON with `schemaVersion` and `command` fields.

---

## Common Patterns

### Copy data between indices

```bash
# Copy all records
algolia objects browse SOURCE_INDEX | algolia objects import DEST_INDEX -F -

# Copy rules
algolia rules browse SOURCE_INDEX | algolia rules import DEST_INDEX -F - -y

# Copy synonyms
algolia synonyms browse SOURCE_INDEX | algolia synonyms import DEST_INDEX -F -

# Copy settings
algolia settings get SOURCE_INDEX | algolia settings import DEST_INDEX -F -
```

### Export and backup

```bash
# Full index backup
algolia objects browse MOVIES > movies_records.ndjson
algolia settings get MOVIES > movies_settings.json
algolia rules browse MOVIES > movies_rules.ndjson
algolia synonyms browse MOVIES > movies_synonyms.ndjson
```

### Restore from backup

```bash
# Restore everything
algolia objects import MOVIES -F movies_records.ndjson -w
algolia settings import MOVIES -F movies_settings.json -w
algolia rules import MOVIES -F movies_rules.ndjson -c -y -w
algolia synonyms import MOVIES -F movies_synonyms.ndjson -r -w
```

### ndjson format tips

The CLI uses **ndjson** (newline-delimited JSON) for records, rules, and synonyms. Each line is a standalone JSON object:

```
{"objectID":"1","title":"The Matrix","year":1999}
{"objectID":"2","title":"Inception","year":2010}
```

**Do not** wrap in a JSON array. This is wrong:

```json
[{"objectID":"1"},{"objectID":"2"}]
```

To convert a JSON array to ndjson:

```bash
# Using jq
jq -c '.[]' array.json > records.ndjson
```
