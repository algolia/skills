---
description: Statically audit an Algolia Agent Studio agent config for prompt/tool mismatches and costly defaults before running any paid evaluation.
---

# Audit Agent (zero-cost static audit)

Read an Agent Studio agent's configuration and return a ranked fix list. No
completions, no judge calls, no writes: this costs nothing and should run
before any paid evaluation (`/improve-agent`).

Load the `agent-studio-evaluations` skill first. For CLI mechanics (install,
auth, profiles) see the `algobot-cli` skill; for what a healthy agent looks
like see the `algolia-agent-studio` skill (its Anti-Patterns section and
`references/agent-studio-guide.md`).

## Step 1: Get the config

Use a live agent id, or a config saved earlier (for example the output of
`algobot agents get <AGENT_ID>`, or `algobot agents export <AGENT_ID> --output agent.json`).
Do not paste credentials into the file.

## Step 2: Run the audit

`SKILL_DIR` is the directory containing the `agent-studio-evaluations`
skill's `SKILL.md` (wherever your agent installed it); the script lives in its
`scripts/` folder.

```bash
python3 "$SKILL_DIR/scripts/audit_agent.py" <AGENT_ID>
# or, offline:
python3 "$SKILL_DIR/scripts/audit_agent.py" agent.json
```

Run it with `--help` for options. The script only reads; it never patches or
publishes.

## Step 3: Read the findings

The script prints a ranked markdown fix list. Defect classes it checks:

| Check | Why it matters |
|---|---|
| Backticked identifiers in `instructions` that match no `tools[].name` / `type` or attached index name | Observed: a prompt named a display tool that was not attached under that name, and a prompt told the agent to search an index or tool that was not attached. The agent cannot follow either instruction. |
| Search tool with null `searchParameters` | Default retrieval is large (20 full records with highlight and snippet markup), which inflates input tokens and latency. See [Integration Facts](../skills/algolia-agent-studio/references/agent-studio-guide.md#integration-facts) in the `algolia-agent-studio` guide. |
| `max_iterations` set to 0 | 0 falls back to the service default (observed); set an explicit value if you want a specific tool-loop budget. |
| Deprecated config keys | Stale keys that `agents scaffold` 2.1.0 strips (for example `enableAlgoliaMcp`); remove them from saved configs. |

Treat each finding as a lead to confirm against the config, not as proof.
A heuristic match on a backticked word can be a false positive (for example a
field name the prompt quotes on purpose).

## Step 4: Report and hand off

Present the top fixes first, each with the config field to change and the
expected effect. Do not modify the agent from this command. To apply fixes
safely (draft clone, eval, explicit approval before promotion), continue with
`/improve-agent` (`commands/improve-agent.md`), and include the audit result
in its run card notes.
