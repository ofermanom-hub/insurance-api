# Dashboard Config Prompt

Convert the metrics section of the project manifest into a Grafana-compatible dashboard definition.

Output format:
```json
{
  "dashboards": [{
    "title": "...",
    "widgets": [
      {"type": "...", "metric": "...", "threshold": "...", "alert": "..."}
    ]
  }]
}
```

Also produce a mapping table: Metric -> Related Risk -> Alert Threshold.

---

```json
// paste full docs/project-manifest.json
```
