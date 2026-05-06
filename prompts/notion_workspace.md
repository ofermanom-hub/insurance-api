# Notion Workspace Prompt

Convert the full project manifest into a structured Notion workspace outline.

Output as Markdown with Notion-style hierarchy:

```
# Project Name
## Overview
## Architecture
## Risks
  ### Risk 1
  ### Risk 2
## Onboarding
  ### Phase 1
  ### Phase 2
## Metrics & Alerts
## Runbooks
## Decisions (ADRs)
```

Populate each section from the manifest. Add "Last Updated" and "Owner" at the top of each page.

---

```json
// paste full docs/project-manifest.json
```
