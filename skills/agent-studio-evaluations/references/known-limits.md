# Known limits and quirks

Everything on this page was observed on `algobot-ai` 2.1.0 during real tuning
sessions. The evals endpoints are experimental (undocumented, may change
without notice), so treat each entry as "observed", not as a contract.
Re-check after an upgrade.

## Limits

| Area | Limit (observed) | What to do |
|---|---|---|
| `runs judgments` | `--limit` is 1 to 200 (default 50) | Page with `--offset`; `$SKILL_DIR/scripts/fetch_run.py` does it for you |
| `datasets list-cases` | `--limit` is 1 to 200 (default 50) | Page with `--offset` |
| `datasets create --generation-params` | `targetCount` <= 100, `minPerMetric` <= 20 | For more cases per metric, merge several datasets (see "N per metric above the cap" in [evaluations.md](evaluations.md)) |
| `datasets create --generation-params` | `metricSlugs` was ignored; every builtin metric was planned | Filter with `list-cases --metric-slug` after generation |
| `experiments create --num-cases` | A TOTAL across the selected metrics, split evenly (100 with 2 metrics gave 50 each); CLI default is 25 | Multiply: 3 metrics x 100 each = `--num-cases 300` |
| `datasets delete` | Refused with HTTP 409 while the dataset is generating | Wait for generation to finish, then delete |
| `datasets import` | A row whose `messages` history ends on a user turn that differs from `query` is rejected | Trim trailing user turns from the history |

## Output and status values

- `algobot evals <group> <command> --help` printed the top-level `evals`
  help instead of the command's options. Use
  `algobot evals <group> help <command>` to see a command's flags.

- `--jq` returns JSON-quoted strings (there is no raw mode). Strip the quotes
  before reusing a value: `... --jq '.data[0].id' | tr -d '"'`.
- `profiles build-status` reports `PENDING`, `STARTED`, `SUCCESS` or
  `FAILURE`, and `datasets build-status` reports `STARTED`, `SUCCESS` or
  `FAILURE` (per their `help` text), never `completed`. Poll for `SUCCESS`,
  not for the experiment status vocabulary.
- Experiments use a different vocabulary: `resolving_profiles`, `generating`,
  `awaiting_review`, `running`, `judging`, `completed`, plus `failed` and
  `cancelled`.

## Agents and chat

- A `draft` agent cannot be chatted with: `algobot ask` returned HTTP 422
  "Agent is not published". Evaluations still run on drafts, so smoke test a
  draft with a 3-case experiment instead (see `commands/improve-agent.md`,
  Step 4).
- `conversations list --page` must use the long flag. The short `-p` collides
  with the global `--profile` flag ("Profile '2' not found").

## Datasets

- `experiments create` without `--dataset-id` resolved to an existing dataset
  for the same index, even when the agent differed. A second agent then
  inherited the first agent's tone contract. Always pass `--dataset-id` for
  comparisons and print a run card first
  ([../templates/run-card.md](../templates/run-card.md)).
- Generated tone cases carried a fixed style contract (for example no
  exclamation marks, no emoji, no ampersands, or no slang or hype words)
  regardless of the agent's own voice instructions. Review the contracts
  before trusting a tone score.

## Shell and timeouts

- zsh does not word-split unquoted variables. `for id in $IDS` iterates once
  over the whole string. Use `for id in ${=IDS}` in zsh, an array, or a
  `while read` loop.
- Long foreground polls can exceed the calling tool's shell timeout. Run them
  in the background or use `$SKILL_DIR/scripts/wait_experiments.py`
  (`SKILL_DIR` is the directory containing this skill's `SKILL.md`).
- The CLI sometimes printed "operation was aborted due to timeout" yet the
  call had succeeded server-side. Before retrying a mutation, check whether it
  landed (for example `experiments list` or `datasets list`) so you do not
  create a duplicate.
- A 150-case experiment took about 10 minutes end to end in our runs.
