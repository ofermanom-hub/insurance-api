# Test Generation Prompt

Generate comprehensive pytest tests for the module below.

Include:
- Happy path (valid inputs, expected outputs)
- Edge cases (boundary values, empty/None, whitespace)
- Error cases (upstream failures, malformed data, invalid input)
- Use `pytest.mark.asyncio` for async functions
- Mock external HTTP calls with `respx` or `unittest.mock`

Target: 90%+ branch coverage.

---

```python
# paste module here
```
