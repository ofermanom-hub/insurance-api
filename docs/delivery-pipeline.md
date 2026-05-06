# Delivery Pipeline

`docs/project-manifest.json` is the single source of truth. Claude translates it into outputs for every tool.

## Flow

```
docs/project-manifest.json
        |
        +-- prompts/gamma_risks.md       --> Gamma (risk slides)
        +-- prompts/dashboard_config.md  --> Grafana / Datadog (metrics)
        +-- prompts/monday_board.md      --> Monday.com (project board)
        +-- prompts/notion_workspace.md  --> Notion (knowledge base)
        +-- prompts/full_pipeline.md     --> all outputs in one run
```

## How To Use

1. Update `docs/project-manifest.json` with current project state
2. Open the relevant prompt from `prompts/`
3. Paste the manifest + prompt into Claude
4. Paste the output into the target tool
