# API Specification

## Base URL

`http://localhost:8080` (local dev)

---

## POST /vehicle-info

### Request Body

```json
{ "license_plate": "1234567" }
```

| Field | Type | Validation |
|-------|------|-----------|
| `license_plate` | string | 7-8 digits only |

### Success — 200

```json
{
  "success": true,
  "data": {
    "license_plate": "1234567",
    "manufacturer": "Toyota",
    "model": "Corolla",
    "year": "2020",
    "color": "White"
  }
}
```

### Errors

| Status | Code | Cause |
|--------|------|-------|
| 404 | `NOT_FOUND` | Vehicle not in upstream system |
| 422 | *(Pydantic)* | Invalid plate format |
| 429 | *(slowapi)* | Rate limit exceeded |
| 502 | `UPSTREAM_MALFORMED` | Upstream returned unexpected shape |
| 503 | `UPSTREAM_UNAVAILABLE` | Upstream unreachable after 3 retries |
| 500 | `INTERNAL_ERROR` | Unhandled exception |

---

## GET /health

```json
{"status": "ok"}
```
