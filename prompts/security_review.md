# Security Review Prompt

Perform a security audit against OWASP Top 10.

Check for:
- Input validation gaps (injection, type confusion, oversized payloads)
- Sensitive data exposure (logs, error messages, responses)
- Authentication and authorization gaps
- Rate limiting and abuse vectors
- Insecure direct object references
- Dependency vulnerabilities

Output format:
```
[SEVERITY: HIGH/MEDIUM/LOW] <finding>
  File/line: <location>
  Risk: <what could go wrong>
  Fix: <concrete recommendation>
```

---

```python
# paste code here
```
