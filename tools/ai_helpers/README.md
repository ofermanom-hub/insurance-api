# AI Helpers

Scripts and utilities that use Claude to automate project delivery tasks.

## Capabilities (via prompts/)

| Prompt | Output | Target tool |
|--------|--------|-------------|
| `gamma_risks.md` | Risk presentation | Gamma AI |
| `dashboard_config.md` | Metrics dashboard JSON | Grafana / Datadog |
| `monday_board.md` | Project board JSON | Monday.com |
| `notion_workspace.md` | Internal wiki structure | Notion |
| `full_pipeline.md` | All of the above | All tools |

## How to Run

Paste a prompt + the manifest into Claude Code:

```bash
cat docs/project-manifest.json
# then open the relevant prompt from prompts/
```

## Extending

Add a new prompt file in `prompts/` for any new tool.
Update `docs/project-manifest.json` as the project evolves.
The manifest is the single source of truth — everything else is a view on it.
