# Algobot CLI — Command Reference

## agents

```bash
algobot agents list [--jq '<expr>']
algobot agents get <agent-id>
algobot agents create --name <name> --model <model> [--config <file>] [--var k=v]
algobot agents update <agent-id> [--name <name>] [--model <model>] [--config <file>] [--var k=v] [--publish]
algobot agents patch <agent-id> --file <json-file>
algobot agents delete <agent-id>
algobot agents publish <agent-id>
algobot agents unpublish <agent-id>
algobot agents export <agent-id>                      # JSON to stdout
algobot agents copy <id> --from-env <env> --to-env <env>
algobot agents scaffold <agent-id>                    # → agent-config.json + PROMPT.md
algobot agents watch <patch-file>                     # Live reload on file change
algobot agents edit                                   # Open in $EDITOR
```

## ask / interactive

```bash
algobot ask "<prompt>"                                # One-shot, streams response
algobot interactive                                   # TUI (requires TTY)
algobot interactive --text "<prompt> ||| <prompt2>"  # Scripted multi-turn
```

## profiles

```bash
algobot profiles list
algobot profiles add --name <name> --env <dev|staging|prod>
algobot profiles show [name]                          # JSON output
algobot profiles setdefault <name>
algobot profiles remove <name>
```

## providers

```bash
algobot providers list
algobot providers get <provider-id>
algobot providers create --name <name>
algobot providers patch <provider-id> --file <json-file>
algobot providers delete <provider-id>
```

## tools

```bash
algobot tools list
algobot tools add --tool-file <json-file>
algobot tools remove <toolType>
```

## history / conversations

```bash
algobot history search "<query>"
algobot history recent [--short]
algobot history stats
algobot history interactive                           # Fuzzy search (requires TTY)
algobot history clear

algobot conversations list [--short]
algobot conversations get <id>
algobot conversations search "<query>"
algobot conversations export
algobot conversations delete <id>
```

## auth / permissions

```bash
algobot auth show                                     # Current credentials
algobot permissions list
algobot permissions init
algobot permissions add <path>
algobot permissions test --command "<cmd>"
algobot permissions logs
```

## Other

```bash
algobot init                                          # Interactive first-time wizard
algobot version
```

## Environment URLs

| Env | Base URL |
|-----|----------|
| `prod` | `https://agent-studio.eu.algolia.com` |
| `staging` | `https://agent-studio.staging.eu.algolia.com` |
| `dev` | `https://conversational-ai-dev.algolia.com` |
| `local` | `http://localhost:8000` |

## TUI Slash Commands (interactive mode only)

```
/config          Edit agent in $EDITOR
/model           Switch model interactively
/provider        Switch LLM provider
/temperature     Adjust creativity (0.0–2.0)
/reasoning       Set reasoning effort: minimal|low|medium|high
/verbosity       Set response verbosity: low|medium|high
/compact         Summarize conversation to free context
/tools           Show agent tools
/context         Token usage stats
/verbose         Toggle HTTP logging
/search <q>      Search conversation history
/conversations   List recent conversations
/reset           Clear conversation context
/help            Full command list
```
