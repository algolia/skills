# Algolia CLI reference (Crawler)

Everything in this skill runs through the **Algolia CLI**. Read the [gotchas](#gotchas) — a couple of them will save you an afternoon.

Install: `brew install algolia/algolia-cli/algolia` (or see the CLI docs for other platforms). For deeper CLI usage on the index side (records, synonyms, rules), see the **algolia-cli** skill.

## Setup and credentials

Two distinct sets of credentials are involved — they're commonly confused:

1. **Crawler API credentials** — a Crawler **user ID** + **API key**, found in the Crawler dashboard under Settings → API credentials. These authenticate the `algolia crawler` commands. They are **not** your app's search/admin keys.
2. **An Algolia write API key** for the target app — embedded in the crawler config (`apiKey`) so the crawler can write records. Prefer a **restricted key** scoped to the index pattern with ACLs: `addObject, deleteObject, deleteIndex, editSettings, settings, listIndexes, browse, search`. Plus your **App ID** (public).

The `algolia crawler` commands read the Crawler credentials from these exact environment variables:

```bash
export ALGOLIA_CRAWLER_USER_ID="…"     # Crawler user ID
export ALGOLIA_CRAWLER_API_KEY="…"     # Crawler API key
export APP_ID="…"                       # Algolia App ID (public)
export WRITE_KEY="…"                    # restricted write key for the index
```

You can also store them in a profile at `~/.config/algolia/config.toml` (`crawler_user_id` / `crawler_api_key`). Never paste secret keys into chats, tickets, or committed files. If a key is exposed, rotate it.

## Command cheatsheet

```bash
# --- crawler lifecycle ---
algolia crawler create <name> -F config.json     # create (prints nothing on success)
algolia crawler list                              # list crawlers (find an id)
algolia crawler get <id>                          # inspect crawler + config + status (UUID only, not a name)
algolia crawler test <id> --url <url> [-F cfg]    # extract records WITHOUT indexing
algolia crawler reindex <id>                      # start a crawl that writes records
algolia crawler run <id> | pause <id>             # resume / pause
algolia crawler stats <id>                        # crawl status summary
algolia crawler crawl <id> --url <url>            # crawl specific URL(s)
algolia crawler unblock <id>                      # clear a blocked crawler

# --- index side (same CLI) ---
algolia settings import <index> --application-id $APP_ID --api-key $WRITE_KEY -F settings.json --wait
algolia settings get <index> --application-id $APP_ID --api-key $WRITE_KEY
algolia search <index> --application-id $APP_ID --api-key $SEARCH_KEY --query "…" --hitsPerPage 3
```

The `recordExtractor` inside `config.json` is stored as `{"__type": "function", "source": "<stringified function>"}`. Build configs with `jq --rawfile` so the function's quotes/newlines are escaped correctly (see [workflow.md](workflow.md#2-write-the-config)).

## Gotchas

### The `renderJavaScript` gotcha
The CLI models `renderJavaScript` as a **boolean only**. If your config uses the documented object form (`{ "enabled": true, "patterns": [...], "waitTime": {...} }`) or the array (patterns) form, the CLI fails to deserialize it:

```
json: cannot unmarshal object into Go struct field Config.config.renderJavaScript of type bool
```

This breaks `crawler get`, `crawler list`, and `crawler create -F` for that config. So:

- **Use `renderJavaScript: true`.** In practice the default render wait is enough for most pages — validate with `crawler test` (empty field/score values mean the page needs more render time).
- `crawler list` fails account-wide if *any* crawler in the app uses a non-boolean `renderJavaScript` — even one you didn't create. When `list` errors with the message above, use `crawler get <id>` for a crawler whose id you already have, or recover the id via the REST list endpoint (see the id-recovery note above) — `get` cannot look a crawler up by name.

### `create` prints nothing on success — and id recovery can be fiddly
`algolia crawler create` returns silently — it does not echo the new crawler id. Recover it from `algolia crawler list`. Note `algolia crawler get` takes a **UUID only** — passing a crawler *name* returns `malformed_id`, so `get <name>` is not a recovery path.

If `list` itself errors (see the `renderJavaScript` gotcha below — one non-boolean crawler anywhere in the account breaks it), there is **no pure-CLI way to get the id**. Fall back to the Crawler REST list endpoint:

```bash
curl -sS -u "$ALGOLIA_CRAWLER_USER_ID:$ALGOLIA_CRAWLER_API_KEY" \
  "https://crawler.algolia.com/api/1/crawlers?name=<crawler-name>" | jq -r '.items[0].id'
```

### No config-update or delete command
The CLI can create crawlers but has no command to *update* an existing crawler's config or to *delete* one. To change a config, re-create the crawler (delete the old one first). Crawler deletion is done from the Algolia dashboard.

### `initialIndexSettings` often doesn't apply
Even when stored correctly in the config, `initialIndexSettings` frequently does not get applied to the index on the first crawl — the index comes up with null settings, so `filters`/facets silently fail. **Always apply settings explicitly** with `algolia settings import` after the index exists ([rag-index-settings.md](rag-index-settings.md)). A scheduled reindex also does not re-apply settings.
