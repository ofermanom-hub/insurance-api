# Monday.com Board Prompt

Convert the onboarding section of the project manifest into a Monday.com board structure.

Output format:
```json
{
  "groups": [{
    "name": "Phase name",
    "tasks": [
      {"name": "...", "owner": "...", "status": "Not Started", "risk_flag": false}
    ]
  }]
}
```

Rules:
- Add sensible owner roles (Dev, PM, Architect, QA)
- Flag tasks that have an associated risk in the manifest
- Add dependencies where logical order matters

---

```json
// paste full docs/project-manifest.json
```
