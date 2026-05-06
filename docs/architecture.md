# Architecture

## Overview

Insurance API is a FastAPI proxy that validates Israeli license plates and retrieves vehicle data from an upstream service.

## Request Flow

```
Client
  └─ POST /vehicle-info
       └─ Input validation (Pydantic / PlateRequest)
            └─ core/vehicle_lookup.py
                 └─ integrations/vehicle_service.py → Upstream API
                 ← (vehicle dict, error_code)
            ← (vehicle dict, error_code, http_status)
       ← JSON response
```

## Layer Responsibilities

| Layer | Path | Responsibility |
|-------|------|----------------|
| API | `src/api/` | HTTP routing, rate limiting, response shaping |
| Core | `src/core/` | Business logic, plate masking, error-to-status mapping |
| Integrations | `src/integrations/` | Upstream HTTP calls, retry/backoff |
| Models | `src/models/` | Pydantic request/response schemas |
| Config | `src/config/` | Environment-based settings |
| Auth | `src/auth/` | Auth layer (placeholder for JWT/SAML) |

## Key Design Decisions

- **Retry with exponential backoff** — up to 3 attempts (0.5s, 1.0s)
- **Rate limiting** — 30 req/min per IP via slowapi
- **Plate masking in logs** — last 2 digits only; full plates never appear in logs
- **Env-based Swagger** — `/docs` and `/redoc` disabled in `production`
- **Layer separation** — `core/` has zero HTTP dependencies; fully unit-testable
